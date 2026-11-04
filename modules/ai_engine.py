import os
import json
import datetime
import requests
from core.config import GEMINI_API_KEY, REPORTS_DIR, VAULT_DIR
from core.logger import log_info, log_warn, log_error
from modules.vault import encrypt_path

def generate_local_heuristics(audit_data):
    issues = []
    adb_devices = [d["ip"] for d in audit_data if 5555 in d.get("open_ports", [])]
    ssh_devices = [d["ip"] for d in audit_data if any(p in d.get("open_ports", []) for p in [22, 8022])]

    if adb_devices:
        issues.append(f"[تحذير حرج] تم اكتشاف منافذ ADB مفتوحة بدون تشفير على الأجهزة: {', '.join(adb_devices)}")
    if ssh_devices:
        issues.append(f"[ملاحظة] تم العثور على خوادم SSH نشطة على الأجهزة: {', '.join(ssh_devices)}")

    total = len(audit_data)
    summary = f"تقرير فحص محلي (Fallback):\n- إجمالي الأجهزة: {total}\n"
    if issues:
        summary += "\n".join(issues)
    else:
        summary += "لم يتم رصد ثغرات ظاهرة في المنافذ القياسية المفحوصة."
    return summary

def analyze_audit_report(audit_data, save_to_vault=True):
    if not audit_data:
        return "لا توجد بيانات شبكة للتحليل."

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_content = ""

    if not GEMINI_API_KEY:
        log_warn("مفتاح GEMINI_API_KEY غير موجود في المتغيرات. جاري استخدام التحليل المحلي الهيورستي.")
        report_content = generate_local_heuristics(audit_data)
    else:
        log_info("إرسال بيانات الفحص إلى محرك التحليل الأمني الذكي...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        prompt = f"""أنت خبير أمني مختص في أمن الشبكات والأنظمة المضمنة. حلل نتائج الفحص التالية بدقة وأعطِ تقييماً شاملاً للمخاطر وتوصيات عملية للحماية:
{json.dumps(audit_data, indent=2, ensure_ascii=False)}
"""
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            res = requests.post(url, json=payload, timeout=25)
            if res.status_code == 200:
                data = res.json()
                report_content = data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                log_error(f"فشل الاتصال بمحرك التحليل الذكي (رمز: {res.status_code}). الاعتماد على التحليل المحلي.")
                report_content = generate_local_heuristics(audit_data)
        except Exception as e:
            log_error(f"خطأ أثناء طلب التحليل الذكي: {e}")
            report_content = generate_local_heuristics(audit_data)

    # حفظ وتشفير التقرير داخل الخزنة
    if save_to_vault:
        raw_report_path = os.path.join(REPORTS_DIR, f"audit_report_{timestamp}.txt")
        try:
            with open(raw_report_path, "w", encoding="utf-8") as f:
                f.write(f"=== تقرير تدقيق أمني: {timestamp} ===\n\n")
                f.write(report_content)
            
            # تشفير الملف وإيداعه في الخزنة
            if encrypt_path(raw_report_path):
                log_info(f"تم تشفير التقرير وإيداعه في الخزنة: audit_report_{timestamp}.txt.enc")
                # حذف النسخة غير المشفرة لحماية البيانات
                if os.path.exists(raw_report_path):
                    os.remove(raw_report_path)
        except Exception as e:
            log_error(f"تعذر حفظ التقرير في الخزنة: {e}")

    return report_content
