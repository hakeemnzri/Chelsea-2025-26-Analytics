# Architecture

## Overview

Chelsea Analytics follows a modular pipeline architecture.

```
FBref
   │
   ▼
Scraper
   │
   ▼
Raw Data
   │
   ▼
Processing
   │
   ▼
SQLite Database
   │
   ▼
CSV Export
   │
   ▼
Power BI
```

---

# Components

## Scraper

Responsible for collecting data from FBref.

No data transformation should occur here.

---

## Processing

Responsible for:

- Cleaning
- Validation
- Standardization
- Feature engineering

---

## Database

Stores processed historical data using SQLite.

---

## Export

Generates datasets suitable for Power BI.

---

## Dashboard

Power BI consumes exported datasets.

Dashboard logic does not belong inside Python.

---

# Folder Responsibilities

## data/

Stores project datasets.

### raw/

Unmodified downloaded data.

### processed/

Cleaned datasets.

### exports/

Power BI datasets.

---

## database/

SQLite database files.

---

## docs/

Project documentation.

---

## powerbi/

Power BI resources.

---

## src/

Application source code.

---

## tests/

Automated testing.