FROM postgres:15

ARG DB_DATABASE

ARG DB_REPL_USER

ARG DB_REPL_PASSWORD

COPY init.sql /init.sql

RUN apt-get update && apt-get install gettext-base
RUN envsubst '${DB_REPL_USER} ${DB_REPL_PASSWORD} ${DB_DATABASE} ${DB_DATABASE}' </init.sql> /docker-entrypoint-initdb.d/init.sql

RUN mkdir -p /oracle/pg_data/archive/ 
RUN chown -R postgres:postgres /oracle/pg_data/archive/