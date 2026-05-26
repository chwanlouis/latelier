from typing import Any, Dict, List, Optional
from neomodel import adb
from tools.neo4jtools import neo4j_manager
from tools.log import logger
from model.response.graph import GraphEdge, GraphNode, GraphResponse

_FOOD_SUBGRAPH_QUERY = """
MATCH (f:Food {food_id: $food_id})
OPTIONAL MATCH (f)-[rc:CONTAINS_COMPOUND]->(c:Compound)
OPTIONAL MATCH (f)-[rn:HAS_NUTRIENT]->(n:Nutrient)
OPTIONAL MATCH (c)-[rf:HAS_FLAVOR]->(fl:Flavor)
RETURN
    f,
    collect(DISTINCT {compound: c, rel: rc}) AS compound_rels,
    collect(DISTINCT {nutrient: n, rel: rn}) AS nutrient_rels,
    collect(DISTINCT {compound: c, flavor: fl, rel: rf}) AS flavor_rels
"""

_ALL_FOODS_QUERY = """
MATCH (f:Food)
WITH f SKIP $skip LIMIT $limit
OPTIONAL MATCH (f)-[rc:CONTAINS_COMPOUND]->(c:Compound)
OPTIONAL MATCH (f)-[rn:HAS_NUTRIENT]->(n:Nutrient)
RETURN
    f,
    collect(DISTINCT {compound: c, rel: rc}) AS compound_rels,
    collect(DISTINCT {nutrient: n, rel: rn}) AS nutrient_rels
"""


def _node_id(neo4j_node) -> Optional[str]:
    """Return a stable string identifier for a neo4j node."""
    if neo4j_node is None:
        return None
    element_id = getattr(neo4j_node, "element_id", None) or str(neo4j_node.id)
    return str(element_id)


def _node_props(neo4j_node) -> Dict[str, Any]:
    """Extract serialisable properties from a neo4j node."""
    if neo4j_node is None:
        return {}
    try:
        return dict(neo4j_node.items())
    except Exception:
        return {}


def _rel_props(neo4j_rel) -> Dict[str, Any]:
    """Extract serialisable properties from a neo4j relationship."""
    if neo4j_rel is None:
        return {}
    try:
        return dict(neo4j_rel.items())
    except Exception:
        return {}


def _primary_label(neo4j_node) -> str:
    """Return the first label of a node."""
    if neo4j_node is None:
        return "Unknown"
    try:
        labels = list(neo4j_node.labels)
        return labels[0] if labels else "Unknown"
    except Exception:
        return "Unknown"


def _process_compound_rels(
    food_node,
    compound_rels: List[Dict],
    nodes: Dict[str, GraphNode],
    edges: List[GraphEdge],
) -> None:
    """Add compound nodes and food→compound edges to the accumulators."""
    fid = _node_id(food_node)
    for entry in compound_rels:
        c_node = entry.get("compound")
        rel = entry.get("rel")
        if c_node is None:
            continue
        cid = _node_id(c_node)
        if cid and cid not in nodes:
            nodes[cid] = GraphNode(
                id=cid,
                label=_primary_label(c_node),
                properties=_node_props(c_node),
            )
        if food_node is not None and cid and fid:
            rel_type = rel.type if rel else "CONTAINS_COMPOUND"
            edges.append(
                GraphEdge(
                    source=fid,
                    target=cid,
                    type=rel_type,
                    properties=_rel_props(rel),
                )
            )


def _process_nutrient_rels(
    food_node,
    nutrient_rels: List[Dict],
    nodes: Dict[str, GraphNode],
    edges: List[GraphEdge],
) -> None:
    """Add nutrient nodes and food→nutrient edges to the accumulators."""
    fid = _node_id(food_node)
    for entry in nutrient_rels:
        n_node = entry.get("nutrient")
        rel = entry.get("rel")
        if n_node is None:
            continue
        nid = _node_id(n_node)
        if nid and nid not in nodes:
            nodes[nid] = GraphNode(
                id=nid,
                label=_primary_label(n_node),
                properties=_node_props(n_node),
            )
        if food_node is not None and nid and fid:
            rel_type = rel.type if rel else "HAS_NUTRIENT"
            edges.append(
                GraphEdge(
                    source=fid,
                    target=nid,
                    type=rel_type,
                    properties=_rel_props(rel),
                )
            )


class GraphRepository:
    def __init__(self):
        if not neo4j_manager._initialized:
            neo4j_manager.initialize_ogm()

    async def get_food_subgraph(self, food_id: str) -> GraphResponse:
        """Return a graph centred on the food identified by *food_id*."""
        try:
            results, _ = await adb.cypher_query(
                _FOOD_SUBGRAPH_QUERY, {"food_id": food_id}
            )
        except Exception as exc:
            logger.error(f"GraphRepository.get_food_subgraph failed: {exc}")
            raise exc

        nodes: Dict[str, GraphNode] = {}
        edges: List[GraphEdge] = []

        for row in results:
            food_node, compound_rels, nutrient_rels, flavor_rels = row

            if food_node is not None:
                fid = _node_id(food_node)
                if fid and fid not in nodes:
                    nodes[fid] = GraphNode(
                        id=fid,
                        label=_primary_label(food_node),
                        properties=_node_props(food_node),
                    )

            _process_compound_rels(food_node, compound_rels, nodes, edges)
            _process_nutrient_rels(food_node, nutrient_rels, nodes, edges)

            for entry in flavor_rels:
                c_node = entry.get("compound")
                fl_node = entry.get("flavor")
                rel = entry.get("rel")
                if c_node is None or fl_node is None:
                    continue
                cid = _node_id(c_node)
                flid = _node_id(fl_node)
                if flid and flid not in nodes:
                    nodes[flid] = GraphNode(
                        id=flid,
                        label=_primary_label(fl_node),
                        properties=_node_props(fl_node),
                    )
                if cid and flid:
                    rel_type = rel.type if rel else "HAS_FLAVOR"
                    edges.append(
                        GraphEdge(
                            source=cid,
                            target=flid,
                            type=rel_type,
                            properties=_rel_props(rel),
                        )
                    )

        return GraphResponse(nodes=list(nodes.values()), edges=edges)

    async def get_foods_graph(self, skip: int = 0, limit: int = 50) -> GraphResponse:
        """Return a paged graph of food nodes with their compounds and nutrients."""
        try:
            results, _ = await adb.cypher_query(
                _ALL_FOODS_QUERY, {"skip": skip, "limit": limit}
            )
        except Exception as exc:
            logger.error(f"GraphRepository.get_foods_graph failed: {exc}")
            raise exc

        nodes: Dict[str, GraphNode] = {}
        edges: List[GraphEdge] = []

        for row in results:
            food_node, compound_rels, nutrient_rels = row

            if food_node is not None:
                fid = _node_id(food_node)
                if fid and fid not in nodes:
                    nodes[fid] = GraphNode(
                        id=fid,
                        label=_primary_label(food_node),
                        properties=_node_props(food_node),
                    )

            _process_compound_rels(food_node, compound_rels, nodes, edges)
            _process_nutrient_rels(food_node, nutrient_rels, nodes, edges)

        return GraphResponse(nodes=list(nodes.values()), edges=edges)


graph_repository = GraphRepository()
