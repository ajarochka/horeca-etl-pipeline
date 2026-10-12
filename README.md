# 🍽️ HoReCa ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DWH-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-ETL-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

End-to-end ETL пайплайн...

End-to-end ETL pipeline для аналитики продаж в сфере HoReCa (Hotel, Restaurant, Cafe).

Проект демонстрирует полный цикл Data Engineering: от извлечения сырых данных до загрузки в аналитическое хранилище и построения витрин.

### 🏗️ Архитектура

`Raw CSV / API` → `Python (Pandas) ETL` → `PostgreSQL (DWH)` → `SQL Витрины / Analytics`

**Пайплайн состоит из 3 шагов:**
1.  **Extract:** Чтение сырых данных о продажах, заказах и продуктах из CSV
2.  **Transform:** Очистка, дедупликация, нормализация, расчет KPI (выручка, средний чек, ABC-анализ)
3.  **Load:** Загрузка в PostgreSQL, создание схемы star-schema и аналитических витрин

### 🛠️ Tech Stack
- **Language:** Python 3.11+
- **Data Processing:** Pandas, SQLAlchemy
- **Database:** PostgreSQL
- **Orchestration Ready:** Структура готова для Airflow / Docker
- **Version Control:** Git, GitHub

### 📁 Структура проекта
.
├── data/
│   ├── raw/              # сырые данные
│   └── processed/        # очищенные данные
├── etl/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── sql/
│   ├── dwh_schema.sql    # DDL для DWH
│   └── marts.sql         # витрины данных
├── main.py               # точка входа в пайплайн
├── requirements.txt
└── .env.example

### 🚀 Как запустить

1.  Клонировать репо:
```bash
git clone https://github.com/ajarochka/horeca-etl-pipeline.git
cd horeca-etl-pipeline