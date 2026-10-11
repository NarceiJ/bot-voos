from datetime import datetime, timezone, timedelta
import json
import os
import requests

# --- CONFIGURAÇÕES DE AMBIENTE ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# API do Google Flights no RapidAPI (Nikita Iakovlev)
RAPIDAPI_HOST = "google-flights-api.p.rapidapi.com"

# --- CONFIGURAÇÃO DA VIAGEM ---
ORIGEM = "GRU"          # Aeroporto de Origem (ex: Guarulhos)
DESTINO = "MCZ"         # Aeroporto de Destino (ex: Maceió)
DATA_IDA = "2027-01-01" # Data ajustada para 01/01/2027
PRECO_MAXIMO = 800.0    # Teto de preço máximo em Reais (R$)

ARQUIVO_HISTORICO = "historico_precos.json"

def enviar_telegram(mensagem):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Erro: Credenciais do Telegram não configuradas.")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        return False

def buscar_voo():
    if not RAPIDAPI_KEY:
        print("Erro: RAPIDAPI_KEY não configurada.")
        return None

    url = f"https://{RAPIDAPI_HOST}/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    params = {
        "departure_id": ORIGEM,
        "arrival_id": DESTINO,
        "outbound_date": DATA_IDA,
        "currency": "BRL",
        "hl": "pt"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"Status da API: {response.status_code}")
        
        if response.status_code == 200:
            dados = response.json()
            lista_voos = dados.get("best_flights", []) or dados.get("other_flights", [])
            if lista_voos:
                primeiro = lista_voos[0]
                return {
                    "preco": float(primeiro.get("price", 0)),
                    "link": "https://www.google.com/travel/flights"
                }
    except Exception as e:
        print(f"Erro na requisição: {e}")

    return None

def main():
    print("Iniciando verificação de voos...")
    
    menor_historico = 999999.0
    if os.path.exists(ARQUIVO_HISTORICO):
        try:
            with open(ARQUIVO_HISTORICO, "r") as f:
                menor_historico = json.load(f).get("menor_preco", 999999.0)
        except Exception:
            pass

    voo = buscar_voo()

    if voo:
        preco_atual = voo["preco"]
        print(f"Preço encontrado: R$ {preco_atual}")

        if preco_atual <= PRECO_MAXIMO or preco_atual < menor_historico:
            msg_promo = (
                f"✈️ *ALERTA DE PASSAGEM BARATA!* ✈️\n\n"
                f"📍 *Rota:* {ORIGEM} ➡️ {DESTINO}\n"
                f"📅 *Data:* {DATA_IDA}\n"
                f"💰 *Preço Atual:* R$ {preco_atual:.2f}\n\n"
                f"🔗 [Ver no Google Flights]({voo['link']})"
            )
            enviar_telegram(msg_promo)

            if preco_atual < menor_historico:
                menor_historico = preco_atual
                with open(ARQUIVO_HISTORICO, "w") as f:
                    json.dump({"menor_preco": menor_historico}, f)

    # --- STATUS DIÁRIO NO TELEGRAM ---
    try:
        fuso_br = timezone(timedelta(hours=-3))
        data_hora = datetime.now(fuso_br).strftime('%d/%m/%Y %H:%M')
    except Exception:
        data_hora = datetime.now().strftime('%d/%m/%Y %H:%M')

    status_msg = (
        "🤖 *Status do Bot de Voos*\n"
        f"🕒 *Verificado em:* {data_hora}\n"
        f"🎯 *Rota:* {ORIGEM} ➡️ {DESTINO} ({DATA_IDA})\n"
        f"📊 *Menor preço registado:* R$ {menor_historico if menor_historico != 999999 else 'N/A'}\n"
        "🟢 *Status:* Monitoramento ativo!"
    )
    enviar_telegram(status_msg)

if __name__ == "__main__":
    main()
