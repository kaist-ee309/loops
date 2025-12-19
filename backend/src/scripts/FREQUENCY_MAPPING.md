# Frequency Mapping & CEFR Level Assignment Guide

This document explains how to use the frequency mapping and CEFR level assignment system for vocabulary cards.

## Overview

The system automatically assigns:
- **Frequency ranks** to English words (rank 1 = most common, 999999 = unmatched/rare)
- **CEFR levels** (A1-C2) based on Oxford data or frequency ranks

Both features are integrated into database seeding and bulk update scripts.

## Scripts

### 1. `update_cards_via_api.py` - REST API Bulk Update Script ⭐ RECOMMENDED

Updates existing vocabulary cards with frequency ranks AND CEFR levels via Supabase REST API.

**Features:**
- Updates both `frequency_rank` and `cefr_level` in one pass
- Uses Supabase REST API (works through firewalls)
- Automatic CEFR assignment from Oxford 3000/5000 data
- Fallback to frequency-based CEFR estimation
- Dry-run mode for previewing changes
- Detailed statistics and distribution reports
- Generates unmatched words report

**Usage:**

```bash
# Preview changes without updating database (recommended first)
cd src
uv run python scripts/update_cards_via_api.py --dry-run

# Apply updates to all cards (both frequency_rank and cefr_level)
uv run python scripts/update_cards_via_api.py
```

**Example Output:**

```
======================================================================
VOCABULARY CARDS UPDATE SCRIPT (REST API)
======================================================================
Loading all frequency data sources...
Loaded 246590 words from Google Ngram
Loaded 4380 words from COCA
Total combined: 246621 unique words
Loading Oxford CEFR data...
Loaded 4958 words with CEFR levels from Oxford

Fetching vocabulary cards from Supabase...
Total cards fetched: 20047

Processing cards...
  Processed 20047/20047 cards...

[OK] Updated 17284 fields in 20047 cards

======================================================================
FREQUENCY RANK STATISTICS
======================================================================
Total cards: 20047
Matched: 19458 (97.1%)
Unmatched: 589 (2.9%)
Updated: 9637
Already set: 10410

RANK DISTRIBUTION
----------------------------------------------------------------------
0-1000              :  1917 (  9.6%)
1000-5000           :  6664 ( 33.2%)
5000-10000          :  1998 ( 10.0%)
10000-50000         :  7231 ( 36.1%)
50000+              :  1648 (  8.2%)
unmatched           :   589 (  2.9%)

======================================================================
CEFR LEVEL STATISTICS
======================================================================
From Oxford data: 6442 (32.1%)
From frequency: 13605 (67.9%)
Updated: 7647
Already set: 12400

LEVEL DISTRIBUTION
----------------------------------------------------------------------
A1                  :  1934 (  9.6%)
A2                  :  1471 (  7.3%)
B1                  :  1476 (  7.4%)
B2                  :  2805 ( 14.0%)
C1                  :  3278 ( 16.4%)
C2                  :  9079 ( 45.3%)
======================================================================

[REPORT] Unmatched words report saved to: unmatched_words_report.txt
```

### 2. `map_frequency.py` - Frequency Rank Mapping Script (Direct DB)

Assigns frequency ranks to existing vocabulary cards via direct database connection.

**Note:** Use `update_cards_via_api.py` instead if you're behind a firewall or need CEFR levels.

**Features:**
- Supports multiple data sources (COCA, Google Ngram)
- Priority system: COCA > Google
- Case-insensitive matching
- Handles punctuation and multi-word phrases
- Dry-run mode for previewing changes
- Detailed statistics output

**Usage:**

```bash
# Preview changes without updating database (recommended first)
cd src
uv run python scripts/map_frequency.py --source all --dry-run

# Apply frequency ranks to all cards
uv run python scripts/map_frequency.py --source all

# Use specific data source
uv run python scripts/map_frequency.py --source coca
uv run python scripts/map_frequency.py --source google
```

**Example Output:**

