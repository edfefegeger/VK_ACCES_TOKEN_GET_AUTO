import os
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import base64
import requests
from language import LANGUAGES, choose_language
import configparser
# ==== SETTINGS ====
L = choose_language()
CLIENT_ID = "6121396"
REDIRECT_URI = "https://oauth.vk.com/blank.html"
SCOPES = "215985366"
ACCOUNTS_FILE = "accounts.txt"  # формат: email:password
OUTPUT_FILE = "output.txt"
config = configparser.ConfigParser()
config.read("config.ini")

API_KEY = config.get("settings", "RUCAPTCHA_API_KEY") 
API_CREATE_TASK = "https://api.rucaptcha.com/createTask"
API_GET_RESULT = "https://api.rucaptcha.com/getTaskResult"





def choose_mode():
    print("\nВыберите режим работы:")
    print("  A — Проверка аккаунтов (имя, дата регистрации)")
    print("  C — Получение токенов (как сейчас)")
    while True:
        mode = input("Введите режим (A/C): ").strip().upper()
        if mode in {"A", "C"}:
            return mode
        else:
            print("Неверный ввод. Введите A или C.")

MODE = choose_mode()


url = f"https://api.rucaptcha.com/proxy/balance?key={API_KEY}"
try:
    response = requests.get(url)
    data = response.json()
    if data.get("status") == "OK":
        print(f" \n \n 💰 {L['balance']}: {data['balance']} \n \n")
    else:
        print(f"❌ {L['balance_error']}: {data}")
except Exception as e:
    print(f"⚠️ {L['balance_request_error']}: {e}")
import re
from bs4 import BeautifulSoup

def check_vk_account(email, password):
    session = requests.Session()
    login_url = "https://vk.com"
    try:
        # Попробуем авторизоваться (через обычный POST запрос)
        auth_data = {
            "act": "login",
            "role": "al_frame",
            "email": email,
            "pass": password
        }
        response = session.post("https://login.vk.com/?act=login", data=auth_data, allow_redirects=True)
        if "remixsid" not in session.cookies.get_dict():
            return None  # не авторизовались

        # Перейдем в профиль
        profile = session.get("https://vk.com/settings").text
        soup = BeautifulSoup(profile, "html.parser")

        # Поиск имени и фамилии
        full_name = soup.find("div", class_="SettingsUserBlock__name")
        if not full_name:
            full_name = soup.find("h2")  # запасной вариант
        name = full_name.get_text(strip=True) if full_name else "Неизвестно"

        # Поиск даты регистрации (часто внизу страницы)
        join_match = re.search(r"на сайте с (\d{1,2} \w+ \d{4})", profile)
        joined = join_match.group(1) if join_match else "Неизвестно"

        return name, joined

    except Exception as e:
        print(f"[!] Ошибка при проверке: {e}")
        return None

def choose_output_format():
    print(L["select_format"])
    for line in L["formats"]:
        print(" ", line)
    while True:
        choice = input(L["enter_format"]).strip()
        if choice in {"1", "2", "3"}:
            return int(choice)
        else:
            print(L["invalid_input"])


OUTPUT_FORMAT = choose_output_format()


def build_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "token",
        "scope": SCOPES,
        "revoke": "1",
        "display": "page",
    }
    return "https://oauth.vk.com/oauth/authorize?" + urllib.parse.urlencode(params)


