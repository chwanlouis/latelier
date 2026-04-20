FROM postgres:15

# Default Credentials
ENV POSTGRES_DB=latelier_db
ENV POSTGRES_USER=louis_admin
ENV POSTGRES_PASSWORD=secure_latelier_pass

# Load Schema
COPY init.sql /docker-entrypoint-initdb.d/

EXPOSE 5432