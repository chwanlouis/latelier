"""
ingest_recipes.py — Parse A_GUIDE_TO_MODERN_COOKERY.txt and insert Recipe + Technique
nodes into Neo4j according to the Knowledge Graph schema in README.md.

Usage:
    python -m scripts.ingest_recipes [--data-path PATH] [--embed]

Options:
    --data-path PATH   Path to the cookbook txt file.
                       Default: mcp/data/A_GUIDE_TO_MODERN_COOKERY.txt
    --embed            Compute OpenAI text-embedding-3-small embeddings and store
                       them on each Recipe node (requires OPENAI_API_KEY env var).
    --batch-size N     Number of recipes to insert per Neo4j transaction (default 50).
    --dry-run          Parse only; print the first 5 recipes without writing to Neo4j.

The script splits the book on the pattern  NUMBER-- TITLE  which marks every
numbered recipe heading.  The full text up to the next heading becomes the
recipe's `instructions` field.  Technique keywords are matched against the
title and instructions to create :Technique nodes and :USES_TECHNIQUE edges.
"""

from __future__ import annotations

import argparse
import asyncio
import re
import uuid
from pathlib import Path
from typing import NamedTuple

# ---------------------------------------------------------------------------
# Technique keyword mapping
# ---------------------------------------------------------------------------
# Maps a canonical technique name (and Neo4j node type) to a list of lowercase
# keyword fragments that indicate the technique is used in a recipe.
TECHNIQUE_MAP: dict[str, tuple[str, list[str]]] = {
    "Boiling":    ("Thermal",    ["boil", "boiling", "boiled"]),
    "Simmering":  ("Thermal",    ["simmer", "simmering"]),
    "Poaching":   ("Thermal",    ["poach", "poaching", "poached"]),
    "Steaming":   ("Thermal",    ["steam", "steaming", "steamed"]),
    "Roasting":   ("Thermal",    ["roast", "roasting", "roasted"]),
    "Grilling":   ("Thermal",    ["grill", "grilling", "grilled"]),
    "Frying":     ("Thermal",    ["fry", "frying", "fried", "deep-fry", "sauté", "saute"]),
    "Braising":   ("Thermal",    ["brais", "braised", "braising"]),
    "Baking":     ("Thermal",    ["bak", "baked", "baking"]),
    "Broiling":   ("Thermal",    ["broil", "broiled", "broiling"]),
    "Smoking":    ("Thermal",    ["smok", "smoking", "smoked"]),
    "Fermenting": ("Chemical",   ["ferment", "fermenting", "fermented"]),
    "Curing":     ("Chemical",   ["cur", "curing", "cured"]),
    "Pickling":   ("Chemical",   ["pickl", "pickling", "pickled"]),
    "Marinating": ("Chemical",   ["marinat", "marinating", "marinated"]),
    "Pounding":   ("Mechanical", ["pound", "pounding", "pounded"]),
    "Grinding":   ("Mechanical", ["grind", "grinding", "ground"]),
    "Kneading":   ("Mechanical", ["knead", "kneading", "kneaded"]),
    "Whipping":   ("Mechanical", ["whip", "whipping", "whipped"]),
    "Straining":  ("Mechanical", ["strain", "straining", "strained"]),
}

# Pre-compile a combined regex per technique for performance
_TECHNIQUE_PATTERNS: dict[str, tuple[str, re.Pattern[str]]] = {
    name: (typ, re.compile("|".join(kw), re.IGNORECASE))
    for name, (typ, kw) in TECHNIQUE_MAP.items()
}

# ---------------------------------------------------------------------------
# Recipe data class
# ---------------------------------------------------------------------------

class ParsedRecipe(NamedTuple):
    number: int
    title: str
    instructions: str
    techniques: list[tuple[str, str]]  # [(name, type), ...]


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

# Matches a recipe heading: a number at the start of a line followed by an
# em-dash (—) and the recipe title.  Some entries span two physical lines.
_HEADING_RE = re.compile(r"^(\d+)—\s*(.+)$", re.MULTILINE)


