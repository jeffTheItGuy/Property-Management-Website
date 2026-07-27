.PHONY: run stop migrate seed backup test

run:
	docker-compose up -d

stop:
	docker-compose down

migrate:
	docker-compose exec api alembic revision --autogenerate -m "$(m)"
	docker-compose exec api alembic upgrade head

seed:
	docker-compose exec api python -m seeds.seed_data

backup:
	docker-compose exec db pg_dump -U zimrental zimrental > backups/zimrental_$$(date +%Y%m%d_%H%M%S).sql

test:
	docker-compose exec api pytest tests/ -v

logs:
	docker-compose logs -f api
