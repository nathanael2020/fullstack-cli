#!/usr/bin/env python3
from pathlib import Path

def create_package_structure():
    """Creates the basic package structure for fullstack-cli with src layout"""
    
    # Create src and package directories
    src_dir = Path("src")
    package_dir = src_dir / "fullstack"
    src_dir.mkdir(exist_ok=True)
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Create README.md
    readme_content = """# Full Stack CLI

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
"""

    # Create pyproject.toml
    pyproject_content = """[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "fullstack-cli"
version = "0.1.0"
authors = [
    {name = "Nathanael Miksis"},
]
description = "A CLI tool to bootstrap full-stack web applications"
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
dependencies = [
    "python-dotenv>=1.0.0",
    "subprocess.run",
    "alembic==1.12.1",
    "flake8==6.1.0",
    "black==24.3.0",
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "gunicorn==21.0.0",
    "sqlalchemy==2.0.23",
    "python-dotenv==1.0.0",
    "pydantic==2.5.1"
]

[project.urls]
"Homepage" = "https://github.com/nathanael2020/fullstack-cli"
"Bug Tracker" = "https://github.com/nathanael2020/fullstack-cli/issues"

[project.scripts]
fullstack = "fullstack.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
"""

    # Write the files
    Path("README.md").write_text(readme_content)
    Path("pyproject.toml").write_text(pyproject_content)
    (package_dir / "__init__.py").touch()

    print("✓ Created package structure")
    print("\nNext steps:")
    print("1. Copy your cli.py and bootstrap.py files into the 'src/fullstack' directory")
    print("2. Run: pip install -e .")
    print("3. You can then use 'fullstack' command from anywhere")

if __name__ == "__main__":
    create_package_structure()