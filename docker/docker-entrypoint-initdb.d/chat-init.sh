#!/usr/bin/env bash
# ------------------------------------------------------------------------
# Creates the chat bot database and respective user. This database location
# and access credentials are defined on the environment variables
# ------------------------------------------------------------------------
set -e

psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" <<-EOSQL
  CREATE USER ${CHAT_DATABASE_USER} WITH PASSWORD '${CHAT_DATABASE_PASSWORD}';
  CREATE DATABASE ${CHAT_DATABASE};
  GRANT ALL PRIVILEGES ON DATABASE ${CHAT_DATABASE} TO ${CHAT_DATABASE_USER};
EOSQL

psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" -d "${CHAT_DATABASE}" <<-EOSQL
   GRANT ALL ON SCHEMA public TO ${CHAT_DATABASE_USER};
EOSQL
