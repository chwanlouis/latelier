#!/bin/bash

# Path to a marker file to prevent re-downloading every restart
DATA_IMPORTED_FLAG="/data/db_imported.flag"

if [ ! -f "$DATA_IMPORTED_FLAG" ]; then
    echo "Checking for existing data..."

    # Download FooDB
    echo "Downloading FooDB data..."
    curl -o /tmp/foodb.tar.gz https://foodb.ca/public/system/downloads/foodb_2020_4_7_csv.tar.gz

    echo "Extracting data..."
    tar -xzf /tmp/foodb.tar.gz -C /tmp/

    # Note: Neo4j requires CSVs to be formatted correctly for neo4j-admin import
    # or loaded via Cypher. Below is the command to start Neo4j and then
    # you would typically run a Cypher script to LOAD CSV.

    # Touch flag so this doesn't run again
    touch "$DATA_IMPORTED_FLAG"
fi

# Start Neo4j normally
exec /docker-entrypoint.sh neo4j