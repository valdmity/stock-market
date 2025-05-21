run:
	@docker-compose up --build

run-db:
	@docker-compose up db

run-pgadmin:
	@docker-compose up pgadmin

clean:
	@docker-compose down
