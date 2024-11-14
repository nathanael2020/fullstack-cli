# src/fullstack/cli.py
#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from .bootstrap import FullStackBootstrap

import subprocess
import sys
import os
from pathlib import Path

def check_venv():
    """Check if running in a virtual environment and handle accordingly"""
    if not os.environ.get('VIRTUAL_ENV'):
        venv_dir = Path('.venv')
        
        if venv_dir.exists():
            print("\nFound existing .venv directory but it's not activated.")
            print("Please activate it with:")
            print("    source .venv/bin/activate")
            sys.exit(1)
        
        print("\nNo virtual environment detected. You have two options:")
        print("1. Create a new .venv in the current directory")
        print("2. Exit and activate an existing virtual environment")
        
        while True:
            choice = input("\nWould you like to create a new .venv here? (y/n): ").lower()
            if choice in ['y', 'n']:
                break
            print("Please answer 'y' or 'n'")
        
        if choice == 'y':
            print("\nCreating virtual environment...")
            try:
                # Create the virtual environment
                subprocess.run([sys.executable, '-m', 'venv', '.venv'], check=True)
                
                venv_pip = str(venv_dir / 'bin' / 'pip')
                print("Installing required packages...")
                
                # Upgrade pip and install packages
                subprocess.run([venv_pip, 'install', '-U', 'pip'], check=True)
                subprocess.run([venv_pip, 'install', 
                             'fastapi==0.104.1',
                             'uvicorn[standard]==0.24.0',
                             'gunicorn==21.0.0',
                             'sqlalchemy==2.0.23',
                             'python-dotenv==1.0.0',
                             'psycopg2-binary==2.9.10',
                             'pydantic==2.5.1'], check=True)
                
                print("\n✓ Virtual environment created and packages installed")
                
                # # Relaunch the script within the virtual environment
                # python_in_venv = str(venv_dir / 'bin' / 'python')
                # print("Re-launching script within the virtual environment...")
                # subprocess.run([python_in_venv] + sys.argv)

                # # Exit to prevent further execution in the outer environment
                # sys.exit(0)


                # Manually activate the virtual environment in this script's context
                venv_lib_path = venv_dir / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
                sys.path.insert(0, str(venv_lib_path))
                
                # Set VIRTUAL_ENV environment variable and adjust PATH
                os.environ['VIRTUAL_ENV'] = str(venv_dir)
                os.environ['PATH'] = f"{venv_dir / 'bin'}:{os.environ['PATH']}"
                
                print("Virtual environment activated in the current process.")
                
            except subprocess.CalledProcessError as e:
                print(f"Error creating virtual environment: {e}")
                sys.exit(1)
        else:
            print("\nPlease activate your preferred virtual environment and run fullstack again")
            sys.exit(0)