def solve_captcha_from_base64(base64_img):
    try:
        task_payload = {
            "clientKey": API_KEY,
            "task": {
                "type": "ImageToTextTask",
                "body": base64_img,
                "phrase": False,
                "case": True,
                "numeric": 0,
                "math": False,
                "minLength": 3,
                "maxLength": 7,
                "comment": "VK CAPTCHA"
            },
            "softId": 3898,
            "languagePool": "rn"
        }

        task_response = requests.post(API_CREATE_TASK, json=task_payload).json()
        if task_response.get("errorId") != 0:
            print(f"[!] Ошибка создания задачи капчи: {task_response}")
            return None

        task_id = task_response["taskId"]
        for _ in range(100):
            time.sleep(1)
            result = requests.post(API_GET_RESULT, json={"clientKey": API_KEY, "taskId": task_id}).json()
            if result.get("status") == "ready":
                return result["solution"]["text"]

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
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    #chrome_options.add_argument("--headless")  # убери если хочешь видеть браузер

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(auth_url)
        time.sleep(2)

        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "pass").send_keys(password)
        driver.find_element(By.ID, "install_allow").click()
        time.sleep(2)

        # Проверка на капчу
        try:
            captcha_element = driver.find_element(By.CLASS_NAME, "oauth_captcha")
            if captcha_element.is_displayed():
                print(f"[!] {L['captcha_found']}")
                # Сохраняем как PNG и конвертируем в base64
                captcha_png = captcha_element.screenshot_as_png
                base64_img = base64.b64encode(captcha_png).decode()

                captcha_text = solve_captcha_from_base64(base64_img)
                if captcha_text:
                    print(f"{L['captcha_ok']} {captcha_text}")

                    # Повторный ввод логина и пароля
                    try:
                        email_input = driver.find_element(By.NAME, "email")
                        pass_input = driver.find_element(By.NAME, "pass")
                        captcha_input = driver.find_element(By.NAME, "captcha_key")

                        email_input.clear()
                        pass_input.clear()
                        captcha_input.clear()

                        email_input.send_keys(email)
                        pass_input.send_keys(password)
                        captcha_input.send_keys(captcha_text)

                        driver.find_element(By.ID, "install_allow").click()
                        time.sleep(2)
                    except Exception as e:
                        print(f"[!] Ошибка при повторном вводе: {e}")
                        return None, user_agent
                else:
                    print(L["captcha_failed"])
                    return None, user_agent

        except:
            print(L["no_captcha"])

        # Разрешаем доступ
        for _ in range(20):
            time.sleep(0.5)
            try:
                allow_button = driver.find_element(By.XPATH, '//button[contains(text(), "Allow")]')
                if allow_button.is_displayed():
                    allow_button.click()
                    print(L["button_clicked"])
                    break
            except:
                continue

        # Получение токена из URL
        for _ in range(20):
            time.sleep(0.5)
            if "#access_token=" in driver.current_url:
                fragment = driver.current_url.split("#", 1)[1]
                access_token = urllib.parse.parse_qs(fragment).get("access_token", [None])[0]
                return access_token, user_agent

        print(f"{L['token_missing']} {email}")
        return None, user_agent

    except Exception as e:
        print(f"{L['error_for']} {email}: {e}")
        return None, user_agent

    finally:
        driver.quit()

def process_accounts():
    auth_url = build_auth_url()
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as file:
        for line in file:
            email, password = line.strip().split(":", 1)
            print(f"{L['processing']} {email}")

            if MODE == "C":
                token, ua = get_access_token(email, password, auth_url)

                with open(OUTPUT_FILE, "a", encoding="utf-8") as outfile:
                    if token:
                        if OUTPUT_FORMAT == 1:
                            outfile.write(f"{email}:{password}:{token}\n")
                        elif OUTPUT_FORMAT == 2:
                            outfile.write(f"{email}:{password}:{token}:{ua}\n")
                        elif OUTPUT_FORMAT == 3:
                            outfile.write(f"{token}:{ua}\n")
                        print(f"{L['success']} {email}")
                    else:
                        outfile.write(f"{email}:{password}:FAILED\n")
                        print(f"{L['failed']} {email}")

                time.sleep(1)

            elif MODE == "A":
                result = check_vk_account(email, password)
                with open("accounts_checked.txt", "a", encoding="utf-8") as checked_file:
                    if result:
                        name, joined = result
                        checked_file.write(f"{email}:{password}:{name}:{joined}\n")
                        print(f"✅ {email} → {name}, зарегистрирован: {joined}")
                    else:
                        checked_file.write(f"{email}:{password}:FAILED\n")
                        print(f"❌ {email} — не удалось авторизоваться")
                time.sleep(1)



if __name__ == "__main__":
    process_accounts()
