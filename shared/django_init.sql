-- Django database initialization
SELECT 'CREATE DATABASE django_legislators_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'django_legislators_db')\gexec

