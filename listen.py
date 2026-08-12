import os, json, re, subprocess, datetime, urllib.request, urllib.parse

TG       = os.environ["TELEGRAM_TOKEN"].strip()
CHAT     = os.environ["TELEGRAM_CHAT_ID"].strip()
IG_TOKEN = os.environ["IG_TOKEN"].strip()
IG_ID    = os.environ["IG_USER_ID"].strip()
STATE    = "state.json"
CDMX_OFFSET = 6  # UTC-6, sin horario de verano

def tg(method, **params):
    data = urllib.parse.urlencode(params).encode()
    return json.load(urllib.request.urlopen(f"https://api.telegram.org/bot{TG}/{method}", data=data, timeout=60))

APPROVE = re.compile(r"(^|\s)(va|ok|okey|okay|s[uú]belo|s[uú]bela|sube|publica|dale|listo)(\s|$|,|\.|!)", re.I)
EDIT    = re.compile(r"(cambia|c[aá]mbiale|ponle|edita|quita|agrega)", re.I)

def load_state():
    try:
        return json.load(open(STATE))
    except:
        return {"pending": None}

def save_state(s):
    json.dump(s, open(STATE, "w"))

def parse_hour(text):
    m = re.search(r"(?:a\s*las?\s*)?(\d{1,2})\s*(?::00)?\s*(am|pm|hrs|h)?", text, re.I)
    if not m: return None
    h = int(m.group(1)); ap = (m.group(2) or "").lower()
    if ap == "pm" and h < 12: h += 12
    elif ap == "am" and h == 12: h = 0
    elif not ap and 1 <= h <= 11: h += 12   # sin am/pm asumimos tarde/noche
    return h if 0 <= h <= 23 else None

def target_epoch(hour):
    now = datetime.datetime.utcnow()
    cdmx = now - datetime.timedelta(hours=CDMX_OFFSET)
    tgt = cdmx.replace(hour=hour, minute=0, second=0, microsecond=0)
    if tgt <= cdmx:  # ya pasó hoy -> publicar ya
        return now.timestamp()
    return (tgt + datetime.timedelta(hours=CDMX_OFFSET)).timestamp()

def clean_caption(cap):
    out = []
    for ln in (cap or "").splitlines():
        if ln.startswith("🔥 POST DE HOY"): continue
        if ln.strip() == "—": continue
        if ln.startswith("Si te late"): continue
        out.append(ln)
    return "\n".join(out).strip()

def custom_caption(text):
    t = re.sub(APPROVE, " ", text)
    t = re.sub(r"(a\s*las?\s*)?\d{1,2}\s*(:00)?\s*(am|pm|hrs|h)?", " ", t, flags=re.I)
    t = re.sub(r"\b(hora|de|m[eé]xico|mexico|y|lo|la|sube|subir)\b", " ", t, flags=re.I)
    t = t.strip(" ,.-")
    return t if len(t) > 15 else None

def download_photo(file_id):
    fp = tg("getFile", file_id=file_id)["result"]["file_path"]
    open("pub.jpg","wb").write(urllib.request.urlopen(f"https://api.telegram.org/file/bot{TG}/{fp}", timeout=60).read())

def uguu(path):
    for _ in range(3):
        r = subprocess.run(["curl","-s","--max-time","60","-F",f"files[]=@{path}","https://uguu.se/upload.php"], capture_output=True, text=True)
        try: return json.loads(r.stdout)["files"][0]["url"]
        except: pass
    raise RuntimeError("upload fail")

def ig_publish(image_url, caption):
    base = f"https://graph.instagram.com/v21.0/{IG_ID}"
    def post(path, **p):
        p["access_token"] = IG_TOKEN
        return json.load(urllib.request.urlopen(urllib.request.Request(base+path, data=urllib.parse.urlencode(p).encode()), timeout=90))
    cont = post("/media", image_url=image_url, caption=caption)
    return post("/media_publish", creation_id=cont["id"])

def publish(pending):
    download_photo(pending["file_id"])
    url = uguu("pub.jpg")
    ig_publish(url, pending["caption"])

def main():
    st = load_state()
    ups = tg("getUpdates")["result"]
    last = ups[-1]["update_id"] if ups else None
    for u in ups:
        m = u.get("message", {})
        if str(m.get("chat", {}).get("id")) != CHAT: continue
        text  = (m.get("text") or "").strip()
        reply = m.get("reply_to_message")
        if reply and reply.get("photo") and APPROVE.search(text):
            fid = reply["photo"][-1]["file_id"]
            cap = custom_caption(text) or clean_caption(reply.get("caption", ""))
            hour = parse_hour(text)
            tgt  = target_epoch(hour) if hour is not None else datetime.datetime.utcnow().timestamp()
            st["pending"] = {"file_id": fid, "caption": cap, "target": tgt}
            hh = int((datetime.datetime.utcfromtimestamp(tgt) - datetime.timedelta(hours=CDMX_OFFSET)).hour)
            if tgt > datetime.datetime.utcnow().timestamp() + 60:
                tg("sendMessage", chat_id=CHAT, text=f"✅ Agendado. Lo subo a las {hh}:00 (hora MX).")
            else:
                tg("sendMessage", chat_id=CHAT, text="✅ ¡Va! Publicando en un momento…")
        elif EDIT.search(text):
            tg("sendMessage", chat_id=CHAT, text="✏️ Los cambios por chat aún los estoy afinando. Por ahora: responde VA (o 'VA' + tu texto) para publicar.")
    # ¿toca publicar un pendiente?
    p = st.get("pending")
    if p and datetime.datetime.utcnow().timestamp() >= p["target"]:
        try:
            publish(p); tg("sendMessage", chat_id=CHAT, text="✅ ¡Publicado en Instagram! 🔥")
        except Exception as e:
            tg("sendMessage", chat_id=CHAT, text="❌ No se pudo publicar: " + str(e)[:250])
        st["pending"] = None
    save_state(st)
    if last is not None:
        tg("getUpdates", offset=last + 1)

if __name__ == "__main__":
    main()
