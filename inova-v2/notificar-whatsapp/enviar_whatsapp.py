"""
Envio de mensagem por WhatsApp (Inova v2), via WhatsApp Business Platform
(Cloud API) da Meta - a API oficial, nao uma automacao por fora do
WhatsApp Web (essas violam os termos de uso e arriscam banir o numero).

Isso exige configurar uma conta antes de funcionar - ver README.md desta
pasta. Sem essa configuracao, o script so avisa que falta credencial e
nao tenta enviar nada.
"""
import os
import re
import sys

import requests

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_API_VERSION = os.environ.get("WHATSAPP_API_VERSION", "v21.0")
DDI_PADRAO = "55"  # Brasil - usado quando o telefone cadastrado nao tem o codigo do pais


def normalizar_telefone(telefone, ddi_padrao=DDI_PADRAO):
    digitos = re.sub(r"\D", "", telefone or "")
    if digitos and not digitos.startswith(ddi_padrao) and len(digitos) <= 11:
        digitos = ddi_padrao + digitos
    return digitos


def _enviar(payload):
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print("WHATSAPP_TOKEN / WHATSAPP_PHONE_NUMBER_ID nao configurados - ver README.md.")
        return False
    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.RequestException as exc:
        print(f"Erro de rede enviando WhatsApp: {exc}")
        return False
    if resp.status_code >= 400:
        print(f"WhatsApp recusou o envio ({resp.status_code}): {resp.text}")
        return False
    print("Mensagem aceita pela API do WhatsApp.")
    return True


def enviar_teste(telefone):
    """Manda o template 'hello_world', que a Meta ja deixa pre-aprovado
    pra qualquer conta - serve so pra confirmar que token/phone_number_id
    estao certos, antes de criar um template proprio."""
    payload = {
        "messaging_product": "whatsapp",
        "to": telefone,
        "type": "template",
        "template": {"name": "hello_world", "language": {"code": "en_US"}},
    }
    return _enviar(payload)


def enviar_template(telefone, nome_template, parametros_corpo=None, idioma="pt_BR"):
    """Manda um template proprio, ja aprovado pela Meta (ver README.md -
    sem isso, nao tem como avisar alguem que nao te escreveu antes)."""
    template = {"name": nome_template, "language": {"code": idioma}}
    if parametros_corpo:
        template["components"] = [
            {
                "type": "body",
                "parameters": [{"type": "text", "text": str(p)} for p in parametros_corpo],
            }
        ]
    payload = {
        "messaging_product": "whatsapp",
        "to": telefone,
        "type": "template",
        "template": template,
    }
    return _enviar(payload)


def enviar_texto_livre(telefone, mensagem):
    """Texto livre - so entrega se esse telefone tiver escrito pra sua
    conta nas ultimas 24h, ou for um numero de teste cadastrado no painel
    da Meta. Pra alerta automatico (a empresa nao te escreveu antes),
    use enviar_template."""
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": telefone,
        "type": "text",
        "text": {"body": mensagem},
    }
    return _enviar(payload)


def main():
    if len(sys.argv) < 3:
        print("Uso:")
        print("  python enviar_whatsapp.py --teste <telefone>")
        print('  python enviar_whatsapp.py --texto <telefone> "mensagem"')
        print("  python enviar_whatsapp.py --template <telefone> <nome_template> [param1 param2 ...]")
        return

    comando = sys.argv[1]
    telefone = normalizar_telefone(sys.argv[2])

    if comando == "--teste":
        enviar_teste(telefone)
    elif comando == "--texto" and len(sys.argv) >= 4:
        enviar_texto_livre(telefone, sys.argv[3])
    elif comando == "--template" and len(sys.argv) >= 4:
        enviar_template(telefone, sys.argv[3], sys.argv[4:])
    else:
        print("Argumentos invalidos - rode sem argumentos pra ver o uso.")


if __name__ == "__main__":
    main()