```
============================================================
FREQUENCY RANK MAPPING SCRIPT
============================================================

Loading all frequency data sources...
Loaded 246590 words from Google Ngram
Loaded 4380 words from COCA
Total combined: 246621 unique words

Fetching vocabulary cards from database...
Found 100 vocabulary cards

Mapping frequency ranks...

✓ Updated 85 cards in database

============================================================
MAPPING STATISTICS
============================================================
Source: All Sources (COCA + Google)
Total cards: 100
Matched: 85 (85.0%)
Unmatched: 15 (15.0%)
Updated: 85
Already set: 0

RANK DISTRIBUTION
------------------------------------------------------------
0-1000:            20 ( 20.0%)
1000-5000:         35 ( 35.0%)
5000-10000:        15 ( 15.0%)
10000-50000:       10 ( 10.0%)
50000+:             5 (  5.0%)
unmatched:         15 ( 15.0%)
============================================================
```

### 3. `seed_data.py` - Database Seeding with Automatic Mapping

Seeds sample data with automatic frequency rank AND CEFR level assignment for new cards.

**Features:**
- Automatically loads frequency data (COCA + Google Ngram)
- Automatically loads CEFR data (Oxford 3000/5000)
- Assigns both `frequency_rank` and `cefr_level` to all new cards
- No manual rank entry needed

**Usage:**

```bash
cd src
uv run python scripts/seed_data.py
```

**Example Output:**

```
==================================================
DATABASE SEEDING SCRIPT
==================================================

Loading frequency and CEFR data...
  ✅ Loaded 246621 frequency mappings
  ✅ Loaded 4958 CEFR mappings

Seeding users...
  ✅ Added user: testuser (test@example.com)
  ✅ Added user: kaiststudent (demo@kaist.ac.kr)
✅ Users seeded successfully

Seeding vocabulary cards...
  ✅ Added card: contract (freq: 1253, CEFR: A2)
  ✅ Added card: algorithm (freq: 2508, CEFR: B1)
  ✅ Added card: challenge (freq: 794, CEFR: A1)
✅ Vocabulary cards seeded successfully

==================================================
✅ ALL DATA SEEDED SUCCESSFULLY!
==================================================
```

## Data Sources

### Frequency Data

#### COCA (Corpus of Contemporary American English)
- **Words:** 4,380 (top 5k)
- **Coverage:** American English, 1990-2019
- **Best for:** Common everyday vocabulary
- **File:** `data/frequency/COCA_5000.csv`

#### Google Ngram
- **Words:** 246,590
- **Coverage:** Google Books corpus
- **Best for:** Technical terms and less common words
- **File:** `data/frequency/google_ngram_frequency_alpha.txt`

#### Priority System

When using combined sources, the system prioritizes:
1. **COCA** (highest priority) - More accurate for common words
2. **Google Ngram** (fallback) - Broader coverage

### CEFR Level Data

#### Oxford 3000 & 5000
- **Words:** 4,958 total
  - Oxford 3000: Core vocabulary (A1-B2)
  - Oxford 5000: Extended vocabulary (up to C2)
- **Coverage:** British/International English
- **Best for:** Learner-appropriate level assignment
- **Files:**
  - `data/frequency/oxford-3000.csv`
  - `data/frequency/oxford-5000.csv`

#### Frequency-Based Estimation (Fallback)

For words not in Oxford data, CEFR levels are estimated from frequency ranks:

| CEFR Level | Frequency Range | Description |
|------------|-----------------|-------------|
| A1 | 1-500 | Most common words |
| A2 | 501-1,500 | Basic everyday vocabulary |
| B1 | 1,501-3,000 | Intermediate vocabulary |
| B2 | 3,001-5,000 | Upper intermediate |
| C1 | 5,001-10,000 | Advanced vocabulary |
| C2 | 10,001+ | Rare/specialized terms |

## Workflow

### Initial Setup (One-time)

1. **Seed initial data with automatic mapping:**
   ```bash
   cd src
   uv run python scripts/seed_data.py
   ```
   This automatically assigns both `frequency_rank` and `cefr_level` to new cards.

