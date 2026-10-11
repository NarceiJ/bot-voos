import os
import requests

# 1. Carregar as Secrets configuradas no GitHub Actions
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 2. Configurações da API de Voos (Baseado no RapidAPI)
URL = "https://google-flights-api.p.rapidapi.com/search"

headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "google-flights-api.p.rapidapi.com"
}

# Parâmetros oficiais exigidos pelo esquema da API
params = {
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
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url_telegram, json=payload)
        if response.status_code == 200:
            print("Mensagem enviada com sucesso para o Telegram!")
        else:
            print(f"Erro ao enviar para o Telegram: {response.text}")
    except Exception as e:
        print(f"Falha de conexão com o Telegram: {e}")

def verificar_voos():
    print("Iniciando verificação de voos GRU -> MCZ (01/01/2027)...")
    
    try:
        response = requests.get(URL, headers=headers, params=params)
        print(f"Status da API: {response.status_code}")
        
        if response.status_code == 200:
            dados = response.json()
            
            # Tenta extrair os voos da resposta da API
            # (A estrutura exata costuma vir em listas de voos ou iterários)
            voos = dados.get("data", []) or dados.get("flights", []) or dados.get("itineraries", [])
            
            if voos:
                # Pega o primeiro voo (geralmente o mais barato/melhor)
                melhor_voo = voos[0]
                preco = melhor_voo.get("price", "Preço sob consulta")
                
                mensagem = f"✈️ *Alerta de Voo Encontrado!*\n\n" \
                           f"📍 Rota: GRU ➡️ MCZ\n" \
                           f"📅 Data: 01/01/2027\n" \
                           f"💰 Menor Preço: {preco}"
                
                enviar_telegram(mensagem)
            else:
                # Caso a API retorne com sucesso mas sem voos exatos estruturados na lista padrão
                # Vamos enviar um aviso genérico de que o endpoint respondeu bem
                print("A API respondeu com sucesso, mas a estrutura de dados precisa de ajuste nos campos.")
                enviar_telegram("🤖 O monitor de voos executou, a API respondeu 200, mas precisamos refinar a leitura do preço.")
                
        elif response.status_code == 403:
            print("Erro 403: Acesso negado. Verifique se a RAPIDAPI_KEY nas Secrets está correta e sem espaços extras.")
        else:
            print(f"A API retornou um código inesperado: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Erro na execução da requisição: {e}")

if __name__ == "__main__":
    verificar_voos()
