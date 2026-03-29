import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from django.conf import settings

MODEL_NAME = 'all-MiniLM-L6-v2'
_model =  None

def get_Model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    
    return _model

def embed_Texts(texts: list[str]) -> np.ndarray:

    model = get_Model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embeddings.astype('float32')

def build_Faiss_Index(embeddings: np.ndarray) -> faiss.IndexFlatIP:

    faiss.normalize_L2(embeddings)
    dimension  = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    return index

def search_Index(index: faiss.IndexFlatIP,  query_embedding = np.ndarray, top_k:  int =  5):

    query =  query_embedding.astype('float32').reshape(1,-1)
    faiss.normalize_L2(query)
    distances,indices = index.search(query,top_k)
    return distances[0], indices[0]

def cosine_similarity(text_a : str, text_b : str):

    embeddings = embed_Texts([text_a,text_b])
    faiss.normalize_L2(embeddings)
    similarity = float(np.dot(embeddings[0], embeddings[1]))
    return similarity

