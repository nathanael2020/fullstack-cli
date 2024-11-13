import os
import sys
import json
import shutil
import subprocess
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

        # Rest of the init...
        
        # Validate required env vars
        # required_vars = ['APP_NAME', 'API_PORT', 'FRONTEND_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        # missing = [var for var in required_vars if not os.getenv(var)]
        # if missing:
        #     print(f"Error: Missing required environment variables: {', '.join(missing)}")
        #     sys.exit(1)

# Get current directory name as default app name if not in env
        default_name = Path.cwd().name.replace(' ', '-').lower()
        
        # Store configuration with defaults
        self.config = {
            'app_name': os.getenv("APP_NAME", default_name),
            'api_port': os.getenv("API_PORT", "8000"),
            'frontend_port': os.getenv("FRONTEND_PORT", "3000"),
            'db_name': os.getenv("DB_NAME", f"{default_name.replace('-', '_')}_db"),
            'db_user': os.getenv("DB_USER", f"{default_name.replace('-', '_')}_user"),
            'db_password': os.getenv("DB_PASSWORD", "change_me_in_production"),
            'db_host': os.getenv("DB_HOST", "localhost"),
            'db_port': os.getenv("DB_PORT", "5432")
        }
        
        # Set up paths
        self.root_dir = Path.cwd()
        self.app_dir = self.root_dir / self.config['app_name']
        self.backend_dir = self.app_dir / 'backend'
        self.frontend_dir = self.app_dir / 'frontend'


    def check_dependencies(self):
        """Verify all required system dependencies are available"""
        dependencies = {
            'postgres': 'psql --version',
            'node': 'node --version',
            'npm': 'npm --version',
            'python3': 'python3 --version'
        }
        
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
        try:
            print("\nStarting project setup...")
            self.check_dependencies()
            
            # Create project structure
            if self.app_dir.exists():
                print(f"\nWarning: Project directory {self.app_dir} already exists.")
                response = input("Do you want to remove it and start fresh? (y/N): ")
                if response.lower() == 'y':
                    shutil.rmtree(self.app_dir)
                else:
                    print("Setup aborted.")
                    return

            self.create_directory_structure()
            self.create_backend_files()
            self.create_frontend_files()
            self.reset_database()
            self.create_start_script()
            
            print("\n✓ Setup completed successfully!")
            print("\nTo start your application:")
            print(f"1. cd {self.config['app_name']}")
            print("2. python start.py start both --daemon")
            
        except Exception as e:
            print(f"\nError during setup: {str(e)}")
            print("Setup failed. Please check the error message above.")
            sys.exit(1)

    def create_start_script(self):
        """Create the service controller script"""
        start_script = '''#!/usr/bin/env python3

import os
import subprocess
import argparse
from pathlib import Path
from dotenv import load_dotenv

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
            subprocess.run(["npm", "install", "-g", "npm@latest"], 
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
            "name": self.config['app_name'],
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": f"next dev -p {self.config['frontend_port']}",
                "build": "next build",
                "start": f"next start -p {self.config['frontend_port']}",
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
            self.frontend_dir / 'src' / 'components',
            self.frontend_dir / 'src' / 'styles',
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def create_backend_files(self):
        """Create backend files"""
        # Requirements file
        requirements = [
            'fastapi==0.104.1',
            'uvicorn[standard]==0.24.0',
            'gunicorn==21.0.0',
            'sqlalchemy==2.0.23',
            'python-dotenv==1.0.0',
            'pydantic==2.5.1',
        ]

        with open(self.backend_dir / 'requirements.txt', 'w') as f:
            f.write('\n'.join(requirements))

        # Create main FastAPI application file
        main_app = """
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="{app_name}")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:{frontend_port}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {{"status": "healthy"}}
""".format(**self.config)

        with open(self.backend_dir / 'app' / 'main.py', 'w') as f:
            f.write(main_app.strip())

    def create_frontend_files(self):
        """Create frontend configuration and files"""
        package_json = {
            "name": self.config['app_name'],
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": f"next dev -p {self.config['frontend_port']}",
                "build": "next build",
                "start": f"next start -p {self.config['frontend_port']}",
                "lint": "next lint"
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


    def reset_database(self):
        """Drop and recreate PostgreSQL user and database with specified privileges"""
        try:
            # Drop the database if it exists
            subprocess.run([
                "psql", "-h", self.config['db_host'], "-p", self.config['db_port'],
                "-U", os.getenv("USER"),  # Uses the current system user
                "-c", f"DROP DATABASE IF EXISTS {self.config['db_name']};"
            ], check=True)
            print("✓ Dropped existing database")

            # Drop the user if it exists
            subprocess.run([
                "psql", "-h", self.config['db_host'], "-p", self.config['db_port'],
                "-U", os.getenv("USER"),
                "-c", f"DROP ROLE IF EXISTS {self.config['db_user']};"
            ], check=True)
            print("✓ Dropped existing user")

            # Create the user with the specified password
            subprocess.run([
                "psql", "-h", self.config['db_host'], "-p", self.config['db_port'],
                "-U", os.getenv("USER"),
                "-c", f"CREATE USER {self.config['db_user']} WITH PASSWORD '{self.config['db_password']}' CREATEDB;"
            ], check=True)
            print("✓ Created PostgreSQL user")

            # Create the database owned by the new user
            subprocess.run([
                "psql", "-h", self.config['db_host'], "-p", self.config['db_port'],
                "-U", os.getenv("USER"),
                "-c", f"CREATE DATABASE {self.config['db_name']} OWNER {self.config['db_user']};"
            ], check=True)
            print("✓ Created PostgreSQL database")

        except subprocess.CalledProcessError as e:
            print("Error setting up database or user:", e)

    def create_nextjs_files(self):
        """Create basic Next.js files"""
        # Create tsconfig.json
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
                "moduleResolution": "bundler",
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

        # Create basic page component
        page_content = f"""
export default function Home() {{
    return (
        <main className="flex min-h-screen flex-col items-center justify-between p-24">
            <h1 className="text-4xl font-bold">{self.config['app_name']}</h1>
            <p>Your application is ready!</p>
        </main>
    )
}}
        """.strip()
        
        with open(self.frontend_dir / 'src' / 'app' / 'page.tsx', 'w') as f:
            f.write(page_content)

    def setup_virtual_environment(self):
        """Set up Python virtual environment and install requirements"""
        subprocess.run([sys.executable, '-m', 'venv', self.project_dir / '.venv'])
        
        # Install requirements
        venv_pip = str(self.project_dir / '.venv' / 'bin' / 'pip')
        subprocess.run([venv_pip, 'install', '-r', str(self.backend_dir / 'requirements.txt')])

    # def setup_project(self):
    #     """Main setup function"""
    #     print(f"Setting up project: {self.config['app_name']}")
        
    #     # Create project structure
    #     self.create_directory_structure()
    #     print("✓ Created directory structure")

    #     # Create backend files
    #     self.create_backend_files()
    #     print("✓ Created backend files")

    #     # Set up virtual environment
    #     self.setup_virtual_environment()
    #     print("✓ Set up Python virtual environment")

    #     # Create frontend files
    #     self.create_frontend_files()
    #     print("✓ Created frontend files")

    #     # Reset database
    #     self.reset_database()
    #     print("✓ Database setup complete")

    #     print("\nProject setup complete!")
    #     print("\nTo start the project:")
    #     print(f"1. cd {self.config['app_name']}")
    #     print("2. To start the backend:")
    #     print(f"   cd backend")
    #     print(f"   source .venv/bin/activate")
    #     print(f"   uvicorn app.main:app --reload --port {self.config['api_port']}")
    #     print("3. In a new terminal, to start the frontend:")
    #     print(f"   cd frontend")
    #     print(f"   npm install")
    #     print(f"   npm run dev")
    #     print(f"\nFrontend will be available at: http://localhost:{self.config['frontend_port']}")
    #     print(f"API will be available at: http://localhost:{self.config['api_port']}")


if __name__ == "__main__":
    bootstrap = FullStackBootstrap()
    bootstrap.setup_project()
