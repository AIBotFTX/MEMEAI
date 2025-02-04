from langchain.memory import RedisChatMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from memeai.memory.config import settings
import faiss


history_redis = RedisChatMessageHistory(
    session_id="",
    url=settings.construct_redis_url,  # Use correct format for URL
)
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
index = faiss.IndexFlatL2(settings.EMBEDDINGS_SIZE)
memory_vector = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {}) 