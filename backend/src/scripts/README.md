# Database Scripts

Utility scripts for database operations.

## Seed Data

Populates the database with sample data for development and testing.

### Usage

```bash
# Make sure database is running and migrations are applied first
uv run python src/scripts/seed_data.py
```

### What gets seeded:

**Users:**
- `testuser` (test@example.com) - IT Developer, intermediate level
- `kaiststudent` (demo@kaist.ac.kr) - Student, advanced level
- Password for both: `password123`

**Vocabulary Cards:**
- `contract` (계약) - Business/Legal, intermediate
- `algorithm` (알고리즘) - IT/CS, advanced
- `challenge` (도전, 과제) - General/Business, beginner

### Notes:

- Script is idempotent - won't create duplicates if run multiple times
- Checks for existing data before inserting
- Uses proper password hashing via bcrypt
- JSONB fields are properly formatted (example_sentences, tags)
