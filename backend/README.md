# PRJ_628 Backend

FastAPI + SQLAlchemy backend using MySQL.

## MySQL configuration

1. Create database `prj628`.
2. Copy `.env.example` to `.env`.
3. Set `MYSQL_PASSWORD` and other values as required.
4. Install dependencies with `pip install -r requirements.txt`.

The backend builds the connection using SQLAlchemy's MySQL/PyMySQL dialect and reads credentials from environment variables.
