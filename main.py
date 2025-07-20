import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ==== SETTINGS ====
CLIENT_ID = "6121396"
REDIRECT_URI = "https://oauth.vk.com/blank.html"
SCOPES = "215985366"
ACCOUNTS_FILE = "accounts.txt"  # format: email:password
OUTPUT_FILE = "output.txt"

OUTPUT_FORMAT = 1  # 1, 2, or 3
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

def get_access_token(email, password, auth_url):
    chrome_options = Options()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--headless")  # optional

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(auth_url)
        time.sleep(3)

        # Enter email
        login_input = driver.find_element(By.NAME, "email")
        login_input.clear()
        login_input.send_keys(email)

        # Enter password
        password_input = driver.find_element(By.NAME, "pass")
        password_input.clear()
        password_input.send_keys(password)

        # Click "Log in" button
        login_button = driver.find_element(By.ID, "install_allow")
        login_button.click()

        # Wait for the "Allow" button
        for _ in range(20):
            time.sleep(0.5)
            try:
                allow_button = driver.find_element(By.XPATH, '//button[contains(text(), "Allow")]')
                if allow_button.is_displayed() and allow_button.is_enabled():
                    allow_button.click()
                    break
            except:
                continue

        # Wait for redirect with token in the URL
        for _ in range(20):
            time.sleep(0.5)
            current_url = driver.current_url
            if "#access_token=" in current_url:
                fragment = current_url.split("#", 1)[1]
                params = urllib.parse.parse_qs(fragment)
                access_token = params.get("access_token", [None])[0]
                return access_token, user_agent

        print(f"[!] Token not found for {email}")
        return None, user_agent

    except Exception as e:
        print(f"[!] Error for {email}: {e}")
        return None, user_agent

    finally:
        driver.quit()

def process_accounts():
    auth_url = build_auth_url()
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for line in lines:
            email, password = line.strip().split(":", 1)
            print(f"[•] Processing: {email}")
            token, ua = get_access_token(email, password, auth_url)
            if token:
                if OUTPUT_FORMAT == 1:
                    outfile.write(f"{email}:{password}:{token}\n")
                elif OUTPUT_FORMAT == 2:
                    outfile.write(f"{email}:{password}:{token}:{ua}\n")
                elif OUTPUT_FORMAT == 3:
                    outfile.write(f"{token}:{ua}\n")
                print(f"[+] Success: {email}")
            else:
                print(f"[!] Failed: {email}")
            time.sleep(1)

if __name__ == "__main__":
    process_accounts()
