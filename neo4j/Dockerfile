# Use the official Neo4j image
FROM neo4j:latest

# Switch to root to install utilities and move files
USER root

# Install curl and tar for downloading/extracting FooDB
RUN apt-get update && apt-get install -y curl tar && rm -rf /var/lib/apt/lists/*

# Copy the wrapper script into the image
COPY wrapper.sh /wrapper.sh
RUN chmod +x /wrapper.sh

# Set the custom wrapper as the entrypoint
ENTRYPOINT ["/wrapper.sh"]