def _detect_techniques(text: str) -> list[tuple[str, str]]:
    """Return (name, type) pairs for every technique found in *text*."""
    found: list[tuple[str, str]] = []
    for name, (typ, pattern) in _TECHNIQUE_PATTERNS.items():
        if pattern.search(text):
            found.append((name, typ))
    return found


def parse_book(text: str) -> list[ParsedRecipe]:
    """Split *text* into individual recipes using numbered headings as delimiters."""
    matches = list(_HEADING_RE.finditer(text))
    recipes: list[ParsedRecipe] = []

    for idx, match in enumerate(matches):
        number = int(match.group(1))
        # Title may wrap onto the next physical line — take everything on
        # the same line, then optionally the immediately following line if
        # it looks like a continuation (all-caps words, no numbers).
        raw_title = match.group(2).strip()
        end_of_match = match.end()

        # Determine where the next recipe starts
        next_start = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)

        # Check whether the title continues on the very next line
        after_heading = text[end_of_match:next_start]
        first_line = after_heading.split("\n")[0].strip() if after_heading else ""
        # If the line is all-caps (common for split titles) and short, treat
        # it as a continuation of the title
        if first_line and re.fullmatch(r"[A-Z][A-Z\s',=\-\.()]+", first_line) and len(first_line) <= 80:
            raw_title = f"{raw_title} {first_line}"
            # Skip that line in the instructions
            rest = "\n".join(after_heading.split("\n")[1:])
        else:
            rest = after_heading

        # Clean up OCR artefacts: collapse multiple spaces / normalise whitespace
        title = re.sub(r"\s{2,}", " ", raw_title).strip()
        instructions = re.sub(r"[ \t]{2,}", " ", rest).strip()

        techniques = _detect_techniques(f"{title} {instructions}")
        recipes.append(ParsedRecipe(number, title, instructions, techniques))

    return recipes


# ---------------------------------------------------------------------------
# Neo4j insertion
# ---------------------------------------------------------------------------

async def _ensure_technique(session, name: str, typ: str) -> None:
    """MERGE a :Technique node so duplicates are never created."""
    await session.run(
        """
        MERGE (t:Technique {name: $name})
        ON CREATE SET t.type = $type
        """,
        name=name,
        type=typ,
    )


async def insert_recipes(
    recipes: list[ParsedRecipe],
    neo4j_uri: str,
    neo4j_user: str,
    neo4j_password: str,
    batch_size: int = 50,
    embeddings: dict[int, list[float]] | None = None,
) -> None:
    """Insert ParsedRecipe objects into Neo4j."""
    from neo4j import AsyncGraphDatabase

    driver = AsyncGraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    try:
        async with driver.session() as session:
            # Create unique constraint (idempotent)
            await session.run(
                "CREATE CONSTRAINT recipe_id IF NOT EXISTS "
                "FOR (r:Recipe) REQUIRE r.id IS UNIQUE"
            )
            await session.run(
                "CREATE CONSTRAINT technique_name IF NOT EXISTS "
                "FOR (t:Technique) REQUIRE t.name IS UNIQUE"
            )

        total = len(recipes)
        for batch_start in range(0, total, batch_size):
            batch = recipes[batch_start : batch_start + batch_size]
            async with driver.session() as session:
                async with session.begin_transaction() as tx:
                    for recipe in batch:
                        recipe_id = str(uuid.uuid4())
                        emb = embeddings.get(recipe.number) if embeddings else None
                        props: dict = {
                            "id": recipe_id,
                            "title": recipe.title,
                            "instructions": recipe.instructions,
                            "book_number": recipe.number,
                        }
                        if emb is not None:
                            props["embedding"] = emb

                        # MERGE on book_number to make the script re-runnable
                        await tx.run(
                            """
                            MERGE (r:Recipe {book_number: $book_number})
                            ON CREATE SET r += $props
                            ON MATCH  SET r.title = $props.title,
                                         r.instructions = $props.instructions
                            """,
                            book_number=recipe.number,
                            props=props,
                        )

                        for tech_name, tech_type in recipe.techniques:
                            await tx.run(
                                """
                                MERGE (t:Technique {name: $name})
                                ON CREATE SET t.type = $type
                                WITH t
                                MATCH (r:Recipe {book_number: $book_number})
                                MERGE (r)-[:USES_TECHNIQUE]->(t)
                                """,
                                name=tech_name,
                                type=tech_type,
                                book_number=recipe.number,
                            )

                    await tx.commit()

            done = min(batch_start + batch_size, total)
            print(f"  Inserted {done}/{total} recipes…")

    finally:
        await driver.close()

    print("Done.")


