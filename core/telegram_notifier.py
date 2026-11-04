import os
import json
import requests

CONFIG_PATH = os.path.expanduser("~/ghostsync/config/settings.json")

def load_telegram_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            cfg = json.load(f)
            return cfg.get("telegram", {})
    return {}

def send_telegram_alert(message: str, file_path: str = None) -> bool:
    config = load_telegram_config()
    token = config.get("bot_token")
    chat_id = config.get("chat_id")

    if not token or not chat_id or token == "YOUR_BOT_TOKEN":
        return False

    base_url = f"https://api.telegram.org/bot{token}"

    try:
        # إرسال الرسالة النصية
        msg_payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        res = requests.post(f"{base_url}/sendMessage", json=msg_payload, timeout=10)
        
        # إرسال الملف المشفر إذا تم تحديده
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                requests.post(
                    f"{base_url}/sendDocument",
                    data={"chat_id": chat_id},
                    files={"document": f},
                    timeout=20
                )
        return res.status_code == 200
    except Exception as e:
        print(f"[!] خطأ في إرسال إشعار تيليجرام: {e}")
        return False

if __name__ == "__main__":
    success = send_telegram_alert("🛡️ *GhostSync-AI:* اختبار اتصال ناجح من Termux!")
    if success:
        print("✔ تم إرسال رسالة الاختبار بنجاح.")
    else:
        print("[!] لم يتم الإرسال. تأكد من إعداد Bot Token و Chat ID في config/settings.json.")
