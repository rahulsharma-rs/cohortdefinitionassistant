"""
Catalog service — ingests EHR catalog CSVs into SQLite tables.
Provides query functions for agents to lookup conditions, drugs, procedures, etc.
"""
import os
import pandas as pd
from config import Config
from database.db import get_connection, init_db


# Mapping from CSV filename patterns to table + metadata
CSV_MAPPINGS = {
    "01_domain_summary": {
        "table": "domain_summary",
        "type": "direct",
    },
    "02_vocabulary_usage": {
        "table": "vocabulary_usage",
        "type": "direct",
    },
    "03_standard_concept_coverage_conditions": {
        "table": "standard_concepts",
        "type": "standard",
        "source_table": "conditions",
    },
    "05_standard_concept_coverage_drugs": {
        "table": "standard_concepts",
        "type": "standard",
        "source_table": "drugs",
    },
    "06_standard_concept_coverage_procedures": {
        "table": "standard_concepts",
        "type": "standard",
        "source_table": "procedures",
    },
    "07_standard_concept_coverage_devices": {
        "table": "standard_concepts",
        "type": "standard",
        "source_table": "devices",
    },
    "08_standard_concept_coverage_visits": {
        "table": "standard_concepts",
        "type": "standard",
        "source_table": "visits",
    },
    "09_source_code_coverage_conditions": {
        "table": "source_concepts",
        "type": "source",
        "source_table": "conditions",
    },
    "10_source_code_coverage_measurements": {
        "table": "source_concepts",
        "type": "source",
        "source_table": "measurements",
    },
    "11_source_code_coverage_drugs": {
        "table": "source_concepts",
        "type": "source",
        "source_table": "drugs",
    },
    "12_source_code_coverage_procedures": {
        "table": "source_concepts",
        "type": "source",
        "source_table": "procedures",
    },
    "13_source_code_coverage_devices": {
        "table": "source_concepts",
        "type": "source",
        "source_table": "devices",
    },
    "14_source_code_coverage_visits": {
        "table": "source_concepts",
        "type": "source",
        "source_table": "visits",
    },
    "19_ancestor_concept_coverage_devices": {
        "table": "ancestor_concepts",
        "type": "ancestor",
        "source_table": "devices",
    },
    "20_ancestor_concept_coverage_visits": {
        "table": "ancestor_concepts",
        "type": "ancestor",
        "source_table": "visits",
    },
    "22_demographic_coverage_gender": {
        "table": "demographics",
        "type": "demographic",
        "demographic_type": "gender",
    },
    "23_demographic_coverage_race": {
        "table": "demographics",
        "type": "demographic",
        "demographic_type": "race",
    },
    "24_demographic_coverage_ethnicity": {
        "table": "demographics",
        "type": "demographic",
        "demographic_type": "ethnicity",
    },
    "26_note_and_nlp_presence": {
        "table": "note_nlp_presence",
        "type": "direct",
    },
}


