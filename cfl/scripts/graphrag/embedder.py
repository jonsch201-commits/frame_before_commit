#!/usr/bin/env python3
"""Pluggable local embedder for the CFL GraphRAG index.

⛔ WHY LOCAL, AND WHY THIS PARTICULAR MODEL — the constraint chain, so nobody re-argues it:

  1. Jon (2026-08-17 11:5x, verbatim, typos his): "I know graph rag alone will fail if we don't
     also implement vector embeding. Think about all my typos and imprecise language and the
     stylomantic differences between trunks."
  2. Anthropic ships NO embeddings model. VERIFIED verbatim from their docs, 2026-08-17:
     "Anthropic does not offer its own embedding model." So the `anthropic` SDK already installed
     on this machine is a completions client and cannot serve this lane.
  3. The Secretary's assignment letter named two roads: (a) a generic local model, or (b) a hosted
     embedding API -- which costs money, needs a key, and is therefore a JON DECISION.
     ⭐ There is a third: an OPEN-WEIGHT model that runs locally with no key and no cost, so the
     money question never has to reach him for v0.

  ⭐ `minishlab/potion-retrieval-32M` (MIT, retrieval-tuned static embeddings) needs numpy +
  tokenizers ONLY. No torch, no CUDA, no ~2.5 GB install. Inference is a vocabulary lookup plus a
  mean -- it runs on CPU at corpus scale in seconds.

⚠️ THE HONEST COST OF THAT CHOICE, stated here rather than discovered later: static embeddings are
ORDER-INSENSITIVE. "wiki wins on conflict" and "conflict wins on wiki" embed identically. They buy
recall and speed; they do not model syntax. That is acceptable for v0 retrieval (the graph carries
provenance and the reader is an LLM) and it is the first thing to revisit if precision disappoints.

⚠️ AND THE SECOND LIMIT, which is why this module is not the whole answer: an embedder that has
never seen the token "embeding" cannot fix it. Static models tokenize a typo into different
subwords than the correct spelling. ⛔ SO TYPO ROBUSTNESS IS NOT DELIVERED HERE -- it is delivered
by query-time fuzzy lexical expansion in `retrieve.py`. Read the two together or the design looks
like it is relying on a property this model does not have.
"""

from __future__ import annotations

import hashlib
import struct
import sys

import numpy as np

STATIC_MODEL = "minishlab/potion-retrieval-32M"
HASH_DIMS = 256


class Embedder:
    """Common surface: .name, .dims, .encode(list[str]) -> float32 (n, dims), L2-normalized."""

    name = "base"
    dims = 0

    def encode(self, texts):  # pragma: no cover - interface
        raise NotImplementedError


def _l2(mat: np.ndarray) -> np.ndarray:
    mat = np.asarray(mat, dtype=np.float32)
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    # A zero vector stays zero rather than becoming NaN. An empty chunk must score 0.0
    # against every query, not poison the ranking with NaN comparisons.
    norms[norms == 0.0] = 1.0
    return (mat / norms).astype(np.float32)


class StaticEmbedder(Embedder):
    """model2vec static embeddings. Local, open-weight, no key, no network after first fetch."""

    name = "potion-retrieval-32M"

    def __init__(self, model_name: str = STATIC_MODEL):
        from model2vec import StaticModel  # imported lazily so the fallback needs no dependency

        self.model = StaticModel.from_pretrained(model_name)
        self.name = model_name.split("/")[-1]
        probe = self.model.encode(["dimension probe"])
        self.dims = int(np.asarray(probe).shape[1])

    def encode(self, texts):
        if not texts:
            return np.zeros((0, self.dims), dtype=np.float32)
        return _l2(self.model.encode(list(texts)))


class HashEmbedder(Embedder):
    """Deterministic hashed char-trigram projection. Pure numpy, zero downloads.

    ⚠️ THIS IS A DEGRADATION PATH, NOT A PEER. It is lexical shape, not meaning: it will match
    "vector embeding" to "vector embedding" (shared trigrams) but it will NOT match "how much
    budget is left" to a page about "spend headroom". It exists so a machine with no model can
    still build and query an index, and so the acceptance test can prove which half of the hybrid
    is carrying which query. Any report produced on this backend must say so on its face.
    """

    name = "hash-trigram"

    def __init__(self, dims: int = HASH_DIMS):
        self.dims = dims

    def encode(self, texts):
        out = np.zeros((len(texts), self.dims), dtype=np.float32)
        for i, text in enumerate(texts):
            low = " " + " ".join(str(text).lower().split()) + " "
            for j in range(len(low) - 2):
                tri = low[j : j + 3]
                digest = hashlib.blake2b(tri.encode("utf-8"), digest_size=8).digest()
                slot = struct.unpack("<Q", digest)[0]
                out[i, slot % self.dims] += 1.0 if (slot >> 63) else -1.0
        return _l2(out)


def load_embedder(prefer: str = "auto") -> Embedder:
    """prefer: 'auto' | 'static' | 'hash'. 'auto' takes static when importable, else hash."""
    if prefer in ("auto", "static"):
        try:
            return StaticEmbedder()
        except Exception as exc:
            if prefer == "static":
                raise
            print(f"[embedder] static unavailable ({exc.__class__.__name__}: {exc}); "
                  f"falling back to {HashEmbedder.name} -- SEMANTIC RECALL IS NOT AVAILABLE",
                  file=sys.stderr)
    return HashEmbedder()


if __name__ == "__main__":
    emb = load_embedder(sys.argv[1] if len(sys.argv) > 1 else "auto")
    vecs = emb.encode(["the fence is wider than you assume", "gates are wider than expected",
                       "sqlite index rebuild lock"])
    print(f"backend={emb.name} dims={emb.dims}")
    sim = vecs @ vecs.T
    print("self-sim diag :", np.round(np.diag(sim), 4).tolist())
    print("paraphrase pair:", round(float(sim[0, 1]), 4))
    print("unrelated pair :", round(float(sim[0, 2]), 4))
