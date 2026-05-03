# L'atelier
Computational Gastronomy project

**Summary:** Develop Molecular Food Pairing Engine for Restaurant Formula Licensing

**Description:**
The objective is to build a predictive model that identifies optimal food pairings based on molecular chemistry. The primary business use case is to license these data-driven formulas to restaurants. By integrating a **Recipe Book Knowledge Graph**, the system utilizes **RAG (Retrieval-Augmented Generation)** to bridge the gap between raw chemical data and culinary tradition, providing context-aware ingredient substitutes.

A key challenge the model accounts for is genetic flavor sensitivities, specifically the **OR6A2** gene mutation, which causes certain populations (10–20%, predominantly East Asians) to perceive aldehydes in cilantro as "soapy" rather than herbal.

**User Story:**
As a Restaurant Menu Developer, I want to access chemically validated food pairings and ingredient substitutes—informed by both molecular science and historical recipe data—so that I can create universally appealing recipes and license proprietary flavor formulas.

---

## Technical Architecture: Knowledge Graph Specification

To ensure high-performance RAG and molecular similarity lookups, the system utilizes a single Neo4j graph with the following node and relationship specifications.

### 1. Node Types & Properties

| Domain | Label | Property | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Culinary** | `:Recipe` | `id` | UUID | Primary Key |
| | | `title` | String | Dish name |
| | | `instructions` | Text | Raw preparation steps |
| | | `embedding` | Vector(1536) | Semantic vector for RAG |
| | `:Ingredient` | `name` | String | Resolved entity name (e.g., "Cilantro") |
| | | `foodb_id` | Integer | FK to FooDB |
| | | `raw_names` | Array | Aliases found in text (e.g., "Chinese Parsley") |
| | `:Technique` | `name` | String | e.g., "Fermentation", "Sous-vide", "Smoking" |
| | | `type` | String | Thermal, Chemical, or Mechanical |
| | | `embedding` | Vector(1536) | Semantic vector for process similarity |
| **Chemical** | `:Compound` | `cid` | String | Compound ID (FooDB/PubChem) |
| | | `smiles` | String | SMILES notation for RDKit |
| | | `fingerprint` | Vector(2048) | RDKit Morgan Fingerprint (Bit-vector) |
| | `:FlavorProfile`| `descriptor` | String | Sensory tags (e.g., "Nutty", "Soapy") |
| **Biological**| `:OdorReceptor` | `gene_symbol` | String | e.g., "OR6A2" |
| | `:Perception` | `genotype` | String | e.g., "Carrier", "Non-Carrier" |

### 2. Relationship Schema (Edges)

*   `(:Recipe)-[:CONTAINS {quantity: float, unit: string}]->(:Ingredient)`
*   `(:Recipe)-[:USES_TECHNIQUE]->(:Technique)`
*   `(:Ingredient)-[:HAS_COMPOUND {concentration: float}]->(:Compound)`
*   `(:Compound)-[:HAS_FLAVOR {intensity: int}]->(:FlavorProfile)`
*   `(:Compound)-[:TRIGGERS]->(:OdorReceptor)`
*   `(:OdorReceptor)-[:AFFECTS {valence: string}]->(:Perception)`
*   `(:Ingredient)-[:MOLECULAR_MATCH {score: float}]->(:Ingredient)`

---

## Implementation Roadmap

### Data Acquisition & Knowledge Engineering
* **Pipeline:** Integrate datasets from **FooDB** and **FlavorDB**.
* **NER & Linking:** Extract ingredients from recipe books and map them to `foodb_id` via semantic similarity.
* **Graph-RAG Pipeline:** Use Neo4j Vector Search on `:Recipe(embedding)` and `:Compound(fingerprint)` to provide hybrid retrieval.

### Library Implementation
* **RDKit:** Calculate Tanimoto similarity between `:Compound` fingerprints to generate `:MOLECULAR_MATCH` edges.
* **M2OR:** Map compounds to `:OdorReceptor` nodes to simulate sensory perception.

### Algorithm Development
* **The "Genetic Filter":** A Cypher query that traverses `(:Ingredient)-[:HAS_COMPOUND]->(c)-[:TRIGGERS]->(:OdorReceptor {gene_symbol: "OR6A2"})` to flag high-risk items.
* **Hybrid Scoring:** 
    1. **Chemical Similarity:** Shared molecular profiles.
    2. **Culinary Co-occurrence:** Graph-based frequency in existing recipes.

---

## Acceptance Criteria
* [ ] System can successfully parse a SMILES string and return its molecular properties.
* [ ] Model identifies ingredients with high "soap-flavor" risk for OR6A2 carriers.
* [ ] **RAG Functionality:** System can provide a "Reasoning Path" for a pairing (e.g., "Pairing X works chemically via Y molecule and is historically validated in Z cuisine").
* [ ] Output provides a "Pairing Score" between two given ingredients using RDKit and Graph-derived weights.
* [ ] The database includes at least 80% coverage of common commercial restaurant ingredients.

---

## Assumptions & Constraints
* **Data Standardization:** All chemical data must be converted to SMILES format for consistency across FooDB and FlavorDB.
* **Contextual Variance:** The model must treat "flavor perception" as a variable (User A vs. User B) due to the OR6A2 findings.
* **LLM Dependency:** The RAG component requires a stable connection to an LLM for synthesizing Knowledge Graph queries into natural language advice.

---

## Reference Links
* **M2OR Mapping:** [https://m2or.chemsensim.fr](https://m2or.chemsensim.fr)
* **RDKit Documentation:** [https://www.rdkit.org/docs/GettingStartedInPython.html](https://www.rdkit.org/docs/GettingStartedInPython.html)
* **FooDB Downloads:** [https://foodb.ca/downloads](https://foodb.ca/downloads)
* **FlavorDB Search:** [https://cosylab.iiitd.edu.in/flavordb/search](https://cosylab.iiitd.edu.in/flavordb/search)