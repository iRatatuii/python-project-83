### Hexlet tests and linter status:
[![Actions Status](https://github.com/iRatatuii/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/iRatatuii/python-project-83/actions)[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=iRatatuii_python-project-83&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=iRatatuii_python-project-83)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=iRatatuii_python-project-83&metric=bugs)](https://sonarcloud.io/summary/new_code?id=iRatatuii_python-project-83)[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=iRatatuii_python-project-83&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=iRatatuii_python-project-83)[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=iRatatuii_python-project-83&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=iRatatuii_python-project-83)[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=iRatatuii_python-project-83&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=iRatatuii_python-project-83)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=iRatatuii_python-project-83&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=iRatatuii_python-project-83)[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=iRatatuii_python-project-83&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=iRatatuii_python-project-83)[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=iRatatuii_python-project-83&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=iRatatuii_python-project-83)

 ## Демо

Проект развернут на сервисе Render и доступен по ссылке:

👉 https://python-project-83-sus2.onrender.com

Приложение работает в production-режиме с использованием Gunicorn и базы данных PostgreSQL.


# Page Analyzer

Page Analyzer — это учебный веб‑проект на Python (Flask), который позволяет добавлять сайты в базу и выполнять их SEO‑проверку.
Проект разработан в рамках обучения бэкенд‑разработке и демонстрирует работу с базой данных, HTTP‑запросами и шаблонами Jinja2

## Возможности

- Добавление URL для анализа
- Выполнение SEO‑проверок страниц
- Сохранение результатов проверок в базе данных
- Отображение истории проверок для каждого сайта

## Стек технологий

- Python 3
- Flask
- PostgreSQL
- Jinja2
- Requests
- BeautifulSoup4
- uv (менеджер зависимостей)
- ruff
- GitHub Actions

## Требования

- Python 3.10+
- PostgreSQL
- uv

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/iRatatuii/python-project-83.git
cd python-project-83
```
### 2. Установка зависимостей
```bash
make install
```

### 3. Запуск в режиме разработки
```bash
make dev
```
Сервер будет запущен по адресу http://127.0.0.1:5000

### 4. Проверка Ruff
```bash
make lint
```

### 5. Проверка кода линтером Ruff
```bash
make lint
```

## CI / GitHub Actions

В проекте настроен GitHub Actions для:

- линтинга
- проверки качества кода

Workflow автоматически запускается при push и pull request.


## Учебные цели проекта

- Практика Flask и MVC‑подхода
- Работа с PostgreSQL
- HTTP и парсинг HTML

Проект создан в образовательных целях.