"""
Database schema definitions for the Cohort Refinement Assistant.
"""

CREATE_TABLES_SQL = [
    # --- Catalog tables (populated from CSVs) ---
    """
    CREATE TABLE IF NOT EXISTS domain_summary (
        domain TEXT,
        table_name TEXT,
        total_rows INTEGER,
        distinct_persons INTEGER,
        first_date TEXT,
        last_date TEXT,
        missing_value_rate REAL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS vocabulary_usage (
        domain TEXT,
        vocabulary_id TEXT,
        distinct_concepts_in_use INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS standard_concepts (
        concept_id REAL,
        concept_name TEXT,
        domain_id TEXT,
        vocabulary_id TEXT,
        concept_class_id TEXT,
        standard_concept TEXT,
        concept_code TEXT,
        total_rows INTEGER,
        distinct_persons INTEGER,
        first_date TEXT,
        last_date TEXT,
        source_table TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS source_concepts (
        source_value TEXT,
        source_concept_id REAL,
        mapped_standard_concept_id REAL,
        mapped_standard_concept_name TEXT,
        mapped_standard_vocabulary_id TEXT,
        mapped_standard_concept_code TEXT,
        mapped_standard_concept_flag TEXT,
        total_rows INTEGER,
        source_table TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ancestor_concepts (
        ancestor_concept_id REAL,
        ancestor_concept_name TEXT,
        ancestor_domain_id TEXT,
        ancestor_vocabulary_id TEXT,
        ancestor_concept_class_id TEXT,
        ancestor_standard_concept TEXT,
        ancestor_concept_code TEXT,
        descendant_concepts_present TEXT,
        total_rows INTEGER,
        distinct_persons INTEGER,
        first_date TEXT,
        last_date TEXT,
        source_table TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS demographics (
        concept_id INTEGER,
        concept_name TEXT,
        person_count INTEGER,
        demographic_type TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS note_nlp_presence (
        source_table TEXT,
        total_rows INTEGER,
        distinct_persons INTEGER
    )
    """,
    # --- Session tables ---
    """
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT NOT NULL,
        refined_definition TEXT,
        reasoning_steps TEXT,
        verification_status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
]
