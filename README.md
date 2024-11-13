# Full Stack CLI

A command-line tool to quickly bootstrap full-stack web applications with FastAPI and Next.js.

## Installation

```bash
pip install fullstack-cli
```

## Usage

Basic usage:
```bash
fullstack my-project
```

Custom configuration:
```bash
fullstack my-project --api-port 8000 --frontend-port 3000 --db-name custom_db
```

## Project Structure

The generated project includes:

- FastAPI backend
- Next.js frontend with TypeScript
- PostgreSQL database setup
- Development server management script
- Environment configuration

## Requirements

- Python 3.8+
- Node.js and npm
- PostgreSQL

## License

MIT
