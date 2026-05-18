#!/usr/bin/env python3
"""
Script pour vérifier l'état actuel de ENABLE_QUERY_ENHANCEMENT
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def check_query_enhancement_status():
    """Vérifie l'état de ENABLE_QUERY_ENHANCEMENT"""
    
    print("=" * 50)
    print("VÉRIFICATION DE L'ÉTAT DE QUERY ENHANCEMENT")
    print("=" * 50)
    
    # Vérifier la variable d'environnement brute
    raw_value = os.getenv('ENABLE_QUERY_ENHANCEMENT')
    print(f"Valeur brute de ENABLE_QUERY_ENHANCEMENT: '{raw_value}'")
    
    # Vérifier la conversion en booléen (comme dans config.py)
    bool_value = os.getenv("ENABLE_QUERY_ENHANCEMENT", "true").lower() == "true"
    print(f"Valeur booléenne: {bool_value}")
    
    # Vérifier si le fichier .env existe
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ Fichier {env_file} trouvé")
        
        # Lire le contenu du fichier .env
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Chercher la ligne ENABLE_QUERY_ENHANCEMENT
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'ENABLE_QUERY_ENHANCEMENT' in line and not line.strip().startswith('#'):
                print(f"Ligne {i} dans .env: {line.strip()}")
    else:
        print(f"❌ Fichier {env_file} non trouvé")
    
    # Vérifier le fichier .env.exemple
    env_example = ".env.exemple"
    if os.path.exists(env_example):
        print(f"✅ Fichier {env_example} trouvé")
        
        with open(env_example, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'ENABLE_QUERY_ENHANCEMENT' in line and not line.strip().startswith('#'):
                print(f"Ligne {i} dans .env.exemple: {line.strip()}")
    
    print("\n" + "=" * 50)
    print("RECOMMANDATIONS:")
    print("=" * 50)
    
    if bool_value:
        print("❌ ENABLE_QUERY_ENHANCEMENT est actuellement ACTIVÉ")
        print("📝 Pour le désactiver:")
        print("   1. Vérifiez que .env contient: ENABLE_QUERY_ENHANCEMENT=false")
        print("   2. Redémarrez complètement le serveur uvicorn")
        print("   3. Vérifiez qu'aucune autre variable d'environnement ne surcharge cette valeur")
    else:
        print("✅ ENABLE_QUERY_ENHANCEMENT est actuellement DÉSACTIVÉ")
        print("🔄 Si vous voyez encore 2 appels OpenAI, redémarrez le serveur")
    
    print("\n🔄 Commande pour redémarrer:")
    print("   Ctrl+C puis: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    check_query_enhancement_status()