#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour le système de réponses multiples aléatoires
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.predefined_qa import PredefinedQASystem

def test_multiple_answers():
    """Test le système de réponses multiples"""
    print("=== Test du système de réponses multiples aléatoires ===")
    print()
    
    # Initialiser le système
    qa_system = PredefinedQASystem()
    
    # Questions à tester (celles qui ont plusieurs réponses)
    test_questions = [
        "Bonjour",
        "Salut",
        "Comment ça va",
        "Comment vous appelez-vous",
        "Comment vous présentez-vous"
    ]
    
    # Tester chaque question plusieurs fois pour voir la variété des réponses
    for question in test_questions:
        print(f"\n🔍 Question: '{question}'")
        print("-" * 50)
        
        # Poser la même question 5 fois pour voir les différentes réponses
        responses_seen = set()
        for i in range(5):
            result = qa_system.get_predefined_answer(question)
            if result:
                answer = result['answer']
                responses_seen.add(answer)
                total_available = result.get('total_answers_available', 1)
                print(f"  {i+1}. {answer}")
                if i == 0:  # Afficher les infos seulement la première fois
                    print(f"     📊 Réponses disponibles: {total_available}")
                    print(f"     🎯 Confiance: {result['confidence']}")
            else:
                print(f"  {i+1}. Aucune réponse trouvée")
        
        print(f"\n📈 Variété observée: {len(responses_seen)} réponses différentes sur 5 essais")
    
    print("\n" + "=" * 60)
    print("🧪 Test d'ajout de nouvelles Q&A avec réponses multiples")
    print("=" * 60)
    
    # Test d'ajout avec réponses multiples
    qa_system.add_qa_pair(
        question="Comment allez-vous",
        answer=[
            "Je vais très bien, merci !",
            "Parfaitement bien, et vous ?",
            "Ça va super bien !",
            "Tout roule de mon côté !"
        ],
        keywords=["comment", "allez", "vous"],
        confidence=0.9
    )
    
    # Test d'ajout avec réponse unique (rétrocompatibilité)
    qa_system.add_qa_pair(
        question="Au revoir",
        answer="Au revoir ! À bientôt !",
        keywords=["au revoir", "bye"],
        confidence=0.95
    )
    
    # Tester les nouvelles questions
    print("\n🆕 Test des nouvelles questions ajoutées:")
    
    print("\n🔍 Question: 'Comment allez-vous' (réponses multiples)")
    for i in range(3):
        result = qa_system.get_predefined_answer("Comment allez-vous")
        if result:
            print(f"  {i+1}. {result['answer']}")
    
    print("\n🔍 Question: 'Au revoir' (réponse unique)")
    for i in range(3):
        result = qa_system.get_predefined_answer("Au revoir")
        if result:
            print(f"  {i+1}. {result['answer']}")
    
    # Statistiques finales
    print("\n" + "=" * 60)
    print("📊 Statistiques du système")
    print("=" * 60)
    stats = qa_system.get_statistics()
    print(f"Total des questions: {stats['total_questions']}")
    print(f"Confiance moyenne: {stats['average_confidence']:.2f}")
    print(f"Total des mots-clés: {stats['total_keywords']}")
    
    print("\n✅ Test terminé avec succès !")

if __name__ == "__main__":
    test_multiple_answers()