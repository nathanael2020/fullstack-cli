# Full Stack CLI

A command-line tool to quickly bootstrap full-stack web applications with FastAPI and Next.js.

## Installation

```bash
pip install fullstack-cli
```

## Usage

Basic usage with PostgreSQL (default):
```bash
fullstack my-project
```

Use SQLite instead:
```bash
fullstack my-project --database sqlite
```


Custom configuration (example):
```bash
fullstack my-project --api-port 8000 --frontend-port 3000 --db-port 5432 --db-name custom_db --database postgres
```

## Project Structure

The generated project includes:

- FastAPI backend
- Next.js frontend with TypeScript
- PostgreSQL database setup (or SQLite)
- Development server management script
- Environment configuration

## Requirements

- Python 3.8+
- Node.js and npm
- Database (choose one):
  - PostgreSQL installed and running locally (5432)
  - SQLite (no installation needed)

## License

MIT
