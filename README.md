# Bankruptcy Parser

Парсер данных о банкротствах с сайтов [fedresurs.ru](https://fedresurs.ru) и [kad.arbitr.ru](https://kad.arbitr.ru).

## Стек технологий

- **Python 3.11+**
- **Requests + BeautifulSoup4** — парсинг fedresurs.ru
- **SeleniumBase** — парсинг kad.arbitr.ru
- **SQLAlchemy 2.0**
- **SQLite / PostgreSQL**
- **Docker & Docker Compose**

## Структура проекта

```
bankruptcy_parser/
├── src/
│   ├── main.py                 # Точка входа
│   ├── config.py               # Конфигурация
│   ├── models.py               # SQLAlchemy модели
│   ├── database.py             # Работа с БД
│   ├── parsers/
│   │   ├── fedresurs_parser.py # Парсинг fedresurs.ru
│   │   └── arbitr_parser.py   # Парсинг kad.arbitr.ru
│   └── utils/
│       ├── excel_reader.py     # Чтение Excel
│       ├── logger.py           # Логирование
│       └── retry.py            # Повторные попытки
├── data/
│   ├── inn_list.xlsx           # Входной файл
│   └── bankruptcy.db          # База данных (SQLite)
├── logs/                       # Логи
├── .env                        # Переменные окружения
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/alexmustdie/bankruptcy-parser.git
cd bankruptcy-parser
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка окружения

```bash
cp .env.example .env
# Отредактируйте .env при необходимости
```

### 5. Подготовка входных данных

Создайте файл `data/inn_list.xlsx` с колонкой `ИНН`:

| ИНН            |
|----------------|
| 231138771115   |
| 222307980200   |
| 301500615700   |

### 6. Запуск

```bash
python -m src.main
```

#### Запуск через Docker

```bash
docker-compose up --build
```

## Конфигурация

| Переменная       | Описание                              | Значение по умолчанию              |
|------------------|---------------------------------------|------------------------------------|
| `DATABASE_URL`   | Строка подключения к БД               | `sqlite:///./data/bankruptcy.db`   |
| `INPUT_FILE`     | Путь к Excel-файлу                    | `./data/inn_list.xlsx`             |
| `LOG_LEVEL`      | Уровень логирования                   | `INFO`                             |
| `REQUEST_DELAY`  | Задержка между запросами (сек)        | `2`                                |
| `MAX_CONCURRENT` | Количество параллельных потоков       | `1`                                |
| `MAX_RETRIES`    | Количество повторных попыток          | `3`                                |
| `USE_PROXY`      | Использовать прокси                   | `false`                            |
| `PROXY_URL`      | URL прокси (если `USE_PROXY=true`)    | —                                  |

## Результат

Данные сохраняются в две таблицы SQLite/PostgreSQL.

**`fedresurs_data`**

| id | inn          | case_number      | last_date  |
|----|--------------|------------------|------------|
| 1  | 231138771115 | А32-28873/2024   | 2025-10-03 |

**`arbitr_data`**

| id | case_number    | last_date  | document_name                      | fedresurs_id |
|----|----------------|------------|------------------------------------|--------------|
| 1  | А32-28873/2024 | 2025-11-19 | О возвращении заявления/жалобы     | 1            |

## Логирование

Логи пишутся в:

- консоль (stdout)
- файлы `logs/parser_YYYYMMDD.log`

## Примечания

- Для kad.arbitr.ru используется SeleniumBase с режимом `uc=True` (Undetected Chrome).
- При первом запуске SeleniumBase автоматически скачает ChromeDriver.
- Для массового парсинга рекомендуется использовать прокси.
