#!/usr/bin/env python3
import os
import sys
from modules.net_audit import run_audit
from modules.vault import encrypt_path, decrypt_file, list_vault
from modules.ai_engine import analyze_audit_report
from modules.sync_engine import sync_vault_to_cloud
from core.config import VAULT_DIR

BANNER = """\033[96m
   ____ _               _   ____                  
  / ___| |__   ___  ___| |_/ ___| _   _ _ __   ___ 
 | |  _| '_ \ / _ \/ __| __\___ \| | | | '_ \ / __|
 | |_| | | | | (_) \__ \ |_ ___) | |_| | | | | (__ 
  \____|_| |_|\___/|___/\__|____/ \__, |_| |_|\___|
                                  |___/            
       >> Modular Security & Vault Suite <<
\033[0m"""

def menu():
    last_audit_data = []
    while True:
        os.system("clear")
        print(BANNER)
        print("\033[93m[1]\033[0m تدقيق الشبكة المحلية والأجهزة المتصلة")
        print("\033[93m[2]\033[0m تشفير ملف وإيداعه في الخزنة")
        print("\033[93m[3]\033[0m استعراض محتويات الخزنة المشفرة")
        print("\033[93m[4]\033[0m فك تشفير ملف من الخزنة")
        print("\033[93m[5]\033[0m تحليل أمني ذكي لتقرير الشبكة (AI Security Audit)")
        print("\033[93m[6]\033[0m مزامنة الخزنة المشفرة إلى السحابة (Rclone)")
        print("\033[91m[0]\033[0m خروج")
        print("-" * 50)
        
        choice = input("\033[92mاختر عملية:\033[0m ").strip()
        
        if choice == "1":
            print("\n" + "=" * 40)
            last_audit_data = run_audit()
            input("\nاضغط Enter للمتابعة...")
        elif choice == "2":
            path = input("\nأدخل مسار الملف أو المجلد المراد تشفيره: ").strip()
            path = os.path.expanduser(path)
            encrypt_path(path)
            input("\nاضغط Enter للمتابعة...")
        elif choice == "3":
            print("\n=== محتويات الخزنة ===")
            files = list_vault()
            if files:
                for idx, f in enumerate(files, 1):
                    print(f"[{idx}] {f}")
            else:
                print("الخزنة فارغة حالياً.")
            input("\nاضغط Enter للمتابعة...")
        elif choice == "4":
            files = list_vault()
            if not files:
                print("\nالخزنة فارغة.")
            else:
                print("\nالملفات المتوفرة:")
                for idx, f in enumerate(files, 1):
                    print(f"[{idx}] {f}")
                target = input("\nأدخل اسم الملف المشفر كاملاً (مع .enc): ").strip()
                full_path = os.path.join(VAULT_DIR, target)
                decrypt_file(full_path)
            input("\nاضغط Enter للمتابعة...")
        elif choice == "5":
            print("\n" + "=" * 40)
            if not last_audit_data:
                print("جاري فحص الشبكة أولاً للحصول على بيانات حديثة...")
                last_audit_data = run_audit()
            report = analyze_audit_report(last_audit_data)
            print("\n" + "-" * 20 + " تقرير التحليل الأمني " + "-" * 20)
            print(report)
            input("\nاضغط Enter للمتابعة...")
        elif choice == "6":
            print("\n" + "=" * 40)
            sync_vault_to_cloud()
            input("\nاضغط Enter للمتابعة...")
        elif choice == "0":
            print("\nإغلاق GhostSync... في أمان الله.")
            sys.exit(0)
        else:
            input("\nخيار غير صالح. اضغط Enter للمحاولة مجدداً...")

if __name__ == "__main__":
    menu()
