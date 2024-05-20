CREATE USER ${DB_REPL_USER} WITH REPLICATION ENCRYPTED PASSWORD '${DB_REPL_PASSWORD}';
SELECT pg_create_physical_replication_slot('replication_slot');

CREATE DATABASE ${DB_DATABASE};

\connect ${DB_DATABASE}

CREATE TABLE phone_numbers(
  id SERIAL PRIMARY KEY,
  phone_number VARCHAR(100) NOT NULL
);
CREATE TABLE emails(
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL
);

INSERT INTO emails (email) VALUES ('aboba@aboba.com'), ('hello@hello.ru');
INSERT INTO phone_numbers (phone_number) VALUES ('89438374650'), ('+7-942-666-77-88');