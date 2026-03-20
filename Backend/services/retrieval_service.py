"""
Retrieval service — hybrid retrieval combining SQL exact match and TF-IDF semantic search.
Agents call this to find matching catalog entries for clinical terms.
"""
from services.catalog_service import CatalogService
from services.vector_service import VectorService


class RetrievalService:
    """Hybrid retrieval: SQL LIKE + TF-IDF semantic search."""

    def __init__(self, catalog_service: CatalogService, vector_service: VectorService):
        self.catalog = catalog_service
        self.vector = vector_service

    def retrieve_concepts(self, query: str, domain: str = None, top_k: int = 10):
        """
        Retrieve matching concepts using semantic vector search.
        """
        # Search via LlamaIndex vector store
        semantic = self.vector.search(query, top_k=top_k, domain=domain)

        # Map to common output format
        combined = []
        for item in semantic:
            item["match_type"] = "semantic"
            combined.append(item)

        return {
            "query": query,
            "domain": domain,
            "total_matches": len(combined),
            "matches": combined[:top_k],
        }

    def verify_criterion(self, concept_name: str, domain: str = None):
        """
        Verify whether a criterion is supported by the EHR catalog.

        Returns:
            Dict with 'supported' bool, 'matches', and 'confidence'.
        """
        results = self.retrieve_concepts(concept_name, domain=domain, top_k=5)
        matches = results["matches"]
        supported = len(matches) > 0
        confidence = "high" if matches and matches[0].get("match_type") == "exact" else (
            "medium" if matches else "none"
        )
        return {
            "concept": concept_name,
            "domain": domain,
            "supported": supported,
            "confidence": confidence,
            "matches": matches,
        }
