# Docker Compose local
compose_base_cmd = docker compose -f 
local_compose_file = docker-compose-local.yml
local_compose_cmd = $(compose_base_cmd) $(local_compose_file)
local_compose_up = $(local_compose_cmd) up -d

# Docker
docker_exec_base_cmd = docker exec
docker_exec_it_base_cmd = $(docker_exec_base_cmd) -it

# Services
BACKEND_SERVICE_NAME = backend

# Containeer
BACKEND_CONTAINER_NAME = highlight-extractor-backend

### BASH ###
be_bash:
	$(docker_exec_it_base_cmd) $(BACKEND_CONTAINER_NAME) bash

fe_bash:
	$(docker_exec_it_base_cmd) $(FRONTEND_CONTAINER_NAME) sh

# Only the first time you run the project

up_rebuilding: 
	$(local_compose_up) $(BACKEND_SERVICE_NAME) --build

up: 
	$(local_compose_up) $(BACKEND_SERVICE_NAME)
	$(local_compose_up) $(FRONTEND_SERVICE_NAME)

# LOCAL
up_backend:
	$(local_compose_up) $(BACKEND_SERVICE_NAME)
	make be_bash

up_backend_rebuilding:
	$(local_compose_up) $(BACKEND_SERVICE_NAME) --build
	make be_bash

stop:
	$(local_compose_cmd) stop 

# LOCAL
down:
	$(local_compose_cmd) down