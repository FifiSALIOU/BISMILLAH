#!/usr/bin/env python3

import requests
import json

def test_no_source_citations():
    """Test pour vérifier que les citations de sources n'apparaissent plus"""
    
    url = "http://localhost:8000/ask-question-ultra"
    
    # Question de test
    question_data = {
        "question": "Comment créer un compte sur la plateforme CSS-IPRES ?",
        "provider": "openai",
        "top_k": 3,
        "temperature": 0.3,
        "max_tokens": 512
    }
    
    try:
        print("=== Test: Question sans citations de sources ===")
        print(f"Question: {question_data['question']}")
        print("\n=== Envoi de la requête ===")
        
        response = requests.post(url, json=question_data)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            
            print("\n=== RÉPONSE ===")
            print(answer)
            
            # Vérifier s'il y a des citations de sources
            has_source_citations = any([
                'Source 1' in answer,
                'Source 2' in answer, 
                'Source 3' in answer,
                '(Source' in answer
            ])
            
            print("\n=== ANALYSE ===")
            if has_source_citations:
                print("❌ ÉCHEC: La réponse contient encore des citations de sources")
                # Identifier les citations trouvées
                citations_found = []
                if 'Source 1' in answer:
                    citations_found.append('Source 1')
                if 'Source 2' in answer:
                    citations_found.append('Source 2')
                if 'Source 3' in answer:
                    citations_found.append('Source 3')
                if '(Source' in answer:
                    citations_found.append('(Source...)')
                print(f"Citations trouvées: {', '.join(citations_found)}")
            else:
                print("✅ SUCCÈS: Aucune citation de source trouvée dans la réponse")
                
            print(f"\nLongueur de la réponse: {len(answer)} caractères")
            print(f"Nombre de sources utilisées: {len(result.get('sources', []))}")
            
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
    test_no_source_citations()