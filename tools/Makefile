dev:
	docker-compose -f environment/development.yml up --build -d
dev-down:
	docker-compose -f environment/development.yml down
qa:
	docker-compose -f environment/qa.yml up --build -d
qa-down:
	docker-compose -f environment/qa.yml down
production:
	docker-compose -f environment/production.yml up --build -d
production-down:
	docker-compose -f environment/production.yml down
cleanup: dev-down qa-down production-down
	docker volume prune -f
	docker network prune -f
	docker image prune -f
