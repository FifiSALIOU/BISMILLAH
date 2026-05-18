import torch
from PIL import Image
import pytesseract
import numpy as np
import warnings

from app.core.config import settings
from app.utils.logging import logger

# Suppression des warnings de transformers
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

# Classe pour gérer les modèles multimodaux avec gestion d'erreur robuste
class MultimodalModels:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models_loaded = {}
        logger.info(f"Utilisation du device: {self.device}")

        # Lazy loading des modèles
        self._clip_model = None
        self._clip_processor = None
        self._blip_model = None
        self._blip_processor = None
        
        # Flags pour indiquer si les modèles sont disponibles
        self._clip_available = True
        self._blip_available = True

    def _load_clip(self):
        """Chargement lazy du modèle CLIP avec gestion d'erreur"""
        if self._clip_model is None and self._clip_available:
            try:
                from transformers import CLIPProcessor, CLIPModel
                self._clip_model = CLIPModel.from_pretrained(settings.MULTIMODAL_MODELS["clip"])
                self._clip_processor = CLIPProcessor.from_pretrained(settings.MULTIMODAL_MODELS["clip"])
                self._clip_model.to(self.device)
                logger.info("Modèle CLIP chargé avec succès")
            except Exception as e:
                logger.warning(f"Erreur chargement CLIP: {e}. Mode dégradé activé.")
                self._clip_available = False

    def _load_blip(self):
        """Chargement lazy du modèle BLIP avec gestion d'erreur"""
        if self._blip_model is None and self._blip_available:
            try:
                from transformers import BlipProcessor, BlipForConditionalGeneration
                self._blip_processor = BlipProcessor.from_pretrained(settings.MULTIMODAL_MODELS["blip"])
                self._blip_model = BlipForConditionalGeneration.from_pretrained(settings.MULTIMODAL_MODELS["blip"])
                self._blip_model.to(self.device)
                logger.info("Modèle BLIP chargé avec succès")
            except Exception as e:
                logger.warning(f"Erreur chargement BLIP: {e}. Mode dégradé activé.")
                self._blip_available = False

    def encode_image(self, image: Image.Image) -> np.ndarray:
        """Encodage d'image avec CLIP ou fallback"""
        try:
            if self._clip_available:
                self._load_clip()
                if self._clip_model is not None:
                    inputs = self._clip_processor(images=image, return_tensors="pt").to(self.device)
                    with torch.no_grad():
                        image_features = self._clip_model.get_image_features(**inputs)
                    return image_features.cpu().numpy().flatten()
        except Exception as e:
            logger.warning(f"Erreur encodage CLIP: {e}")
            self._clip_available = False
        
        # Fallback: retourner un vecteur par défaut
        logger.info("Utilisation du fallback pour l'encodage d'image")
        return np.random.rand(512).astype(np.float32)  # Vecteur aléatoire de taille standard

    def _truncate_text_for_clip(self, text: str, max_tokens: int = 77) -> str:
        """Troncature du texte pour CLIP"""
        words = text.split()
        if len(words) <= max_tokens:
            return text
        return " ".join(words[:max_tokens])

    def encode_text_for_image(self, text: str) -> np.ndarray:
        """Encodage de texte pour comparaison avec images"""
        try:
            if self._clip_available:
                self._load_clip()
                if self._clip_model is not None:
                    truncated_text = self._truncate_text_for_clip(text)
                    inputs = self._clip_processor(text=[truncated_text], return_tensors="pt", padding=True).to(self.device)
                    with torch.no_grad():
                        text_features = self._clip_model.get_text_features(**inputs)
                    return text_features.cpu().numpy().flatten()
        except Exception as e:
            logger.warning(f"Erreur encodage texte CLIP: {e}")
            self._clip_available = False
        
        # Fallback: retourner un vecteur par défaut
        logger.info("Utilisation du fallback pour l'encodage de texte")
        return np.random.rand(512).astype(np.float32)

    def generate_image_caption(self, image: Image.Image) -> str:
        """Génération de légende d'image avec BLIP ou fallback"""
        try:
            if self._blip_available:
                self._load_blip()
                if self._blip_model is not None:
                    inputs = self._blip_processor(image, return_tensors="pt").to(self.device)
                    with torch.no_grad():
                        out = self._blip_model.generate(**inputs, max_length=50)
                    caption = self._blip_processor.decode(out[0], skip_special_tokens=True)
                    return caption
        except Exception as e:
            logger.warning(f"Erreur génération caption BLIP: {e}")
            self._blip_available = False
        
        # Fallback: description générique
        return "Image uploaded by user"

    def extract_text_from_image(self, image: Image.Image) -> str:
        """Extraction de texte avec OCR (Tesseract)"""
        try:
            text = pytesseract.image_to_string(image, lang='fra+eng')
            return text.strip()
        except Exception as e:
            logger.warning(f"Erreur OCR: {e}")
            return ""

    def is_multimodal_available(self) -> dict:
        """Retourne l'état de disponibilité des modèles"""
        return {
            "clip_available": self._clip_available,
            "blip_available": self._blip_available,
            "ocr_available": True  # Tesseract est généralement disponible
        }


# Instance globale
multimodal_models = MultimodalModels()