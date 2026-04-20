# FooDB Data Reference

1. The `AccessionNumber.csv` file serves as a **cross-reference registry**. It maps L'atelier's internal `compound_id` to external accession numbers used by international scientific databases. This enables the engine to fetch external metadata (like precise odor thresholds or binding affinities) that may not be present in the local FooDB export.


| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | The primary key for this specific record. | Internal database management. |
| **`number`** | String | The actual identifier from the external source (e.g., "CID 12345", "HMDB00001"). | Used for API lookups in external databases like PubChem or HMDB. |
| **`compound_id`** | Integer | Foreign key linking to `Compound.csv`. | Connects an external identity to a specific molecule in the engine. |
| **`created_at`** | Timestamp | The date and time the record was added to the database. | Data lineage and version control. |
| **`updated_at`** | Timestamp | The date and time the record was last modified. | Ensuring the most recent cross-reference is used. |
| **`source_id`** | Integer | Internal reference ID for the data source provider. | Tracking the origin of the cross-reference entry. |
| **`source_type`** | String | The name/category of the external database (e.g., "PubchemCompound", "Hmdb", "ChemSpider"). | Tells the engine which external API or schema to use for data enrichment. |

---

2. The `Compound.csv` file is the **central nervous system** of the L'atelier engine. It contains the molecular blueprints required for chemical vectorization, structural similarity analysis, and taxonomic classification. Every flavor pairing and genetic exclusion calculation starts here.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | The unique identifier used to join with `Content.csv` and `CompoundsFlavor.csv`. |
| **`public_id`** | String | External-facing unique ID. | Used for stable referencing in public APIs or exported recipes. |
| **`name`** | String | Common chemical name. | Display name for the chef (e.g., "Linalool" or "Vanillin"). |
| **`moldb_iupac`** | String | Systematic IUPAC name. | Used for disambiguation and precise chemical identification. |
| **`state`** | String | Physical state at room temp. | Critical for **Thermodynamic State** logic (Solid vs. Liquid vs. Gas). |
| **`annotation_quality`** | String | Data reliability score. | Filters out "noise" or unverified compounds from calculations. |
| **`description`** | Text | Chemical characteristics. | Provides contextual notes for the R&D process. |
| **`cas_number`** | String | Chemical Abstracts Service ID. | Standardized global ID for cross-referencing external safety data. |
| **`moldb_inchikey`** | String | 27-character hashed ID. | Used for ultra-fast database indexing and collision-free chemical matching. |
| **`moldb_inchi`** | String | IUPAC Chemical Identifier. | A non-proprietary identifier used in advanced bioinformatics. |
| **`moldb_smiles`** | String | Molecular ASCII string. | **CRITICAL:** The input for RDKit to generate the **2048-bit fingerprints** for Tanimoto Similarity. |
| **`moldb_mono_mass`** | Float | Monoisotopic mass. | Used in precision infusion calculations and molecular weight analysis. |
| **`kingdom`** | String | Biological Kingdom. | High-level classification (e.g., Organic Compounds). |
| **`superklass`** | String | Major chemical class. | Defines broad behavior (e.g., Lipids and lipid-like molecules). |
| **`klass`** | String | Mid-level chemical class. | Refines flavor logic (e.g., Prenol lipids). |
| **`subklass`** | String | Specific chemical subclass. | Fine-grained grouping (e.g., Terpene lactones). |

---

3. FILE: CompoundAlternateParent.csv

This file maps secondary hierarchical classifications. Many flavor compounds belong to multiple structural families; this table ensures the engine captures these multi-dimensional relationships.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier for the mapping record. |
| **`name`** | String | Alternate Class Name. | The name of the secondary chemical family (e.g., "Fatty Acids"). |
| **`compound_id`** | Integer | Foreign Key. | Links to `Compound.csv`. |
| **`creator_id`** | Integer | Metadata. | Tracking user/system creation. |
| **`updater_id`** | Integer | Metadata. | Tracking record modifications. |
| **`created_at`** | Timestamp | Metadata. | Record creation timestamp. |
| **`updated_at`** | Timestamp | Metadata. | Last update timestamp. |

---

4. FILE: CompoundExternalDescriptor.csv

This table stores descriptive metadata and annotations from external databases (e.g., ChEBI, PubChem). It is vital for understanding the "character" of a molecule beyond its formula.




| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier for the descriptor. |
| **`external_id`** | String | External DB Reference. | ID from the source database (e.g., "CHEBI:1234"). |
| **`annotations`** | Text | Descriptive Text. | Natural language descriptions of the molecule's properties. |
| **`compound_id`** | Integer | Foreign Key. | Links the description to the molecule. |
| **`creator_id`** | Integer | Metadata. | Data lineage tracking. |
| **`updater_id`** | Integer | Metadata. | Data lineage tracking. |
| **`created_at`** | Timestamp | Metadata. | Metadata. |
| **`updated_at`** | Timestamp | Metadata. | Metadata. |

---

5. FILE: CompoundOntologyTerm.csv

This is the "Bridge Table" between raw compounds and the formal chemical ontology. It allows L'atelier to navigate the tree of chemical logic.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier for the ontology link. |
| **`compound_id`** | Integer | Foreign Key. | Links to `Compound.csv`. |
| **`export`** | Boolean | Flag. | Indicates if this term should be included in external data exports. |
| **`ontology_term_id`** | Integer | Foreign Key. | Links to `OntologyTerm.csv`. |
| **`created_at`** | Timestamp | Metadata. | Metadata. |
| **`updated_at`** | Timestamp | Metadata. | Metadata. |

---

6. FILE: CompoundSubstituent.csv

This table identifies the functional groups and side chains (substituents) of a molecule. In flavor chemistry, the presence of specific substituents (like a methoxy group) often defines the "aromatic family."



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier for the substituent record. |
| **`name`** | String | Substituent Name. | The specific chemical group (e.g., "Methyl", "Hydroxyl"). |
| **`compound_id`** | Integer | Foreign Key. | Links the substituent to its parent `Compound.csv`. |
| **`creator_id`** | Integer | Metadata. | Record creation metadata. |
| **`updater_id`** | Integer | Metadata. | Record modification metadata. |

---

7. FILE: CompoundSynonym.csv

A critical mapping table for the User Interface. It translates technical chemical strings into terminology a chef or guest would recognize.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier for the synonym record. |
| **`synonym`** | String | Alternate Name. | Common name (e.g., "Vitamin C", "Menthol"). |
| **`synonym_source`** | String | Data Origin. | Where the name was sourced (e.g., "PubChem"). |
| **`source_id`** | Integer | Reference ID. | Internal source tracker. |
| **`source_type`** | String | Source Category. | Category of the source database. |

---

8. FILE: CompoundsEnzyme.csv

**The "Genetic Shield" Data.** This file links compounds to the enzymes and receptors they interact with.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier for the interaction. |
| **`compound_id`** | Integer | Foreign Key. | The ligand (molecule). |
| **`enzyme_id`** | Integer | Foreign Key. | The human protein (from `Enzyme.csv`). |
| **`citations`** | Text | Scientific Proof. | References to the study proving the binding. |

---

9. FILE: CompoundsFlavor.csv

The primary link between the molecular math and the sensory experience.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier for the flavor link. |
| **`compound_id`** | Integer | Foreign Key. | Links to `Compound.csv`. |
| **`flavor_id`** | Integer | Foreign Key. | Links to `Flavor.csv`. |
| **`source_type`** | String | Source Category. | e.g., "FlavorDB". |

10. FILE: CompoundsHealthEffect.csv

Maps the physiological impact of ingredients, allowing for "Functional Gastronomy."



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier. |
| **`compound_id`** | Integer | Foreign Key. | Links to `Compound.csv`. |
| **`health_effect_id`** | Integer | Foreign Key. | Links to `HealthEffect.csv`. |
| **`orig_citation`** | Text | Scientific Link. | The research paper validating the effect. |

---

11. FILE: CompoundsPathway.csv

Maps the metabolic pathways where a compound is synthesized in nature.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier. |
| **`compound_id`** | Integer | Foreign Key. | Links to `Compound.csv`. |
| **`pathway_id`** | Integer | Foreign Key. | Links to `Pathway.csv`. |

---

12. FILE: Content.csv

