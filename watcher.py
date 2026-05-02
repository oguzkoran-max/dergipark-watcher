import requests, json, os, sys, re
from pathlib import Path
from datetime import datetime, timezone, date, timedelta

# ---- Dergi listesi (zenginleştirilmiş metadata) ----
JOURNALS = {
    "soylem": {
        "name": "Söylem Filoloji",
        "url": "https://dergipark.org.tr/tr/pub/soylemdergi",
        "indexes": ["TR Dizin", "MLA", "EBSCO", "ERIH PLUS"],
        "paid": False, "duration_days": 119, "issues_per_year": 4,
        "critical_for": "Boccaccio-Bergson",
    },
    "iulitera": {
        "name": "Litera (İstanbul Ü.)",
        "url": "https://dergipark.org.tr/tr/pub/iulitera",
        "indexes": ["MLA", "ESCI", "Scopus", "DOAJ", "ERIH PLUS", "EBSCO"],
        "paid": False, "duration_days": None, "issues_per_year": 2,
        "critical_for": "Pavese İntihar",
    },
    "deuefad": {
        "name": "Dokuz Eylül Ü. EFD",
        "url": "https://dergipark.org.tr/tr/pub/deuefad",
        "indexes": ["TR Dizin", "MLA", "SOBIAD"],
        "paid": False, "duration_days": None, "issues_per_year": 2,
        "critical_for": "Sciascia A planı",
    },
    "diledeara": {
        "name": "Dil ve Edebiyat Araştırmaları",
        "url": "https://dergipark.org.tr/tr/pub/diledeara",
        "indexes": ["TR Dizin", "MLA", "ESCI", "Scopus", "DOAJ", "ERIH PLUS"],
        "paid": None, "duration_days": 155, "issues_per_year": 2,
        "critical_for": "Sciascia B planı",
    },
    "eeder": {
        "name": "Edebî Eleştiri Dergisi",
        "url": "https://dergipark.org.tr/tr/pub/eeder",
        "indexes": ["TR Dizin", "MLA"],
        "paid": None, "duration_days": None, "issues_per_year": 2,
        "critical_for": None,
        "warning": "Sistem otomatik kapanma durumu olabilir, sayfayı doğrula",
    },
    "humanitas": {
        "name": "Humanitas (NKÜ)",
        "url": "https://dergipark.org.tr/tr/pub/humanitas",
        "indexes": ["TR Dizin", "MLA", "EBSCO", "ERIH PLUS", "Index Copernicus"],
        "paid": None, "duration_days": 162, "issues_per_year": 2,
        "critical_for": None,
    },
    "sosbilder": {
        "name": "Uludağ FEF Sos. Bil.",
        "url": "https://dergipark.org.tr/tr/pub/sosbilder",
        "indexes": ["TR Dizin", "MLA", "EBSCO", "Index Copernicus", "SOBIAD"],
        "paid": None, "duration_days": None, "issues_per_year": 2,
        "critical_for": None,
    },
    "cankujhss": {
        "name": "Çankaya CUJHSS",
        "url": "https://dergipark.org.tr/tr/pub/cankujhss",
        "indexes": ["TR Dizin", "MLA", "EBSCO", "ERIH PLUS"],
        "paid": None, "duration_days": 180, "issues_per_year": None,
        "critical_for": None,
    },
    "sefad": {
        "name": "SEFAD (Selçuk Ü.)",
        "url": "https://dergipark.org.tr/tr/pub/sefad",
        "indexes": ["ESCI", "DOAJ", "MLA", "EBSCO", "Index Copernicus"],
        "paid": None, "duration_days": None, "issues_per_year": 2,
        "critical_for": None,
    },
    "suitder": {
        "name": "SUİTDER (SDÜ)",
        "url": "https://dergipark.org.tr/tr/pub/suitder",
        "indexes": ["TR Dizin", "MLA", "ERIH PLUS", "DOAJ"],
        "paid": None, "duration_days": 188, "issues_per_year": 2,
        "critical_for": None,
    },
    "litandhum": {
        "name": "Edebiyat ve Beşeri Bilimler",
        "url": "https://dergipark.org.tr/tr/pub/literatureandhumanities",
        "indexes": ["TR Dizin", "DOAJ"],
        "paid": None, "duration_days": None, "issues_per_year": 3,
        "critical_for": None,
        "warning": "1 Oca 2026'dan beri sadece İngilizce makale alıyor",
    },
    "udekad": {
        "name": "UDEKAD",
        "url": "https://dergipark.org.tr/tr/pub/udekad",
        "indexes": ["TR Dizin", "MLA", "ERIH PLUS", "Index Copernicus"],
        "paid": True, "fee_note": "6.000 TL",
        "duration_days": 115, "issues_per_year": 4, "critical_for": None,
    },
    "dtcf": {
        "name": "Ankara Ü. DTCF",
        "url": "https://dergipark.org.tr/tr/pub/dtcfdergisi",
        "indexes": ["DOAJ"],
        "paid": None, "duration_days": 274, "issues_per_year": 2,
        "critical_for": None,
    },
    "huefd": {
        "name": "Hacettepe Ü. EFD",
        "url": "https://dergipark.org.tr/tr/pub/huefd",
        "indexes": [],
        "paid": None, "duration_days": None, "issues_per_year": 2,
        "critical_for": None,
    },
    "nesir": {
        "name": "Nesir",
        "url": "https://dergipark.org.tr/tr/pub/nesir",
        "indexes": ["DOAJ"],
        "paid": None, "duration_days": None, "issues_per_year": 2,
        "critical_for": None,
    },
    "ceviri": {
        "name": "Çeviribilim ve Uygulamaları",
        "url": "https://dergipark.org.tr/tr/pub/ceviri",
        "indexes": ["TR Dizin", "MLA"],
        "paid": False, "duration_days": None, "issues_per_year": 2,
        "critical_for": None,
    },
    "dilder": {
        "name": "Dil Dergisi (TÖMER)",
        "url": "https://dergipark.org.tr/tr/pub/dilder",
        "indexes": ["TR Dizin", "MLA", "CEEOL", "SOBIAD"],
        "paid": None, "duration_days": 216, "issues_per_year": 2,
        "critical_for": None,
    },
    "trkede": {
        "name": "Trakya Ü. EFD",
        "url": "https://dergipark.org.tr/tr/pub/trkede",
        "indexes": ["TR Dizin", "MLA", "EBSCO", "SOBIAD"],
        "paid": None, "duration_days": None, "issues_per_year": 2,
        "critical_for": None,
    },
    "dilarast": {
        "name": "Dil Araştırmaları",
        "url": "https://dergipark.org.tr/tr/pub/dilarastirmalari",
        "indexes": ["TR Dizin", "MLA", "ESCI", "Scopus", "DOAJ"],
        "paid": None, "duration_days": 217, "issues_per_year": 2,
        "critical_for": None,
    },
    "bilig": {
        "name": "bilig (Türk Dünyası)",
        "url": "https://dergipark.org.tr/tr/pub/bilig",
        "indexes": ["TR Dizin", "SSCI", "Scopus"],
        "paid": None, "duration_days": None, "issues_per_year": 4,
        "critical_for": None,
    },
    "fe": {
        "name": "Folklor/Edebiyat",
        "url": "https://dergipark.org.tr/tr/pub/fe",
        "indexes": ["TR Dizin", "ESCI", "DOAJ"],
        "paid": None, "duration_days": None, "issues_per_year": 4,
        "critical_for": None,
    },
}

