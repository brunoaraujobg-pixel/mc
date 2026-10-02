"""Registra cada operação em log.csv (data, produto, etapa, resultado)."""
import csv
from datetime import datetime
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parent.parent / "log.csv"


def registrar(produto, etapa, resultado):
    novo = not ARQUIVO.exists()
    with open(ARQUIVO, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        if novo:
            w.writerow(["data", "produto", "etapa", "resultado"])
        w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), produto, etapa, resultado])
