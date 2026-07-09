# Architectural Decisions

This document records important architectural and technical decisions made throughout the project.

---

## Decision 1

### Primary Data Source

**Selected**

FBref

**Reason**

FBref provides comprehensive publicly available football statistics suitable for player performance analysis.

---

## Decision 2

### Programming Language

**Selected**

Python

**Reason**

Python provides an extensive ecosystem for web scraping, data processing, automation, and analytics.

---

## Decision 3

### Database

**Selected**

SQLite

**Reason**

SQLite is lightweight, requires no server configuration, and is well suited for a portfolio-sized analytics project.

---

## Decision 4

### Visualization Platform

**Selected**

Microsoft Power BI

**Reason**

Power BI provides powerful interactive dashboards and integrates well with CSV and SQLite data sources.

---

## Decision 5

### Project Architecture

**Selected**

Modular Architecture

**Reason**

Separating scraping, processing, storage, and export logic improves maintainability, scalability, and readability.

---

## Decision 6

### Development Workflow

Development follows an incremental milestone-based approach.

Each milestone consists of:

1. Planning
2. Implementation
3. Validation
4. Documentation
5. Version control

Major architectural decisions are documented before implementation to ensure consistency throughout the project.

---

## Future Decisions

Additional architectural decisions will be documented as new project requirements arise.