CLOSED_MARKERS = ["Makale Gönderimine Kapalı"]
OPEN_DATE_PATTERN = re.compile(
    r"Makale\s+Gönderimine\s+Açılacak\s+Tarih[:\s]+(\d{1,2})\s+(\w+)\s+(\d{4})",
    re.IGNORECASE,
)
ISSUE_PATTERN = re.compile(r"Cilt[:\s]+(\d+)\s*[,·]?\s*Sayı[:\s]+(\d+)", re.IGNORECASE)
TR_MONTHS = {
    "ocak": 1, "şubat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "haziran": 6,
    "temmuz": 7, "ağustos": 8, "eylül": 9, "ekim": 10, "kasım": 11, "aralık": 12,
}
TR_TO_ASCII = str.maketrans("ıİğĞşŞçÇöÖüÜ", "iIgGsScCoOuU")

STATE_FILE = Path("state.json")
TG_TOKEN   = os.environ["TG_TOKEN"]
TG_CHAT    = os.environ["TG_CHAT"]
HEADERS    = {"User-Agent": "Mozilla/5.0 (compatible; dergipark-watcher/2.0)"}
ERROR_RATE_LIMIT_HOURS = 24


def fetch(url):
    r = requests.get(url, timeout=30, headers=HEADERS)
    r.raise_for_status()
    return r.text


