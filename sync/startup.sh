#!/bin/bash

if [ "$CREATE_DATA" == "1" ]; then
    if command -v apt-get &> /dev/null; then
        apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*
    else
        echo "Ошибка установки psql."
        exit 1
    fi
    
    export PGPASSWORD="postgres"

    sleep 5

    echo "Применяем дамп к PostgreSQL..."

    psql -f /FINISH.sql -h postgresql_container -U postgres
    
    echo "Синхронизируем остальные хранилища с PostgreSQL..."
    # poetry run python generate.py
else
    echo "Данные синхронизировать не нужно, скипаюсь."
fi