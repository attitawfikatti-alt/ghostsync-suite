#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "============================================"
echo "🛡️  GhostSync-AI Auto Installer for Termux"
echo "============================================"

# 1. تحديث الحزم وتثبيت المتطلبات
echo "[*] التحقق من حزم النظام..."
pkg update -y
pkg install -y python python-pip gnupg cronie git

# 2. تثبيت مكتبات بايثون المطلوبة مباشرة دون ترقية pip
echo "[*] تثبيت مكتبات بايثون المطلوبة..."
pip install rich requests python-gnupg

# 3. إعداد المجلدات
INSTALL_DIR="$HOME/ghostsync"
echo "[*] تهيئة مجلدات التخزين والتقارير..."
mkdir -p "$INSTALL_DIR/reports" "$INSTALL_DIR/vault" "$INSTALL_DIR/config"

# 4. ضبط الصلاحيات والروابط الرمزية
echo "[*] إنشاء وتحديث الرابط الرمزي..."
chmod +x "$INSTALL_DIR/ghostsync.py"
chmod +x "$INSTALL_DIR/core/cron_task.sh"
ln -sf "$INSTALL_DIR/ghostsync.py" "$PREFIX/bin/ghostsync"

echo ""
echo "✔ اكتمل التثبيت والتهيئة بنجاح!"
echo "يمكنك تشغيل الأداة مباشرة: ghostsync"
