#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de mesure de latence pour les endpoints de chat:
- /ask-question-stream-ultra (streaming)
- /ask-question-ultra (non-stream)

Mesure: temps au premier chunk, durée complète du stream, temps total JSON.
"""

import requests
import json
import time
from time import perf_counter

BASE_URL = "http://localhost:8000"


def wait_for_api(timeout_sec: int = 180, interval_sec: float = 2.0) -> bool:
    """Attend que l'API soit disponible sur /health."""
    deadline = time.time() + timeout_sec
    last_err = None
    while time.time() < deadline:
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=5)
            if r.status_code == 200:
                return True
        except Exception as e:
            last_err = e
        time.sleep(interval_sec)
    if last_err:
        print(f"❌ API non accessible: {last_err}")
    return False


def measure_stream_latency(question: str, provider: str = "mistral") -> dict:
    """Mesure la latence du streaming: premier chunk et fin du stream."""
    url = f"{BASE_URL}/ask-question-stream-ultra"
    payload = {
        "question": question,
        "provider": provider,
        "temperature": 0.3,
        "max_tokens": 512,
        "top_k": 3,
    }
    headers = {"Content-Type": "application/json", "accept": "text/plain"}

    t0 = perf_counter()
    try:
        resp = requests.post(url, json=payload, headers=headers, stream=True, timeout=60)
    except Exception as e:
        return {"ok": False, "error": str(e), "question": question}

    first_chunk_ms = None
    final_event_ms = None
    chunks = 0
    content_len = 0
    is_predefined = False

    for raw in resp.iter_lines(decode_unicode=True):
        if not raw or not raw.startswith("data: "):
            continue
        now = perf_counter()
        try:
            data = json.loads(raw[6:])
        except json.JSONDecodeError:
            continue

        typ = data.get("type")
        if typ == "init":
            meta = data.get("metadata", {})
            if meta.get("provider") == "predefined_qa":
                is_predefined = True
        elif typ == "chunk":
            chunks += 1
            content_len += len(data.get("content", ""))
            if first_chunk_ms is None:
                first_chunk_ms = (now - t0) * 1000
        elif typ in ("final", "error"):
            final_event_ms = (now - t0) * 1000
            break

    total_ms = (perf_counter() - t0) * 1000
    return {
        "ok": resp.status_code == 200,
        "status_code": resp.status_code,
        "question": question,
        "is_predefined": is_predefined,
        "first_chunk_ms": first_chunk_ms or 0.0,
        "full_stream_ms": final_event_ms or total_ms,
        "chunks": chunks,
        "content_len": content_len,
    }


def measure_json_latency(question: str, provider: str = "mistral") -> dict:
    """Mesure la latence de l'endpoint non-stream /ask-question-ultra."""
    url = f"{BASE_URL}/ask-question-ultra"
    payload = {
        "question": question,
        "provider": provider,
        "top_k": 3,
        "temperature": 0.3,
        "max_tokens": 512,
    }
    t0 = perf_counter()
    try:
        resp = requests.post(url, json=payload, timeout=60)
        elapsed_ms = (perf_counter() - t0) * 1000
    except Exception as e:
        return {"ok": False, "error": str(e), "question": question}

    body = {}
    try:
        body = resp.json()
    except Exception:
        pass

    return {
        "ok": resp.status_code == 200,
        "status_code": resp.status_code,
        "question": question,
        "elapsed_ms": round(elapsed_ms, 2),
        "response_time_ms": body.get("response_time_ms"),
        "context_found": body.get("context_found"),
        "provider_used": body.get("provider_used"),
        "model_used": body.get("model_used"),
    }


def main():
    print("🚀 Mesure de latence des endpoints de chat CSS AI")
    print("Vérification de l'API...")
    if not wait_for_api():
        print("❌ Impossible de contacter l'API. Assurez-vous qu'elle est démarrée.")
        return
    print("✅ API disponible")

    tests = [
        {"type": "stream", "question": "Bonjour"},
        {"type": "stream", "question": "Explique-moi la théorie de la relativité"},
        {"type": "json", "question": "Bonjour"},
        {"type": "json", "question": "Quelle est la capitale du Sénégal?"},
    ]

    results = []
    for t in tests:
        if t["type"] == "stream":
            print(f"\n🧪 Streaming: '{t['question']}'")
            r = measure_stream_latency(t["question"])
            print(
                f"Status={r['status_code']} | prédéfini={r['is_predefined']} | "
                f"first_chunk={r['first_chunk_ms']:.1f}ms | full_stream={r['full_stream_ms']:.1f}ms | chunks={r['chunks']}"
            )
            results.append(("stream", r))
        else:
            print(f"\n🧪 Non-stream: '{t['question']}'")
            r = measure_json_latency(t["question"]) 
            print(
                f"Status={r['status_code']} | ctx={r.get('context_found')} | "
                f"client_elapsed={r['elapsed_ms']:.1f}ms | server_reported={r.get('response_time_ms')}ms"
            )
            results.append(("json", r))

    print("\n📊 Résumé")
    # Calculs simples
    stream_pre = [r for k, r in results if k == "stream" and r.get("is_predefined")]
    stream_non = [r for k, r in results if k == "stream" and not r.get("is_predefined")]
    json_pre = [r for k, r in results if k == "json" and r.get("context_found")]
    json_nocontext = [r for k, r in results if k == "json" and r.get("context_found") is False]

    def avg(values):
        return sum(values) / len(values) if values else 0.0

    print(
        f"Streaming prédéfini: first_chunk_avg={avg([x['first_chunk_ms'] for x in stream_pre]):.1f}ms, "
        f"full_stream_avg={avg([x['full_stream_ms'] for x in stream_pre]):.1f}ms"
    )
    print(
        f"Streaming non-prédéfini: first_chunk_avg={avg([x['first_chunk_ms'] for x in stream_non]):.1f}ms, "
        f"full_stream_avg={avg([x['full_stream_ms'] for x in stream_non]):.1f}ms (nécessite clé API)"
    )
    print(
        f"Non-stream prédéfini: client_elapsed_avg={avg([x['elapsed_ms'] for x in json_pre]):.1f}ms, "
        f"server_reported_avg={avg([x.get('response_time_ms') or 0 for x in json_pre]):.1f}ms"
    )
    print(
        f"Non-stream sans contexte: client_elapsed_avg={avg([x['elapsed_ms'] for x in json_nocontext]):.1f}ms, "
        f"server_reported_avg={avg([x.get('response_time_ms') or 0 for x in json_nocontext]):.1f}ms"
    )


if __name__ == "__main__":
    main()