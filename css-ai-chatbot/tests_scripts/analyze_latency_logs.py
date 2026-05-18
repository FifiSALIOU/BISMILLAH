#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse des logs CSV de l'API pour mesurer la latence des endpoints chat:
- responses_ask_question_ultra.csv (non-stream)
- responses_ask_question_stream_ultra.csv (stream)

Produit des agrégats (moyenne, médiane p50, p90, p95) par type (prédéfini vs normal).
"""

import csv
import os
from statistics import mean, median


STREAM_CSV = os.path.join('app', 'for-analysis', 'questions-answered', 'responses_ask_question_stream_ultra.csv')
JSON_CSV = os.path.join('app', 'for-analysis', 'questions-answered', 'responses_ask_question_ultra.csv')


def percentile(sorted_values, p):
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return sorted_values[int(k)]
    d0 = sorted_values[f] * (c - k)
    d1 = sorted_values[c] * (k - f)
    return d0 + d1


def safe_float(value):
    try:
        if value is None:
            return None
        s = str(value).strip()
        if not s:
            return None
        return float(s)
    except Exception:
        return None


def analyze_stream_csv(path=STREAM_CSV):
    if not os.path.exists(path):
        print(f"❌ Fichier manquant: {path}")
        return None
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    # Filtrer erreurs
    ok_rows = [r for r in rows if not r.get('error_message')]
    predefined = [r for r in ok_rows if (r.get('model_used') == 'predefined_qa')]
    normal = [r for r in ok_rows if (r.get('model_used') != 'predefined_qa')]

    def extract(vals, key):
        arr = [safe_float(v.get(key)) for v in vals]
        arr = [x for x in arr if x is not None]
        return sorted(arr)

    stats = {}
    for label, subset in [('stream_predefined', predefined), ('stream_normal', normal), ('stream_all', ok_rows)]:
        pt = extract(subset, 'processing_time_ms')
        sd = extract(subset, 'stream_duration_ms')
        stats[label] = {
            'count': len(subset),
            'processing_time_ms': {
                'avg': mean(pt) if pt else 0.0,
                'p50': median(pt) if pt else 0.0,
                'p90': percentile(pt, 90) if pt else 0.0,
                'p95': percentile(pt, 95) if pt else 0.0,
            },
            'stream_duration_ms': {
                'avg': mean(sd) if sd else 0.0,
                'p50': median(sd) if sd else 0.0,
                'p90': percentile(sd, 90) if sd else 0.0,
                'p95': percentile(sd, 95) if sd else 0.0,
            }
        }
    return stats


def analyze_json_csv(path=JSON_CSV):
    if not os.path.exists(path):
        print(f"❌ Fichier manquant: {path}")
        return None
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    ok_rows = [r for r in rows if not r.get('error_message')]
    predefined = [r for r in ok_rows if (r.get('model_used') == 'predefined_qa')]
    normal = [r for r in ok_rows if (r.get('model_used') != 'predefined_qa')]

    def extract(vals, key):
        arr = [safe_float(v.get(key)) for v in vals]
        arr = [x for x in arr if x is not None]
        return sorted(arr)

    stats = {}
    for label, subset in [('json_predefined', predefined), ('json_normal', normal), ('json_all', ok_rows)]:
        pt = extract(subset, 'processing_time_ms')
        stats[label] = {
            'count': len(subset),
            'processing_time_ms': {
                'avg': mean(pt) if pt else 0.0,
                'p50': median(pt) if pt else 0.0,
                'p90': percentile(pt, 90) if pt else 0.0,
                'p95': percentile(pt, 95) if pt else 0.0,
            },
        }
    return stats


def print_stats(title, stats, keys):
    print(f"\n=== {title} ===")
    for key in keys:
        if key not in stats:
            continue
        s = stats[key]
        print(f"{key}: count={s['count']}")
        if 'processing_time_ms' in s:
            pm = s['processing_time_ms']
            print(
                f"  processing_time_ms: avg={pm['avg']:.1f}ms, p50={pm['p50']:.1f}ms, p90={pm['p90']:.1f}ms, p95={pm['p95']:.1f}ms"
            )
        if 'stream_duration_ms' in s:
            sd = s['stream_duration_ms']
            print(
                f"  stream_duration_ms:   avg={sd['avg']:.1f}ms, p50={sd['p50']:.1f}ms, p90={sd['p90']:.1f}ms, p95={sd['p95']:.1f}ms"
            )


def main():
    print("🚀 Analyse des latences via CSV")
    stream_stats = analyze_stream_csv()
    json_stats = analyze_json_csv()
    if stream_stats:
        print_stats("Streaming /ask-question-stream-ultra", stream_stats, [
            'stream_predefined', 'stream_normal', 'stream_all'
        ])
    if json_stats:
        print_stats("Non-stream /ask-question-ultra", json_stats, [
            'json_predefined', 'json_normal', 'json_all'
        ])
    print("\n✅ Analyse terminée")


if __name__ == '__main__':
    main()