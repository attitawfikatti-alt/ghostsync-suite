import os
import json
import requests
from core.logger import log_info, log_warn, log_error

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

def local_heuristic_analysis(audit_data):
    """تحليل محلي سريع في حال عدم توفر اتصال بالإنترنت أو مفتاح API"""
    report = ["\n[تحليل استدلالي محلي]:"]
    for item in audit_data:
        ip = item.get("ip")
        ports = item.get("open_ports", [])
        if 5555 in ports:
            report.append(f"• تحذير حرج: الجهاز {ip} يفتح منفذ تصحيح أندرويد (ADB 5555). الجهاز معرض للاختراق والتحكم الكامل بدون مصادقة!")
        if 8022 in ports or 22 in ports:
            report.append(f"• تنبيه أمني: الجهاز {ip} يفتح خدمة SSH. تأكد من تعطيل مصادقة كلمة المرور والاعتماد كلياً على المفاتيح (Key-based).")
        if 80 in ports or 443 in ports:
            report.append(f"• ملاحظة: الجهاز {ip} يقدم واجهة ويب (HTTP/HTTPS) - غالباً ما يكون المودم/الراوتر أو كاميرا مراقبة.")
    if len(report) == 1:
        report.append("• الحالة العامة: جميع الأجهزة المفحوصة لا تكشف منافذ حساسة شائعة.")
    return "\n".join(report)

def analyze_audit_report(audit_data):
    if not audit_data:
        log_warn("لا توجد بيانات تدقيق للتحليل.")
        return "لا توجد أجهزة مفحوصة."

    log_info("بدء معالجة التقرير الأمني...")
    
    # التحقق من وجود مفتاح API للتحليل العميق
    if not GEMINI_API_KEY:
        log_warn("المتغير GEMINI_API_KEY غير معين. سيتم الاعتماد على المحرك الاستدلالي المحلي.")
        return local_heuristic_analysis(audit_data)

    prompt = (
        "أنت مهندس أمن شبكات متخصص. حلل نتائج فحص الشبكة التالية لبيئة شبكة محلية (LAN):\n"
        f"{json.dumps(audit_data, indent=2)}\n\n"
        "المطلوب باختصار ودقة:\n"
        "1. تقييم مستوى المخاطر لكل عنوان IP.\n"
        "2. تحديد أي خدمات حساسة (مثل ADB 5555 أو SSH أو واجهات الويب).\n"
        "3. خطوات علاجية فورية قابلة للتنفيذ لتأمين الأجهزة المعرضة للخطر."
    )

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=15
        )
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            log_error(f"خطأ في الاتصال بالواجهة (كود {response.status_code}). سيتم استخدام التحليل المحلي.")
            return local_heuristic_analysis(audit_data)
    except Exception as e:
        log_error(f"تعذر الاتصال بخدمة الذكاء: {e}")
        return local_heuristic_analysis(audit_data)
