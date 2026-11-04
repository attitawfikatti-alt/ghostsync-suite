import subprocess
import shutil
from core.config import VAULT_DIR
from core.logger import log_info, log_warn, log_error

def get_configured_remotes():
    if not shutil.which("rclone"):
        log_error("أداة rclone غير مثبتة في النظام.")
        return []
    try:
        res = subprocess.run(["rclone", "listremotes"], stdout=subprocess.PIPE, text=True)
        remotes = [r.strip() for r in res.stdout.strip().split("\n") if r.strip()]
        return remotes
    except Exception as e:
        log_error(f"خطأ أثناء قراءة إعدادات rclone: {e}")
        return []

def sync_vault_to_cloud(remote_target="ghostdrive:GhostSync_Vault"):
    remotes = get_configured_remotes()
    if not remotes:
        log_warn("لم يتم العثور على حساب سحابي مهيأ في rclone. نفذ أمر rclone config أولاً.")
        return False

    remote_name = remote_target.split(":")[0] + ":"
    if remote_name not in remotes:
        log_warn(f"الخادم {remote_name} غير موجود. الخوادم المتوفرة: {remotes}")
        remote_target = f"{remotes[0]}GhostSync_Vault"
        log_info(f"سيتم استخدام الخادم الافتراضي الأول: {remote_target}")

    log_info(f"بدء مزامنة الخزنة المشفرة إلى {remote_target}...")
    try:
        cmd = [
            "rclone", "copy",
            VAULT_DIR,
            remote_target,
            "--include", "*.enc",
            "-v"
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            log_info("تمت مزامنة الملفات المشفرة مع السحابة بنجاح.")
            return True
        else:
            log_error(f"فشلت المزامنة: {res.stderr}")
            return False
    except Exception as e:
        log_error(f"حدث خطأ أثناء تنفيذ rclone: {e}")
        return False
