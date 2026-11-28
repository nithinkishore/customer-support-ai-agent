
from pathlib import Path
from functools import lru_cache

import chromadb
from sentence_transformers import SentenceTransformer
import hashlib

# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]
POLICY_FILE = BASE_DIR / "Knowledge_Base" / "support_policies.md"
CHROMA_DIR = BASE_DIR / "chroma_db"

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

@lru_cache(maxsize=1)
def get_embedding_model():
    """Load the embedding model once and reuse it across requests."""
    return SentenceTransformer(EMBEDDING_MODEL)

# Initialize ChromaDB
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_or_create_collection(
    name="customer_support_policies"
)


def load_policy_document():
    """Read the customer support policy document."""

    if not POLICY_FILE.exists():
        raise FileNotFoundError(
            f"Policy document not found: {POLICY_FILE}"
        )

    return POLICY_FILE.read_text(encoding="utf-8")


def split_into_chunks(text, chunk_size=120, overlap=30):
    """Split policy text into overlapping word chunks."""

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks







def index_knowledge_base():
    """Index policies only when the source document changes."""

    document = load_policy_document()
    chunks = split_into_chunks(document)

    if not chunks:
        raise ValueError("The policy document is empty.")

    # Calculate a fingerprint of the policy document.
    document_hash = hashlib.sha256(
        document.encode("utf-8")
    ).hexdigest()

    # Check whether this version is already indexed.
    metadata = collection.metadata or {}

    if (
        collection.count() > 0
        and metadata.get("policy_hash") == document_hash
    ):
        print("Knowledge base is already up to date.")
        return collection.count()

    # Load the model on first use, then reuse the cached instance.
    model = get_embedding_model()

    # Generate embeddings only when the document changes.
    embeddings = model.encode(
        chunks,
        convert_to_numpy=True
    ).tolist()

    ids = [f"policy_{i}" for i in range(len(chunks))]

    # Replace the previous indexed documents.
    existing = collection.get()

    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings
    )

    # Save the document fingerprint.
    collection.modify(
        metadata={"policy_hash": document_hash}
    )

    print("Knowledge base indexed successfully.")

    return len(chunks)




def search_knowledge_base(question, top_k=3):
    """Retrieve the most relevant policy chunks."""

    if collection.count() == 0:
        return []

    # Reuse the same cached model used during indexing.
    model = get_embedding_model()
    query_embedding = model.encode([question]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count())
    )

    return results["documents"][0]
