curl -X POST -H "Content-Type: application/json" \
 --data @connectors/debezium-config.json \
 http://localhost:8083/connectors


curl -X POST -H "Content-Type: application/json" \
 --data @connectors/redis-config.json \
 http://localhost:8083/connectors

curl -X POST -H "Content-Type: application/json" \
 --data @connectors/elastic-config.json \
 http://localhost:8083/connectors


curl http://localhost:8083/connectors/elasticsearch-sink/status | jq
curl http://localhost:8083/connectors/debezium-postgres-connector/status | jq
curl http://localhost:8083/connectors/redis/status | jq