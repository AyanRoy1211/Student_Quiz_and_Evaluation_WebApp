import fitz
from .embedder import embed_Texts, build_Faiss_Index, search_Index

def parse_PDF(file_path: str) -> str:

    doc = fitz.open(file_path)
    full_text =  ""
    for page in doc:
        full_text += page.get_text()
    
    doc.close()
    return full_text

def chunk_text(text: str, chunk_size: int=300, overlap: int=50) -> list[str]:

    words = text.split()
    chunks = []
    step = chunk_size - overlap

    for i in range(0, len(words), step):
        chunk =  ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)

    return chunks

def build_retriever_from_pdf(file_path: str):
    
    text = parse_PDF(file_path)

    if not text.strip():
        raise ValueError("PDF appears to be empty or unraedable. Try a text-based PDF")
    
    chunks = chunk_text(text)

    if len(chunks) == 0:
        raise ValueError("Could not extract any useful texts from the PDF")
    
    embeddings = embed_Texts(chunks)
    index = build_Faiss_Index(embeddings)

    return chunks,index

def retrieve_top_k(query: str, chunks: list[str], index, top_k: int=5) -> list[str]:

    query_embedding = embed_Texts([query])
    distances,indices = search_Index(index, query_embedding[0], top_k=top_k)

    retrieved = []
    for idx in indices:
        if idx < len(chunks):
            retrieved.append(chunks[idx])

    return retrieved