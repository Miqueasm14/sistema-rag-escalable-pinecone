"""Evaluación del recuperador híbrido con Precision@5 y Recall@5 sobre un Golden Set.

Uso: python evaluate.py
"""

import json

from config import TOP_K
from rag_system import RAGSystem

GOLDEN_SET_PATH = "golden_set.json"


def evaluar(rag: RAGSystem, golden_set: list[dict], k: int = TOP_K) -> dict:
    detalle = []
    for caso in golden_set:
        recuperados = [doc.metadata["source"] for doc in rag.buscar(caso["pregunta"])]
        esperado = caso["documento_id_esperado"]
        utiles = sum(1 for fuente in recuperados if fuente == esperado)

        detalle.append({
            "pregunta": caso["pregunta"],
            "esperado": esperado,
            "recuperados": recuperados,
            # Recall@k: ¿el documento correcto está entre los k recuperados? (1 o 0)
            "recall": 1.0 if esperado in recuperados else 0.0,
            # Precision@k: proporción de los k recuperados que vienen del documento correcto
            "precision": utiles / k,
        })

    return {
        "detalle": detalle,
        "recall_promedio": sum(d["recall"] for d in detalle) / len(detalle),
        "precision_promedio": sum(d["precision"] for d in detalle) / len(detalle),
    }


def imprimir_reporte(reporte: dict, k: int = TOP_K) -> None:
    print("=" * 80)
    for d in reporte["detalle"]:
        estado = "✅" if d["recall"] else "❌"
        print(f"{estado} {d['pregunta']}")
        print(f"   Esperado: {d['esperado']}")
        print(f"   Recuperados: {d['recuperados']}")
        print(f"   Recall@{k}: {d['recall']:.0%} | Precision@{k}: {d['precision']:.0%}\n")
    print("=" * 80)
    print(f"📊 RECALL@{k} PROMEDIO:    {reporte['recall_promedio']:.1%}")
    print(f"📊 PRECISION@{k} PROMEDIO: {reporte['precision_promedio']:.1%}")


if __name__ == "__main__":
    with open(GOLDEN_SET_PATH, encoding="utf-8") as f:
        golden_set = json.load(f)

    imprimir_reporte(evaluar(RAGSystem(), golden_set))
