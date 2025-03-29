## Запуск

```
   docker-compose up 
```

## Подгрузка данных

Установить poetry  
Настроить conf.toml  
```
    psql -f FINISH.sql -U postgres -h localhost
    poetry install
    poetry shell
    python generate.py
```