2. **Verify ranks and levels assigned**

### Bulk Update Existing Cards (REST API - Recommended)

When you need to update existing cards (e.g., after data import):

1. **Preview the update:**
   ```bash
   cd src
   uv run python scripts/update_cards_via_api.py --dry-run
   ```

2. **Review the statistics** (matched vs unmatched, CEFR distribution)

3. **Apply the update:**
   ```bash
   uv run python scripts/update_cards_via_api.py
   ```

4. **Review unmatched words report:**
   ```bash
   # Report is automatically saved
   cat src/scripts/unmatched_words_report.txt
   ```

### Alternative: Direct Database Update

If you have direct database access and only need frequency ranks:

1. **Preview the update:**
   ```bash
   cd src
   uv run python scripts/map_frequency.py --source all --dry-run
   ```

2. **Apply the update:**
   ```bash
   uv run python scripts/map_frequency.py --source all
   ```

## Matching Logic

### Edge Cases Handled

1. **Case Insensitive:** "Hello" = "hello" = "HELLO"
2. **Punctuation Removal:** "hello!" → "hello"
3. **Whitespace Trimming:** "  contract  " → "contract"
4. **Multi-word Phrases:** "make up" → falls back to "make"
5. **Empty Strings:** "" → rank 999999

## Understanding Ranks

| Rank Range | Category | Example Words |
|------------|----------|---------------|
| 1-1000 | Very Common | the, hello, make |
| 1001-5000 | Common | contract, challenge |
| 5001-10000 | Less Common | |
| 10001-50000 | Uncommon | algorithm |
| 50000+ | Rare | antidisestablishmentarianism |
| 999999 | Unmatched | Not in corpus |

## Best Practices

1. **Always dry-run first:**
   ```bash
   uv run python scripts/update_cards_via_api.py --dry-run
   ```

2. **Use REST API script for bulk updates:**
   - Updates both frequency_rank AND cefr_level in one pass
   - Works through firewalls (uses HTTPS)
   - Generates comprehensive reports

3. **Monitor unmatched words:**
   - Review `unmatched_words_report.txt` after updates
   - Words with rank 999999 may be typos, proper nouns, or rare terms
   - Verify data quality

4. **CEFR Level Assignment Strategy:**
   - Oxford data (32% of words) = Most accurate
   - Frequency-based estimation (68% of words) = Reasonable fallback
   - Review C2 words - may need manual adjustment

5. **Future Card Creation:**
   - Use `seed_data.py` as template
   - Always include FrequencyMapper and CEFRMapper
   - Automatic assignment prevents inconsistencies

## Completed Updates

### Issue #24: Update Existing Cards with Frequency Ranks ✅
- **Date Completed:** 2025-12-10
- **Cards Updated:** 20,047 vocabulary cards
- **Script Used:** `update_cards_via_api.py`
- **Results:**
  - Matched: 19,458 (97.1%)
  - Unmatched: 589 (2.9%)
  - Unmatched words saved to: `src/scripts/unmatched_words_report.txt`

### Issue #26: Add CEFR Levels to Vocabulary Cards ✅
- **Date Completed:** 2025-12-10
- **Cards Updated:** 20,047 vocabulary cards
- **Script Used:** `update_cards_via_api.py`
- **Results:**
  - From Oxford data: 6,442 (32.1%)
  - From frequency estimation: 13,605 (67.9%)
  - Distribution: A1 (9.6%), A2 (7.3%), B1 (7.4%), B2 (14.0%), C1 (16.4%), C2 (45.3%)

## References

- **Issue #22:** English word frequency data collection
- **Issue #23:** Frequency rank mapping script (map_frequency.py)
- **Issue #24:** Update existing cards with frequency ranks ✅ COMPLETED
- **Issue #26:** Add CEFR levels to vocabulary cards ✅ COMPLETED
- **Data Sources:** See `data/README.md` for detailed source information
- **Script Documentation:** See individual script docstrings for technical details
