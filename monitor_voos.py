import os
import time
import requests

# 1. Carregar as Secrets
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

URL = "https://google-flights-api4.p.rapidapi.com/v1/google-flights-scraper/run"

headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "google-flights-api4.p.rapidapi.com",
    "Content-Type": "application/json"
}

payload = {
    "origin": "GRU",
    "destination": "MCZ",
    "departureDate": "2027-01-01",
    "currency": "BRL",
    "adults": 1,
    "cabinClass": "economy"
}

def enviar_telegram(mensagem):
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
        response = requests.post(URL, headers=headers, json=payload)
        print(f"Status inicial da API: {response.status_code}")
        
        if response.status_code in [200, 202]:
            dados = response.json()
            
            # Se retornar um pollUrl, precisamos aguardar e buscar os resultados
            poll_url = dados.get("pollUrl")
            
            if poll_url:
                print("Job iniciado em segundo plano. Aguardando processamento...")
                
                # Tenta consultar o resultado até 5 vezes (aguardando alguns segundos entre cada tentativa)
                for tentativa in range(6):
                    time.sleep(10) # espera 10 segundos
                    print(f"Tentativa {tentativa + 1} de buscar resultados...")
                    
                    poll_response = requests.get(poll_url, headers=headers)
                    if poll_response.status_code == 200:
                        poll_data = poll_response.json()
                        status_job = poll_data.get("status")
                        print(f"Status atual do job: {status_job}")
                        
                        if status_job == "SUCCEEDED":
                            voos = poll_data.get("items", []) or poll_data.get("data", [])
                            if voos:
                                melhor_voo = voos[0]
                                preco = melhor_voo.get("priceLabel", melhor_voo.get("price", "Preço sob consulta"))
                                
                                mensagem = f"✈️ *Alerta de Voo Encontrado!*\n\n" \
                                           f"📍 Rota: GRU ➡️ MCZ\n" \
                                           f"📅 Data: 01/01/2027\n" \
                                           f"💰 Menor Preço: {preco}"
                                
                                enviar_telegram(mensagem)
                                return
                        elif status_job in ["FAILED", "ABORTED"]:
                            print("O processamento da pesquisa falhou no servidor da API.")
                            break
                
                print("Tempo limite excedido aguardando os resultados da pesquisa.")
            else:
                # Caso já venha direto na resposta
                voos = dados.get("items", []) or dados.get("data", [])
                if voos:
                    melhor_voo = voos[0]
                    preco = melhor_voo.get("priceLabel", "Preço sob consulta")
                    enviar_telegram(f"✈️ *Voo GRU ➡️ MCZ (01/01/2027)*\n💰 Menor Preço: {preco}")
        else:
            print(f"A API retornou um código inesperado: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Erro na execução da requisição: {e}")

if __name__ == "__main__":
    verificar_voos()
