import os
requests_import = __import__('requests')

# 1. Carregar as Secrets do GitHub Actions
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Novo Host e Endpoint de One-Way da scrappa
URL = "https://google-flights-scraper.p.rapidapi.com/api/flights/one-way"

headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "google-flights-scraper.p.rapidapi.com"
}

# Parâmetros enviados via Query String (GET)
params = {
    "origin": "GRU",
    "destination": "MCZ",
    "departure_date": "2026-12-31",
    "adults": 1,
    "cabin_class": "economy",
    "sort_by": "cheapest"
}

def enviar_telegram(mensagem):
    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    body = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        response = requests_import.post(url_telegram, json=body)
        if response.status_code == 200:
            print("Mensagem enviada com sucesso para o Telegram!")
        else:
            print(f"Erro ao enviar para o Telegram: {response.text}")
    except Exception as e:
        print(f"Falha de conexão com o Telegram: {e}")

def verificar_voos():
    print("Iniciando verificação de voos GRU -> MCZ (31/12/2026)...")
    
    try:
        # Requisição GET com parâmetros de query
        response = requests_import.get(URL, headers=headers, params=params)
        print(f"Status da API: {response.status_code}")
        
        if response.status_code == 200:
            dados = response.json()
            voos = dados.get("flights", [])
            
            if voos:
                melhor_voo = voos[0]
                
                # Extração de campos conforme a documentação da scrappa
                preco = melhor_voo.get("price", "Sob consulta")
                moeda = melhor_voo.get("currency", "BRL")
                companhia = melhor_voo.get("airline_name", "Não informada")
                escalas = melhor_voo.get("stops", 0)
                
                tipo_voo = "Voo Direto ✈️" if escalas == 0 else f"{escalas} escala(s)"
                
                # Opcional: token para detalhamento ou montagem de link
                # A documentação indica o uso de booking_token ou links de provedores via booking-details
                mensagem = f"✈️ *Alerta de Voo Encontrado (31/12)*\n\n" \
                           f"📍 Rota: GRU ➡️ MCZ\n" \
                           f"📅 Data: 31/12/2026\n" \
                           f"🏢 Companhia: {companhia}\n" \
                           f"🔄 Tipo: {tipo_voo}\n" \
                           f"💰 Menor Preço: {moeda} {preco}"
                
                enviar_telegram(mensagem)
            else:
                print("Nenhum voo encontrado para os parâmetros informados.")
        else:
            print(f"Erro na API: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Erro na execução da requisição: {e}")

if __name__ == "__main__":
    verificar_voos()
