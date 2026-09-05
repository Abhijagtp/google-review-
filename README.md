# AI Review Booster App

An AI-powered Google Review generation platform built with **Django 5.x**, **Docker**, **Neon PostgreSQL**, **HTMX**, and **Tailwind CSS**.

---

## 🎯 Product Overview

### Distribution Model: Turnkey / Installable Product (White-Label)
This application is designed as an **installable, self-hosted product** rather than a shared SaaS platform. You can deploy and sell dedicated instances to individual client businesses with zero code modifications needed per deployment.

### Problem Statement
Customers often want to leave a positive Google review for a business, but struggle with "writer's block" (not knowing what to type or how to express their feedback). This friction leads to low review conversion rates or generic 1-word feedback.

### Solution
The **AI Review Booster App** solves this problem by providing customers with instant, context-aware AI review suggestions that they can copy with 1 click and paste directly into Google Reviews.

---

## 💻 Frontend & UI/UX Stack

- **HTMX**: Powers seamless, single-page application (SPA) interactions without full page reloads, driving dynamic AI generation and real-time dashboard updates.
- **Tailwind CSS**: Utility-first CSS framework for clean, responsive, modern, and high-performance design across all views.
- **Business Admin Dashboard**: Built using **Tailwind CSS + HTMX + Shadcn-style UI components** for a sleek, enterprise-grade management interface.
- **Customer Review Interface**: Built using **Tailwind CSS + HTMX** optimized for mobile-first user experience, fluid micro-interactions, zero friction, and maximum review conversion rates.

---

## 🔑 Key Features & Architecture

- **100% Dynamic Configuration (Zero Hardcoding)**:
  - All business metadata (Name, Logo, Industry, Google Place ID / Direct Review Link, Theme Colors, AI Providers & Keys) is fully configurable via the Admin Panel.
  - Allows instant setup for any new client without changing a single line of codebase.

- **BYOK (Bring Your Own Key)**:
  - Each business instance uses its own AI API Key (e.g., OpenAI / Gemini) configured dynamically in the database/admin setting, ensuring complete isolation and zero shared API costs.

- **Business Context Engine ("Skill" System)**:
  - Businesses configure rich context (key services, unique selling points, tone/style guidelines, custom prompts).
  - This acts as a tailored "skill" system that grounds the AI to generate accurate, authentic, and highly relevant review options for that specific business.

- **1-Click Copy & Redirect**:
  - Customers select an AI-generated suggestion, copy it with a single click, and are automatically redirected to the business's Google Review page.

---

## 🚀 Quick Start

### 1. Environment Setup
Copy `.env.example` to `.env` (or update `.env`):
```bash
cp .env.example .env
```

Ensure your **Neon Database URL** is set in `.env`:
```env
DATABASE_URL=postgresql://user:password@ep-xyz.region.aws.neon.tech/neondb?sslmode=require
```

---

## 🐳 Docker Commands

### Build & Start Containers
```bash
docker compose up --build
```
The server will be running at `http://localhost:8000`.

### Run Database Migrations
```bash
docker compose run --rm web python manage.py migrate
```

### Create Superuser (Admin Account)
```bash
docker compose run --rm web python manage.py createsuperuser
```

---

## 📂 Project Structure

```
├── apps/               # Modular Django Applications
│   ├── __init__.py
│   └── business/       # Dynamic Business settings, AI Context & Skills engine
├── config/             # Core Django configuration (settings, urls, wsgi)
├── templates/          # Global HTML templates (Admin Dashboard & Customer UI)
├── .env                # Environment variables (Neon DB, Secret Keys)
├── docker-compose.yml  # Docker Compose orchestration
├── Dockerfile          # Python 3.12 container specification
├── manage.py
├── README.md
└── requirements.txt
```
