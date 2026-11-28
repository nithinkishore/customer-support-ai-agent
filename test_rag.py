
from app.rag.knowledge_base import (
    index_knowledge_base,
    search_knowledge_base
)

print("Indexing customer support policies...")

count = index_knowledge_base()

print(f"Successfully indexed {count} chunks.")

question = "How many days do customers have to return a product?"

print("\nCustomer question:")
print(question)

results = search_knowledge_base(question)

print("\nRetrieved knowledge:")

for result in results:
    print("-", result)
