#!/usr/bin/env python3
"""
Script de test pour vérifier l'activation/désactivation des enhanced_queries
Permet de mesurer l'impact sur les performances
"""

import asyncio
import time
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.rag_service import UltraPerformantRAG
from app.models.enums import Provider
from app.core.config import settings


async def test_query_with_enhancement():
    """Test avec enhancement activé"""
    print("\n=== TEST AVEC QUERY ENHANCEMENT ACTIVÉ ===")
    print(f"ENABLE_QUERY_ENHANCEMENT = {settings.ENABLE_QUERY_ENHANCEMENT}")
    
    rag_system = UltraPerformantRAG()
    test_question = "Comment centrer un div en CSS ?"
    
    start_time = time.time()
    
    try:
        response = await rag_system.query(
            question=test_question,
            provider=Provider.DEEPSEEK,
            top_k=3
        )
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)
        
        print(f"✅ Réponse reçue en {response_time}ms")
        print(f"Enhanced queries utilisées: {response.get('enhanced_queries', [])}")
        print(f"Nombre de requêtes: {len(response.get('enhanced_queries', []))}")
        print(f"Provider utilisé: {response.get('provider_used')}")
        print(f"Temps de réponse API: {response.get('response_time_ms')}ms")
        
        return response_time, len(response.get('enhanced_queries', []))
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None, 0


async def test_query_without_enhancement():
    """Test avec enhancement désactivé"""
    print("\n=== TEST AVEC QUERY ENHANCEMENT DÉSACTIVÉ ===")
    
    # Temporairement désactiver l'enhancement
    original_setting = settings.ENABLE_QUERY_ENHANCEMENT
    settings.ENABLE_QUERY_ENHANCEMENT = False
    print(f"ENABLE_QUERY_ENHANCEMENT = {settings.ENABLE_QUERY_ENHANCEMENT}")
    
    rag_system = UltraPerformantRAG()
    test_question = "Comment centrer un div en CSS ?"
    
    start_time = time.time()
    
    try:
        response = await rag_system.query(
            question=test_question,
            provider=Provider.DEEPSEEK,
            top_k=3
        )
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)
        
        print(f"✅ Réponse reçue en {response_time}ms")
        print(f"Enhanced queries utilisées: {response.get('enhanced_queries', [])}")
        print(f"Nombre de requêtes: {len(response.get('enhanced_queries', []))}")
        print(f"Provider utilisé: {response.get('provider_used')}")
        print(f"Temps de réponse API: {response.get('response_time_ms')}ms")
        
        # Restaurer le paramètre original
        settings.ENABLE_QUERY_ENHANCEMENT = original_setting
        
        return response_time, len(response.get('enhanced_queries', []))
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        # Restaurer le paramètre original même en cas d'erreur
        settings.ENABLE_QUERY_ENHANCEMENT = original_setting
        return None, 0


async def performance_comparison():
    """Compare les performances avec et sans enhancement"""
    print("\n" + "="*60)
    print("🚀 COMPARAISON DES PERFORMANCES")
    print("="*60)
    
    # Test avec enhancement
    time_with, queries_with = await test_query_with_enhancement()
    
    # Attendre un peu entre les tests
    await asyncio.sleep(2)
    
    # Test sans enhancement
    time_without, queries_without = await test_query_without_enhancement()
    
    # Analyse des résultats
    print("\n" + "="*60)
    print("📊 ANALYSE DES RÉSULTATS")
    print("="*60)
    
    if time_with and time_without:
        difference = time_with - time_without
        percentage = round((difference / time_without) * 100, 1)
        
        print(f"Temps avec enhancement:    {time_with}ms ({queries_with} requêtes)")
        print(f"Temps sans enhancement:    {time_without}ms ({queries_without} requête)")
        print(f"Différence:                {difference:+.1f}ms ({percentage:+.1f}%)")
        
        if difference > 0:
            print(f"\n💡 L'enhancement ajoute {difference:.1f}ms au temps de réponse")
            print(f"   Cela représente {percentage:.1f}% de temps supplémentaire")
        else:
            print(f"\n🎉 L'enhancement améliore les performances de {abs(difference):.1f}ms")
            
        # Recommandations
        print("\n🔧 RECOMMANDATIONS:")
        if percentage > 50:
            print("   - L'enhancement a un impact significatif sur les performances")
            print("   - Considérez désactiver avec ENABLE_QUERY_ENHANCEMENT=false")
        elif percentage > 20:
            print("   - L'enhancement a un impact modéré sur les performances")
            print("   - Évaluez le compromis qualité/vitesse selon vos besoins")
        else:
            print("   - L'impact sur les performances est acceptable")
            print("   - L'enhancement peut être maintenu activé")
    else:
        print("❌ Impossible de comparer - erreurs lors des tests")


async def main():
    """Fonction principale"""
    print("🧪 TEST DE LA FONCTIONNALITÉ QUERY ENHANCEMENT")
    print(f"Configuration actuelle: ENABLE_QUERY_ENHANCEMENT = {settings.ENABLE_QUERY_ENHANCEMENT}")
    
    await performance_comparison()
    
    print("\n" + "="*60)
    print("✅ Tests terminés")
    print("\n💡 Pour désactiver l'enhancement, ajoutez dans votre .env:")
    print("   ENABLE_QUERY_ENHANCEMENT=false")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())