#!/usr/bin/env python3
"""
Tests de base pour le serveur en mode debug (Starlette).
- Vérifie /health
- Vérifie / (root)
- Vérifie /query avec plusieurs questions
"""

import requests
import time

BASE_URL = "http://localhost:8000"


def test_health():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"GET /health -> {r.status_code}")
        if r.status_code == 200:
            print("✅ Health OK")
            return True
        else:
            print(f"❌ Health NOK: {r.text}")
            return False
    except Exception as e:
        print(f"❌ Exception /health: {e}")
        return False


def test_root():
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"GET / -> {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Root: {data}")
            return True
        else:
            print(f"❌ Root NOK: {r.text}")
            return False
    except Exception as e:
        print(f"❌ Exception /: {e}")
        return False


def test_query():
    questions = [
        "Bonjour",
        "Comment puis-je m'inscrire?",
        "Quel est le montant des cotisations?",
    ]
    all_ok = True
    for q in questions:
        try:
            r = requests.post(
                f"{BASE_URL}/query",
                json={"question": q},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            print(f"POST /query -> {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"✅ Réponse: {data.get('response', '')}")
            else:
                print(f"❌ /query NOK: {r.text}")
                all_ok = False
        except Exception as e:
            print(f"❌ Exception /query: {e}")
            all_ok = False
        time.sleep(0.5)
    return all_ok


def main():
    print("🚀 Tests du serveur debug")
    ok = test_health() and test_root() and test_query()
    print("\n" + ("🎉 Tous les tests debug ont réussi" if ok else "💥 Certains tests debug ont échoué"))


if __name__ == "__main__":
    main()