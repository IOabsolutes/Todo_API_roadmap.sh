#!/bin/bash
set -e

echo "Environment variables:"
env

# Use the environment variables set in docker-compose.yml
DB_HOST=${DB_HOST:-postgres}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}
DB_NAME=${DB_NAME:-todo_database}

echo "Using DB_HOST: $DB_HOST"
echo "Using DB_PORT: $DB_PORT"
echo "Using DB_NAME: $DB_NAME"

# Wait for the PostgreSQL server to become available
echo "Waiting for PostgreSQL to become available..."
until PGPASSWORD=$DB_PASSWORD pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo >&2 "PostgreSQL is unavailable - sleeping"
  sleep 5
done

echo "PostgreSQL is available"

echo "Creating database and user if they don't exist..."
PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" <<-EOSQL
    SELECT 'CREATE DATABASE $DB_NAME'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

    DO
    \$\$
    BEGIN
      IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
        CREATE ROLE $DB_USER LOGIN PASSWORD '$DB_PASSWORD';
      END IF;
    END
    \$\$;

    GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOSQL