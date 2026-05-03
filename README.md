# L'atelier
Computational Gastronomy project

**Summary:** Develop Molecular Food Pairing Engine for Restaurant Formula Licensing

**Description:**
The objective is to build a predictive model that identifies optimal food pairings based on molecular chemistry. The primary business use case is to license these data-driven formulas to restaurants. By integrating a **Recipe Book Knowledge Graph**, the system utilizes **RAG (Retrieval-Augmented Generation)** to bridge the gap between raw chemical data and culinary tradition, providing context-aware ingredient substitutes.

A key challenge the model accounts for is genetic flavor sensitivities, specifically the **OR6A2** gene mutation, which causes certain populations (10–20%, predominantly East Asians) to perceive aldehydes in cilantro as "soapy" rather than herbal.

**User Story:**
As a Restaurant Menu Developer, I want to access chemically validated food pairings and ingredient substitutes—informed by both molecular science and historical recipe data—so that I can create universally appealing recipes and license proprietary flavor formulas.

---

## Technical Requirements / Tasks

### Data Acquisition & Knowledge Engineering
* Integrate and clean datasets from **FooDB** and **FlavorDB**.
* Ingest **SMILES** (Simplified Molecular Input Line Entry System) strings as the primary chemical notation format.
* **Knowledge Graph Construction:** Ingest digitized recipe books to create a graph of ingredient relationships, techniques, and regional flavor profiles.

### Library & Architecture Implementation
* Set up **RDKit** in a Python environment for cheminformatics processing.
* Integrate the **M2OR** (Molecule to Odor Receptors) mapping library to simulate sensory perception.
* **Graph-RAG Pipeline:** Implement a vector database (e.g., Weaviate or Pinecone) alongside a Graph Database (e.g., Neo4j) to retrieve recipe-based context for molecular pairings.

### Algorithm Development
* Map molecules to specific odor receptors.
* Build a **"Genetic Filter"** to identify ingredients containing aldehydes that trigger the OR6A2 receptor.
* Develop a **Hybrid Scoring Algorithm** for pairing compatibility based on:
    1. **Chemical Similarity:** Shared molecular profiles.
    2. **Culinary Co-occurrence:** Frequency and success in the Recipe Knowledge Graph.

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