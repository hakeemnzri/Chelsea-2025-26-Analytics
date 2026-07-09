# Chelsea Analytics

## Overview

Chelsea Analytics is a Python-based football analytics project designed to collect, process, store, and analyze Chelsea FC player performance data.

The project aims to build a reliable data pipeline that transforms publicly available football statistics into structured datasets for visualization using Microsoft Power BI.

This project serves as a portfolio demonstrating software engineering, data engineering, data analysis, and business intelligence practices.

---

# Objectives

- Collect Chelsea FC player statistics from FBref.
- Build a modular and maintainable web scraping pipeline.
- Clean and validate collected data.
- Store historical records in a SQLite database.
- Export datasets for Power BI.
- Create an interactive dashboard for player performance analysis.
- Follow software engineering best practices throughout development.

---

# Technology Stack

- Python
- Pandas
- Requests
- BeautifulSoup4
- SQLite
- Power BI
- Git

---

# Project Structure

```
ChelseaAnalytics/

├── data/
│   ├── raw/
│   ├── processed/
│   └── exports/
│
├── database/
│
├── docs/
│
├── powerbi/
│   └── datasets/
│
├── src/
│   ├── scraper/
│   ├── processing/
│   ├── database/
│   └── utils/
│
├── tests/
│
├── README.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
└── LICENSE
```

---

# Planned Features

- FBref web scraper
- Data validation pipeline
- Data cleaning and transformation
- SQLite database integration
- CSV export for Power BI
- Historical player performance tracking
- Interactive Power BI dashboard
- Automated data updates
- Testing and documentation

---

# Development Approach

The project follows an incremental milestone-based development process.

Each milestone is planned, implemented, documented, and validated before moving to the next stage.

Major architectural decisions are recorded to maintain consistency throughout the project.

---

# Project Status

Current Milestone

✅ Milestone 0 — Project Foundation

Next Milestone

Design and implement the FBref data scraper.