#!/usr/bin/env python3

import requests
import json

def test_ipres_question():
    """Test avec la question sur l'IPRES pour vérifier les citations"""
    
    url = "http://localhost:8000/ask-question-ultra"
    
    # Question similaire à celle de l'utilisateur
    question_data = {
        "question": "Qu'est-ce que l'IPRES et comment est-elle organisée ?",
        "provider": "openai",
        "top_k": 5,
        "temperature": 0.3,
        "max_tokens": 800
    }
    
    try:
        print("=== Test: Question sur l'IPRES ===")
        print(f"Question: {question_data['question']}")
        print("\n=== Envoi de la requête ===")
        
        response = requests.post(url, json=question_data)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            
            print("\n=== RÉPONSE COMPLÈTE ===")
            print(answer)
            
            # Vérifier s'il y a des citations de sources
            source_patterns = [
                'Source 1', 'Source 2', 'Source 3', 'Source 4', 'Source 5',
                '(Source 1)', '(Source 2)', '(Source 3)', '(Source 4)', '(Source 5)',
                '[Source 1]', '[Source 2]', '[Source 3]', '[Source 4]', '[Source 5]'
            ]
            
            citations_found = []
            for pattern in source_patterns:
                if pattern in answer:
                    citations_found.append(pattern)
            
            print("\n=== ANALYSE DÉTAILLÉE ===")
            if citations_found:
                print("❌ PROBLÈME: Citations de sources trouvées:")
                for citation in citations_found:
                    print(f"  - {citation}")
                    # Montrer le contexte autour de chaque citation
                    index = answer.find(citation)
                    start = max(0, index - 50)
                    end = min(len(answer), index + len(citation) + 50)
                    context = answer[start:end].replace('\n', ' ')
                    print(f"    Contexte: ...{context}...")
            else:
                print("✅ SUCCÈS: Aucune citation de source trouvée")
                
            print(f"\nLongueur de la réponse: {len(answer)} caractères")
            print(f"Nombre de sources utilisées: {len(result.get('sources', []))}")
            print(f"Provider utilisé: {result.get('provider_used', 'N/A')}")
            print(f"Temps de réponse: {result.get('response_time_ms', 'N/A')} ms")
            
        else:
            print(f"❌ Erreur: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Détail: {error_detail}")
            except:
                print(f"Réponse brute: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ipres_question()