# src/fullstack/cli.py (the relevant part)
def load_env_or_defaults():
    """Load environment variables or set defaults"""
    # Be explicit about using current working directory
    env_path = Path.cwd() / '.env'
    if not env_path.exists():
        print(f"\nNo .env file found in current directory: {env_path}")
        print("You have two options:")
        print("1. Create a new .env with your settings")
        print("2. Exit and create/move your .env file manually")
        
        while True:
            choice = input("\nWould you like to create a new .env here? (y/n): ").lower()
            if choice in ['y', 'n']:
                break
            print("Please answer 'y' or 'n'")
        
        if choice == 'y':
            create_env_file()
        else:
            print("\nPlease create or move your .env file and run fullstack again")
            sys.exit(0)
    
    # Load from explicit path
    load_dotenv(env_path)
    
    # Debug output
    print(f"Loading .env from: {env_path}")
    print("Environment variables loaded:")
    print(f"APP_NAME: {os.getenv('APP_NAME')}")
    print(f"API_PORT: {os.getenv('API_PORT')}")
    print(f"FRONTEND_PORT: {os.getenv('FRONTEND_PORT')}")

    
    # Set defaults if not in .env
    env_vars = {
        'APP_NAME': os.getenv('APP_NAME', Path.cwd().name),
        'API_PORT': os.getenv('API_PORT', '8000'),
        'FRONTEND_PORT': os.getenv('FRONTEND_PORT', '3000'),
        'DB_NAME': os.getenv('DB_NAME'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD', 'change_me_in_production'),
        'DB_HOST': os.getenv('DB_HOST', 'localhost'),
        'DB_PORT': os.getenv('DB_PORT', '5432'),
        'DATABASE_URL': 'postgresql://' + os.getenv('DB_USER') + ':' + os.getenv('DB_PASSWORD') + '@' + os.getenv('DB_HOST') + ':' + os.getenv('DB_PORT') + '/' + os.getenv('DB_NAME')
    }
    
    # If DB_NAME or DB_USER not set, derive from APP_NAME
    if not env_vars['DB_NAME']:
        env_vars['DB_NAME'] = f"{env_vars['APP_NAME'].replace('-', '_')}_db"
    if not env_vars['DB_USER']:
        env_vars['DB_USER'] = f"{env_vars['APP_NAME'].replace('-', '_')}_user"
    
    return env_vars

def create_env_file(env_vars=None):
    """Create a .env file with provided vars or prompt for values"""
    if env_vars is None:
        # Get current directory name as default app name
        default_name = Path.cwd().name
        
        env_vars = {
            'APP_NAME': input(f"Project name (default: {default_name}): ") or default_name,
            'API_PORT': input("API port (default: 8000): ") or "8000",
            'FRONTEND_PORT': input("Frontend port (default: 3000): ") or "3000",
            'DB_NAME': "",  # Will be derived from APP_NAME if empty
            'DB_USER': "",  # Will be derived from APP_NAME if empty
            'DB_PASSWORD': input("Database password (default: change_me_in_production): ") or "change_me_in_production",
            'DB_HOST': input("Database host (default: localhost): ") or "localhost",
            'DB_PORT': input("Database port (default: 5432): ") or "5432",
            'DATABASE_URL': ""  # Will be derived from other vars if empty
        }
        
        # Derive DB_NAME and DB_USER from APP_NAME if not provided
        if not env_vars['DB_NAME']:
            env_vars['DB_NAME'] = f"{env_vars['APP_NAME'].replace('-', '_')}_db"
        if not env_vars['DB_USER']:
            env_vars['DB_USER'] = f"{env_vars['APP_NAME'].replace('-', '_')}_user"
        if not env_vars['DATABASE_URL']:
            env_vars['DATABASE_URL'] = 'postgresql://' + env_vars['DB_USER'] + ':' + env_vars['DB_PASSWORD'] + '@' + env_vars['DB_HOST'] + ':' + env_vars['DB_PORT'] + '/' + env_vars['DB_NAME']

    # Create .env file
    env_content = "\n".join(f"{k}={v}" for k, v in env_vars.items())
    
    if Path('.env').exists():
        while True:
            choice = input("\n.env file already exists. Overwrite? (y/n): ").lower()
            if choice in ['y', 'n']:
                break
            print("Please answer 'y' or 'n'")
        
        if choice == 'n':
            return False

    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✓ Created .env file")
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Bootstrap a full-stack web application'
    )
    
    # All arguments are optional now
    parser.add_argument(
        '--name',
        help='Override the project name from .env or directory name'
    )
    parser.add_argument(
        '--api-port',
        help='Override API port from .env'
    )
    parser.add_argument(
        '--frontend-port',
        help='Override frontend port from .env'
    )
    parser.add_argument(
        '--db-name',
        help='Override database name from .env'
    )
    parser.add_argument(
        '--db-user',
        help='Override database user from .env'
    )
    parser.add_argument(
        '--db-password',
        help='Override database password from .env'
    )
    parser.add_argument(
        '--db-host',
        help='Override database host from .env'
    )
    parser.add_argument(
        '--db-port',
        help='Override database port from .env'
    )
    parser.add_argument(
        '--skip-venv-check',
        action='store_true',
        help='Skip virtual environment check'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing files without asking'
    )

    args = parser.parse_args()

    # Check virtual environment unless explicitly skipped
    if not args.skip_venv_check:
        check_venv()
    
    # Load from .env or set defaults
    env_vars = load_env_or_defaults()
    
    # Override with any command line arguments
    if args.name:
        env_vars['APP_NAME'] = args.name
    if args.api_port:
        env_vars['API_PORT'] = args.api_port
    if args.frontend_port:
        env_vars['FRONTEND_PORT'] = args.frontend_port
    if args.db_name:
        env_vars['DB_NAME'] = args.db_name
    if args.db_user:
        env_vars['DB_USER'] = args.db_user
    if args.db_password:
        env_vars['DB_PASSWORD'] = args.db_password
    if args.db_host:
        env_vars['DB_HOST'] = args.db_host
    if args.db_port:
        env_vars['DB_PORT'] = args.db_port

    # Write environment variables back to .env file
    if args.force:
        create_env_file(env_vars)
    
    # Initialize and run the bootstrap process
    try:
        bootstrap = FullStackBootstrap()
        bootstrap.setup_project()
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()