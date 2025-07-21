# ==== LANGUAGE ====
# ==== LANGUAGE ====
LANGUAGES = {
    "RU": {
        "select_format": "Выберите формат вывода результата:",
        "formats": [
            "1 — логин:пароль:токен",
            "2 — логин:пароль:токен:user-agent",
            "3 — токен:user-agent"
        ],
        "invalid_input": "❌ Неверный ввод. Пожалуйста, введите 1, 2 или 3.",
        "enter_format": "Введите номер формата (1 / 2 / 3): ",
        "captcha_found": "[!] Капча найдена",
        "captcha_ok": "[✓] Распознано:",
        "captcha_failed": "[!] Не удалось распознать капчу",
        "no_captcha": "[•] Капча не обнаружена — продолжаем",
        "button_clicked": "[•] Кнопка 'Разрешить' нажата",
        "token_missing": "[!] Токен не найден для",
        "error_for": "[!] Ошибка для",
        "processing": "[•] Обработка:",
        "success": "[+] Успешно:",
        "failed": "[!] Не удалось:",
        "balance": "Баланс",
        "balance_error": "Ошибка при получении баланса",
        "balance_request_error": "Ошибка при запросе баланса"
    },
    "EN": {
        "select_format": "Select output format:",
        "formats": [
            "1 — login:password:token",
            "2 — login:password:token:user-agent",
            "3 — token:user-agent"
        ],
        "invalid_input": "❌ Invalid input. Please enter 1, 2, or 3.",
        "enter_format": "Enter format number (1 / 2 / 3): ",
        "captcha_found": "[!] Captcha found",
        "captcha_ok": "[✓] Solved:",
        "captcha_failed": "[!] Failed to solve captcha",
        "no_captcha": "[•] No captcha found — continuing",
        "button_clicked": "[•] 'Allow' button clicked",
        "token_missing": "[!] Token not found for",
        "error_for": "[!] Error for",
        "processing": "[•] Processing:",
        "success": "[+] Success:",
        "failed": "[!] Failed:",
        "balance": "Balance",
        "balance_error": "Error retrieving balance",
        "balance_request_error": "Request error while checking balance"
    },
    "CN": {
        "select_format": "请选择输出格式：",
        "formats": [
            "1 — 登录:密码:令牌",
            "2 — 登录:密码:令牌:user-agent",
            "3 — 令牌:user-agent"
        ],
        "invalid_input": "❌ 输入无效。请输入 1、2 或 3。",
        "enter_format": "输入格式编号 (1 / 2 / 3): ",
        "captcha_found": "[!] 发现验证码",
        "captcha_ok": "[✓] 解码为：",
        "captcha_failed": "[!] 无法解码验证码",
        "no_captcha": "[•] 未发现验证码 — 继续",
        "button_clicked": "[•] 点击了 '允许' 按钮",
        "token_missing": "[!] 未找到令牌：",
        "error_for": "[!] 错误：",
        "processing": "[•] 处理：",
        "success": "[+] 成功：",
        "failed": "[!] 失败：",
        "balance": "余额",
        "balance_error": "获取余额时出错",
        "balance_request_error": "请求余额时发生错误"
    },
}


def choose_language():
    print("Choose language / Выберите язык / 选择语言:")
    print(" 1 — RU (Русский)")
    print(" 2 — EN (English)")
    print(" 3 — CN (中文)")
    while True:
        lang_choice = input("Enter 1, 2, or 3: ").strip()
        if lang_choice == "1":
            return LANGUAGES["RU"]
        elif lang_choice == "2":
            return LANGUAGES["EN"]
        elif lang_choice == "3":
            return LANGUAGES["CN"]
        else:
            print("❌ Invalid choice. Try again.")
