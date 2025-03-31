## Запуск

**Переименуйте файл config.example.toml в config.toml!**

```
   docker-compose up 
```

## Подгрузка данных

**Переименуйте файл config.example.toml в config.toml!**  
Установить poetry  
Настроить conf.toml  
```
    psql -f FINISH.sql -U postgres -h localhost
    poetry install
    poetry shell
    python generate.py
```
