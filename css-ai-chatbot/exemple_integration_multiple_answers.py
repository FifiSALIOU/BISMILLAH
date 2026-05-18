#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemple d'intégration du système de réponses multiples dans l'API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.predefined_qa import PredefinedQASystem
import json

def simulate_api_responses():
    """Simule des réponses API avec le système de réponses multiples"""
    print("=== Simulation d'intégration API avec réponses multiples ===")
    print()
    
    qa_system = PredefinedQASystem()
    
    # Simulation de requêtes utilisateur
    user_queries = [
        "Bonjour",
        "Comment ça va ?",
        "Comment vous appelez-vous ?",
        "Qu'est-ce que la retraite ?",  # Cette question a une seule réponse
        "Salut",
        "Comment vous présentez-vous ?"
    ]
    
    print("🔄 Simulation de plusieurs sessions utilisateur:")
    print()
    
    for session in range(1, 4):  # 3 sessions différentes
        print(f"📱 === SESSION {session} ===")
        
        for query in user_queries:
            result = qa_system.get_predefined_answer(query)
            
            if result:
                # Format de réponse API
                api_response = {
                    "status": "success",
                    "query": query,
                    "response": {
                        "answer": result["answer"],
                        "confidence": result["confidence"],
                        "source": result["source"],
                        "matched_question": result["matched_question"],
                        "total_variants": result.get("total_answers_available", 1),
                        "is_random_selection": result.get("total_answers_available", 1) > 1
                    },
                    "metadata": {
                        "processing_time": "0.001s",
                        "cache_hit": True,
                        "llm_call_avoided": True
                    }
                }
                
                print(f"❓ Q: {query}")
                print(f"💬 R: {result['answer']}")
                if result.get('total_answers_available', 1) > 1:
                    print(f"   🎲 (Sélection aléatoire parmi {result['total_answers_available']} variantes)")
                print()
            else:
                print(f"❓ Q: {query}")
                print(f"❌ R: Aucune réponse prédéfinie trouvée")
                print()
        
        print("-" * 50)
        print()

def demonstrate_configuration():
    """Démontre comment configurer le système avec de nouvelles réponses multiples"""
    print("\n=== Configuration de nouvelles réponses multiples ===")
    print()
    
    qa_system = PredefinedQASystem()
    
    # Ajouter des questions avec réponses multiples pour différents contextes
    configurations = [
        {
            "question": "Quel est le délai de traitement",
            "answers": [
                "Les délais de traitement varient selon le type de dossier : remboursements maladie (15-30 jours), prestations familiales (7-15 jours).",
                "Le traitement de votre dossier prend généralement entre 7 et 30 jours selon la complexité.",
                "Nos délais standards sont de 15-30 jours pour les remboursements et 7-15 jours pour les allocations.",
                "Comptez environ 2 à 4 semaines pour le traitement de votre demande, selon le service concerné."
            ],
            "keywords": ["délai", "traitement", "temps", "combien"],
            "confidence": 0.85
        },
        {
            "question": "Comment contacter la CSS",
            "answers": [
                "Vous pouvez nous contacter par téléphone, email, ou en vous rendant dans nos agences régionales.",
                "Plusieurs moyens s'offrent à vous : numéro vert, site web, ou visite en agence.",
                "Contactez-nous via notre numéro gratuit, notre site internet, ou rendez-vous dans l'agence la plus proche.",
                "Nous sommes joignables par téléphone, en ligne, ou directement dans nos bureaux régionaux."
            ],
            "keywords": ["contacter", "contact", "téléphone", "agence"],
            "confidence": 0.9
        }
    ]
    
    # Ajouter les configurations
    for config in configurations:
        qa_system.add_qa_pair(
            question=config["question"],
            answer=config["answers"],
            keywords=config["keywords"],
            confidence=config["confidence"]
        )
        print(f"✅ Ajouté: '{config['question']}' avec {len(config['answers'])} variantes")
    
    print("\n🧪 Test des nouvelles configurations:")
    print()
    
    test_queries = [
        "Quel est le délai de traitement ?",
        "Comment puis-je contacter la CSS ?"
    ]
    
    for query in test_queries:
        print(f"❓ Question: {query}")
        for i in range(3):
            result = qa_system.get_predefined_answer(query)
            if result:
                print(f"  {i+1}. {result['answer']}")
        print()

def show_benefits():
    """Montre les avantages du système de réponses multiples"""
    print("\n=== Avantages du système de réponses multiples ===")
    print()
    
    benefits = [
        "🎯 **Variété conversationnelle**: Évite la répétition robotique",
        "👥 **Expérience utilisateur améliorée**: Conversations plus naturelles",
        "⚡ **Performance optimisée**: Pas d'appels LLM pour les questions fréquentes",
        "🔧 **Flexibilité**: Facile d'ajouter de nouvelles variantes",
        "📊 **Contrôle qualité**: Réponses pré-validées et cohérentes",
        "🎲 **Randomisation intelligente**: Sélection aléatoire mais contrôlée",
        "🔄 **Rétrocompatibilité**: Fonctionne avec l'ancien format",
        "📈 **Évolutivité**: Système extensible facilement"
    ]
    
    for benefit in benefits:
        print(benefit)
    
    print("\n💡 **Cas d'usage recommandés:**")
    use_cases = [
        "• Salutations et politesse (Bonjour, Au revoir, Merci)",
        "• Questions fréquentes avec formulations similaires",
        "• Réponses d'information générale",
        "• Messages d'aide et de guidance",
        "• Confirmations et accusés de réception"
    ]
    
    for use_case in use_cases:
        print(use_case)

if __name__ == "__main__":
    simulate_api_responses()
    demonstrate_configuration()
    show_benefits()
    
    print("\n" + "=" * 60)
    print("🎉 Démonstration terminée avec succès !")
    print("Le système de réponses multiples est prêt à être utilisé.")
    print("=" * 60)