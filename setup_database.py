"""
Database Setup Script
Creates PostgreSQL database and initializes tables
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()


def create_database():
    """Create PostgreSQL databases for development, testing, and production"""
    
    # Database configuration
    databases = {
        'development': 'picme_dev',
        'testing': 'picme_test',
        'production': 'picme_prod'
    }
    
    db_user = 'picme_user'
    db_password = 'picme_pass'
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host='localhost',
            user='postgres',
            password=input('Enter PostgreSQL admin password: ')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create user if not exists
        print(f"\nCreating database user: {db_user}")
        cursor.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '{db_user}') THEN
                    CREATE USER {db_user} WITH PASSWORD '{db_password}';
                END IF;
            END
            $$;
        """)
        print(f"✓ User '{db_user}' ready")
        
        # Create databases
        for env, db_name in databases.items():
            print(f"\nSetting up {env} database: {db_name}")
            
            # Drop database if exists (optional - comment out if you want to preserve data)
            # cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
            
            # Create database
            cursor.execute(f"""
                SELECT 1 FROM pg_database WHERE datname = '{db_name}';
            """)
            if not cursor.fetchone():
                cursor.execute(f"CREATE DATABASE {db_name} OWNER {db_user};")
                print(f"✓ Database '{db_name}' created")
            else:
                print(f"✓ Database '{db_name}' already exists")
            
            # Grant privileges
            cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*50)
        print("Database setup completed successfully!")
        print("="*50)
        print("\nConnection strings:")
        for env, db_name in databases.items():
            print(f"{env}: postgresql://{db_user}:{db_password}@localhost/{db_name}")
        
        print("\nNext steps:")
        print("1. Update your .env file with the database URLs")
        print("2. Run: flask db init (if not already done)")
        print("3. Run: flask db migrate -m 'Initial migration'")
        print("4. Run: flask db upgrade")
        print("5. Run: python run.py")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is installed and running")
        print("2. Verify you have admin credentials")
        print("3. Check if port 5432 is available")


if __name__ == '__main__':
    print("="*50)
    print("PICME Database Setup")
    print("="*50)
    create_database()