def is_open(html):
    return not any(m in html for m in CLOSED_MARKERS)


def parse_open_date(html):
    m = OPEN_DATE_PATTERN.search(html)
    if not m:
        return None
    try:
        day = int(m.group(1))
        month = TR_MONTHS.get(m.group(2).lower())
        year = int(m.group(3))
        if not month:
            return None
        return date(year, month, day).isoformat()
    except (ValueError, AttributeError):
        return None


def parse_latest_issue(html):
    m = ISSUE_PATTERN.search(html)
    if not m:
        return None
    return f"Cilt {m.group(1)} Sayı {m.group(2)}"


def notify(text, disable_preview=True):
    requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        json={"chat_id": TG_CHAT, "text": text, "parse_mode": "Markdown",
              "disable_web_page_preview": disable_preview},
        timeout=15,
    ).raise_for_status()


def get_updates(offset=None):
    params = {"timeout": 0}
    if offset is not None:
        params["offset"] = offset
    r = requests.get(
        f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates",
        params=params, timeout=15,
    )
    r.raise_for_status()
    return r.json().get("result", [])


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def hours_since(iso_str):
    if not iso_str:
        return float("inf")
    return (datetime.now(timezone.utc) - datetime.fromisoformat(iso_str)).total_seconds() / 3600


def days_until(iso_date_str):
    if not iso_date_str:
        return None
    try:
        return (date.fromisoformat(iso_date_str) - date.today()).days
    except ValueError:
        return None


def normalize_command(text):
    return text.translate(TR_TO_ASCII).lower()


def journal_meta_line(meta):
    parts = []
    indexes = meta.get("indexes", [])
    if indexes:
        priority = ["TR Dizin", "MLA", "ESCI", "Scopus", "SSCI", "DOAJ"]
        sorted_idx = sorted(indexes, key=lambda x: (priority.index(x) if x in priority else 99, x))
        shown = sorted_idx[:3]
        if len(sorted_idx) > 3:
            shown = sorted_idx[:3] + [f"+{len(sorted_idx)-3}"]
        parts.append(" + ".join(shown))
    if meta.get("paid") is True:
        parts.append(meta.get("fee_note") or "Ücretli")
    elif meta.get("paid") is False:
        parts.append("Ücretsiz")
    if meta.get("duration_days"):
        parts.append(f"{meta['duration_days']} gün")
    return " · ".join(parts) if parts else None


def list_by_status(state, want_open):
    return [(slug, j) for slug, j in JOURNALS.items()
            if state.get(slug, {}).get("open") == want_open]