The most critical data bridge in the engine. It maps the concentration of specific chemical compounds within individual food items, enabling quantitative flavor analysis and intensity modeling.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier for the concentration record. |
| **`source_id`** | Integer | Foreign Key. | Usually links to `Compound.id` or `Nutrient.id`. |
| **`source_type`** | String | Source Category. | Defines if the source is a "Compound" or "Nutrient". |
| **`food_id`** | Integer | Foreign Key. | Links to `Food.csv`. |
| **`orig_food_common_name`** | String | Raw food name. | Used for data verification against the primary food name. |
| **`orig_content`** | Float | Raw concentration value. | The value as reported in the original scientific literature. |
| **`orig_unit`** | String | Measurement unit. | e.g., mg/100g, ppm, or percentage. |
| **`standard_content`** | Float | Normalized value. | **Critical:** Used for Odor Activity Value (OAV) and intensity calculations. |
| **`preparation_type`** | String | State of food. | **Critical:** Distinguishes between "Raw", "Cooked", "Dried", etc., for thermodynamic scaling. |

---

13. FILE: Enzyme.csv

A registry of human proteins, including the olfactory and taste receptors necessary for personalized sensory filtering and genetic exclusion.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier for the enzyme/protein. |
| **`name`** | String | Common protein name. | The standard name of the receptor or enzyme. |
| **`gene_name`** | String | Genetic identifier. | Links the protein to a specific gene (e.g., OR6A2). |
| **`uniprot_id`** | String | Universal Protein ID. | **Critical:** Cross-reference ID (e.g., Q9NYW7) for external bioinformatics lookups. |
| **`general_function`** | Text | Biological role. | Describes what the enzyme does in the human body. |
| **`pdb_id`** | String | 3D Structure ID. | Used for molecular docking simulations of flavor ligands. |

---

14. FILE: EnzymeSynonym.csv

Provides alternate names for enzymes to ensure high-accuracy mapping across different scientific datasets and research papers.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier. |
| **`enzyme_id`** | Integer | Foreign Key. | Links to `Enzyme.csv`. |
| **`synonym`** | String | Alternate name. | Ensures the engine recognizes multiple names for the same receptor. |

---

15. FILE: Flavor.csv

Defines the qualitative sensory profiles that humans perceive when interacting with volatile chemical compounds.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier for the flavor note. |
| **`name`** | String | Sensory descriptor. | e.g., "Citrusy", "Earthy", "Waxy", "Bitter". |
| **`flavor_group`** | String | Broad category. | Groups notes like "Floral" or "Fruity" for synergy logic. |

---

16. FILE: Food.csv

The master list of all ingredients available in the L'atelier ecosystem. This is the primary entry point for culinary R&D.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Primary key used for all concentration and taxonomy joins. |
| **`name`** | String | Common name. | The primary display name of the ingredient (e.g., "Yuzu"). |
| **`name_scientific`** | String | Biological name. | Precise Latin name (e.g., "Citrus junos"). |
| **`food_group`** | String | High-level category. | e.g., "Fruits", "Herbs and Spices", "Fungi". |
| **`food_subgroup`** | String | Specific category. | e.g., "Citrus fruits". |
| **`ncbi_taxonomy_id`** | Integer | Genetic link. | Links to the global NCBI taxonomy tree for botanical substitution. |
| **`public_id`** | String | Public reference. | Stable ID for external API calls and documentation. |

---

17. FILE: FoodTaxonomy.csv

Maps the hierarchical classification of foods, allowing the engine to navigate botanical relationships for substitute modeling.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier. |
| **`food_id`** | Integer | Foreign Key. | Links to `Food.csv`. |
| **`classification_name`** | String | Taxonomic rank. | e.g., "Genus", "Family", "Order". |

---

18. FILE: HealthEffect.csv

Defines the physiological and pharmacological impacts of specific compounds found within the ingredients.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier for the effect. |
| **`name`** | String | Effect name. | e.g., "Antioxidant", "Anti-inflammatory", "Anti-mutagenic". |
| **`description`** | Text | Detailed impact. | Explanation of how the compound affects human health. |
| **`chebi_id`** | String | Chemical Ontology ID. | Links the effect to the ChEBI database for scientific rigor. |


19. FILE: MapItemsPathway.csv

