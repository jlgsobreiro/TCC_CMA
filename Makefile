# Subir os containers
up:
	docker compose up -d

# Parar os containers
down:
	docker compose down

# Rodar os testes
test:
	python3 -m unittest discover -s tests