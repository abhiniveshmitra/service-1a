"""
Embedding generation for semantic similarity
"""

import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Union

class EmbeddingGenerator:
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        '''Load the sentence transformer model'''
        try:
            self.model = SentenceTransformer(self.model_name)
            self.logger.info(f'Loaded embedding model: {self.model_name}')
        except Exception as e:
            self.logger.error(f'Failed to load model {self.model_name}: {str(e)}')
            raise
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        '''Generate embeddings for a list of texts'''
        if not self.model:
            raise RuntimeError('Model not loaded')
        
        # Clean and preprocess texts
        clean_texts = [self._preprocess_text(text) for text in texts]
        
        # Generate embeddings
        embeddings = self.model.encode(clean_texts, normalize_embeddings=True)
        return embeddings
    
    def encode_single(self, text: str) -> np.ndarray:
        '''Generate embedding for a single text'''
        return self.encode_texts([text])[0]
    
    def _preprocess_text(self, text: str) -> str:
        '''Clean and preprocess text for embedding'''
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Limit length (models have token limits)
        if len(text) > 500:
            text = text[:500] + '...'
        
        return text
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        '''Calculate cosine similarity between two embeddings'''
        return float(np.dot(embedding1, embedding2))
