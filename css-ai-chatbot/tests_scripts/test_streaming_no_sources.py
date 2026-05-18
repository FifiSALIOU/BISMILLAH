import requests
import json
import re

def test_streaming_no_sources():
    """Test que l'endpoint de streaming ne retourne pas de citations de sources"""
    
    url = "http://localhost:8000/ask-question-stream-ultra"
    
    payload = {
        "question": "Qu'est-ce que l'IPRES et comment est-elle organisée ?",
        "provider": "openai",
        "top_k": 5
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Envoi de la requête à {url}")
    print(f"Question: {payload['question']}")
    print("\n" + "="*50)
    
    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            full_response = ""
            chunks = []
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                            if data.get('type') == 'chunk' and 'content' in data:
                                chunk_content = data['content']
                                chunks.append(chunk_content)
                                full_response += chunk_content
                                print(chunk_content, end='', flush=True)
                        except json.JSONDecodeError:
                            continue
            
            print("\n" + "="*50)
            print("\nAnalyse de la réponse:")
            
            # Vérifier l'absence de citations
            source_patterns = [
                r'Source \d+',
                r'\(Source \d+\)',
                r'source \d+',
                r'\(source \d+\)'
            ]
            
            citations_found = []
            for pattern in source_patterns:
                matches = re.findall(pattern, full_response, re.IGNORECASE)
                citations_found.extend(matches)
            
            if citations_found:
                print(f"❌ ÉCHEC: Citations trouvées: {citations_found}")
                return False
            else:
                print("✅ SUCCÈS: Aucune citation de source trouvée")
                print(f"Nombre de chunks reçus: {len(chunks)}")
                print(f"Longueur de la réponse: {len(full_response)} caractères")
                return True
                
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la requête: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_streaming_no_sources()
    if success:
        print("\n🎉 Test réussi: L'endpoint de streaming ne génère plus de citations!")
    else:
        print("\n💥 Test échoué: Des citations sont encore présentes.")