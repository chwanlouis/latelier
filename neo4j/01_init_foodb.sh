#!/bin/bash
set -e

# Configuration
DATA_DIR="/var/lib/neo4j/import"
FLAG_FILE="/data/import_complete.flag"
URL="https://foodb.ca/public/system/downloads/foodb_2020_4_7_csv.tar.gz"

# 1. Check if the database has already been initialized
if [ -f "$FLAG_FILE" ]; then
    echo "--- FooDB already initialized. Skipping import. ---"
    exit 0
fi

echo "--- Starting FooDB Initialization ---"

# 2. Download and Extract
echo "Downloading FooDB archive..."
curl -L $URL -o /tmp/foodb.tar.gz

echo "Extracting CSVs to import directory..."
# We only extract the specific files needed to save space
tar -xzf /tmp/foodb.tar.gz -C $DATA_DIR --strip-components=1

# 3. Wait for Neo4j to be available
echo "Waiting for Neo4j to start..."
until cypher-shell -u neo4j -p "$NEO4J_AUTH" "RETURN 1" > /dev/null 2>&1; do
    sleep 5
done

# 4. Execute Initial Database Script (Cypher)
echo "Running Cypher import commands..."

cypher-shell -u neo4j -p "$NEO4J_AUTH" <<EOF
// Create Constraints for speed/integrity
CREATE CONSTRAINT IF NOT EXISTS FOR (f:Food) REQUIRE f.public_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (c:Compound) REQUIRE c.public_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (fl:Flavor) REQUIRE fl.public_id IS UNIQUE;

// Load Foods
LOAD CSV WITH HEADERS FROM 'file:///Food.csv' AS row
MERGE (f:Food {public_id: row.public_id})
SET f.name = row.name,
    f.description = row.description,
    f.food_group = row.food_group;

// Load Compounds
LOAD CSV WITH HEADERS FROM 'file:///Compound.csv' AS row
MERGE (c:Compound {public_id: row.public_id})
SET c.name = row.name,
    c.cas_number = row.cas_number;

// Load Flavors
LOAD CSV WITH HEADERS FROM 'file:///Flavor.csv' AS row
MERGE (fl:Flavor {name: row.name});
EOF

# 5. Cleanup and Flagging
echo "Cleaning up temporary files..."
rm /tmp/foodb.tar.gz
touch "$FLAG_FILE"

echo "--- FooDB Initialization Complete ---"