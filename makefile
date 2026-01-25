APP_NAME=delivery
PYTHON_VERSION=3.13
VENV_DIR=.venv

.PHONY: help venv install test lint format type-check migrate upgrade downgrade run

help: ## Показать справку по командам
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## Создать virtualenv с помощью uv
	@if command -v uv > /dev/null 2>&1; then \
		echo "Создание virtualenv через uv..."; \
		uv venv --python $(PYTHON_VERSION); \
		echo "Virtualenv создан в $(VENV_DIR)"; \
		echo "Активируйте его командой:"; \
		echo "  Windows: $(VENV_DIR)\\Scripts\\activate"; \
		echo "  Linux/Mac: source $(VENV_DIR)/bin/activate"; \
	else \
		echo "Ошибка: uv не установлен. Установите его с https://github.com/astral-sh/uv"; \
		exit 1; \
	fi

install: venv ## Установить зависимости через uv
	@if command -v uv > /dev/null 2>&1; then \
		echo "Установка зависимостей через uv..."; \
		uv pip install -r requirements.txt; \
		echo "Зависимости установлены"; \
	else \
		echo "Ошибка: uv не установлен. Используйте: pip install -r requirements.txt"; \
		exit 1; \
	fi

test: ## Запустить тесты
	pytest

lint: ## Проверить код с помощью ruff
	ruff check app/ tests/

format: ## Форматировать код с помощью ruff
	ruff format app/ tests/

type-check: ## Проверить типы с помощью mypy
	mypy app/

migrate: ## Создать новую миграцию (использовать: make migrate MESSAGE="описание")
	@if [ -z "$(MESSAGE)" ]; then \
		echo "Ошибка: укажите MESSAGE для миграции"; \
		echo "Пример: make migrate MESSAGE=\"Initial migration\""; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(MESSAGE)"

upgrade: ## Применить миграции
	alembic upgrade head

downgrade: ## Откатить последнюю миграцию
	alembic downgrade -1

run: ## Запустить приложение
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8082

# Старые Go команды (можно удалить после полной миграции)
generate-server:
	@go tool oapi-codegen -config configs/server.cfg.yaml https://gitlab.com/microarch-ru/ddd-in-practice/system-design/-/raw/main/services/delivery/contracts/openapi.yml

generate-geo-client:
	@rm -rf internal/generated/clients/geosrv
	@curl -s -o configs/geo.proto https://gitlab.com/microarch-ru/ddd-in-practice/system-design/-/raw/main/services/geo/contracts/contract.proto
	@protoc --go_out=internal/generated/clients --go-grpc_out=internal/generated/clients configs/geo.proto

generate-basket-queue:
	@rm -rf internal/generated/queues/basketconfirmedpb
	@curl -s -o configs/basket_confirmed.proto https://gitlab.com/microarch-ru/ddd-in-practice/system-design/-/raw/main/services/basket/contracts/basket_confirmed.proto
	@protoc --go_out=internal/generated --go-grpc_out=internal/generated configs/basket_confirmed.proto

generate-order-queue:
	@rm -rf internal/generated/queues/orderstatuschangedpb
	@curl -s -o configs/order_status_changed.proto https://gitlab.com/microarch-ru/ddd-in-practice/system-design/-/raw/main/services/delivery/contracts/order_status_changed.proto
	@protoc --go_out=internal/generated --go-grpc_out=internal/generated configs/order_status_changed.proto