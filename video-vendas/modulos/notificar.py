"""Notificação no celular via ntfy (https://ntfy.sh). Nunca derruba o programa."""
import json
import urllib.request


def enviar(config, titulo, mensagem, prioridade=3, tags=""):
    topico = config.get("notificacao", "ntfy_topico", fallback="").strip()
    if not topico or topico.startswith("TROQUE"):
        print("  (aviso) Notificação desligada: defina ntfy_topico no config.ini")
        return False
    corpo = {"topic": topico, "title": titulo, "message": mensagem, "priority": prioridade}
    if tags:
        corpo["tags"] = [tags]
    try:
        req = urllib.request.Request(
            "https://ntfy.sh",
            data=json.dumps(corpo).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=15).read()
        return True
    except Exception as e:  # rede fora, etc.
        print(f"  (aviso) Não consegui enviar a notificação: {e}")
        return False
