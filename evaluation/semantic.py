"""Exact cosine search and equal-weight reciprocal rank fusion."""
from collections import defaultdict
import math

import numpy as np


class DenseIndex:
    """Small exact index: normalize vectors and rank by cosine similarity.

    The caller supplies genuine model embeddings in the same order as chunks.
    No thresholds, annotations, or question rewriting affect the rankings.
    """
    def __init__(self, chunks, vectors):
        self.chunks=list(chunks)
        values=np.asarray(vectors,dtype=np.float32)
        if values.ndim!=2 or values.shape[0]!=len(self.chunks) or values.shape[1]<1:
            raise ValueError('Embedding matrix must have one row per chunk and a nonempty dimension')
        if len({c.chunk_id for c in self.chunks})!=len(self.chunks):
            raise ValueError('Duplicate chunk IDs')
        if not np.isfinite(values).all():
            raise ValueError('Non-finite document embedding')
        norms=np.linalg.norm(values,axis=1,keepdims=True)
        if np.any(norms==0):
            raise ValueError('Zero document embedding')
        self.vectors=values/norms

    def search(self, vector, k=10):
        if type(k) is not int or k<1:
            raise ValueError('k must be a positive integer')
        query=np.asarray(vector,dtype=np.float32)
        if query.shape!=(self.vectors.shape[1],) or not np.isfinite(query).all():
            raise ValueError('Invalid query embedding shape or values')
        norm=np.linalg.norm(query)
        if norm==0:
            raise ValueError('Zero query embedding')
        scores=self.vectors@(query/norm)
        ranked=sorted(range(len(self.chunks)),key=lambda i:(-float(scores[i]),self.chunks[i].chunk_id))[:k]
        return [(self.chunks[i],float(scores[i])) for i in ranked]


def reciprocal_rank_fusion(rankings, k=10, constant=60):
    """Fuse rankings by ID using sum(1/(constant+one_based_rank)).

    Raw scores from unlike retrieval methods are deliberately not mixed.
    Duplicate IDs within a ranking are rejected instead of boosting a candidate.
    """
    if type(k) is not int or k<1 or not math.isfinite(constant) or constant<0:
        raise ValueError('Invalid fusion parameters')
    scores=defaultdict(float)
    chunks={}
    for ranking in rankings:
        seen=set()
        for rank,(chunk,_) in enumerate(ranking,1):
            if chunk.chunk_id in seen:
                raise ValueError('Duplicate chunk within a ranking')
            if chunk.chunk_id in chunks and chunks[chunk.chunk_id]!=chunk:
                raise ValueError('Conflicting records for the same chunk ID')
            seen.add(chunk.chunk_id)
            chunks[chunk.chunk_id]=chunk
            scores[chunk.chunk_id]+=1/(constant+rank)
    ids=sorted(scores,key=lambda key:(-scores[key],key))[:k]
    return [(chunks[key],scores[key]) for key in ids]
