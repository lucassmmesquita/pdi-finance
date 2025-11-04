.PHONY: help install setup-db run-backend run-frontend dev clean

help:
	@echo "PDI Finance - Comandos Disponíveis:"
	@echo "  make install      - Instala todas as dependências"
	@echo "  make setup-db     - Configura o banco de dados"
	@echo "  make run-backend  - Inicia o backend"
	@echo "  make run-frontend - Inicia o frontend"
	@echo "  make dev          - Inicia backend e frontend"
	@echo "  make clean        - Limpa arquivos temporários"

install:
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

setup-db:
	psql -U postgres -c "CREATE DATABASE pdi_finance;"
	psql -U postgres -d pdi_finance -f database/migrations/001_initial_schema.sql

run-backend:
	cd backend && . venv/bin/activate && uvicorn main:app --reload --port 8000

run-frontend:
	cd frontend && npm run dev

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
