#!/usr/bin/env python3
"""
Script de mesure pour le chapitre 4 du mémoire.
Envoie des scénarios de test à /ask-question-ultra et résume les latences.
Prérequis : API locale sur http://localhost:8000
"""
import requests
import time
from statistics import mean

BASE = "http://localhost:8000"
scenarios = [
    ("Bonjour", "predefined"),
    ("quel est l'âge de la retraite", "predefined"),
    ("numéro de téléphone css", "predefined"),
    ("Qu'est-ce que l'IPRES et comment est-elle organisée ?", "rag"),
    ("Comment créer un compte sur la plateforme CSS-IPRES ?", "rag"),
    ("Quelle est la capitale du Sénégal ?", "no_context"),
]


def main():
    print("=== TESTS FONCTIONNELS ===")
    results = []
    for q, typ in scenarios:
        payload = {
            "question": q,
            "provider": "mistral",
            "top_k": 3,
            "temperature": 0.3,
            "max_tokens": 512,
        }
        t0 = time.perf_counter()
        try:
            r = requests.post(f"{BASE}/ask-question-ultra", json=payload, timeout=120)
            elapsed = round((time.perf_counter() - t0) * 1000, 1)
            if r.status_code == 200:
                d = r.json()
                row = {
                    "question": q,
                    "type": typ,
                    "provider": d.get("provider_used"),
                    "context_found": d.get("context_found"),
                    "response_time_ms": d.get("response_time_ms"),
                    "client_ms": elapsed,
                    "search_results": d.get("search_results"),
                    "ranked_results": d.get("ranked_results"),
                    "answer_len": len(d.get("answer", "")),
                    "id": d.get("id"),
                }
                results.append(row)
                print(
                    f"OK | {typ:12} | srv={row['response_time_ms']} ms | "
                    f"provider={row['provider']} | ctx={row['context_found']} | {q[:50]}"
                )
            else:
                print(f"ERR {r.status_code} | {q[:50]}")
        except Exception as e:
            print(f"EXC | {q[:50]} | {e}")

    if results:
        rid = results[0]["id"]
        sr = requests.post(
            f"{BASE}/record-satisfaction",
            json={"response_id": rid, "is_satisfied": True},
            timeout=10,
        )
        print(f"SATISFACTION | status={sr.status_code}")

    print("\n=== RESUME PERF ===")
    for typ in ["predefined", "rag", "no_context"]:
        subset = [
            x["response_time_ms"]
            for x in results
            if x["type"] == typ and x.get("response_time_ms")
        ]
        if subset:
            print(
                f"{typ}: min={min(subset):.1f} max={max(subset):.1f} "
                f"avg={mean(subset):.1f} ms (n={len(subset)})"
            )

    hr = requests.get(f"{BASE}/health", timeout=5)
    print(f"HEALTH | {hr.status_code}")


if __name__ == "__main__":
    main()
