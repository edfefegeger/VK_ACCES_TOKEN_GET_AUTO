import os
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import base64
import requests
from io import BytesIO
from PIL import Image

# ==== SETTINGS ====
CLIENT_ID = "6121396"
REDIRECT_URI = "https://oauth.vk.com/blank.html"
SCOPES = "215985366"
ACCOUNTS_FILE = "accounts.txt"  # format: email:password
OUTPUT_FILE = "output.txt"
API_KEY = os.getenv("ANTICAPTCHA_API_KEY")
OUTPUT_FORMAT = 1  # 1, 2, or 3
API_CREATE_TASK = "https://api.anti-captcha.com/createTask"
API_GET_RESULT = "https://api.anti-captcha.com/getTaskResult"

# ==================

def build_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "token",
        "scope": SCOPES,
        "revoke": "1",
        "display": "page",
    }
    url = "https://oauth.vk.com/oauth/authorize?" + urllib.parse.urlencode(params)
    return url

def solve_captcha(image_url):
    try:
        # Скачать изображение
        response = requests.get(image_url)
        img_bytes = response.content
        base64_img = base64.b64encode(img_bytes).decode()

        # Отправка задачи
        task_payload = {
            "clientKey": API_KEY,
            "task": {
                "type": "ImageToTextTask",
                "body": base64_img,
                "phrase": False,
                "case": True,
                "numeric": 0,
                "math": False,
                "minLength": 1,
                "maxLength": 5,
                "comment": "введите текст, который вы видите на изображении"
            },
            "softId": 3898,
            "languagePool": "rn"
        }

        task_response = requests.post(API_CREATE_TASK, json=task_payload).json()
        if task_response.get("errorId") != 0:
            print(f"[!] Ошибка создания задачи капчи: {task_response}")
            return None

        task_id = task_response["taskId"]

        # Получение результата
        for _ in range(20):
            time.sleep(2)
            result_payload = {
                "clientKey": API_KEY,
                "taskId": task_id
            }
            result_response = requests.post(API_GET_RESULT, json=result_payload).json()
            if result_response.get("status") == "ready":
                return result_response["solution"]["text"]

        print("[!] Решение капчи не получено вовремя")
        return None

    except Exception as e:
        print(f"[!] Ошибка при решении капчи: {e}")
        return None
def get_access_token(email, password, auth_url):
    chrome_options = Options()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # chrome_options.add_argument("--headless")  # по желанию

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(auth_url)
        time.sleep(3)

        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "pass").send_keys(password)
        driver.find_element(By.ID, "install_allow").click()
        time.sleep(2)

        # ==== Проверка на капчу ====
        captcha_present = False
        try:
            captcha_img = driver.find_element(By.CLASS_NAME, "oauth_captcha")
            captcha_present = captcha_img.is_displayed()
        except:
            captcha_present = False

        if captcha_present:
            captcha_url = captcha_img.get_attribute("src")
            print(f"[!] Капча найдена: {captcha_url}")
            captcha_text = solve_captcha(captcha_url)
            if captcha_text:
                print(f"[✓] Распознано: {captcha_text}")
                captcha_input = driver.find_element(By.NAME, "captcha_key")
                captcha_input.send_keys(captcha_text)
                driver.find_element(By.ID, "install_allow").click()
                time.sleep(2)
            else:
                print("[!] Не удалось распознать капчу")
                return None, user_agent
        else:
            print("[•] Капча не обнаружена — продолжаем")

        # ==== Нажатие кнопки 'Разрешить' (Allow), если появится ====
        for _ in range(20):
            time.sleep(0.5)
            try:
                allow_button = driver.find_element(By.XPATH, '//button[contains(text(), "Allow")]')
                if allow_button.is_displayed() and allow_button.is_enabled():
                    allow_button.click()
                    print("[•] Кнопка 'Разрешить' нажата")
                    break
            except:
                continue

        # ==== Получение access_token ====
        for _ in range(20):
            time.sleep(0.5)
            current_url = driver.current_url
            if "#access_token=" in current_url:
                fragment = current_url.split("#", 1)[1]
                params = urllib.parse.parse_qs(fragment)
                access_token = params.get("access_token", [None])[0]
                return access_token, user_agent

        print(f"[!] Токен не найден для {email}")
        return None, user_agent

    except Exception as e:
        print(f"[!] Ошибка для {email}: {e}")
        return None, user_agent

    finally:
        driver.quit()


def process_accounts():
    auth_url = build_auth_url()
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        email, password = line.strip().split(":", 1)
        print(f"[•] Processing: {email}")
        token, ua = get_access_token(email, password, auth_url)

        # 📥 Сохраняем результат сразу после обработки
        with open(OUTPUT_FILE, "a", encoding="utf-8") as outfile:
            if token:
                if OUTPUT_FORMAT == 1:
                    outfile.write(f"{email}:{password}:{token}\n")
                elif OUTPUT_FORMAT == 2:
                    outfile.write(f"{email}:{password}:{token}:{ua}\n")
                elif OUTPUT_FORMAT == 3:
                    outfile.write(f"{token}:{ua}\n")
                print(f"[+] Success: {email}")
            else:
                outfile.write(f"{email}:{password}:FAILED\n")
                print(f"[!] Failed: {email}")

        time.sleep(1)


if __name__ == "__main__":
    process_accounts()
