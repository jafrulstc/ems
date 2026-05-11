#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# EMS Backend Docker Entrypoint
#
# 1. Wait for PostgreSQL to be ready
# 2. Run Alembic migrations
# 3. Optionally run seed data (if SEED_DATABASE=true)
# 4. Start uvicorn
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-ems}"
DB_USER="${POSTGRES_USER:-ems}"
SEED_DATABASE="${SEED_DATABASE:-false}"
MAX_RETRIES="${DB_MAX_RETRIES:-30}"
RETRY_INTERVAL="${DB_RETRY_INTERVAL:-2}"

# ── Helper Functions ──────────────────────────────────────────────────────────

echo_info()  { echo -e "\\033[1;34m[INFO]\\033[0m  $*"; }
echo_ok()    { echo -e "\\033[1;32m[OK]\\033[0m    $*"; }
echo_warn()  { echo -e "\\033[1;33m[WARN]\\033[0m  $*"; }
echo_error() { echo -e "\\033[1;31m[ERROR]\\033[0m $*"; }

# ── Step 1: Wait for PostgreSQL ───────────────────────────────────────────────
wait_for_postgres() {
    echo_info "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT} ..."

    local retries=0
    while [ $retries -lt $MAX_RETRIES ]; do
        if python -c "
import asyncio, asyncpg
async def check():
    conn = await asyncpg.connect(
        host='${DB_HOST}', port=${DB_PORT},
        user='${DB_USER}', database='${DB_NAME}',
        timeout=2
    )
    await conn.close()
asyncio.run(check())
" 2>/dev/null; then
            echo_ok "PostgreSQL is ready!"
            return 0
        fi

        retries=$((retries + 1))
        echo_info "Attempt ${retries}/${MAX_RETRIES} — PostgreSQL not ready, retrying in ${RETRY_INTERVAL}s ..."
        sleep "$RETRY_INTERVAL"
    done

    echo_error "PostgreSQL did not become ready in time."
    exit 1
}

# ── Step 2: Run Alembic Migrations ────────────────────────────────────────────
run_migrations() {
    echo_info "Running Alembic migrations ..."
    alembic upgrade head
    echo_ok "Alembic migrations completed."
}

# ── Step 3: Optionally Seed Database ──────────────────────────────────────────
seed_database() {
    if [ "${SEED_DATABASE}" = "true" ]; then
        echo_info "Seeding database ..."
        python seed_data.py
        echo_ok "Database seeding completed."
    else
        echo_info "SEED_DATABASE=${SEED_DATABASE} — skipping seed."
    fi
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
    echo_info "=== EMS Backend Entrypoint ==="

    wait_for_postgres
    run_migrations
    seed_database

    echo_info "Starting application: $*"
    exec "$@"
}

main "$@"
