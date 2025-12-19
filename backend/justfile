# Loops API - Just Commands
# Install just: brew install just (or see https://just.systems)
# Run: just <command>

# Show all available commands
default:
    @just --list

# Complete project setup
setup:
    @echo "🔧 Setting up Loops API..."
    uv sync
    @if [ ! -f .env ]; then cp .env.example .env && echo "✓ Created .env"; fi
    @echo "⚠️  Update DATABASE_URL in .env, then run: just migrate"

# Start development server
dev:
    @echo "🚀 Starting development server..."
    cd src && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run database migrations
migrate:
    @echo "📦 Running migrations..."
    uv run alembic upgrade head

# Rollback last migration
rollback:
    @echo "↩️  Rolling back migration..."
    uv run alembic downgrade -1

# Create new migration with autogenerate
[confirm("This will create a new migration. Continue?")]
revision MESSAGE:
    @echo "📝 Creating migration: {{MESSAGE}}"
    uv run alembic revision --autogenerate -m "{{MESSAGE}}"

# Show migration history
history:
    @echo "📜 Migration history:"
    uv run alembic history

# Show current revision
current:
    @echo "📍 Current revision:"
    uv run alembic current

# List all migration files
migrations:
    @echo "📂 Migration files:"
    @ls -lth alembic/versions/ | head -20

# View latest migration file
migration-latest:
    @echo "📄 Latest migration file:"
    @ls -t alembic/versions/*.py | head -1 | xargs cat

# Check for pending migrations
check-migrations:
    @echo "🔍 Checking for pending migrations..."
    @uv run alembic current
    @echo ""
    @echo "Expected head:"
    @uv run alembic heads

# Reset database (requires confirmation)
[confirm("⚠️  This will reset the database. Continue?")]
reset:
    @echo "🔄 Resetting database..."
    uv run alembic downgrade base
    uv run alembic upgrade head

# Seed database with sample data
db-seed:
    @echo "🌱 Seeding database..."
    uv run python src/scripts/seed_data.py

# Reset and seed database (requires confirmation)
[confirm("⚠️  This will reset and seed the database. Continue?")]
db-refresh:
    @echo "🔄 Refreshing database..."
    uv run alembic downgrade base
    uv run alembic upgrade head
    uv run python src/scripts/seed_data.py
    @echo "✅ Database refreshed!"

# Test database connection
db-test:
    @echo "🔌 Testing database connection..."
    @uv run python -c "import asyncio; from app.database import engine; from sqlalchemy import text; exec('async def test():\\n    async with engine.begin() as conn:\\n        await conn.execute(text(\"SELECT 1\"))\\n        print(\"✅ Database connection successful!\")\\nasyncio.run(test())')"

# Check API health
health:
    @echo "🏥 Checking API health..."
    @curl -f -s http://localhost:8080/health | python -m json.tool || echo "❌ API not running at http://localhost:8080"

# Start Docker containers with build
docker-up:
    @echo "🐳 Starting Docker containers..."
    docker-compose up --build -d
    @echo "✅ Docker containers started"

# Stop Docker containers
docker-down:
    @echo "🛑 Stopping Docker containers..."
    docker-compose down

# View Docker logs (follow mode)
docker-logs:
    docker-compose logs -f

# Docker Alembic Commands
# ========================

# Run migrations inside Docker container
docker-migrate:
    @echo "📦 Running migrations in Docker..."
    docker-compose exec api uv run alembic upgrade head

# Create new migration inside Docker container
docker-revision MESSAGE:
    @echo "📝 Creating migration in Docker: {{MESSAGE}}"
    docker-compose exec api uv run alembic revision --autogenerate -m "{{MESSAGE}}"

# Rollback last migration inside Docker container
docker-rollback:
    @echo "↩️  Rolling back migration in Docker..."
    docker-compose exec api uv run alembic downgrade -1

# Reset database inside Docker container
[confirm("⚠️  This will reset the database in Docker. Continue?")]
docker-reset:
    @echo "🔄 Resetting database in Docker..."
    docker-compose exec api uv run alembic downgrade base
    docker-compose exec api uv run alembic upgrade head

# Seed database inside Docker container
docker-seed:
    @echo "🌱 Seeding database in Docker..."
    docker-compose exec api uv run python src/scripts/seed_data.py

# Reset and seed database inside Docker container
[confirm("⚠️  This will reset and seed the database in Docker. Continue?")]
docker-refresh:
    @echo "🔄 Refreshing database in Docker..."
    docker-compose exec api uv run alembic downgrade base
    docker-compose exec api uv run alembic upgrade head
    docker-compose exec api uv run python src/scripts/seed_data.py
    @echo "✅ Database refreshed in Docker!"

# Clean Python cache files
clean:
    @echo "🧹 Cleaning Python cache files..."
    @find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @find . -type f -name "*.pyc" -delete 2>/dev/null || true
    @find . -type f -name "*.pyo" -delete 2>/dev/null || true
    @find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    @find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    @echo "✅ Cleaned"

# Install dependencies
install:
    uv sync

# Add a new dependency
add PACKAGE:
    uv add {{PACKAGE}}

# Show environment info
info:
    @echo "📊 Environment Info:"
    @echo "Python: $(python --version)"
    @echo "UV: $(uv --version)"
    @echo ""
    @echo "🗄️  Database Migration Status:"
    @uv run alembic current 2>/dev/null || echo "Not initialized"
