import os
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import base64
import requests
from language import LANGUAGES, choose_language

# ==== SETTINGS ====
L = choose_language()
CLIENT_ID = "6121396"
REDIRECT_URI = "https://oauth.vk.com/blank.html"
SCOPES = "215985366"
ACCOUNTS_FILE = "accounts.txt"  # format: email:password
OUTPUT_FILE = "output.txt"
API_KEY = os.getenv("ANTICAPTCHA_API_KEY")
API_CREATE_TASK = "https://api.anti-captcha.com/createTask"
API_GET_RESULT = "https://api.anti-captcha.com/getTaskResult"

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

def solve_captcha(image_url):
    try:
        img_bytes = requests.get(image_url).content
        base64_img = base64.b64encode(img_bytes).decode()

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
        for _ in range(20):
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
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(auth_url)
        time.sleep(2)

        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "pass").send_keys(password)
        driver.find_element(By.ID, "install_allow").click()
        time.sleep(1)

        try:
            captcha_img = driver.find_element(By.CLASS_NAME, "oauth_captcha")
            if captcha_img.is_displayed():
                print(f"[!] {L['captcha_found']} {captcha_img.get_attribute('src')}")
                captcha_text = solve_captcha(captcha_img.get_attribute("src"))
                if captcha_text:
                    print(f"{L['captcha_ok']} {captcha_text}")
                    driver.find_element(By.NAME, "captcha_key").send_keys(captcha_text)
                    driver.find_element(By.ID, "install_allow").click()
                else:
                    print(L["captcha_failed"])
                    return None, user_agent
        except:
            print(L["no_captcha"])

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

if __name__ == "__main__":
    process_accounts()
