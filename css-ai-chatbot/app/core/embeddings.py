import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Union, Optional
from functools import lru_cache
import hashlib
import time

from app.core.cache import cache
from app.core.config import settings
from app.utils.logging import logger


# Modèles d'embeddings avancés
class AdvancedEmbeddings:
    def __init__(self):
        try:
            # Modèle principal optimisé
            self.primary_model = SentenceTransformer(
                'all-mpnet-base-v2',
                device='cpu',
                cache_folder='./.cache/sentence_transformers'
            )
            logger.info("Modèle principal all-mpnet-base-v2 chargé")

            # Modèle multilingue en lazy loading (chargé seulement si nécessaire)
            self.multilingual_model = None
            self._multilingual_loaded = False

        except Exception as e:
            logger.error(f"Erreur chargement modèles: {e}")
            # Fallback sur un modèle plus léger
            self.primary_model = SentenceTransformer('all-MiniLM-L6-v2')

    def _load_multilingual_if_needed(self):
        """Chargement lazy du modèle multilingue"""
        if not self._multilingual_loaded:
            try:
                self.multilingual_model = SentenceTransformer(
                    'paraphrase-multilingual-mpnet-base-v2',
                    device='cpu',
                    cache_folder='./.cache/sentence_transformers'
                )
                self._multilingual_loaded = True
                logger.info("Modèle multilingue chargé")
            except Exception as e:
                logger.error(f"Erreur chargement modèle multilingue: {e}")
                self.multilingual_model = None

    @lru_cache(maxsize=5000)
    def embed_query(self, text: str) -> np.ndarray:
        """Cache des embeddings de requêtes avec LRU"""
        start_time = time.time()
        embedding = self.primary_model.encode([text])[0]
        
        # Appliquer la quantization si activée
        quantized = False
        if settings.ENABLE_EMBEDDING_QUANTIZATION:
            embedding = self._quantize_embeddings([embedding])[0]
            quantized = True
        
        # Enregistrer les métriques de performance
        duration = time.time() - start_time
        from app.core.metrics import metrics_collector
        metrics_collector.record_embedding_performance("query", duration, quantized)
        
        return embedding

    def embed_documents(self, texts: List[str], use_cache: bool = True) -> List[np.ndarray]:
        """Embedding de documents avec cache intelligent"""
        start_time = time.time()
        embeddings = []
        uncached_texts = []
        uncached_indices = []

        for i, text in enumerate(texts):
            if use_cache:
                cached = cache.get(text, "embeddings")
                if cached is not None:
                    embeddings.append(cached)
                    continue

            uncached_texts.append(text)
            uncached_indices.append(i)
            embeddings.append(None)  # Placeholder

        # Traitement par batch des textes non cachés
        if uncached_texts:
            new_embeddings = self.primary_model.encode(uncached_texts)

            for idx, embedding in zip(uncached_indices, new_embeddings):
                embeddings[idx] = embedding
                if use_cache:
                    cache.set(uncached_texts[uncached_indices.index(idx)],
                              embedding, cache_type="embeddings")

        # Appliquer la quantization si activée
        quantized = False
        if settings.ENABLE_EMBEDDING_QUANTIZATION:
            embeddings = self._quantize_embeddings(embeddings)
            quantized = True
        
        # Enregistrer les métriques de performance
        duration = time.time() - start_time
        from app.core.metrics import metrics_collector
        metrics_collector.record_embedding_performance("documents", duration, quantized)
        
        return embeddings
    
    def _quantize_embeddings(self, embeddings: List[np.ndarray]) -> List[np.ndarray]:
        """Quantization des embeddings pour réduire l'usage mémoire"""
        if not settings.ENABLE_EMBEDDING_QUANTIZATION:
            return embeddings
        
        quantized_embeddings = []
        for embedding in embeddings:
            # Quantization 8-bit avec normalisation
            embedding_normalized = embedding / np.linalg.norm(embedding)
            
            # Quantization linéaire
            min_val, max_val = embedding_normalized.min(), embedding_normalized.max()
            scale = (max_val - min_val) / (2 ** settings.QUANTIZATION_BITS - 1)
            
            quantized = np.round((embedding_normalized - min_val) / scale).astype(np.uint8)
            
            # Dequantization pour compatibilité
            dequantized = (quantized.astype(np.float32) * scale + min_val)
            
            # Compression supplémentaire si demandée
            if settings.EMBEDDING_COMPRESSION_RATIO < 1.0:
                target_dim = int(len(dequantized) * settings.EMBEDDING_COMPRESSION_RATIO)
                dequantized = dequantized[:target_dim]
            
            quantized_embeddings.append(dequantized)
        
        logger.debug(f"Embeddings quantizés: {len(embeddings)} -> économie mémoire estimée: {(1 - settings.EMBEDDING_COMPRESSION_RATIO) * 100:.1f}%")
        return quantized_embeddings
