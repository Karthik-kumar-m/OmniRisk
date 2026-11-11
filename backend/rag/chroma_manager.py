"""ChromaDB Manager for OmniRisk Corporate Underwriting Guidelines.

Indexes domain underwriting guidelines manuals into a persistent ChromaDB collection.
Supports semantic vector search and provides guideline metadata for RAG grounding.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


class ChromaGuidelineManager:
    """Manages persistent ChromaDB vector storage and indexing for underwriting manuals."""

    COLLECTION_NAME = "corporate_underwriting_guidelines"

    def __init__(
        self,
        knowledge_base_dir: str = "knowledge_base",
        chroma_db_dir: Optional[str] = None
    ):
        kb_path = Path(knowledge_base_dir)
        if not kb_path.exists():
            candidate = Path(__file__).resolve().parent.parent.parent / knowledge_base_dir
            if candidate.exists():
                kb_path = candidate
        self.knowledge_base_dir = kb_path

        if chroma_db_dir:
            self.chroma_db_dir = Path(chroma_db_dir)
        else:
            self.chroma_db_dir = self.knowledge_base_dir / "chroma_db"

        self.client = None
        self.collection = None
        self.guidelines_cache: List[Dict[str, Any]] = []

        self._initialize_vector_db()

    def _initialize_vector_db(self):
        """Initializes ChromaDB persistent client and collection, then indexes documents."""
        self._load_local_guideline_documents()

        if not CHROMA_AVAILABLE:
            print("[ChromaManager] ChromaDB not installed; using in-memory semantic fallback.")
            return

        try:
            self.chroma_db_dir.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(self.chroma_db_dir))
            self.collection = self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"description": "Corporate P&C Insurance Underwriting Standards"}
            )

            # Check if collection is empty or needs indexing
            count = self.collection.count()
            if count == 0 and self.guidelines_cache:
                self._index_guidelines_into_chroma()
            else:
                print(f"[ChromaManager] Connected to persistent Chroma collection with {count} guidelines.")
        except Exception as e:
            print(f"[ChromaManager] Warning: Persistent Chroma init failed ({e}); fallback active.")
            self.collection = None

    def _load_local_guideline_documents(self):
        """Parses markdown manuals from knowledge_base directory into structured guideline objects."""
        if not self.knowledge_base_dir.exists():
            return

        self.guidelines_cache = []
        md_files = list(self.knowledge_base_dir.glob("*.md"))

        rule_regex = re.compile(r"^###\s+\[(.*?)\]\s+(.*?)$", re.MULTILINE)

        for md_file in md_files:
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract manual title
                title_match = re.search(r"^#\s+(.*?)$", content, re.MULTILINE)
                manual_title = title_match.group(1).strip() if title_match else md_file.stem.replace("_", " ").title()

                # Determine category
                cat = "General"
                if "property" in md_file.name.lower():
                    cat = "Property"
                elif "hazard" in md_file.name.lower() or "flood" in md_file.name.lower():
                    cat = "Catastrophe"
                elif "fleet" in md_file.name.lower() or "casualty" in md_file.name.lower():
                    cat = "Casualty"
                elif "financial" in md_file.name.lower() or "loss" in md_file.name.lower():
                    cat = "Financial"

                # Find all rules in this manual
                sections = rule_regex.split(content)
                # sections structure: [preamble, rule_id_1, title_1, body_1, rule_id_2, title_2, body_2, ...]
                if len(sections) > 1:
                    for i in range(1, len(sections), 3):
                        if i + 2 <= len(sections):
                            r_id = sections[i].strip()
                            r_title = sections[i + 1].strip()
                            r_body = sections[i + 2].strip()

                            # Extract threshold & mitigation
                            thresh_m = re.search(r"Corporate Standard:\s*(.*?)(?:\n|$)", r_body, re.IGNORECASE)
                            thresh_str = thresh_m.group(1).strip() if thresh_m else "Refer to rule specification."

                            mit_m = re.search(r"Actionable Mitigation:\s*(.*?)(?:\n|$)", r_body, re.IGNORECASE)
                            mit_str = mit_m.group(1).strip() if mit_m else "Standard underwriting referral."

                            doc_text = f"[{r_id}] {r_title}\nManual: {manual_title}\nCategory: {cat}\n{r_body}"

                            self.guidelines_cache.append({
                                "rule_id": r_id,
                                "title": r_title,
                                "manual_source": manual_title,
                                "file_name": md_file.name,
                                "category": cat,
                                "corporate_threshold": thresh_str,
                                "mitigation": mit_str,
                                "text": doc_text
                            })
            except Exception as e:
                print(f"[ChromaManager] Error reading {md_file.name}: {e}")

        print(f"[ChromaManager] Parsed {len(self.guidelines_cache)} rules from {len(md_files)} manuals.")

    def _index_guidelines_into_chroma(self):
        """Indexes cached guidelines into ChromaDB vector collection."""
        if not self.collection or not self.guidelines_cache:
            return

        documents = []
        metadatas = []
        ids = []

        for g in self.guidelines_cache:
            documents.append(g["text"])
            metadatas.append({
                "rule_id": g["rule_id"],
                "title": g["title"],
                "manual_source": g["manual_source"],
                "category": g["category"],
                "corporate_threshold": g["corporate_threshold"],
                "mitigation": g["mitigation"],
            })
            ids.append(g["rule_id"])

        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"[ChromaManager] Successfully indexed {len(ids)} underwriting guidelines into ChromaDB.")
        except Exception as e:
            print(f"[ChromaManager] Error indexing into ChromaDB: {e}")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Performs semantic similarity search against indexed corporate guidelines."""
        if self.collection:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=min(top_k, self.collection.count() or 1)
                )

                hits = []
                docs = results.get("documents", [[]])[0]
                metas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0] if "distances" in results else [0.0] * len(docs)

                for i, doc in enumerate(docs):
                    meta = metas[i] if i < len(metas) else {}
                    dist = distances[i] if i < len(distances) else 0.5
                    # Convert distance to similarity percentage (Chroma L2 distance default)
                    relevance = max(0.1, min(0.99, round(1.0 - (dist / 2.0), 3)))

                    hits.append({
                        "rule_id": meta.get("rule_id", "UNKNOWN"),
                        "title": meta.get("title", "Underwriting Rule"),
                        "manual_source": meta.get("manual_source", "Corporate Guidelines"),
                        "category": meta.get("category", "General"),
                        "corporate_threshold": meta.get("corporate_threshold", ""),
                        "mitigation": meta.get("mitigation", ""),
                        "excerpt": doc[:300] + ("..." if len(doc) > 300 else ""),
                        "full_text": doc,
                        "relevance_score": relevance
                    })

                if hits:
                    return hits
            except Exception as e:
                print(f"[ChromaManager] Chroma search error ({e}); using keyword fallback.")

        # Fallback keyword relevance matcher if ChromaDB query encounters an issue
        return self._keyword_search_fallback(query, top_k)

    def _keyword_search_fallback(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """In-memory keyword ranking fallback."""
        q_tokens = set(re.findall(r"\w+", query.lower()))
        scored = []

        for g in self.guidelines_cache:
            doc_tokens = set(re.findall(r"\w+", g["text"].lower()))
            intersection = q_tokens.intersection(doc_tokens)
            score = len(intersection) / (len(q_tokens) or 1)
            scored.append((score, g))

        scored.sort(key=lambda x: x[0], reverse=True)
        hits = []
        for score, g in scored[:top_k]:
            hits.append({
                "rule_id": g["rule_id"],
                "title": g["title"],
                "manual_source": g["manual_source"],
                "category": g["category"],
                "corporate_threshold": g["corporate_threshold"],
                "mitigation": g["mitigation"],
                "excerpt": g["text"][:300] + "...",
                "full_text": g["text"],
                "relevance_score": max(0.5, round(score, 3))
            })
        return hits

    def get_all_guidelines(self) -> List[Dict[str, Any]]:
        """Returns all indexed guidelines for the UI inspector and API."""
        return self.guidelines_cache
