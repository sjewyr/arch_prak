## Запуск

**Переименуйте файл config.example.toml в config.toml!**

```
   docker-compose up 
```

## Применение дампа к PostgreSQL

**Заходим в контейнер postgres через docker exec и выполняем**  

```
    psql -f FINISH.sql -U postgres 
```

## Синхронизация остальных хранилищ с Postgres'ом

**В docker-compose.yaml у env NEED_DATA_SYNC контейнера api устанавливаем значение 1, после этого перезапускаем только лишь этот контейнер** 

```
    docker compose up -d --no-deps api
```

**Затем возвращаем NEED_DATA_SYNC в значение 0, чтобы при последующих перезапусках контейнера api не происходила повторная синхронизация** 