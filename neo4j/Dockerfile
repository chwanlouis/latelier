# We use the community-supported image as our base
FROM neo4j:latest

# 1. Automatically enable APOC (Awesome Procedures on Cypher)
# This is incredibly helpful for processing giant local JSON chunks 
ENV NEO4J_PLUGINS='["apoc"]'

# 2. Lift standard sandbox restrictions so APOC can read files from your computer
ENV NEO4J_dbms_security_procedures_unrestricted=apoc.*
ENV NEO4J_apoc_import_file_enabled=true
ENV NEO4J_apoc_export_file_enabled=true

# 3. Optimize memory configurations specifically for a 5M relationship stream
# These overrides allocate up to 4GB heap and a 2GB pagecache pool
ENV NEO4J_server_memory_heap_initial__size=2G
ENV NEO4J_server_memory_heap_max__size=4G
ENV NEO4J_server_memory_pagecache_size=2G

# Expose HTTP (7474) for the Browser UI and Bolt (7687) for your Python code
EXPOSE 7474 7687