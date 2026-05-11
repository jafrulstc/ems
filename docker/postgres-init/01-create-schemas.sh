#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
# PostgreSQL initialization script
# Creates the required schemas for the EMS application.
# Runs once when the PostgreSQL container is first initialized.
# ──────────────────────────────────────────────────────────────────────────────
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create application schemas if they don't exist
    CREATE SCHEMA IF NOT EXISTS core;
    CREATE SCHEMA IF NOT EXISTS auth;
    CREATE SCHEMA IF NOT EXISTS academic;
    CREATE SCHEMA IF NOT EXISTS exam;

    -- Grant usage to the application user
    GRANT USAGE ON SCHEMA core TO ${POSTGRES_USER};
    GRANT USAGE ON SCHEMA auth TO ${POSTGRES_USER};
    GRANT USAGE ON SCHEMA academic TO ${POSTGRES_USER};
    GRANT USAGE ON SCHEMA exam TO ${POSTGRES_USER};

    -- Grant full privileges on all objects within schemas
    ALTER DEFAULT PRIVILEGES IN SCHEMA core GRANT ALL ON TABLES TO ${POSTGRES_USER};
    ALTER DEFAULT PRIVILEGES IN SCHEMA auth GRANT ALL ON TABLES TO ${POSTGRES_USER};
    ALTER DEFAULT PRIVILEGES IN SCHEMA academic GRANT ALL ON TABLES TO ${POSTGRES_USER};
    ALTER DEFAULT PRIVILEGES IN SCHEMA exam GRANT ALL ON TABLES TO ${POSTGRES_USER};
EOSQL

echo "✅ Schemas created: core, auth, academic, exam"
