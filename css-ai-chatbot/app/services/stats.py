from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter
import re
from typing import Dict, List, Any
from pathlib import Path


def load_data(base_path: str = "." ):
    """Charge les données du CSV"""
    try:
        base_dir = Path(base_path).resolve()
        csv_path = base_dir / "app" / "for-analysis" / "questions-answered" / "responses_ask_question_stream_ultra.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {csv_path}")
        df = pd.read_csv(csv_path)
        df['question'] = df['question'].fillna('Question vide') #remplace les lignes vides par question vide
        df['question'] = df['question'].str.strip() ## supprime les espaces avant/après 
        df = df[df['question'] != 'Question vide'] # supprime les lignes vides
        df['timestamp'] = pd.to_datetime(df['timestamp']) #transforme les timestamp (type str) en format datetime64
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des données: {str(e)}")

def load_satisfaction_data(base_path: str = "." ):
    """Charge les données du CSV"""
    try:
        base_dir = Path(base_path).resolve()
        csv_path = base_dir / "app" / "for-analysis" / "questions-answered" / "user_satisfaction.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {csv_path}")
        df = pd.read_csv(csv_path)
        df['question'] = df['question'].fillna('Question vide')
        df = df[df['question'] != 'Question vide']
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des données: {str(e)}")

def categorize_question(question: str) -> str:
    """Catégorise une question selon des mots-clés"""
    question_lower = str(question).lower()
    
    if any(word in question_lower for word in ['bonjour', 'salut', 'hello', 'bonsoir']):
        return 'Salutations'
    elif any(word in question_lower for word in ['contact', 'agence', 'fax', 'téléphone', 'adresse', 'bp']):
        return 'Contact/Localisation'
    elif any(word in question_lower for word in ['prestation', 'allocation', 'familiale', 'familiales']):
        return 'Prestations familiales'
    elif any(word in question_lower for word in ['retraite', 'pension', 'ipres']):
        return 'Retraite'
    elif any(word in question_lower for word in ['accident', 'travail', 'at-mp', 'blessure']):
        return 'Accidents de travail'
    elif any(word in question_lower for word in ['compte', 'inscrire', 'adhérer', 'plateforme', 'inscription']):
        return 'Inscription/Compte'
    elif any(word in question_lower for word in ['css', 'caisse', 'sécurité', 'sociale']):
        return 'Informations CSS'
    elif any(word in question_lower for word in ['employeur', 'cotisation', 'déclaration', 'immatriculation']):
        return 'Employeurs'
    else:
        return 'Autres'

def extract_keywords(text: str, stop_words: set = None) -> List[str]:
    """Extrait les mots-clés d'un texte"""
    if stop_words is None:
        stop_words = {
            'le', 'la', 'les', 'de', 'des', 'un', 'une', 'et', 'à', 'pour',
            'comment', 'est', 'ce', 'je', 'moi', 'me', 'qui', 'quoi', 'où',
            'dans', 'sur', 'avec', 'sans', 'plus', 'aussi', 'vous', 'nous',
            'sont', 'être', 'avoir', 'faire', 'tout', 'tous', 'peut', 'quand'
        }
    
    words = re.findall(r'\b\w+\b', str(text).lower())
    return [word for word in words if word not in stop_words and len(word) > 3]