def handle_command(text, state):
    parts = text.strip().split()
    if not parts:
        return None
    cmd = normalize_command(parts[0].split("@")[0])
    args = parts[1:]

    if cmd == "/acik":
        items = list_by_status(state, True)
        if not items:
            return "Şu an hiçbir dergi açık değil."
        lines = [f"🟢 *{len(items)} dergi açık:*", ""]
        lines += [f"• [{j['name']}]({j['url']})" for _, j in items]
        return "\n".join(lines)

    if cmd == "/kapali":
        items = list_by_status(state, False)
        if not items:
            return "Şu an hiçbir dergi kapalı değil."
        lines = [f"🔴 *{len(items)} dergi kapalı:*", ""]
        for slug, j in items:
            extra = ""
            od = state.get(slug, {}).get("open_date")
            if od:
                d = days_until(od)
                if d is not None and d >= 0:
                    extra = f" — {d} gün sonra"
            lines.append(f"• [{j['name']}]({j['url']}){extra}")
        return "\n".join(lines)

    if cmd == "/durum":
        op = list_by_status(state, True)
        cl = list_by_status(state, False)
        lines = [f"📊 *Toplam {len(JOURNALS)} dergi izleniyor*", ""]
        lines.append(f"🟢 *Açık ({len(op)}):*")
        lines += ([f"• [{j['name']}]({j['url']})" for _, j in op] or ["(yok)"])
        lines += ["", f"🔴 *Kapalı ({len(cl)}):*"]
        lines += ([f"• [{j['name']}]({j['url']})" for _, j in cl] or ["(yok)"])
        return "\n".join(lines)

    if cmd == "/takip":
        op_count = sum(1 for s in JOURNALS if state.get(s, {}).get("open") is True)
        cl_count = sum(1 for s in JOURNALS if state.get(s, {}).get("open") is False)
        last = max((state.get(s, {}).get("checked_at", "") for s in JOURNALS), default="")
        last_str = (last[:16] + " UTC") if last else "henüz yok"
        return (f"📊 *Bot {len(JOURNALS)} dergi izliyor*\n"
                f"🟢 {op_count} açık · 🔴 {cl_count} kapalı\n"
                f"Son kontrol: {last_str}")

    if cmd == "/dergi":
        if not args:
            return "Kullanım: `/dergi <slug>` (örn `/dergi soylem`)"
        slug = args[0].lower()
        if slug not in JOURNALS:
            return f"Bilinmeyen slug: `{slug}`. Geçerli slug listesini `/durum` ile görebilirsin."
        meta = JOURNALS[slug]
        s = state.get(slug, {})
        emoji = "🟢" if s.get("open") else "🔴"
        durum = "Açık" if s.get("open") else "Kapalı"
        lines = [f"{emoji} *{meta['name']}*", f"Şu an: {durum}"]
        ml = journal_meta_line(meta)
        if ml:
            lines.append(ml)
        if meta.get("issues_per_year"):
            lines.append(f"Yılda {meta['issues_per_year']} sayı")
        if meta.get("critical_for"):
            lines.append(f"📌 Aktif takip: {meta['critical_for']}")
        if meta.get("warning"):
            lines.append(f"⚠️ {meta['warning']}")
        od = s.get("open_date")
        if od and not s.get("open"):
            d = days_until(od)
            if d is not None and d >= 0:
                lines.append(f"📅 {od} tarihinde açılacak ({d} gün)")
        if s.get("latest_issue"):
            lines.append(f"📚 Son sayı: {s['latest_issue']}")
        if s.get("checked_at"):
            lines.append(f"_Son kontrol: {s['checked_at'][:16]} UTC_")
        lines.append(meta["url"])
        return "\n".join(lines)

    if cmd == "/kritik":
        items = [(slug, j) for slug, j in JOURNALS.items() if j.get("critical_for")]
        if not items:
            return "Kritik takip listesi boş."
        lines = ["📌 *Aktif takip dergileri:*", ""]
        for slug, j in items:
            s = state.get(slug, {})
            emoji = "🟢" if s.get("open") else "🔴"
            durum = "açık" if s.get("open") else "kapalı"
            extra = ""
            if not s.get("open") and s.get("open_date"):
                d = days_until(s["open_date"])
                if d is not None and d >= 0:
                    extra = f" — {d} gün sonra"
            lines.append(f"{emoji} *{j['name']}* ({durum}) — {j['critical_for']}{extra}")
        return "\n".join(lines)

    if cmd == "/yakin":
        upcoming = []
        for slug, j in JOURNALS.items():
            s = state.get(slug, {})
            if s.get("open"):
                continue
            od = s.get("open_date")
            if not od:
                continue
            d = days_until(od)
            if d is not None and 0 <= d <= 30:
                upcoming.append((d, slug, j, od))
        if not upcoming:
            return "30 gün içinde açılacağı bilinen dergi yok."
        upcoming.sort()
        lines = ["🟡 *30 gün içinde açılacaklar:*", ""]
        for d, slug, j, od in upcoming:
            lines.append(f"• [{j['name']}]({j['url']}) — {od} ({d} gün)")
        return "\n".join(lines)

    if cmd == "/indeks":
        if not args:
            return ("Kullanım: `/indeks <ad>`\n"
                    "Geçerli: tr, mla, esci, scopus, ssci, doaj, erih, ebsco, sobiad, copernicus")
        q = args[0].lower()
        qmap = {
            "tr": "TR Dizin", "trdizin": "TR Dizin",
            "mla": "MLA", "esci": "ESCI", "scopus": "Scopus", "ssci": "SSCI",
            "doaj": "DOAJ", "erih": "ERIH PLUS", "erihplus": "ERIH PLUS",
            "ebsco": "EBSCO", "sobiad": "SOBIAD", "copernicus": "Index Copernicus",
        }
        target = qmap.get(q)
        if not target:
            return f"Bilinmeyen indeks: `{q}`."
        items = [(slug, j) for slug, j in JOURNALS.items() if target in j.get("indexes", [])]
        if not items:
            return f"`{target}` indeksli dergi yok."
        lines = [f"🏷️ *{target}'li dergiler ({len(items)}):*", ""]
        for slug, j in items:
            emoji = "🟢" if state.get(slug, {}).get("open") else "🔴"
            lines.append(f"{emoji} [{j['name']}]({j['url']})")
        return "\n".join(lines)

    if cmd == "/sirala":
        with_d = [(j["duration_days"], slug, j) for slug, j in JOURNALS.items() if j.get("duration_days")]
        with_d.sort()
        without_d = [(slug, j) for slug, j in JOURNALS.items() if not j.get("duration_days")]
        lines = ["⚡ *Yayımlanma hızı (kısa → uzun):*", ""]
        for i, (days, slug, j) in enumerate(with_d, 1):
            emoji = "🟢" if state.get(slug, {}).get("open") else "🔴"
            paid = " (ücretli)" if j.get("paid") else ""
            lines.append(f"{i}. {emoji} *{j['name']}* — {days} gün{paid}")
        if without_d:
            lines.append("")
            lines.append(f"_Süre verisi yok ({len(without_d)})_")
            for slug, j in without_d:
                emoji = "🟢" if state.get(slug, {}).get("open") else "🔴"
                lines.append(f"• {emoji} {j['name']}")
        return "\n".join(lines)

    if cmd in ("/yardim", "/help", "/start"):
        return ("*DergiPark watcher komutları*\n\n"
                "• `/acik` — Açık dergiler\n"
                "• `/kapali` — Kapalı dergiler\n"
                "• `/durum` — Tam tablo\n"
                "• `/takip` — Toplam sayım\n"
                "• `/dergi <slug>` — Tek dergi detay\n"
                "• `/kritik` — Aktif takip dergileri\n"
                "• `/yakin` — 30 gün içinde açılacaklar\n"
                "• `/indeks <ad>` — İndekse göre filtre\n"
                "• `/sirala` — Hız sıralı liste\n"
                "• `/yardim` — Bu metin\n\n"
                "Otomatik bildirim 3 saatte bir + gece 00:00 garantili kontrol eder. "
                "Pazartesi 08:30'da haftalık özet gelir.")

    return None


