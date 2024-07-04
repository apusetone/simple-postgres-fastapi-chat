#!/bin/bash
set -e

# データベースが存在しない場合にのみ作成する
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    SELECT 'CREATE DATABASE mydatabase'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mydatabase');\\gexec
EOSQL
