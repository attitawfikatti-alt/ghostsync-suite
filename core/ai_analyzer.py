import os
import json
import requests

class AIAnalyzer:
    def __init__(self):
        # قاعدة بيانات التهديدات السريعة دون اتصال بالإنترنت
        self.signature_db = {
            53: {
                "risk": "MEDIUM",
                "issue": "محلل DNS مفتوح",
                "cve_ref": "DNS Cache Poisoning / Amplification Risks",
                "recommendation": "تأكد من تعطيل Open Recursive Resolving وقصر الاستعلام على الشبكة الداخلية."
            },
            80: {
                "risk": "MEDIUM",
                "issue": "لوحة تحكم أو خادم ويب غير مشفر (HTTP)",
                "cve_ref": "Plaintext Credentials Exposure",
                "recommendation": "تحويل حركة المرور إلى HTTPS (منفذ 443) وتعطيل إدارة الجهاز عبر HTTP."
            },
            443: {
                "risk": "LOW",
                "issue": "خدمة ويب مشفرة (HTTPS)",
                "cve_ref": "SSL/TLS Configuration",
                "recommendation": "تأكد من تعطيل بروتوكولات TLS 1.0 و 1.1 القديمة وتحديث شهادات الأمان."
            },
            5555: {
                "risk": "CRITICAL",
                "issue": "واجهة تصحيح أندرويد لاسلكية مفتوحة (Wireless ADB)",
                "cve_ref": "Remote Shell Execution / Device Takeover",
                "recommendation": "عطّل Wireless Debugging فوراً في إعدادات المطور بالأجهزة المكشوفة لتفادي حقن الأوامر."
            },
            8080: {
                "risk": "HIGH",
                "issue": "خادم ويب بديل / بروكسي محلي",
                "cve_ref": "Misconfigured Admin Endpoints",
                "recommendation": "تحقق من وجود مصادقة قوية على الخدمات العاملة على هذا المنفذ."
            }
        }

    def local_heuristic_eval(self, devices):
        """تقييم أمني داخلي مبني على بصمات المنافذ"""
        lines = []
        critical_count = 0

        for dev in devices:
            ip = dev.get("ip")
            ports = dev.get("open_ports", [])
            if not ports:
                continue

            lines.append(f"• **جهاز `{ip}`:**")
            for port in ports:
                sig = self.signature_db.get(port)
                if sig:
                    risk_tag = f"[{sig['risk']}]"
                    if sig['risk'] == "CRITICAL":
                        critical_count += 1
                    lines.append(f"  - منفذ `{port}` {risk_tag}: {sig['issue']}")
                    lines.append(f"    * الثغرة المحتملة: {sig['cve_ref']}")
                    lines.append(f"    * التوصية: {sig['recommendation']}")
                else:
                    lines.append(f"  - منفذ غير معروف `{port}`: يتطلب تدقيق البانر اليدوي.")

        if not lines:
            return "✔ لم يتم رصد أي منافذ عالية الخطورة في الفحص الحالي. الشبكة مستقرة ظاهرياً."

        summary_header = f"⚠️ تم اكتشاف عدد ({critical_count}) ثغرات خطيرة تستدعي التدخل الفوري.\n\n"
        return summary_header + "\n".join(lines)

    def evaluate_scan(self, devices):
        """التقييم الرئيسي: يدمج الفحص المحلي أو يمرره لمفتاح الذكاء الاصطناعي الخارجي"""
        api_key = os.getenv("GEMINI_API_KEY")
        local_report = self.local_heuristic_eval(devices)

        # إذا توفر مفتاح Gemini API، يتم توليد تقرير تنفيذي أعمق
        if api_key and devices:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                prompt = f"""أنت خبير أمن شبكات. إليك نتائج تدقيق أمني من بيئة أندرويد:
{json.dumps(devices, indent=2)}

حلل هذه البيانات باختصار شديد، حدد أخطر نقطة، واقترح خطوة واحدة سريعة للمعالجة باللغة العربية."""
                
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                res = requests.post(url, json=payload, timeout=12)
                if res.status_code == 200:
                    ai_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return f"{local_report}\n\n---\n**🤖 تحليل الذكاء الاصطناعي:**\n{ai_text}"
            except Exception:
                pass

        return local_report

if __name__ == "__main__":
    analyzer = AIAnalyzer()
    sample_data = [{"ip": "192.168.1.15", "open_ports": [5555, 80], "services": ["Wireless ADB", "HTTP"]}]
    print(analyzer.evaluate_scan(sample_data))