Acts as the link between specific biological map items (compounds, enzymes, or genes) and their respective metabolic pathways.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier for the mapping. |
| **`map_item_id`** | Integer | Item Reference. | Links to the specific item being mapped. |
| **`map_item_type`** | String | Item Category. | Defines if the item is a Compound, Protein, or Gene. |
| **`pathway_id`** | Integer | Foreign Key. | Links to `Pathway.csv`. |

---

20. FILE: NcbiTaxonomyMap.csv

Provides a standardized mapping to the NCBI taxonomy database, ensuring botanical accuracy across the L'atelier ecosystem.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier. |
| **`TaxonomyName`** | String | Scientific Name. | Standardized biological name (e.g., *Citrus*). |
| **`Rank`** | String | Taxonomic Rank. | e.g., "Species", "Genus", "Family". |

---

21. FILE: Nutrient.csv

A specialized registry for non-volatile compounds that provide nutritional value rather than primarily contributing to the volatile aroma profile.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier for the nutrient. |
| **`name`** | String | Common name. | e.g., "Calcium", "Vitamin A", "Riboflavin". |
| **`public_id`** | String | Public reference. | Stable ID for API and documentation use. |
| **`description`** | Text | Nutritional role. | Details on the metabolic impact of the nutrient. |

---

22. FILE: OntologySynonym.csv

Maps alternative names for chemical ontology terms to ensure consistent structural classification.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier. |
| **`ontology_term_id`** | Integer | Foreign Key. | Links to `OntologyTerm.csv`. |
| **`synonym`** | String | Alternate term. | Ensures structural classes are recognized under multiple names. |

---

23. FILE: OntologyTerm.csv

The structural backbone of the chemical classification system, defining the logic behind chemical "families."



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier for the term. |
| **`term`** | String | Classification name. | e.g., "Alcohols", "Esters", "Phenols". |
| **`definition`** | Text | Formal logic. | Defines the chemical requirements to belong to this class. |
| **`parent_id`** | Integer | Recursive Key. | Links to a parent term for hierarchical traversal. |

---

24. FILE: Pathway.csv

The high-level directory of biological pathways, mapping how flavor molecules are naturally synthesized.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier. |
| **`smpdb_id`** | String | External DB ID. | Links to the Small Molecule Pathway Database. |
| **`kegg_map_id`** | String | KEGG reference. | Links to Kyoto Encyclopedia of Genes and Genomes maps. |
| **`name`** | String | Pathway name. | e.g., "Terpene biosynthesis". |

---

25. FILE: PdbIdentifier.csv

Links compounds to 3D protein structures, essential for advanced molecular docking and receptor-binding simulations.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier. |
| **`compound_id`** | Integer | Foreign Key. | Links to `Compound.csv`. |
| **`pdb_id`** | String | Protein Data Bank ID. | Used to visualize or simulate molecule-receptor binding. |

---

26. FILE: Pfam.csv

Defines Protein Families, grouping enzymes and receptors based on shared evolutionary history and structural domains.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier. |
| **`identifier`** | String | Pfam Accession. | Standardized family ID (e.g., PF00001). |
| **`name`** | String | Family name. | Describes the common structural domain. |

---

27. FILE: PfamMembership.csv

Maps specific human receptors and enzymes from L'atelier to their broader Protein Families.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier. |
| **`enzyme_id`** | Integer | Foreign Key. | Links to `Enzyme.csv`. |
| **`pfam_id`** | Integer | Foreign Key. | Links to `Pfam.csv`. |

---

28. FILE: Reference.csv

The scientific verification layer, providing the specific papers and databases that validate the data in L'atelier.



| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier. |
| **`pubmed_id`** | String | Research ID. | Direct link to the scientific study on PubMed. |
| **`link`** | String | External URL. | Direct access to the source documentation. |
| **`title`** | String | Paper Title. | Description of the research findings. |

---

29. FILE: Sequence.csv

Contains the raw FASTA amino acid sequences for receptors and enzymes, used for protein modeling and genetic analysis.

| Column | Data Type | Description | Role in L'atelier Logic |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | Internal Primary Key. | Unique identifier. |
| **`chain`** | Text | Amino acid string. | The raw sequence of the protein. |
| **`sequenceable_id`** | Integer | Reference ID. | Usually links back to `Enzyme.id`. |
| **`type`** | String | Sequence type. | Defines if the sequence is Protein or DNA. |