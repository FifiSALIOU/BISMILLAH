import os
# from pydantic import BaseSettings
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "CSS RAG Multimodal API"
    APP_DESCRIPTION: str = "API RAG multimodale avec recherche hybride, re-ranking et optimisations avancées"
    APP_VERSION: str = "2005.0.3"

    # Redis configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))

    # API Keys
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # ChromaDB path
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./ultra_rag_db")
    MULTIMODAL_CHROMA_DB_PATH: str = os.getenv("MULTIMODAL_CHROMA_DB_PATH", "./multimodal_ultra_rag_db")

    # Model paths
    MULTIMODAL_MODELS: dict = {
        "clip": "openai/clip-vit-base-patch32",
        "blip": "Salesforce/blip-image-captioning-base",
        "text_embedding": "sentence-transformers/clip-ViT-B-32-multilingual-v1"
    }

    # Optimisation LLM
    ENABLE_PREDEFINED_QA: bool = os.getenv("ENABLE_PREDEFINED_QA", "true").lower() == "true"
    ENABLE_QUERY_ENHANCEMENT: bool = os.getenv("ENABLE_QUERY_ENHANCEMENT", "true").lower() == "true"
    
    # Optimisation Cache
    CACHE_DEFAULT_TTL: int = int(os.getenv("CACHE_DEFAULT_TTL", 7200))  # 2 heures au lieu de 1h
    CACHE_MEMORY_MAX_ITEMS: int = int(os.getenv("CACHE_MEMORY_MAX_ITEMS", 2000))  # Doublé
    CACHE_REDIS_TIMEOUT: int = int(os.getenv("CACHE_REDIS_TIMEOUT", 10))  # Timeout plus long
    CACHE_EMBEDDINGS_TTL: int = int(os.getenv("CACHE_EMBEDDINGS_TTL", 14400))  # 4h pour embeddings
    
    # Optimisation Recherche Hybride
    SEARCH_ALPHA: float = float(os.getenv("SEARCH_ALPHA", 0.75))  # Favorise légèrement la recherche dense
    SEARCH_TOP_K: int = int(os.getenv("SEARCH_TOP_K", 15))  # Plus de résultats pour le reranking
    SEARCH_DENSE_TOP_K: int = int(os.getenv("SEARCH_DENSE_TOP_K", 10))
    SEARCH_SPARSE_TOP_K: int = int(os.getenv("SEARCH_SPARSE_TOP_K", 8))
    
    # Optimisation ChromaDB
    CHROMA_BATCH_SIZE: int = int(os.getenv("CHROMA_BATCH_SIZE", 100))  # Traitement par batch
    CHROMA_MAX_RESULTS: int = int(os.getenv("CHROMA_MAX_RESULTS", 50))  # Limite des résultats
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_persist")
    CHROMA_COLLECTION_METADATA: dict = {"hnsw:space": "cosine", "hnsw:construction_ef": 200, "hnsw:M": 16}
    
    # Optimisation Embeddings (Quantization)
    ENABLE_EMBEDDING_QUANTIZATION: bool = os.getenv("ENABLE_EMBEDDING_QUANTIZATION", "false").lower() == "true"
    QUANTIZATION_BITS: int = int(os.getenv("QUANTIZATION_BITS", 8))  # 8-bit quantization par défaut
    EMBEDDING_COMPRESSION_RATIO: float = float(os.getenv("EMBEDDING_COMPRESSION_RATIO", 0.5))  # 50% compression

    # Tokens
    IPINFO_TOKEN: str = os.getenv("IPINFO_TOKEN", "")


settings = Settings()