class CatalogService:
    """Ingests and queries the EHR population catalog."""

    def __init__(self):
        self.catalog_dir = os.path.abspath(Config.CATALOG_DIR)

    def ingest_all(self):
        """Read all catalog CSVs and load into SQLite."""
        init_db()
        conn = get_connection()
        try:
            for filename, meta in CSV_MAPPINGS.items():
                csv_path = os.path.join(self.catalog_dir, f"{filename}.csv")
                if not os.path.exists(csv_path):
                    print(f"  [SKIP] {filename}.csv not found")
                    continue

                df = pd.read_csv(csv_path, encoding="utf-8-sig")
                df.columns = [c.strip().lower() for c in df.columns]

                # Add source_table or demographic_type column if needed
                if meta["type"] in ("standard", "source", "ancestor"):
                    df["source_table"] = meta["source_table"]
                elif meta["type"] == "demographic":
                    df["demographic_type"] = meta["demographic_type"]

                table = meta["table"]
                df.to_sql(table, conn, if_exists="append", index=False)
                print(f"  [OK] {filename}.csv → {table} ({len(df)} rows)")

            conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Query helpers used by agents
    # ------------------------------------------------------------------

    def get_domain_summary(self):
        """Return high-level domain statistics."""
        from database.db import query_db
        return query_db("SELECT * FROM domain_summary")

    def get_catalog_description(self):
        """Read the EHR Population catelogue description text."""
        desc_path = os.path.abspath(Config.CATALOG_DESCRIPTION_FILE)
        if os.path.exists(desc_path):
            with open(desc_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def lookup_conditions(self, term: str, limit: int = 20):
        """Search condition concepts by name (case-insensitive LIKE)."""
        from database.db import query_db
        return query_db(
            """SELECT concept_id, concept_name, vocabulary_id, concept_code,
                      total_rows, distinct_persons
               FROM standard_concepts
               WHERE source_table = 'conditions'
                 AND LOWER(concept_name) LIKE LOWER(?)
               ORDER BY distinct_persons DESC
               LIMIT ?""",
            (f"%{term}%", limit),
        )

    def lookup_drugs(self, term: str, limit: int = 20):
        """Search drug concepts by name."""
        from database.db import query_db
        return query_db(
            """SELECT concept_id, concept_name, vocabulary_id, concept_code,
                      total_rows, distinct_persons
               FROM standard_concepts
               WHERE source_table = 'drugs'
                 AND LOWER(concept_name) LIKE LOWER(?)
               ORDER BY distinct_persons DESC
               LIMIT ?""",
            (f"%{term}%", limit),
        )

    def lookup_procedures(self, term: str, limit: int = 20):
        """Search procedure concepts by name."""
        from database.db import query_db
        return query_db(
            """SELECT concept_id, concept_name, vocabulary_id, concept_code,
                      total_rows, distinct_persons
               FROM standard_concepts
               WHERE source_table = 'procedures'
                 AND LOWER(concept_name) LIKE LOWER(?)
               ORDER BY distinct_persons DESC
               LIMIT ?""",
            (f"%{term}%", limit),
        )

    def lookup_measurements(self, term: str, limit: int = 20):
        """Search measurement source concepts by name or code."""
        from database.db import query_db
        return query_db(
            """SELECT source_value, mapped_standard_concept_name,
                      mapped_standard_vocabulary_id, mapped_standard_concept_code,
                      total_rows
               FROM source_concepts
               WHERE source_table = 'measurements'
                 AND (LOWER(mapped_standard_concept_name) LIKE LOWER(?)
                      OR LOWER(source_value) LIKE LOWER(?))
               ORDER BY total_rows DESC
               LIMIT ?""",
            (f"%{term}%", f"%{term}%", limit),
        )

    def lookup_visits(self, limit: int = 50):
        """Return all visit types."""
        from database.db import query_db
        return query_db(
            """SELECT concept_id, concept_name, total_rows, distinct_persons
               FROM standard_concepts
               WHERE source_table = 'visits'
               ORDER BY distinct_persons DESC
               LIMIT ?""",
            (limit,),
        )

    def get_demographics(self):
        """Return all demographic data."""
        from database.db import query_db
        return query_db("SELECT * FROM demographics ORDER BY demographic_type, person_count DESC")

    def get_vocabularies(self):
        """Return vocabulary usage stats."""
        from database.db import query_db
        return query_db("SELECT * FROM vocabulary_usage ORDER BY domain, distinct_concepts_in_use DESC")

    def check_concept_exists(self, concept_name: str, domain: str = None):
        """Check if a concept exists in the catalog by name."""
        from database.db import query_db
        if domain:
            return query_db(
                """SELECT concept_id, concept_name, vocabulary_id, concept_code,
                          total_rows, distinct_persons, source_table
                   FROM standard_concepts
                   WHERE LOWER(concept_name) LIKE LOWER(?)
                     AND LOWER(source_table) = LOWER(?)
                   ORDER BY distinct_persons DESC
                   LIMIT 5""",
                (f"%{concept_name}%", domain),
            )
        return query_db(
            """SELECT concept_id, concept_name, vocabulary_id, concept_code,
                      total_rows, distinct_persons, source_table
               FROM standard_concepts
               WHERE LOWER(concept_name) LIKE LOWER(?)
               ORDER BY distinct_persons DESC
               LIMIT 10""",
            (f"%{concept_name}%",),
        )
