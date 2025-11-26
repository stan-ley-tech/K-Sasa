import json
import os
from dataclasses import dataclass
from typing import List, Tuple, Dict

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover
    faiss = None  # type: ignore
try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore


@dataclass
class DocChunk:
    text: str
    source: str


class SimpleRetriever:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = None
        if SentenceTransformer is not None:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception:
                self.model = None
        self.index = None
        self.chunks: List[DocChunk] = []

    def build_from_seed(self, seed_dir: str):
        texts: List[str] = []
        metas: List[str] = []

        # JSON seed
        json_path = os.path.join(seed_dir, "gov_form_business.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                texts.append(json.dumps(data))
                metas.append("seed:gov_form_business.json")
            except Exception:
                pass

        # PDFs (placeholder read as filenames)
        for name in ["curriculum_kiswahili.pdf", "moh_leaflet_kiswahili.pdf"]:
            path = os.path.join(seed_dir, name)
            if os.path.exists(path):
                try:
                    # NOTE: keep simple placeholder; integrate PDF parsing later
                    texts.append(f"Placeholder content for {name}")
                    metas.append(f"seed:{name}")
                except Exception:
                    pass

        # TXT notes (read contents)
        try:
            for fname in os.listdir(seed_dir):
                if fname.lower().endswith(".txt"):
                    p = os.path.join(seed_dir, fname)
                    with open(p, "r", encoding="utf-8") as f:
                        content = f.read()
                    texts.append(content)
                    metas.append(f"seed:{fname}")
        except Exception:
            pass

        # Chunk (simple)
        chunks: List[DocChunk] = []
        for t, m in zip(texts, metas):
            for i in range(0, len(t), 400):
                piece = t[i : i + 400]
                if piece.strip():
                    chunks.append(DocChunk(text=piece, source=m))

        if not chunks:
            self.index = None
            self.chunks = []
            return

        # If embedding stack available, build vector index; else fallback to simple mode
        if self.model is not None and faiss is not None:
            try:
                embeddings = self.model.encode([c.text for c in chunks], normalize_embeddings=True)
                dim = embeddings.shape[1]
                index = faiss.IndexFlatIP(dim)
                index.add(embeddings)
                self.index = index
            except Exception:
                self.index = None
        else:
            self.index = None
        self.chunks = chunks

    def retrieve(self, query: str, k: int = 4) -> List[Tuple[DocChunk, float]]:
        if not self.chunks:
            return []
        # Vector search path if available
        if self.index is not None and self.model is not None:
            try:
                q = self.model.encode([query], normalize_embeddings=True)
                scores, idxs = self.index.search(q, k)
                out: List[Tuple[DocChunk, float]] = []
                for i, s in zip(idxs[0], scores[0]):
                    if i == -1:
                        continue
                    out.append((self.chunks[i], float(s)))
                return out
            except Exception:
                pass
        # Fallback: simple keyword overlap scoring
        q_tokens = set([w.lower() for w in query.split() if w.strip()])
        scored: List[Tuple[int, float]] = []
        for idx, ch in enumerate(self.chunks):
            t_tokens = set([w.lower() for w in ch.text.split() if w.strip()])
            inter = q_tokens.intersection(t_tokens)
            score = float(len(inter)) / float(len(q_tokens) or 1)
            scored.append((idx, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:k]
        out: List[Tuple[DocChunk, float]] = []
        for i, s in top:
            out.append((self.chunks[i], float(s)))
        return out


def format_citations(retrieved: List[Tuple[DocChunk, float]]) -> List[Dict]:
    cites = []
    for chunk, score in retrieved:
        cites.append({
            "source": chunk.source,
            "snippet": chunk.text[:200],
            "score": score,
        })
    return cites
