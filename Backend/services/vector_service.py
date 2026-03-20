"""
Vector service — using LlamaIndex for RAG with local vector storage.
"""
import os
import pandas as pd
from llama_index.core import Document, VectorStoreIndex, StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from config import Config


class VectorService:
    """LlamaIndex based semantic search over EHR catalog concepts."""

    def __init__(self):
        self.storage_dir = os.path.join(os.path.dirname(os.path.abspath(Config.SQLITE_DB_PATH)), "storage")
        self.index = None
        self.is_built = False

        # Configure settings for LlamaIndex — using local embedding model
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        # LLM setting is handled by langchain in the agents, 
        # but LlamaIndex might need a placeholder or specific config if used for querying.
        # We'll stick to basic retriever usage which primarily uses embeddings.

    def build_index(self):
        """Build or load LlamaIndex from catalog CSVs."""
        if os.path.exists(self.storage_dir) and os.listdir(self.storage_dir):
            print(f"  [OK] Loading existing vector index from {self.storage_dir}")
            try:
                storage_context = StorageContext.from_defaults(persist_dir=self.storage_dir)
                self.index = load_index_from_storage(storage_context)
                self.is_built = True
                return
            except Exception as e:
                print(f"  [WARN] Failed to load index: {e}. Rebuilding...")

        catalog_dir = os.path.abspath(Config.CATALOG_DIR)
        documents = []

        # Standard concept CSVs
        standard_files = {
            "03_standard_concept_coverage_conditions.csv": "conditions",
            "05_standard_concept_coverage_drugs.csv": "drugs",
            "06_standard_concept_coverage_procedures.csv": "procedures",
            "07_standard_concept_coverage_devices.csv": "devices",
            "08_standard_concept_coverage_visits.csv": "visits",
        }

        for fname, domain in standard_files.items():
            fpath = os.path.join(catalog_dir, fname)
            if not os.path.exists(fpath):
                continue
            
            df = pd.read_csv(fpath, encoding="utf-8-sig")
            df.columns = [c.strip().lower() for c in df.columns]
            
            for _, row in df.iterrows():
                name = str(row.get("concept_name", "")).strip()
                if name and name.lower() != "nan":
                    # Create document with metadata
                    content = f"Concept: {name} (Domain: {domain})"
                    metadata = {
                        "concept_name": name,
                        "concept_id": float(row.get("concept_id", 0)),
                        "vocabulary_id": str(row.get("vocabulary_id", "")),
                        "concept_code": str(row.get("concept_code", "")),
                        "domain": domain,
                        "total_rows": int(row.get("total_rows", 0)),
                        "distinct_persons": int(row.get("distinct_persons", 0)),
                    }
                    documents.append(Document(text=content, metadata=metadata))

        # Source-mapped measurement concepts
        meas_path = os.path.join(catalog_dir, "10_source_code_coverage_measurements.csv")
        if os.path.exists(meas_path):
            df = pd.read_csv(meas_path, encoding="utf-8-sig")
            df.columns = [c.strip().lower() for c in df.columns]
            for _, row in df.iterrows():
                name = str(row.get("mapped_standard_concept_name", "")).strip()
                if name and name.lower() != "nan":
                    content = f"Concept: {name} (Domain: measurements)"
                    metadata = {
                        "concept_name": name,
                        "concept_id": float(row.get("mapped_standard_concept_id", 0)),
                        "vocabulary_id": str(row.get("mapped_standard_vocabulary_id", "")),
                        "concept_code": str(row.get("mapped_standard_concept_code", "")),
                        "domain": "measurements",
                        "total_rows": int(row.get("total_rows", 0)),
                        "distinct_persons": 0,
                    }
                    documents.append(Document(text=content, metadata=metadata))

        if not documents:
            print("  [WARN] No documents found for vector index")
            return

        print(f"  [OK] Indexing {len(documents)} documents into LlamaIndex...")
        self.index = VectorStoreIndex.from_documents(documents)
        
        # Persist to local storage
        os.makedirs(self.storage_dir, exist_ok=True)
        self.index.storage_context.persist(persist_dir=self.storage_dir)
        
        self.is_built = True
        print(f"  [OK] Vector index built and persisted: {len(documents)} concepts")

    def search(self, query: str, top_k: int = 10, domain: str = None):
        """
        Search for concepts using LlamaIndex retriever.
        """
        if not self.is_built or not self.index:
            return []

        # Use retriever for fine-grained control
        retriever = self.index.as_retriever(similarity_top_k=top_k * 2)
        nodes = retriever.retrieve(query)

        results = []
        for node in nodes:
            metadata = node.metadata
            # Filter by domain if requested
            if domain and metadata.get("domain") != domain:
                continue
            
            result = {
                "concept_name": metadata.get("concept_name"),
                "concept_id": metadata.get("concept_id"),
                "vocabulary_id": metadata.get("vocabulary_id"),
                "concept_code": metadata.get("concept_code"),
                "domain": metadata.get("domain"),
                "total_rows": metadata.get("total_rows"),
                "distinct_persons": metadata.get("distinct_persons"),
                "similarity": round(float(node.score), 4) if (node.score is not None) else 0.0
            }
            results.append(result)
            
            if len(results) >= top_k:
                break

        return results

