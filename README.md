# L'atelier
Computational Gastronomy project

**Summary:** Develop Molecular Food Pairing Engine for Restaurant Formula Licensing

**Description:**
The objective is to build a predictive model that identifies optimal food pairings based on molecular chemistry. The primary business use case is to license these data-driven formulas to restaurants. A key challenge the model must account for is genetic flavor sensitivities, specifically the **OR6A2** gene mutation, which causes certain populations (10–20%, predominantly East Asians) to perceive aldehydes in cilantro as "soapy" rather than herbal.

**User Story:**
As a Restaurant Menu Developer, I want to access chemically validated food pairings and ingredient substitutes so that I can create universally appealing recipes and license proprietary flavor formulas.

---

## Technical Requirements / Tasks

### Data Acquisition
* Integrate and clean datasets from **FooDB** and **FlavorDB**.
* Ingest **SMILES** (Simplified Molecular Input Line Entry System) strings as the primary chemical notation format.

### Library Implementation
* Set up **RDKit** in a Python environment for cheminformatics processing.
* Integrate the **M2OR** (Molecule to Odor Receptors) mapping library to simulate sensory perception.

### Algorithm Development
* Map molecules to specific odor receptors.
* Build a **"Genetic Filter"** to identify ingredients containing aldehydes that trigger the OR6A2 receptor.
* Develop a scoring algorithm for "pairing compatibility" based on shared or complementary molecular profiles.

---

## Acceptance Criteria
* [ ] System can successfully parse a SMILES string and return its molecular properties.
* [ ] Model identifies ingredients with high "soap-flavor" risk for OR6A2 carriers.
* [ ] Output provides a "Pairing Score" between two given ingredients using RDKit-processed data.
* [ ] The database includes at least 80% coverage of common commercial restaurant ingredients.

---

## Assumptions & Constraints
* **Standardization:** All chemical data must be converted to SMILES format for consistency across FooDB and FlavorDB.
* **Genetic Variation:** The model must treat "flavor perception" as a variable (User A vs. User B) rather than a fixed attribute, due to the OR6A2 findings.
* **External Dependencies:** Access to the documentation/APIs for the libraries listed below must remain stable.

---

## Reference Links
* **M2OR Mapping:** [https://m2or.chemsensim.fr](https://m2or.chemsensim.fr)
* **RDKit Documentation:** [https://www.rdkit.org/docs/GettingStartedInPython.html](https://www.rdkit.org/docs/GettingStartedInPython.html)
* **FooDB Downloads:** [https://foodb.ca/downloads](https://foodb.ca/downloads)
* **FlavorDB Search:** [https://cosylab.iiitd.edu.in/flavordb/search](https://cosylab.iiitd.edu.in/flavordb/search)