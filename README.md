# Alawel Tech Electric

This is a Flask web application to manage customers' information and their top-up transactions using a SQLite database and SQLAlchemy for database interactions. The app allows you to:

- View all customers and their top-ups
- Add and edit customer records, including account type and numbers
- Manage top-up transactions linked to specific customers
- View advanced statistics on top-ups

## Features

- **Customer & Top-up Management**: Add, view, edit customers and their respective top-up records.
- **Advanced Statistics Dashboard**: View top-up statistics organized by Daily, Monthly, Yearly, By Customer, and By Account Type via a tabbed interface.
- **Live Search**: Integrated live search functionality for scoping searches within statistics tables.
- **Flask SQLAlchemy**: Database ORM for managing data.
- **SQLite**: Local database for development.
- **Bootstrap**: For basic styling and responsive layout of the web interface.

---

## Tech Stack

- **Frontend**: HTML, CSS (with Bootstrap)
- **Backend**: Python (Flask Framework)
- **Database**: SQLite (local development)

---

## Installation & Setup Guide

### Prerequisites

- Python 3.8 or later
- pip (Python package manager)

### 1. Install Dependencies

Install the required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Database Migrations (Schema Updates)

This application uses `Flask-Migrate` to manage database schema changes safely without manually querying SQLite.

**When setting up for the first time or after pulling new changes:**
Run the following command to apply the latest database schemas:
```bash
flask db upgrade
```

**(For Developers) How to create a new migration after modifying models:**
1. Modify `app.py` models.
2. Generate the migration script: `flask db migrate -m "Description of changes"`
3. Apply the changes to the database: `flask db upgrade`

### 3. Running the Application

To run the Flask application, execute the following command:

```bash
python3 app.py
```

The app will be available at `http://0.0.0.0:80/` (or `http://localhost:80/`).
