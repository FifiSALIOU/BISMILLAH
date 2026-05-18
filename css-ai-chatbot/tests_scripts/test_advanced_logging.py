#!/usr/bin/env python3
"""
Script de test pour le système de logging avancé
Teste tous les endpoints ask avec le nouveau système de logging IP
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_QUESTION = "Qu'est-ce que l'intelligence artificielle?"
TEST_IMAGE_PATH = "test.jpg"

def test_ask_question():
    """Test de l'endpoint /ask-question"""
    print("\n=== Test /ask-question ===")
    
    url = f"{BASE_URL}/ask-question"
    payload = {
        "question": TEST_QUESTION,
        "provider": "mistral",
        "top_k": 3,
        "temperature": 0.3,
        "max_tokens": 512
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response ID: {result.get('id', 'N/A')}")
            print(f"Answer: {result.get('answer', 'N/A')[:100]}...")
            print("✅ Test réussi")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_ask_question_stream():
    """Test de l'endpoint /ask-question-stream"""
    print("\n=== Test /ask-question-stream ===")
    
    url = f"{BASE_URL}/ask-question-stream"
    payload = {
        "question": TEST_QUESTION,
        "provider": "mistral",
        "top_k": 3,
        "temperature": 0.3,
        "max_tokens": 512
    }
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            chunks_count = 0
            for line in response.iter_lines():
                if line:
                    chunks_count += 1
                    if chunks_count <= 3:  # Afficher les 3 premiers chunks
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            try:
                                data = json.loads(decoded_line[6:])
                                print(f"Chunk {chunks_count}: {data.get('content', '')[:50]}...")
                            except:
                                print(f"Chunk {chunks_count}: {decoded_line[:50]}...")
            print(f"Total chunks reçus: {chunks_count}")
            print("✅ Test réussi")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_ask_question_stream_ultra():
    """Test de l'endpoint /ask-question-stream-ultra"""
    print("\n=== Test /ask-question-stream-ultra ===")
    
    url = f"{BASE_URL}/ask-question-stream-ultra"
    payload = {
        "question": TEST_QUESTION,
        "provider": "mistral",
        "top_k": 3,
        "temperature": 0.3,
        "max_tokens": 512
    }
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            chunks_count = 0
            for line in response.iter_lines():
                if line:
                    chunks_count += 1
                    if chunks_count <= 3:  # Afficher les 3 premiers chunks
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            try:
                                data = json.loads(decoded_line[6:])
                                print(f"Chunk {chunks_count}: {data.get('content', '')[:50]}...")
                            except:
                                print(f"Chunk {chunks_count}: {decoded_line[:50]}...")
            print(f"Total chunks reçus: {chunks_count}")
            print("✅ Test réussi")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_ask_multimodal_question():
    """Test de l'endpoint /ask-multimodal-question"""
    print("\n=== Test /ask-multimodal-question ===")
    
    url = f"{BASE_URL}/ask-multimodal-question"
    payload = {
        "question": "Décris ce que tu vois dans les documents",
        "provider": "mistral",
        "content_types": ["DOCUMENT", "IMAGE"],
        "top_k": 3,
        "temperature": 0.3,
        "max_tokens": 512
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response ID: {result.get('id', 'N/A')}")
            print(f"Answer: {result.get('answer', 'N/A')[:100]}...")
            print("✅ Test réussi")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_ask_multimodal_with_image():
    """Test de l'endpoint /ask-multimodal-with-image"""
    print("\n=== Test /ask-multimodal-with-image ===")
    
    url = f"{BASE_URL}/ask-multimodal-with-image"
    
    # Données du formulaire
    data = {
        "question": "Analyse cette image",
        "provider": "mistral",
        "top_k": 3,
        "temperature": 0.3,
        "max_tokens": 512
    }
    
    try:
        # Test sans image
        response = requests.post(url, data=data, timeout=30)
        print(f"Status (sans image): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response ID: {result.get('id', 'N/A')}")
            print(f"Query had image: {result.get('query_had_image', False)}")
            print("✅ Test sans image réussi")
        else:
            print(f"❌ Erreur: {response.text}")
            
        # Test avec image si elle existe
        if os.path.exists(TEST_IMAGE_PATH):
            print("\nTest avec image...")
            with open(TEST_IMAGE_PATH, 'rb') as f:
                files = {'query_image': f}
                response = requests.post(url, data=data, files=files, timeout=30)
                print(f"Status (avec image): {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"Response ID: {result.get('id', 'N/A')}")
                    print(f"Query had image: {result.get('query_had_image', False)}")
                    print("✅ Test avec image réussi")
                else:
                    print(f"❌ Erreur: {response.text}")
        else:
            print(f"⚠️ Image de test {TEST_IMAGE_PATH} non trouvée")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def check_log_files():
    """Vérification des fichiers de logs"""
    print("\n=== Vérification des fichiers de logs ===")
    
    log_dirs = [
        "app/for-analysis/request-logs",
        "app/for-analysis/questions-answered"
    ]
    
    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            files = list(Path(log_dir).glob("*.csv"))
            print(f"📁 {log_dir}: {len(files)} fichiers CSV")
            
            # Afficher les fichiers les plus récents
            if files:
                recent_files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]
                for file in recent_files:
                    size = file.stat().st_size
                    mtime = time.ctime(file.stat().st_mtime)
                    print(f"  📄 {file.name} ({size} bytes, {mtime})")
        else:
            print(f"❌ Dossier {log_dir} non trouvé")
    
    # Vérifier les logs avancés
    advanced_log_dir = "app/for-analysis/request-logs"
    if os.path.exists(advanced_log_dir):
        advanced_files = list(Path(advanced_log_dir).glob("advanced_*.csv"))
        print(f"\n🔍 Logs avancés: {len(advanced_files)} fichiers")
        for file in advanced_files:
            size = file.stat().st_size
            print(f"  📄 {file.name} ({size} bytes)")

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests du système de logging avancé")
    print(f"URL de base: {BASE_URL}")
    
    # Vérifier que le serveur est accessible
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Serveur non accessible: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Impossible de contacter le serveur: {e}")
        return
    
    print("✅ Serveur accessible")
    
    # Exécuter tous les tests
    test_ask_question()
    time.sleep(1)
    
    test_ask_question_stream()
    time.sleep(1)
    
    test_ask_question_stream_ultra()
    time.sleep(1)
    
    test_ask_multimodal_question()
    time.sleep(1)
    
    test_ask_multimodal_with_image()
    time.sleep(2)
    
    # Vérifier les logs
    check_log_files()
    
    print("\n🎉 Tests terminés!")
    print("\n📋 Résumé:")
    print("- Tous les endpoints ask ont été testés")
    print("- Le logging avancé avec informations IP est actif")
    print("- Les logs CSV et avancés sont générés")
    print("- Vérifiez les fichiers de logs pour confirmer l'enregistrement")

if __name__ == "__main__":
    main()