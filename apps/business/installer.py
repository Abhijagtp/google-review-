import os
from pathlib import Path
import psycopg
from django.core.management import call_command
from django.conf import settings
import dj_database_url


def test_database_connection(database_url: str) -> tuple[bool, str]:
    """
    Tests connectivity to a PostgreSQL database connection string (e.g. Neon PostgreSQL).
    Returns (success: bool, error_message: str).
    """
    if not database_url or not database_url.strip():
        return False, "Database connection string cannot be empty."

    url_str = database_url.strip()
    if not (url_str.startswith("postgresql://") or url_str.startswith("postgres://")):
        return False, "Invalid connection format. Must start with 'postgresql://' or 'postgres://'."

    try:
        # Parse database parameters using dj_database_url
        db_config = dj_database_url.parse(url_str)
        if not db_config:
            return False, "Could not parse PostgreSQL connection string."

        conn_params = {
            'dbname': db_config.get('NAME'),
            'user': db_config.get('USER'),
            'password': db_config.get('PASSWORD'),
            'host': db_config.get('HOST'),
            'port': db_config.get('PORT') or 5432,
            'connect_timeout': 5,
        }

        # Handle sslmode options from connection string
        options = db_config.get('OPTIONS', {})
        if 'sslmode' in options:
            conn_params['sslmode'] = options['sslmode']
        else:
            conn_params['sslmode'] = 'require'

        # Attempt direct connection using psycopg v3
        with psycopg.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()

        return True, ""
    except Exception as e:
        return False, f"Connection failed: {str(e)}"


def update_env_database_url(database_url: str) -> bool:
    """
    Updates or appends DATABASE_URL in the project root .env file.
    """
    base_dir = settings.BASE_DIR
    env_file = base_dir / '.env'

    new_line = f"DATABASE_URL={database_url.strip()}\n"

    try:
        if not env_file.exists():
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(new_line)
            return True

        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        updated = False
        new_lines = []
        for line in lines:
            if line.strip().startswith("DATABASE_URL="):
                new_lines.append(new_line)
                updated = True
            else:
                new_lines.append(line)

        if not updated:
            new_lines.append("\n" + new_line)

        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        # Update current process environment as well
        os.environ["DATABASE_URL"] = database_url.strip()
        return True
    except Exception:
        return False


def run_database_migrations() -> tuple[bool, str]:
    """
    Executes Django migrations on the connected database.
    Returns (success: bool, output_message: str).
    """
    try:
        call_command('migrate', interactive=False)
        return True, "Migrations executed successfully."
    except Exception as e:
        return False, f"Migration failed: {str(e)}"


def get_env_database_url() -> str:
    """
    Reads DATABASE_URL directly from the .env file on disk.
    """
    env_file = settings.BASE_DIR / '.env'
    if not env_file.exists():
        return ""
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith("DATABASE_URL="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return ""


def is_database_configured() -> bool:
    """
    Checks if a valid DATABASE_URL exists in the .env file and can connect to PostgreSQL.
    """
    db_url = get_env_database_url()
    if not db_url:
        os.environ["DATABASE_URL"] = ""
        return False
    
    # Quick check if it's a valid PostgreSQL connection
    success, _ = test_database_connection(db_url)
    return success