# ---------------------------------------------------------------------------
# Optional embedding computation
# ---------------------------------------------------------------------------

async def compute_embeddings(
    recipes: list[ParsedRecipe], api_key: str
) -> dict[int, list[float]]:
    """Compute text-embedding-3-small embeddings for each recipe."""
    try:
        from openai import AsyncOpenAI
    except ImportError:
        raise SystemExit(
            "openai package is required for --embed.  "
            "Install it with: pip install openai"
        )

    client = AsyncOpenAI(api_key=api_key)
    result: dict[int, list[float]] = {}
    batch_size = 100  # OpenAI allows up to 2048 inputs per request

    all_numbers = [r.number for r in recipes]
    all_texts = [f"{r.title}\n\n{r.instructions[:2000]}" for r in recipes]

    for i in range(0, len(all_texts), batch_size):
        batch_texts = all_texts[i : i + batch_size]
        batch_numbers = all_numbers[i : i + batch_size]
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=batch_texts,
        )
        for j, emb_obj in enumerate(response.data):
            result[batch_numbers[j]] = emb_obj.embedding
        print(f"  Computed embeddings {i + len(batch_texts)}/{len(all_texts)}…")

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    default_data = (
        Path(__file__).parent.parent / "data" / "A_GUIDE_TO_MODERN_COOKERY.txt"
    )
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-path", default=str(default_data), help="Path to cookbook txt file")
    p.add_argument("--embed", action="store_true", help="Compute and store OpenAI embeddings")
    p.add_argument("--batch-size", type=int, default=50, help="Neo4j insert batch size")
    p.add_argument("--dry-run", action="store_true", help="Parse only; print first 5 recipes")
    p.add_argument("--neo4j-uri", default=None, help="Neo4j bolt URI (overrides NEO4J_URI env var)")
    p.add_argument("--neo4j-user", default=None, help="Neo4j user (overrides NEO4J_USER env var)")
    p.add_argument("--neo4j-password", default=None, help="Neo4j password (overrides NEO4J_PASSWORD env var)")
    return p


async def main() -> None:
    import os

    args = _build_arg_parser().parse_args()

    data_path = Path(args.data_path)
    if not data_path.exists():
        raise SystemExit(f"Data file not found: {data_path}")

    print(f"Reading {data_path} …")
    text = data_path.read_text(encoding="utf-8", errors="replace")

    print("Parsing recipes…")
    recipes = parse_book(text)
    print(f"  Found {len(recipes)} recipes.")

    if args.dry_run:
        for r in recipes[:5]:
            print(f"\n[{r.number}] {r.title}")
            print(f"  Techniques: {[t[0] for t in r.techniques]}")
            print(f"  Instructions (first 200 chars): {r.instructions[:200]!r}")
        return

    neo4j_uri = args.neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = args.neo4j_user or os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = args.neo4j_password or os.getenv("NEO4J_PASSWORD", "password")

    embeddings: dict[int, list[float]] | None = None
    if args.embed:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise SystemExit("OPENAI_API_KEY environment variable is required for --embed")
        print("Computing embeddings…")
        embeddings = await compute_embeddings(recipes, api_key)

    print(f"Inserting into Neo4j at {neo4j_uri} …")
    await insert_recipes(
        recipes,
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
        batch_size=args.batch_size,
        embeddings=embeddings,
    )


if __name__ == "__main__":
    asyncio.run(main())
