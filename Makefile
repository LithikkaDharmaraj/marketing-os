.PHONY: dev stop migrate seed qdrant-init logs clean

dev:
	docker compose -f docker/docker-compose.yml up --build -d
	@echo "Services starting... frontend at http://localhost:3000"

stop:
	docker compose -f docker/docker-compose.yml down

migrate:
	docker exec -i docker-postgres-1 psql -U marketing_os -d marketing_os < migrations/versions/0001_initial_schema.sql

seed:
	docker compose -f docker/docker-compose.yml exec intake-service python /app/scripts/seed_data.py

qdrant-init:
	docker exec docker-embedding-service-1 python3 -c "import asyncio,sys; sys.path.insert(0,'/app'); from services.embedding_service.app.service import ensure_collections; asyncio.run(ensure_collections()); print('Qdrant collections ready')"

logs:
	docker compose -f docker/docker-compose.yml logs -f

clean:
	docker compose -f docker/docker-compose.yml down -v --remove-orphans

ps:
	docker compose -f docker/docker-compose.yml ps
