import requests, json, os, sys
from pathlib import Path
from datetime import datetime, timezone

JOURNALS = {
    "soylem":     {"name": "Söylem Filoloji",                  "url": "https://dergipark.org.tr/tr/pub/soylemdergi"},
    "iulitera":   {"name": "Litera (İstanbul Ü.)",             "url": "https://dergipark.org.tr/tr/pub/iulitera"},
    "deuefad":    {"name": "Dokuz Eylül Ü. EFD",               "url": "https://dergipark.org.tr/tr/pub/deuefad"},
    "diledeara":  {"name": "Dil ve Edebiyat Araştırmaları",    "url": "https://dergipark.org.tr/tr/pub/diledeara"},
    "eeder":      {"name": "Edebî Eleştiri Dergisi",           "url": "https://dergipark.org.tr/tr/pub/eeder"},
    "humanitas":  {"name": "Humanitas (NKÜ)",                  "url": "https://dergipark.org.tr/tr/pub/humanitas"},
    "sosbilder":  {"name": "Uludağ FEF Sos. Bil.",             "url": "https://dergipark.org.tr/tr/pub/sosbilder"},
    "cankujhss":  {"name": "Çankaya CUJHSS",                   "url": "https://dergipark.org.tr/tr/pub/cankujhss"},
    "sefad":      {"name": "SEFAD (Selçuk Ü.)",                "url": "https://dergipark.org.tr/tr/pub/sefad"},
    "suitder":    {"name": "SUİTDER (SDÜ)",                    "url": "https://dergipark.org.tr/tr/pub/suitder"},
    "litandhum":  {"name": "Edebiyat ve Beşeri Bilimler",      "url": "https://dergipark.org.tr/tr/pub/literatureandhumanities"},
    "udekad":     {"name": "UDEKAD",                           "url": "https://dergipark.org.tr/tr/pub/udekad"},
    "dtcf":       {"name": "Ankara Ü. DTCF",                   "url": "https://dergipark.org.tr/tr/pub/dtcfdergisi"},
    "huefd":      {"name": "Hacettepe Ü. EFD",                 "url": "https://dergipark.org.tr/tr/pub/huefd"},
    "nesir":      {"name": "Nesir",                            "url": "https://dergipark.org.tr/tr/pub/nesir"},
    "ceviri":     {"name": "Çeviribilim ve Uygulamaları",      "url": "https://dergipark.org.tr/tr/pub/ceviri"},
    "dilder":     {"name": "Dil Dergisi (TÖMER)",              "url": "https://dergipark.org.tr/tr/pub/dilder"},
    "trkede":     {"name": "Trakya Ü. EFD",                    "url": "https://dergipark.org.tr/tr/pub/trkede"},
    "dilarast":   {"name": "Dil Araştırmaları",                "url": "https://dergipark.org.tr/tr/pub/dilarastirmalari"},
    "bilig":      {"name": "bilig (Türk Dünyası Sos. Bil.)",   "url": "https://dergipark.org.tr/tr/pub/bilig"},
    "fe":         {"name": "Folklor/Edebiyat",                 "url": "https://dergipark.org.tr/tr/pub/fe"},
}

CLOSED_MARKERS = [
    "Makale Gönderimine Kapalı",
    "Makale Gönderimine Açılacak Tarih",
]
STATE_FILE = Path("state.json")
TG_TOKEN   = os.environ["TG_TOKEN"]
TG_CHAT    = os.environ["TG_CHAT"]
HEADERS    = {"User-Agent": "Mozilla/5.0 (compatible; dergipark-watcher/1.0)"}
ERROR_RATE_LIMIT_HOURS = 24


def fetch(url):
    r = requests.get(url, timeout=30, headers=HEADERS)
    r.raise_for_status()
    return r.text


def is_open(html):
    return not any(m in html for m in CLOSED_MARKERS)


def notify(text):
    r = requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        json={"chat_id": TG_CHAT, "text": text, "parse_mode": "Markdown",
              "disable_web_page_preview": False},
        timeout=15,
    )
    r.raise_for_status()


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def hours_since(iso_str):
    if not iso_str:
        return float("inf")
    delta = datetime.now(timezone.utc) - datetime.fromisoformat(iso_str)
    return delta.total_seconds() / 3600


def main():
    state = json.loads(STATE_FILE.read_text(encoding="utf-8")) if STATE_FILE.exists() else {}
    state.setdefault("_meta", {})
    errors_today = []

    for slug, j in JOURNALS.items():
        prev = state.get(slug, {})
        try:
            html = fetch(j["url"])
        except Exception as e:
            err_key = f"err_{slug}"
            last_err = state["_meta"].get(err_key)
            if hours_since(last_err) >= ERROR_RATE_LIMIT_HOURS:
                errors_today.append(f"• {j['name']}: {type(e).__name__}")
                state["_meta"][err_key] = now_iso()
            print(f"FETCH FAIL {slug}: {e}", file=sys.stderr)
            continue

        now_open = is_open(html)
        was_open = prev.get("open")
        state[slug] = {"open": now_open, "checked_at": now_iso()}

        if was_open is None:
            print(f"INIT {slug} = {'acik' if now_open else 'kapali'}")
            continue

        if was_open != now_open:
            emoji = "🟢" if now_open else "🔴"
            durum = "AÇILDI" if now_open else "kapandı"
            notify(f"{emoji} *{j['name']}* {durum}\n{j['url']}")
            print(f"CHANGED {slug}: {was_open} -> {now_open}")
        else:
            print(f"NOCHANGE {slug} = {'acik' if now_open else 'kapali'}")

    if errors_today:
        notify("⚠️ *DergiPark watcher hata*\n" + "\n".join(errors_today))

    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
