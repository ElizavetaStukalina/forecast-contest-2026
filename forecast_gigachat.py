# forecast_gigachat.py
# Скрипт для генерации прогнозов через GigaChat API

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import config

load_dotenv()

# Получаем ключ из .env
AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")
RQUID = os.getenv("RQUID", "12345678-1234-1234-1234-123456789012")

if not AUTH_KEY:
    print("❌ Ошибка: API-ключ не найден!")
    print("Создайте файл .env и добавьте: GIGACHAT_AUTH_KEY=ваш_ключ")
    exit(1)

def get_token():
    """Получение токена доступа"""
    auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Authorization": f"Bearer {AUTH_KEY}",
        "RqUID": RQUID,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"scope": "GIGACHAT_API_PERS"}
    response = requests.post(auth_url, headers=headers, data=data, verify=False)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Ошибка авторизации: {response.status_code}")

def generate_forecast(prompt_text, media_name, token):
    """Генерация прогноза"""
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "GigaChat-Max",
        "messages": [
            {"role": "system", "content": "Ты профессиональный журналист. Отвечай строго в формате."},
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }
    response = requests.post(url, headers=headers, json=payload, verify=False)
    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        lines = content.strip().split('\n')
        headline = ""
        lead = ""
        for line in lines:
            if "ЗАГОЛОВОК:" in line:
                headline = line.split(":", 1)[1].strip()
            elif "ПЕРВЫЙ АБЗАЦ:" in line:
                lead = line.split(":", 1)[1].strip()
        return {"media": media_name, "headline": headline, "lead_paragraph": lead}
    else:
        return {"media": media_name, "error": f"API Error: {response.status_code}"}

def main():
    print("🚀 Генерация прогнозов для 2 апреля 2026")
    token = get_token()
    print("✅ Токен получен\n")
    
    results = []
    for idx, item in enumerate(config.PROMPTS, 1):
        print(f"📰 Прогноз {idx}: {item['media']}")
        result = generate_forecast(item['prompt'], item['media'], token)
        if "error" in result:
            print(f"   ❌ {result['error']}")
        else:
            print(f"   ✅ {result['headline'][:70]}...")
            results.append(result)
        print()
    
    os.makedirs("output", exist_ok=True)
    output_file = f"output/forecasts_{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Сохранено {len(results)} прогнозов в {output_file}")

if __name__ == "__main__":
    main()