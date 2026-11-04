import os
import tarfile
import tempfile
import gnupg

class CryptoVault:
    def __init__(self):
        self.vault_dir = os.path.expanduser("~/ghostsync/vault")
        os.makedirs(self.vault_dir, exist_ok=True)
        # استخدام مسار مفاتيح GPG المحلي لـ Termux
        self.gpg = gnupg.GPG(gnupghome=os.path.expanduser("~/.gnupg"))

    def encrypt_file(self, file_path: str, passphrase: str) -> str:
        """ضغط الملف كـ tar.gz ثم تشفيره باستخدام AES-256"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"الملف غير موجود: {file_path}")

        filename = os.path.basename(file_path)
        out_encrypted = os.path.join(self.vault_dir, f"{filename}.tar.gz.gpg")

        # إنشاء أرشيف مضغوط مؤقت
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_tar:
            tmp_tar_path = tmp_tar.name

        try:
            with tarfile.open(tmp_tar_path, "w:gz") as tar:
                tar.add(file_path, arcname=filename)

            with open(tmp_tar_path, "rb") as f_in:
                status = self.gpg.encrypt_file(
                    f_in,
                    recipients=None,
                    symmetric="AES256",
                    passphrase=passphrase,
                    armor=False,
                    output=out_encrypted
                )

            if not status.ok:
                raise RuntimeError(f"فشل التشفير: {status.stderr}")

            return out_encrypted
        finally:
            if os.path.exists(tmp_tar_path):
                os.remove(tmp_tar_path)

    def decrypt_file(self, encrypted_path: str, passphrase: str, output_path: str = None) -> str:
        """فك تشفير الملف ثم استخراج المحتوى المضغوط"""
        if not os.path.exists(encrypted_path):
            raise FileNotFoundError(f"الملف المشفر غير موجود: {encrypted_path}")

        # فك تشفير الحاوية إلى ملف مضغوط مؤقت
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_tar:
            tmp_tar_path = tmp_tar.name

        try:
            with open(encrypted_path, "rb") as f_enc:
                status = self.gpg.decrypt_file(
                    f_enc,
                    passphrase=passphrase,
                    output=tmp_tar_path
                )

            if not status.ok:
                raise RuntimeError(f"فشل فك التشفير: {status.stderr}")

            # استخراج محتوى الأرشيف
            with tarfile.open(tmp_tar_path, "r:gz") as tar:
                members = tar.getmembers()
                if not members:
                    raise RuntimeError("الأرشيف المضغوط فارغ.")
                
                extracted_file_name = members[0].name
                dest_dir = os.path.dirname(output_path) if output_path else os.path.expanduser("~/ghostsync/reports")
                os.makedirs(dest_dir, exist_ok=True)
                
                target_dest = output_path or os.path.join(dest_dir, extracted_file_name)
                
                f_extract = tar.extractfile(members[0])
                with open(target_dest, "wb") as f_out:
                    f_out.write(f_extract.read())

            return target_dest
        finally:
            if os.path.exists(tmp_tar_path):
                os.remove(tmp_tar_path)

    def list_vault(self):
        """عرض كافة الحاويات المشفرة المخزنة"""
        return sorted([
            f for f in os.listdir(self.vault_dir) 
            if f.endswith(".gpg")
        ])

    def cleanup_old_archives(self, keep_latest: int = 5):
        """حذف الحاويات القديمة والاحتفاظ بآخر N ملفات مشفرة"""
        archives = [
            os.path.join(self.vault_dir, f)
            for f in self.list_vault()
        ]
        archives.sort(key=os.path.getmtime, reverse=True)
        removed = []
        for old_file in archives[keep_latest:]:
            os.remove(old_file)
            removed.append(os.path.basename(old_file))
        return removed

if __name__ == "__main__":
    vault = CryptoVault()
    print("قائمة الخزينة الحالية:", vault.list_vault())
