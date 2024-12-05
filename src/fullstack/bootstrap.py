import os
import sys
import json
import shutil
import subprocess
from sqlalchemy import Column, Integer, String
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# src/fullstack/bootstrap.py (the relevant part)
class FullStackBootstrap:
    def __init__(self):
        # Be explicit about using current working directory
        env_path = Path.cwd() / '.env'
        print(f"Looking for .env at: {env_path}")
        
        load_dotenv(env_path)
        
        # Debug output
        print(f"Current working directory: {Path.cwd()}")
        print("Environment variables loaded:")
        print(f"APP_NAME: {os.getenv('APP_NAME')}")
        print(f"API_PORT: {os.getenv('API_PORT')}")
        print(f"FRONTEND_PORT: {os.getenv('FRONTEND_PORT')}")
        print(f"DATABASE: {os.getenv('DATABASE')}")
        print(f"DB_NAME: {os.getenv('DB_NAME')}")
        print(f"DB_USER: {os.getenv('DB_USER')}")
        print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
        print(f"DB_HOST: {os.getenv('DB_HOST')}")
        print(f"DB_PORT: {os.getenv('DB_PORT')}")

        # Rest of the init...
        
        # Validate required env vars

        if os.getenv('DATABASE') == 'postgres':
            required_vars = ['APP_NAME', 'API_PORT', 'FRONTEND_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
        else:
            required_vars = ['APP_NAME', 'API_PORT', 'FRONTEND_PORT']

        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            print(f"Error: Missing required environment variables: {', '.join(missing)}")
            sys.exit(1)

# Get current directory name as default app name if not in env
        default_name = Path.cwd().name.replace(' ', '-').lower()
        
        print(f"Default app name: {default_name}")
        print(f"Setting up configuration")

        APP_NAME = os.getenv("APP_NAME", default_name)

        # Store configuration with defaults
        self.config = {
            'APP_NAME': APP_NAME,
            'API_PORT': os.getenv("API_PORT", "8000"),
            'FRONTEND_PORT': os.getenv("FRONTEND_PORT", "3000"),
            'DATABASE': os.getenv("DATABASE", "postgres"),
            'DB_NAME': os.getenv("DB_NAME", f"{APP_NAME.replace('-', '_')}_db"),
            'DB_USER': os.getenv("DB_USER", f"{APP_NAME.replace('-', '_')}_user"),
            'DB_PASSWORD': os.getenv("DB_PASSWORD", "change_me_in_production"),
            'DB_HOST': os.getenv("DB_HOST", "localhost"),
            'DB_PORT': os.getenv("DB_PORT", "5432"),
        }
        
        print(f"Configuration: {self.config}")
        
        # Set up paths
        self.root_dir = Path.cwd()
        self.app_dir = self.root_dir / self.config['APP_NAME']
        self.backend_dir = self.app_dir / 'backend'
        self.frontend_dir = self.app_dir / 'frontend'
        self.database_dir = self.backend_dir / 'app' / self.config['DB_NAME']

        if self.config['DATABASE'] == 'postgres':
            self.database_url = f"postgresql://{self.config['DB_USER']}:{self.config['DB_PASSWORD']}@{self.config['DB_HOST']}:{self.config['DB_PORT']}/{self.config['DB_NAME']}"
        else:
            self.database_url = f"sqlite:///{self.database_dir / self.config['DB_NAME']}.db"
            self.config['DATABASE_URL'] = self.database_url

    def check_dependencies(self):
        """Verify all required system dependencies are available"""
        
        print(f"Checking dependencies for {self.config['APP_NAME']}")

        dependencies = {
            'node': 'node --version',
            'npm': 'npm --version',
            'python3': 'python3 --version'
        }
        
        print(f"DATABASE: {self.config['DATABASE']}")
        print(f"DB_NAME: {self.config['DB_NAME']}")

        # Only check for postgres if using it
        if self.config['DATABASE'] == 'postgres':
            dependencies['postgres'] = 'psql --version'
    
        missing = []
        for dep, command in dependencies.items():
            try:
                subprocess.run(command.split(), capture_output=True, check=True)
                print(f"✓ Found {dep}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing.append(dep)
                print(f"✗ Missing {dep}")
        
        if missing:
            print(f"\nError: Missing required dependencies: {', '.join(missing)}")
            sys.exit(1)

    def setup_project(self):
        """Main setup function with error handling"""
        print("\nStarting project setup...")
        
        print(f"Checking dependencies for {self.config['APP_NAME']}")

        self.check_dependencies()
        
        print(f"Creating project structure for {self.config['APP_NAME']}")

        # Create project structure
        if self.app_dir.exists():
            print(f"\nWarning: Project directory {self.app_dir} already exists.")
            response = input("Do you want to remove it and start fresh? (y/N): ")
            if response.lower() == 'y':
                shutil.rmtree(self.app_dir)
            else:
                print("Setup aborted.")
                return

        print(f"Creating directory structure for {self.config['APP_NAME']}")
        self.create_directory_structure()

        print(f"Creating backend files for {self.config['APP_NAME']}")
        self.create_backend_files()
        print(f"Creating frontend files for {self.config['APP_NAME']}")
        self.create_frontend_files()
        print(f"Setting up database for {self.config['APP_NAME']}")
        self.setup_database()
        # self.create_demo_table_model()   # Add model definition for demo_table
        print(f"Setting up database migrations for {self.config['APP_NAME']}")
        self.setup_database_migrations() # Initialize Alembic and run migration
        print(f"Populating demo data for {self.config['APP_NAME']}")
        self.populate_demo_data()        # Populate demo_table with demo data
        self.create_start_script()
        
        print("\n✓ Setup completed successfully!")
        print("\nTo start your application, you have several options:")
        print(f"\ncd {self.config['APP_NAME']}")
        print("\nThen use one of these commands:")
        print("\n1. Start both frontend and backend (daemon mode):")
        print("   python start.py start both --daemon")
        print("\n2. Start individual services:")
        print("   • Frontend only:")
        print("     python start.py start front")
        print("   • Backend only:")
        print("     python start.py start back")
        print("\n3. Other useful commands:")
        print("   • Stop all services:")
        print("     python start.py stop both")
        print("   • Restart services:")
        print("     python start.py restart both --daemon")
        print("\nNote: Running without --daemon will show live logs in the terminal")
        print("      but requires keeping the terminal window open.")
                    
        # except Exception as e:
        #     print(f"\nError during setup: {str(e)}")
        #     print("Setup failed. Please check the error message above.")
        #     sys.exit(1)

    def create_start_script(self):
        """Create the service controller script"""
        start_script = '''#!/usr/bin/env python3

import os
import subprocess
import argparse
from pathlib import Path
from dotenv import load_dotenv
import json

load_dotenv()

class ProjectController:
    def __init__(self):
        self.project_dir = Path(__file__).resolve().parent
        parent_dir = self.project_dir.parent  # Go up one level to where setup.py and .env are
        self.backend_dir = self.project_dir / "backend"
        self.frontend_dir = self.project_dir  / "frontend"
        self.api_port = os.getenv("API_PORT")
        self.frontend_port = os.getenv("FRONTEND_PORT")
        self.venv_dir = parent_dir / ".venv"
        self.gunicorn = self.venv_dir / "bin" / "gunicorn"
        self.uvicorn = self.venv_dir / "bin" / "uvicorn"
        self.log_file = self.project_dir / "daemon.log"

    def stop_service(self, service):
        """Stop specified service(s)"""
        try:
            if service in ['back', 'both']:
                subprocess.run(f"pkill -f ':{self.api_port}|\\-p {self.api_port}'", shell=True, check=False)
                print(f"✓ Stopped any process on port {self.api_port} (API)")
            
            if service in ['front', 'both']:
                subprocess.run(f"pkill -f ':{self.frontend_port}|\\-p {self.frontend_port}'", shell=True, check=False)
                print(f"✓ Stopped any process on port {self.frontend_port} (Frontend)")
        except Exception as e:
            print(f"Error stopping {service}:", e)

    def start_service(self, service, daemon=False):
        """Start specified service(s)"""

        if service == 'both' and not daemon:
            print("Error: Cannot start both services in non-daemon mode.")
            print("Please either:")
            print("1. Use --daemon flag to run both services")
            print("2. Or start services separately in different terminals:")
            print(f"   python start.py start back")
            print(f"   python start.py start front")
            return
            
        try:
            if service in ['back', 'both']:
                self._start_backend(daemon)
            
            if service in ['front', 'both']:
                self._start_frontend(daemon)
        except Exception as e:
            print(f"Error starting {service}:", e)

    def _start_backend(self, daemon):
        """Start the backend service"""
        if not self.backend_dir.exists():
            raise FileNotFoundError(f"Backend directory not found: {self.backend_dir}")

        # Activate virtual environment in the environment
        activate_script = self.venv_dir / "bin" / "activate"
        activate_cmd = f"source {activate_script}"
        
        if daemon:
            # Daemon mode uses gunicorn
            backend_command = [
                "nohup", str(self.gunicorn),
                "-k", "uvicorn.workers.UvicornWorker",
                "app.main:app",  # Changed to use the correct module path
                "--bind", f"0.0.0.0:{self.api_port}",
                "--timeout", "600"
            ]
            with open(self.log_file, "a") as log:
                process = subprocess.Popen(
                    backend_command,
                    cwd=self.backend_dir,
                    stdout=log,
                    stderr=log,
                    env={**os.environ, "PYTHONPATH": str(self.backend_dir)}
                )
                print(f"✓ Backend started on port {self.api_port} (daemonized)")
        else:
            # Non-daemon mode uses uvicorn directly
            backend_command = [
                str(self.uvicorn),
                "app.main:app",  # Changed to use the correct module path
                "--host", "0.0.0.0",
                "--port", str(self.api_port),
                "--reload"
            ]
            subprocess.run(
                backend_command,
                cwd=self.backend_dir,
                env={**os.environ, "PYTHONPATH": str(self.backend_dir)},
                check=True
            )

    def _start_frontend(self, daemon):
        """Start the frontend service with improved npm handling"""
        if not self.frontend_dir.exists():
            raise FileNotFoundError(f"Frontend directory not found: {self.frontend_dir}")
        
        # Improved npm installation process
        try:
            print("Setting up frontend dependencies...")
            
            # Update npm itself first
            subprocess.run(["npm", "install", "npm@latest"], 
                        check=True, 
                        capture_output=True,
                        text=True)
            
            # Install dependencies with specific flags to reduce warnings
            install_result = subprocess.run(
                ["npm", "install", 
                "--no-fund", # Disable funding messages
                "--no-audit", # Disable audit warnings
                "--loglevel=error" # Only show errors
                ], 
                cwd=self.frontend_dir,
                capture_output=True,
                text=True
            )
            
            if install_result.returncode == 0:
                print("✓ Frontend dependencies installed")
            else:
                print("! Warning: npm install completed with issues:")
                print(install_result.stderr)
            
            # Run security audit and fix
            print("Checking for security vulnerabilities...")
            audit_result = subprocess.run(
                ["npm", "audit", "fix", "--force"],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True
            )
            
            if audit_result.returncode == 0:
                print("✓ Security vulnerabilities fixed")
            else:
                print("! Warning: Some security issues couldn't be automatically fixed")
                print("  Run 'npm audit' manually in the frontend directory for details")
            
            # Start the frontend
            if daemon:
                frontend_command = ["nohup", "npm", "run", "dev"]

                with open(self.log_file, "a") as log:
                    subprocess.Popen(
                        frontend_command,
                        cwd=self.frontend_dir,
                        stdout=log,
                        stderr=log,
                        env={**os.environ, 
                            "NODE_ENV": "development",
                            "DISABLE_ESLINT_PLUGIN": "true",
                            "PORT": str(self.frontend_port)
                        }
                    )
                    print(f"✓ Frontend started on port {self.frontend_port} (daemonized)")
            else:
                frontend_command = ["npm", "run", "dev"]
                subprocess.run(
                    frontend_command, 
                    cwd=self.frontend_dir, 
                    check=True,
                    env={**os.environ, 
                        "NODE_ENV": "development",
                        "DISABLE_ESLINT_PLUGIN": "true",
                        "PORT": str(self.frontend_port)
                    }
                )


        except subprocess.CalledProcessError as e:
            print(f"Error starting frontend: {e}")
            if e.output:
                print(f"Output: {e.output}")
            raise

    # Update package.json creation to use newer versions and configurations
    def create_frontend_files(self):
        """Create frontend configuration and files with updated dependencies"""
        package_json = {
            "name": self.config['APP_NAME'],
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": f"next dev -p {self.config['FRONTEND_PORT']}",
                "build": "next build",
                "start": f"next start -p {self.config['FRONTEND_PORT']}",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "^14.1.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "@tanstack/react-query": "^5.17.9",
                "axios": "^1.6.7"
            },
            "devDependencies": {
                "typescript": "^5.3.3",
                "@types/node": "^20.11.0",
                "@types/react": "^18.2.48",
                "@types/react-dom": "^18.2.18",
                "autoprefixer": "^10.4.17",
                "postcss": "^8.4.33",
                "tailwindcss": "^3.4.1"
            }
        }

        # Add npm configurations to reduce warnings
        npm_rc = {
            "fund": False,
            "audit": False,
            "loglevel": "error",
            "save-exact": True
        }

        with open(self.frontend_dir / 'package.json', 'w') as f:
            json.dump(package_json, f, indent=2)

        with open(self.frontend_dir / '.npmrc', 'w') as f:
            for key, value in npm_rc.items():
                f.write(f"{key}={str(value).lower()}")

def main():
    parser = argparse.ArgumentParser(description='Control project services')
    parser.add_argument('action', choices=['start', 'stop', 'restart'],
                      help='Action to perform')
    parser.add_argument('service', choices=['front', 'back', 'both'],
                      help='Service to control')
    parser.add_argument('--daemon', action='store_true',
                      help='Run in daemon mode (for start/restart)')
    
    args = parser.parse_args()
    controller = ProjectController()

    if args.action == 'stop':
        controller.stop_service(args.service)
    elif args.action == 'start':
        controller.start_service(args.service, args.daemon)
    elif args.action == 'restart':
        controller.stop_service(args.service)
        controller.start_service(args.service, args.daemon)

if __name__ == "__main__":
    main()
'''
        
        with open(self.app_dir / 'start.py', 'w') as f:
            f.write(start_script)
        os.chmod(self.app_dir / 'start.py', 0o755)

    # (Your existing methods for creating the project structure, 
    #  setting up database, etc. would follow here)

    def create_directory_structure(self):
        """Create the project directory structure"""
        directories = [
            self.backend_dir / 'app' / 'api',
            self.backend_dir / 'app' / 'models',
            self.frontend_dir / 'src' / 'app',
            self.frontend_dir / 'src' / 'app' / 'demo_tables',
            self.frontend_dir / 'src' / 'app' / 'demo_tables' / '[id]',
            self.frontend_dir / 'src' / 'components',
            self.frontend_dir / 'src' / 'pages',
            self.frontend_dir / 'src' / 'styles',
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def create_backend_files(self):
        """Create backend files with main FastAPI setup and essential modules"""

        print(f"Creating backend files for {self.config['APP_NAME']}")

        # Create the `requirements.txt` file with updated dependencies
        requirements = [
            'alembic==1.12.1',
            'flake8==6.1.0',
            'black==24.3.0',
            'fastapi==0.104.1',
            'uvicorn[standard]==0.24.0',
            'gunicorn==21.0.0',
            'sqlalchemy==2.0.23',
            'python-dotenv==1.0.0',
            'pydantic==2.5.1'
        ]

        print(f"Adding postgres-specific requirement: {self.config['DATABASE'] == 'postgres'}")

        # Add postgres-specific requirement
        if self.config['DATABASE'] == 'postgres':
            requirements.append('psycopg2-binary==2.9.10')

        print(f"Writing requirements to {self.backend_dir / 'requirements.txt'}")

        with open(self.backend_dir / 'requirements.txt', 'w') as f:
            f.write('\n'.join(requirements))

        print(f"Writing main FastAPI application file to {self.backend_dir / 'app' / 'main.py'}")

    # Main FastAPI application file
        main_app = """
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.demo_table import DemoTable
from app.crud import create_demo_table, get_demo_table, get_demo_table_by_id
from app.schemas import DemoTable as DemoTableSchema
from app import models, schemas
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

app = FastAPI(title="{APP_NAME}") 

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:{FRONTEND_PORT}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware to add trailing slashes
@app.middleware("http")
async def add_trailing_slash(request: Request, call_next):
    if not request.url.path.endswith("/"):
        return RedirectResponse(url=str(request.url) + "/")
    response = await call_next(request)
    return response

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define routes with different combinations
@app.get("/demo-tables/", response_model=list[DemoTableSchema])
@app.get("/demo_tables/", response_model=list[DemoTableSchema])
@app.get("/demo-tables", response_model=list[DemoTableSchema])
@app.get("/demo_tables", response_model=list[DemoTableSchema])
async def read_demo_tables(db: Session = Depends(get_db)):
    return db.query(DemoTable).all()

@app.get("/demo-tables/{{demo_table_id}}/", response_model=DemoTableSchema)
@app.get("/demo_tables/{{demo_table_id}}/", response_model=DemoTableSchema)
@app.get("/demo-tables/{{demo_table_id}}", response_model=DemoTableSchema)
@app.get("/demo_tables/{{demo_table_id}}", response_model=DemoTableSchema)
async def read_demo_table(demo_table_id: int, db: Session = Depends(get_db)):
    demo_table = db.query(DemoTable).filter(DemoTable.id == demo_table_id).first()
    if demo_table is None:
        raise HTTPException(status_code=404, detail="DemoTable not found")
    return demo_table
""".format(**self.config)

        print(f"Writing main FastAPI application file to {self.backend_dir / 'app' / 'main.py'}")
        with open(self.backend_dir / 'app' / 'main.py', 'w') as f:
            f.write(main_app.strip())

        # `database.py` for DB setup
        database_file = """
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()


# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/database.db")

# Add connect_args only for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
"""
        print(f"Writing database file to {self.backend_dir / 'app' / 'database.py'}")

        with open(self.backend_dir / 'app' / 'database.py', 'w') as f:
            f.write(database_file.strip())

        # `models.py` for defining the PDF model
        demo_table_model = """
from sqlalchemy import Column, Integer, String
from app.database import Base

class DemoTable(Base):
    __tablename__ = "demo_table"
    id = Column(Integer, primary_key=True, index=True)
    demo_field = Column(String, nullable=False)
"""

        print(f"Writing demo table model to {self.backend_dir / 'app' / 'models' / 'demo_table.py'}")

        with open(self.backend_dir / 'app' / 'models' / 'demo_table.py', 'w') as f:
            f.write(demo_table_model.strip())

        # `__init__.py` for models module
        init_file = """
from app.database import Base
from .demo_table import DemoTable
"""

        print(f"Writing models init file to {self.backend_dir / 'app' / 'models' / '__init__.py'}")

        with open(self.backend_dir / 'app' / 'models' / '__init__.py', 'w') as f:
            f.write(init_file.strip())

        # `crud.py` for database operations
        crud_file = """
from sqlalchemy.orm import Session
from . import models, schemas
from app.models.demo_table import DemoTable

def create_demo_table(db: Session, demo_table: schemas.DemoTableCreate):
    db_demo_table = DemoTable(demo_field=demo_table.demo_field)
    db.add(db_demo_table)
    db.commit()
    db.refresh(db_demo_table)
    return db_demo_table

def get_demo_table(db: Session):
    return db.query(DemoTable).all()

def get_demo_table_by_id(db: Session, demo_table_id: int):
    return db.query(DemoTable).filter(DemoTable.id == demo_table_id).first()
"""

        print(f"Writing crud file to {self.backend_dir / 'app' / 'crud.py'}")

        with open(self.backend_dir / 'app' / 'crud.py', 'w') as f:
            f.write(crud_file.strip())

        # `schemas.py` for Pydantic models
        schemas_file = """
from pydantic import BaseModel

class DemoTableBase(BaseModel):
    demo_field: str

class DemoTableCreate(DemoTableBase):
    pass

class DemoTable(DemoTableBase):
    id: int

    class Config:
        orm_mode = True
"""

        print(f"Writing schemas file to {self.backend_dir / 'app' / 'schemas.py'}")

        with open(self.backend_dir / 'app' / 'schemas.py', 'w') as f:
            f.write(schemas_file.strip())


    def create_frontend_files(self):
        """Create frontend configuration and files"""
        package_json = {
            "name": self.config['APP_NAME'],
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": f"next dev -p {self.config['FRONTEND_PORT']}",
                "build": "next build",
                "start": f"next start -p {self.config['FRONTEND_PORT']}",
                "lint": "eslint . --ext .ts,.tsx"
            },
            "dependencies": {
                "next": "14.0.3",
                "react": "^18",
                "react-dom": "^18",
                "@tanstack/react-query": "^5.8.4",
                "axios": "^1.6.2"
            },
            "devDependencies": {
                "typescript": "^5",
                "@types/node": "^20",
                "@types/react": "^18",
                "@types/react-dom": "^18",
                "autoprefixer": "^10.0.1",
                "postcss": "^8",
                "tailwindcss": "^3.3.0",
                "eslint": "^8",
                "eslint-config-next": "14.0.3"
            }
        }

        with open(self.frontend_dir / 'package.json', 'w') as f:
            json.dump(package_json, f, indent=2)

        # Create essential Next.js files
        self.create_nextjs_files()


    def setup_database(self):
        """Drop and recreate PostgreSQL user and database with specified privileges"""
        if self.config['DATABASE'] == 'sqlite':
            # For SQLite, just ensure the directory exists
            # db_path = self.backend_dir / 'app' / self.config['DB_NAME'] / '.db'
            # db_path.parent.mkdir(parents=True, exist_ok=True)
            # print("✓ SQLite database location prepared")
            return
        
        try:
            # Drop the database if it exists
            subprocess.run([
                "psql", "-h", self.config['DB_HOST'], "-p", self.config['DB_PORT'],
                "-U", os.getenv("USER"), "-d", 'postgres',  # Uses the current system user
                "-c", f"DROP DATABASE IF EXISTS {self.config['DB_NAME']};"
            ], check=True)
            print("✓ Dropped existing database")

            # Drop the user if it exists
            subprocess.run([
                "psql", "-h", self.config['DB_HOST'], "-p", self.config['DB_PORT'],
                "-U", os.getenv("USER"), "-d", 'postgres',  # Uses the current system user
                "-c", f"DROP ROLE IF EXISTS {self.config['DB_USER']};"
            ], check=True)
            print("✓ Dropped existing user")

            # Create the user with the specified password
            subprocess.run([
                "psql", "-h", self.config['DB_HOST'], "-p", self.config['DB_PORT'],
                "-U", os.getenv("USER"), "-d", 'postgres',  # Uses the current system user
                "-c", f"CREATE USER {self.config['DB_USER']} WITH PASSWORD '{self.config['DB_PASSWORD']}' CREATEDB;"
            ], check=True)
            print("✓ Created PostgreSQL user")

            # Create the database owned by the new user
            subprocess.run([
                "psql", "-h", self.config['DB_HOST'], "-p", self.config['DB_PORT'],
                "-U", os.getenv("USER"), "-d", 'postgres',  # Uses the current system user
                "-c", f"CREATE DATABASE {self.config['DB_NAME']} OWNER {self.config['DB_USER']};"
            ], check=True)
            print("✓ Created PostgreSQL database")

        except subprocess.CalledProcessError as e:
            print("Error setting up database or user:", e)


    def setup_database_migrations(self):
        """Set up Alembic for database migrations and create initial migration with demo table."""
        # Step 1: Initialize Alembic
        subprocess.run(["alembic", "init", "alembic"], cwd=self.backend_dir)

        # Step 2: Update `alembic.ini` with the database URL
        alembic_ini_path = self.backend_dir / "alembic.ini"
        with open(alembic_ini_path, "r") as file:
            alembic_ini = file.read()

        # Determine the correct database URL based on the database type
        if self.config['DATABASE'] == 'postgres':
            database_url = (
                f"postgresql://{self.config['DB_USER']}:{self.config['DB_PASSWORD']}"
                f"@{self.config['DB_HOST']}:{self.config['DB_PORT']}/{self.config['DB_NAME']}"
            )
        elif self.config['DATABASE'] == 'sqlite':
            database_url = f"sqlite:///{self.backend_dir / 'app' / self.config['DB_NAME']}.db"
        else:
            raise ValueError("Unsupported database type")

        updated_alembic_ini = alembic_ini.replace(
            "sqlalchemy.url = driver://user:pass@localhost/dbname",
            f"sqlalchemy.url = {database_url}"
        )

        with open(alembic_ini_path, "w") as file:
            file.write(updated_alembic_ini)

        # Step 3: Update `env.py` to reference the metadata from your models
        env_path = self.backend_dir / "alembic" / "env.py"
        with open(env_path, "r") as file:
            env_content = file.read()

        # Inject the import statement and metadata setup
        updated_env_content = env_content.replace(
            "target_metadata = None",
            "from app.models import Base\n"
            "target_metadata = Base.metadata"
        )

        with open(env_path, "w") as file:
            file.write(updated_env_content)

        # Step 4: Generate the initial migration
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", "create demo_table"], cwd=self.backend_dir)

        # Step 5: Apply the migration to create the `demo_table`
        subprocess.run(["alembic", "upgrade", "head"], cwd=self.backend_dir)

    def create_demo_table_model(self):
        """Add a DemoTable model to `models.py`."""
        demo_table_model = """
from sqlalchemy import Column, Integer, String
from app.database import Base

class DemoTable(Base):
    __tablename__ = "demo_table"
    id = Column(Integer, primary_key=True, index=True)
    demo_field = Column(String, nullable=False)
"""
        models_path = self.backend_dir / 'app' / 'models' / 'demo_table.py'
        with open(models_path, 'a') as f:
            f.write(demo_table_model)
            
    def populate_demo_data(self):
        """Populate demo_table with initial data."""
        demo_data_script = """
import sys
from pathlib import Path

# Add the root project directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models.demo_table import DemoTable

db = SessionLocal()
# try:
demo_record = DemoTable(demo_field="You're up and running!")
db.add(demo_record)
db.commit()
print("✓ Populated demo data")
# except Exception as e:
#     print(f"Error populating demo data: {e}")
#     db.rollback()
# finally:
# db.close()
"""
        populate_script_path = self.backend_dir / 'app' / 'populate_demo_data.py'
        with open(populate_script_path, 'w') as f:
            f.write(demo_data_script)

        # Run the script to insert the record
        result = subprocess.run(["python", populate_script_path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running populate script: {result.stderr}")
        else:
            print(result.stdout)

    def create_nextjs_files(self):
        """Create basic Next.js files with additional configurations and Tailwind setup"""

        # Create tsconfig.json with updated compiler options
        tsconfig = {
            "compilerOptions": {
                "target": "es5",
                "lib": ["dom", "dom.iterable", "esnext"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "node",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "paths": {
                    "@/*": ["./src/*"]
                }
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"]
        }
        
        with open(self.frontend_dir / 'tsconfig.json', 'w') as f:
            json.dump(tsconfig, f, indent=2)


        # Create next.config.js for Next.js custom configurations
        next_config = """
module.exports = {
    async rewrites() {
        console.log("Processing rewrites...");
        return [
            {
                source: '/demo-tables/',
                destination: '/demo_tables/',
            },
            {
                source: '/demo-tables/:id/',
                destination: '/demo_tables/:id/',
            },
        ];
    },
    webpack: (config) => {
        // Optional: Disable Webpack caching for debugging purposes
        config.cache = false;
        return config;
    },
    trailingSlash: true,
};
""".strip()

        with open(self.frontend_dir / 'next.config.js', 'w') as f:
            f.write(next_config)

        # Set up Tailwind CSS configuration
        tailwind_config = """
module.exports = {
    content: ["./src/**/*.{js,ts,jsx,tsx}"],
    theme: {
        extend: {}
    },
    "plugins": []
}
""".strip()

        with open(self.frontend_dir / 'tailwind.config.js', 'w') as f:
            f.write(tailwind_config)

        # Corrected `postcss.config.js` content as JavaScript, not JSON
        postcss_config = """
module.exports = {
    plugins: {
        tailwindcss: {},
        autoprefixer: {},
    },
};
""".strip()

        with open(self.frontend_dir / 'postcss.config.js', 'w') as f:
            f.write(postcss_config)

        # Set up ESLint configuration
        eslint_config = {
            "extends": ["next", "next/core-web-vitals", "prettier"],
            "rules": {
                "semi": ["error", "always"],
                "quotes": ["error", "single"]
            }
        }

        with open(self.frontend_dir / '.eslintrc.json', 'w') as f:
            json.dump(eslint_config, f, indent=2)

        # Set up Prettier configuration
        prettier_config = {
            "semi": True,
            "singleQuote": True,
            "tabWidth": 2,
            "trailingComma": "all"
        }

        with open(self.frontend_dir / '.prettierrc', 'w') as f:
            json.dump(prettier_config, f, indent=2)

        # Basic Tailwind CSS styles
        tailwind_styles = """
@tailwind base;
@tailwind components;
@tailwind utilities;
""".strip()

        styles_dir = self.frontend_dir / 'src' / 'styles'
        styles_dir.mkdir(parents=True, exist_ok=True)
        
        with open(styles_dir / 'globals.css', 'w') as f:
            f.write(tailwind_styles)

        # Create a basic layout component
        layout_content = f"""
    import React from 'react';
    import Link from 'next/link';
    import '../styles/globals.css';

    export const metadata = {{
        title: '{self.config['APP_NAME']}',
        description: 'Generated by Next.js',
    }}

    export default function RootLayout({{ children }}) {{
        return (
            <html lang="en">
                <body>
                    <header>
                        <nav className="p-4 bg-gray-100">
                            <ul className="flex space-x-4">
                                <li><Link href="/">Home</Link></li>
                                <li><Link href="/about">About</Link></li>
                            </ul>
                        </nav>
                    </header>
                    <main>{{children}}</main>
                </body>
            </html>
        )
    }}
        """.strip()

        with open(self.frontend_dir / 'src' / 'app' / 'layout.tsx', 'w') as f:
            f.write(layout_content)

        # Create the main page component
        page_content = f"""
import Link from 'next/link';
export default function Home() {{
    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-blue-50">
            <h1 className="text-4xl font-bold">{self.config['APP_NAME']}</h1>
            <p className="text-lg mt-4">Your application is ready!</p>
            <p className="text-lg mt-4">You can view the <Link href="/demo-tables/">Demo Tables</Link> page.</p>
        </main>
    )
}}
        """.strip()

        with open(self.frontend_dir / 'src' / 'app' / 'page.tsx', 'w') as f:
            f.write(page_content)

        # Content for demo_tables/page.tsx
        demo_tables_page_content = f"""
"use client";
import {{ useEffect, useState }} from 'react';
import Link from 'next/link';
import axios from 'axios';

type DemoTable = {{
  id: number;
  demo_field: string;
}};

export default function DemoTablesPage() {{
  const [demoTables, setDemoTables] = useState<DemoTable[]>([]);

  useEffect(() => {{
    const fetchDemoTables = async () => {{
      try {{
        const response = await axios.get<DemoTable[]>('http://localhost:{self.config['API_PORT']}/demo-tables/');
        setDemoTables(response.data);
      }} catch (error) {{
        console.error("Error fetching demo tables:", error);
      }}
    }};
    fetchDemoTables();
  }}, []);

  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-4">Demo Tables</h1>
      <ul>
        {{demoTables.map((demoTable) => (
          <li key={{demoTable.id}}>
            <Link href={{`/demo-tables/${{demoTable.id}}/`}}>
              {{demoTable.demo_field}}
            </Link>
          </li>
        ))}}
      </ul>
    </main>
  );
}}
""".strip()

        with open(self.frontend_dir / 'src' / 'app' / 'demo_tables' / 'page.tsx', 'w') as f:
            f.write(demo_tables_page_content)


        # Content for demo_tables/[id]/page.tsx
        demo_table_detail_page_content = f"""
"use client";
import {{ useParams }} from 'next/navigation';
import {{ useEffect, useState }} from 'react';
import axios from 'axios';

type DemoTable = {{
  id: number;
  demo_field: string;
}};

export default function DemoTableDetailPage() {{
    const params = useParams();
    if (!params.id) {{
        return <p>Loading...</p>;
    }}
    const id = params.id as string;
    const [demoTable, setDemoTable] = useState<DemoTable | null>(null);

  useEffect(() => {{
    if (id) {{
      const fetchDemoTable = async () => {{
        try {{
          const response = await axios.get<DemoTable>(`http://localhost:{self.config['API_PORT']}/demo-tables/${{id}}/`);
          setDemoTable(response.data);
        }} catch (error) {{
          console.error("Error fetching demo table:", error);
        }}
      }};
      fetchDemoTable();
    }}
  }}, [id]);

  if (!demoTable) return <p>Loading...</p>;

  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-4">Demo Table Detail</h1>
      <p>ID: {{demoTable.id}}</p>
      <p>Field: {{demoTable.demo_field}}</p>
    </main>
  );
}}
""".strip()

        with open(self.frontend_dir / 'src' / 'app' / 'demo_tables' / '[id]' / 'page.tsx', 'w') as f:
            f.write(demo_table_detail_page_content)

        # Create an About page as an example
        about_page_content = """
    export default function About() {
        return (
            <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-green-50">
                <h1 className="text-4xl font-bold">About Us</h1>
                <p className="text-lg mt-4">This is an example of an About page.</p>
            </main>
        )
    }
        """.strip()

        (self.frontend_dir / 'src' / 'app' / 'about').mkdir(parents=True, exist_ok=True)
        with open(self.frontend_dir / 'src' / 'app' / 'about' / 'page.tsx', 'w') as f:
            f.write(about_page_content)

    def setup_virtual_environment(self):
        """Set up Python virtual environment and install requirements"""
        subprocess.run([sys.executable, '-m', 'venv', self.project_dir / '.venv'])
        
        # Install requirements
        venv_pip = str(self.project_dir / '.venv' / 'bin' / 'pip')
        subprocess.run([venv_pip, 'install', '-r', str(self.backend_dir / 'requirements.txt')])



if __name__ == "__main__":
    bootstrap = FullStackBootstrap()
    bootstrap.setup_project()
