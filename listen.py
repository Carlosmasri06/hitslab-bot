import os, json, re, subprocess, urllib.request, urllib.parse

TG       = os.environ["TELEGRAM_TOKEN"].strip()
CHAT     = os.environ["TELEGRAM_CHAT_ID"].strip()
IG_TOKEN = os.environ["IG_TOKEN"].strip()
IG_ID    = os.environ["IG_USER_ID"].strip()

def tg(method, **params):
    data = urllib.parse.urlencode(params).encode()
    return json.load(urllib.request.urlopen(f"https://api.telegram.org/bot{TG}/{method}", data=data, timeout=60))

APPROVE = re.compile(r"(^|\s)(va|ok|okey|okay|s[uú]belo|s[uú]bela|sube|publica|dale|listo)(\s|$|,|\.|!)", re.I)
EDIT    = re.compile(r"(cambia|c[aá]mbiale|ponle|edita|quita|agrega|otra foto|otro texto)", re.I)

def clean_caption(cap):
    out = []
    for ln in (cap or "").splitlines():
        if ln.startswith("🔥 POST DE HOY"): continue
        if ln.strip() == "—": continue
        if ln.startswith("Si te late"): continue
        out.append(ln)
    return "\n".join(out).strip()

def download_photo(file_id):
    fp = tg("getFile", file_id=file_id)["result"]["file_path"]
    data = urllib.request.urlopen(f"https://api.telegram.org/file/bot{TG}/{fp}", timeout=60).read()
    open("pub.jpg", "wb").write(data)

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

def main():
    ups = tg("getUpdates")["result"]
    if not ups: return
    last = ups[-1]["update_id"]
    for u in ups:
        m = u.get("message", {})
        if str(m.get("chat", {}).get("id")) != CHAT: continue
        text  = (m.get("text") or "").strip()
        reply = m.get("reply_to_message")
        if reply and reply.get("photo") and APPROVE.search(text):
            fid = reply["photo"][-1]["file_id"]
            cap = clean_caption(reply.get("caption", ""))
            try:
                download_photo(fid)
                url = uguu("pub.jpg")
                ig_publish(url, cap)
                tg("sendMessage", chat_id=CHAT, text="✅ ¡Publicado en Instagram! 🔥")
            except Exception as e:
                tg("sendMessage", chat_id=CHAT, text="❌ No se pudo publicar: " + str(e)[:250])
        elif EDIT.search(text):
            tg("sendMessage", chat_id=CHAT, text="✏️ Los cambios por chat todavía los estoy afinando. Por ahora responde *VA* al post para publicarlo.")
    tg("getUpdates", offset=last + 1)  # confirma/limpia lo ya procesado

if __name__ == "__main__":
    main()
