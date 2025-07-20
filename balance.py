import requests

API_KEY = "0ff428e3a77f6ed0d668ab6b39f1ce4c"  # ← Вставь сюда свой API ключ

url = f"https://api.rucaptcha.com/proxy/balance?key={API_KEY}"

try:
    response = requests.get(url)
    data = response.json()

    if data.get("status") == "OK":
        print(f"💰 Баланс: {data['balance']}")
    else:
        print(f"❌ Ошибка: {data}")
except Exception as e:
    print(f"⚠️ Ошибка при запросе: {e}")
