from django.core.management.base import BaseCommand
from processor.models import StaffDetails
from django.db import transaction, connection
from django.conf import settings
from django.core.management import call_command
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Command(BaseCommand):
    help = 'Seed the database with staff details'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing staff data before seeding',
        )

    def create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        try:
            # Get database settings
            db_settings = settings.DATABASES['default']
            db_name = db_settings['NAME']
            db_user = db_settings['USER']
            db_password = db_settings['PASSWORD']
            db_host = db_settings['HOST']
            db_port = db_settings['PORT']
            
            # Connect to PostgreSQL server (not specific database)
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database='postgres'  # Connect to default postgres database
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cursor.fetchone()
            
            if not exists:
                self.stdout.write(f'Creating database "{db_name}"...')
                cursor.execute(f'CREATE DATABASE "{db_name}"')
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created database "{db_name}"')
                )
            else:
                self.stdout.write(f'Database "{db_name}" already exists')
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating database: {str(e)}')
            )
            raise

    def create_departments_table(self):
        """Create the departments table"""
        try:
            # Connect to the database
            conn = psycopg2.connect(
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                database=settings.DATABASES['default']['NAME']
            )
            cursor = conn.cursor()
            
            # Create departments table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS departments (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                code VARCHAR(10) UNIQUE NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            cursor.execute(create_table_sql)
            conn.commit()
            
            self.stdout.write(
                self.style.SUCCESS('Successfully created departments table')
            )
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating departments table: {str(e)}')
            )
            raise

    def create_staff_details_table(self):
        """Create the staff_details table with exact specifications"""
        try:
            # Connect to the database
            conn = psycopg2.connect(
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                database=settings.DATABASES['default']['NAME']
            )
            cursor = conn.cursor()
            
            # Create staff_details table with exact specifications
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS staff_details (
                id SERIAL PRIMARY KEY,
                staffid VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                section VARCHAR(255),
                designation VARCHAR(255),
                department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
                weekly_off VARCHAR(10) CHECK (weekly_off IN ('sun', 'mon', 'tue', 'wed', 'thurs', 'fri', 'sat', '')),
                level INTEGER,
                type_of_employment VARCHAR(20) CHECK (type_of_employment IN ('permanent', 'contract', 'monthly wages')),
                priority INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            cursor.execute(create_table_sql)
            conn.commit()
            
            self.stdout.write(
                self.style.SUCCESS('Successfully created staff_details table')
            )
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating staff_details table: {str(e)}')
            )
            raise

    def handle(self, *args, **options):
        # Create database if it doesn't exist
        self.create_database_if_not_exists()
        
        # Create the departments table first
        self.create_departments_table()
        
        # Create the staff_details table
        self.create_staff_details_table()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Database, departments, and staff_details tables are ready!'
            )
        ) 