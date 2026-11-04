#!/data/data/com.termux/files/usr/bin/bash

# تحميل متغيرات البيئة ومسارات Termux
export PREFIX="/data/data/com.termux/files/usr"
export HOME="/data/data/com.termux/files/home"
export PATH="$PREFIX/bin:$PATH"

PROJECT_DIR="$HOME/ghostsync"
LOG_FILE="$PROJECT_DIR/cron.log"
DATE_STR=$(date "+%Y-%m-%d %H:%M:%S")

echo "=== [GHOSTSYNC CRON START: $DATE_STR] ===" >> "$LOG_FILE"

# تشغيل الفحص الصامت مع التقييم الأمني
cd "$PROJECT_DIR" || exit 1
python "$PROJECT_DIR/ghostsync.py" scan --ai >> "$LOG_FILE" 2>&1

# تشفير آخر تقرير مولد بكلمة المرور الافتراضية
LATEST_REPORT=$(ls -t "$PROJECT_DIR/reports"/*.md 2>/dev/null | head -n 1)

if [ -n "$LATEST_REPORT" ]; then
    python "$PROJECT_DIR/ghostsync.py" vault --encrypt "$LATEST_REPORT" --passphrase "AutoGhostSync2026" >> "$LOG_FILE" 2>&1
    echo "[✔] Encrypted $LATEST_REPORT" >> "$LOG_FILE"
fi

# تنظيف الخزينة والاحتفاظ بآخر 7 حاويات مشفرة
python "$PROJECT_DIR/ghostsync.py" vault --cleanup 7 >> "$LOG_FILE" 2>&1

echo "=== [GHOSTSYNC CRON COMPLETE] ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
