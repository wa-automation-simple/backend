# Alembic Migrations

This directory contains database migration scripts for the Auth Service using Alembic.

## Setup

Alembic is already configured for this service. The configuration files are:
- `alembic.ini` - Main Alembic configuration file
- `alembic/env.py` - Environment configuration
- `alembic/script.py.mako` - Template for new migration scripts

## Usage

### Generate a new migration

After making changes to your SQLAlchemy models, generate a new migration:

```bash
cd microservices/auth
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

To apply all pending migrations to the database:

```bash
alembic upgrade head
```

### Rollback migrations

To rollback the last migration:

```bash
alembic downgrade -1
```

To rollback to a specific revision:

```bash
alembic downgrade <revision_id>
```

### View current status

To see the current migration status:

```bash
alembic current
```

To see all migrations:

```bash
alembic history
```

## Migration Workflow

1. Modify your SQLAlchemy models in the `modules/` directory
2. Generate a new migration with `alembic revision --autogenerate -m "message"`
3. Review the generated migration script in `alembic/versions/`
4. Test the migration with `alembic upgrade head`
5. Commit the migration script to version control

## Notes

- Always review auto-generated migrations before applying them
- Keep migration scripts in version control
- Never modify existing migration scripts that have been applied to production
