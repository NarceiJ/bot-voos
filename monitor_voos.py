import os
import requests

# 1. Carregar as Secrets configuradas no GitHub Actions
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 2. Configurações da API com o endpoint e host corretos
URL = "https://google-flights-api4.p.rapidapi.com/v1/google-flights-scraper/run"

headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "google-flights-api4.p.rapidapi.com",
    "Content-Type": "application/json"
}

# Parâmetros enviados no corpo (payload) do POST
payload = {
    "origin": "GRU",
    "destination": "MCZ",
    "departureDate": "2027-01-01",
    "currency": "BRL",
    "adults": 1,
    "cabinClass": "economy"
}

def enviar_telegram(mensagem):
    """Envia alerta direto para o seu chat do Telegram"""
    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    body = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url_telegram, json=body)
        if response.status_code == 200:
            print("Mensagem enviada com sucesso para o Telegram!")
        else:
            print(f"Erro ao enviar para o Telegram: {response.text}")
    except Exception as e:
        print(f"Falha de conexão com o Telegram: {e}")

def verificar_voos():
    print("Iniciando verificação de voos GRU -> MCZ (01/01/2027)...")
    
    try:
        # Mudamos de GET para POST e enviamos como 'json=payload'
        response = requests.post(URL, headers=headers, json=payload)
        print(f"Status da API: {response.status_code}")
        
        if response.status_code == 200:
            dados = response.json()
            
            # Dependendo de como a resposta é devolvida, procuramos nas chaves comuns
            voos = dados if isinstance(dados, list) else dados.get("data", []) or dados.get("flights", []) or dados.get("itineraries", [])
            
            if voos:
                melhor_voo = voos[0]
                preco = melhor_voo.get("price", "Preço sob consulta")
                
                mensagem = f"✈️ *Alerta de Voo Encontrado!*\n\n" \
                           f"📍 Rota: GRU ➡️ MCZ\n" \
                           f"📅 Data: 01/01/2027\n" \
                           f"💰 Menor Preço: {preco}"
                
                enviar_telegram(mensagem)
            else:
                print("A API respondeu com sucesso (200), mas a lista de voos veio vazia.")
                enviar_telegram("🤖 O monitor executou com sucesso (Status 200), mas nenhum voo foi retornado na lista.")
                
        else:
            print(f"A API retornou um código inesperado: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Erro na execução da requisição: {e}")

if __name__ == "__main__":
    verificar_voos()