def process_commands(state):
    last_id = state["_meta"].get("last_update_id", 0)
    offset = last_id + 1 if last_id else None
    try:
        updates = get_updates(offset)
    except Exception as e:
        print(f"COMMAND FETCH FAIL: {e}", file=sys.stderr)
        return
    for upd in updates:
        upd_id = upd.get("update_id", 0)
        if upd_id > last_id:
            last_id = upd_id
        msg = upd.get("message", {})
        text = msg.get("text", "")
        chat_id = str(msg.get("chat", {}).get("id", ""))
        if chat_id != TG_CHAT or not text.startswith("/"):
            continue
        reply = handle_command(text, state)
        if reply:
            try:
                notify(reply)
                print(f"CMD: {text[:30]}")
            except Exception as e:
                print(f"CMD REPLY FAIL: {e}", file=sys.stderr)
    state["_meta"]["last_update_id"] = last_id


def is_monday_morning_ist():
    now_ist = datetime.now(timezone.utc) + timedelta(hours=3)
    return now_ist.weekday() == 0 and now_ist.hour == 8 and 25 <= now_ist.minute <= 35


def weekly_summary(state):
    history = state.get("_history", [])
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent = [h for h in history if datetime.fromisoformat(h["at"]) >= week_ago]
    op = sum(1 for s in JOURNALS if state.get(s, {}).get("open") is True)
    cl = sum(1 for s in JOURNALS if state.get(s, {}).get("open") is False)
    lines = ["📊 *Haftalık özet*", ""]
    lines.append(f"Son 7 günde {len(recent)} durum değişimi:")
    if recent:
        for h in recent[-10:]:
            durum = "🟢 AÇILDI" if h["open"] else "🔴 kapandı"
            name = JOURNALS.get(h.get("slug", ""), {}).get("name", h.get("slug", ""))
            lines.append(f"• {h['at'][:10]} — {name} {durum}")
    else:
        lines.append("• Yok")
    lines.append("")
    lines.append(f"Şu an: 🟢 {op} açık · 🔴 {cl} kapalı")
    notify("\n".join(lines))


