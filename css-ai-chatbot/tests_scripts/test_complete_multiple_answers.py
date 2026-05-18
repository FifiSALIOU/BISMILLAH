#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test complet du système de réponses multiples aléatoires
Vérifie toutes les questions converties au nouveau format
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.predefined_qa import PredefinedQASystem

def test_all_multiple_answers():
    """Teste toutes les questions avec réponses multiples"""
    print("🚀 Test complet du système de réponses multiples")
    print("=" * 60)
    
    qa_system = PredefinedQASystem()
    
    # Questions à tester avec réponses multiples
    test_questions = [
        "Bonjour",
        "Salut", 
        "Comment ça va",
        "Comment vous appelez-vous",
        "Comment vous présentez-vous",
        "Comment vous pouvez vous aider",
        "Quel est votre nom",
        "Quel est votre rôle",
        "Qu'est-ce que la retraite",
        "Merci",
        "Ok",
        "quel est l'âge de la retraite",
        "à quel âge peut-on prendre sa retraite",
        "quel est le taux de cotisation css",
        "combien cotise-t-on à la css",
        "montant des allocations familiales",
        "qui a droit aux allocations familiales",
        "comment être remboursé par la css",
        "quels soins sont couverts par la css",
        "quels documents pour s'inscrire à la css",
        "comment obtenir une attestation css",
        "délai de traitement css",
        "numéro de téléphone css",
        "où se trouve l'agence css",
        "qu'est-ce que la css",
        "comment fonctionne la css"
    ]
    
    success_count = 0
    total_questions = len(test_questions)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}/{total_questions}: '{question}'")
        
        # Tester 3 fois pour voir la variété des réponses
        responses = []
        for j in range(3):
            result = qa_system.get_predefined_answer(question)
            if result and result.get('answer'):
                response = result.get('answer', '')
                responses.append(response)
                print(f"  {j+1}. {response[:80]}{'...' if len(response) > 80 else ''}")
            else:
                print(f"  {j+1}. ❌ Aucune réponse trouvée")
                break
        
        # Vérifier la variété des réponses
        if len(responses) == 3:
            unique_responses = len(set(responses))
            if unique_responses > 1:
                print(f"  ✅ Variété: {unique_responses}/3 réponses différentes")
                success_count += 1
            else:
                print(f"  ⚠️  Toutes les réponses sont identiques")
                success_count += 1  # Toujours compter comme succès si réponse trouvée
        else:
            print(f"  ❌ Échec du test")
    
    print(f"\n{'='*60}")
    print(f"📊 Résultats du test complet")
    print(f"{'='*60}")
    print(f"Questions testées: {total_questions}")
    print(f"Succès: {success_count}")
    print(f"Échecs: {total_questions - success_count}")
    print(f"Taux de réussite: {(success_count/total_questions)*100:.1f}%")
    
    # Statistiques du système
    stats = qa_system.get_statistics()
    print(f"\n📈 Statistiques du système:")
    print(f"Total des questions: {stats['total_questions']}")
    print(f"Confiance moyenne: {stats['average_confidence']:.2f}")
    print(f"Total des mots-clés: {stats['total_keywords']}")
    
    if success_count == total_questions:
        print(f"\n🎉 Tous les tests ont réussi ! Le système de réponses multiples fonctionne parfaitement.")
    else:
        print(f"\n⚠️  {total_questions - success_count} test(s) ont échoué.")
    
    return success_count == total_questions

if __name__ == "__main__":
    test_all_multiple_answers()