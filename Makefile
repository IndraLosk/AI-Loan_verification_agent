# Переменные
COMPOSE = docker compose
EXEC = $(COMPOSE) exec api
PYTHON = $(EXEC) python
ALEMBIC = $(EXEC) alembic
PYTEST = $(EXEC) pytest

# Цель по умолчанию
.PHONY: help
help:
	@echo "Доступные команды:"
	@echo "  make setup       — первичная настройка: создать .env, собрать и запустить контейнеры, накатить миграции"
	@echo "  make run         — запустить контейнеры в фоновом режиме"
	@echo "  make stop        — остановить контейнеры"
	@echo "  make restart     — перезапустить контейнеры"
	@echo "  make build       — пересобрать образы"
	@echo "  make logs        — показать логи (добавьте сервис, например make logs api)"
	@echo "  make migrate     — выполнить миграции базы данных (alembic upgrade head)"
	@echo "  make makemigrations — создать новую миграцию (укажите MESSAGE, например make makemigrations MESSAGE='add new column')"
	@echo "  make test        — запустить тесты в контейнере"
	@echo "  make shell       — войти в оболочку контейнера api (bash)"
	@echo "  make clean       — остановить и удалить контейнеры, сети и тома (полная очистка)"
	@echo "  make install     — установить зависимости локально (вне Docker)"

# Создать .env из примера, если его нет
.env:
	cp .env.example .env

# Настройка проекта: подготовка .env, сборка, запуск и миграции
setup: .env build run migrate
	@echo "✅ Проект настроен и запущен!"

# Запуск контейнеров в фоне
run:
	$(COMPOSE) up -d

# Остановка контейнеров
stop:
	$(COMPOSE) stop

# Перезапуск
restart: stop run

# Сборка образов
build:
	$(COMPOSE) build

# Логи (можно передать сервис, например make logs api)
logs:
	$(COMPOSE) logs -f

# Миграции
migrate:
	$(ALEMBIC) upgrade head

# Создать новую миграцию (передайте сообщение: make makemigrations MESSAGE='init')
makemigrations:
	$(ALEMBIC) revision --autogenerate -m "$(MESSAGE)"

# Тесты
test:
	$(PYTEST) tests/

# Интерактивная оболочка в контейнере api
shell:
	$(EXEC) /bin/bash

# Полная очистка (удаляет всё, включая volumes)
clean:
	$(COMPOSE) down -v

# Установка зависимостей локально (вне Docker)
install:
	pip install -r requirements.txt