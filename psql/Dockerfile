FROM postgres:15

COPY 01-create-table-user.sql /docker-entrypoint-initdb.d/
COPY 02-clear-db-and-insert-data.sql /docker-entrypoint-initdb.d/

EXPOSE 5432