def append_history(state, slug, now_open):
    history = state.setdefault("_history", [])
    history.append({"at": now_iso(), "slug": slug, "open": now_open})
    if len(history) > 30:
        history[:] = history[-30:]


def main():
    state = json.loads(STATE_FILE.read_text(encoding="utf-8")) if STATE_FILE.exists() else {}
    state.setdefault("_meta", {})
    errors_today = []
    opened, closed_, new_issues = [], [], []

    for slug, j in JOURNALS.items():
        prev = state.get(slug, {})
        try:
            html = fetch(j["url"])
        except Exception as e:
            err_key = f"err_{slug}"
            if hours_since(state["_meta"].get(err_key)) >= ERROR_RATE_LIMIT_HOURS:
                errors_today.append(f"• {j['name']}: {type(e).__name__}")
                state["_meta"][err_key] = now_iso()
            print(f"FETCH FAIL {slug}: {e}", file=sys.stderr)
            continue

        now_open = is_open(html)
        was_open = prev.get("open")
        open_date = parse_open_date(html) if not now_open else None
        latest_issue = parse_latest_issue(html)

        ns = {"open": now_open, "checked_at": now_iso()}
        if open_date:
            ns["open_date"] = open_date
        if latest_issue:
            ns["latest_issue"] = latest_issue
        state[slug] = ns

        if latest_issue and prev.get("latest_issue") and prev["latest_issue"] != latest_issue:
            new_issues.append((slug, j, latest_issue))

        if was_open is None:
            print(f"INIT {slug} = {'acik' if now_open else 'kapali'}")
            continue
        if was_open != now_open:
            append_history(state, slug, now_open)
            (opened if now_open else closed_).append((slug, j))
            print(f"CHANGED {slug}: {was_open} -> {now_open}")
        else:
            print(f"NOCHANGE {slug} = {'acik' if now_open else 'kapali'}")

    # Açılış bildirimleri (toplu birleştirme)
    if len(opened) == 1:
        slug, j = opened[0]
        ml = journal_meta_line(j)
        msg = f"🟢 *{j['name']}* AÇILDI"
        if ml:
            msg += f"\n{ml}"
        if j.get("warning"):
            msg += f"\n⚠️ {j['warning']}"
        if j.get("critical_for"):
            msg += f"\n📌 {j['critical_for']}"
        msg += f"\n{j['url']}"
        notify(msg, disable_preview=False)
    elif len(opened) > 1:
        lines = [f"🟢 *Bu kontrolde {len(opened)} dergi açıldı:*", ""]
        for slug, j in opened:
            crit = f" 📌 {j['critical_for']}" if j.get("critical_for") else ""
            lines.append(f"• [{j['name']}]({j['url']}){crit}")
        notify("\n".join(lines))

    # Kapanış bildirimleri
    if len(closed_) == 1:
        slug, j = closed_[0]
        ml = journal_meta_line(j)
        msg = f"🔴 *{j['name']}* kapandı"
        if ml:
            msg += f"\n{ml}"
        msg += f"\n{j['url']}"
        notify(msg, disable_preview=False)
    elif len(closed_) > 1:
        lines = [f"🔴 *Bu kontrolde {len(closed_)} dergi kapandı:*", ""]
        for slug, j in closed_:
            lines.append(f"• [{j['name']}]({j['url']})")
        notify("\n".join(lines))

    # Yeni sayı bildirimleri
    for slug, j, issue in new_issues:
        notify(f"📚 *{j['name']}* yeni sayı yayımlandı: {issue}\n{j['url']}",
               disable_preview=False)

    # Komutları işle
    process_commands(state)

    # Hata bildirimi
    if errors_today:
        notify("⚠️ *DergiPark watcher hata*\n" + "\n".join(errors_today))

    # Pazartesi 08:30 haftalık özet
    today = date.today().isoformat()
    if is_monday_morning_ist() and state["_meta"].get("last_weekly_summary") != today:
        weekly_summary(state)
        state["_meta"]["last_weekly_summary"] = today

    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
