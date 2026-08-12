import os, math, datetime, subprocess, json, urllib.request, urllib.parse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------- config / secrets ----------
TG_TOKEN   = os.environ["TELEGRAM_TOKEN"].strip()
CHAT       = os.environ["TELEGRAM_CHAT_ID"].strip()
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

W, H = 1080, 1350
GOLD=(239,186,78); NAVY=(7,6,24); WHITE=(247,247,250); MUTED=(150,152,168)
CTX=(206,209,220); PURPLE=(150,90,230,255); FIRE=(230,120,40,255)

def http_get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"hitslab/1"}), timeout=45).read()

def F(sz, b=True):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()

# ---------- assets ----------
open("logo.png","wb").write(http_get("https://chiexfanwfifoyqviyor.supabase.co/storage/v1/object/public/Products/LOGO_FONDO_TRANSPARENTE.png"))
LOGO = Image.open("logo.png").convert("RGBA")

# ---------- theme bank (verified card ids) ----------
THEMES = [
 {"title":"BASE SET","sub":["Los clásicos que","empezaron todo."],"kicker":"CLÁSICO ETERNO","glow":GOLD+(95,),
  "cards":[("base1/4","Charizard","Base Set · 1999","El más buscado de todos los tiempos, ilustrado por Mitsuhiro Arita."),
           ("base1/2","Blastoise","Base Set · 1999","Parte de la trinidad legendaria de la primera generación."),
           ("base1/15","Venusaur","Base Set · 1999","Clásico absoluto y pieza clave de cualquier colección.")]},
 {"title":"EVOLVING SKIES","sub":["Las alt arts que","hicieron historia."],"kicker":"ALT ART · EVOLVING SKIES","glow":PURPLE,
  "cards":[("swsh7/215","Umbreon VMAX","Evolving Skies · Alt Art","La 'Moonbreon': una de las alt arts más buscadas del hobby."),
           ("swsh7/211","Sylveon VMAX","Evolving Skies · Alt Art","Elegancia pura, de las más queridas del set."),
           ("swsh7/209","Glaceon VMAX","Evolving Skies · Alt Art","Frío y espectacular, un fan favorite total.")]},
 {"title":"CHARIZARD","sub":["El rey indiscutible","del hobby."],"kicker":"EL REY DEL HOBBY","glow":FIRE,
  "cards":[("base1/4","Charizard","Base Set · 1999","El original del 99, ilustrado por Mitsuhiro Arita."),
           ("sm115/9","Charizard-GX","Hidden Fates","De un set de culto y de los más buscados de su era."),
           ("swsh35/74","Charizard VMAX","Champion's Path","Rainbow, brillo total. Un grial moderno.")]},
 {"title":"LEGENDARIOS","sub":["Dragones y bestias","de leyenda."],"kicker":"GRAIL DEL HOBBY","glow":PURPLE,
  "cards":[("swsh7/218","Rayquaza VMAX","Evolving Skies · Alt Art","El dragón que todo coleccionista quiere en su binder."),
           ("swsh7/215","Umbreon VMAX","Evolving Skies · Alt Art","La legendaria 'Moonbreon'."),
           ("swsh35/74","Charizard VMAX","Champion's Path","Rainbow rare, un grial moderno.")]},
]

def pick_theme():
    return THEMES[datetime.date.today().toordinal() % len(THEMES)]

# ---------- gemini (copy) ----------
def gemini_caption(theme):
    if not GEMINI_KEY: return None
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_KEY)
        cards = ", ".join(c[1] for c in theme["cards"])
        prompt = (f"Eres el community manager de HITS LAB, tienda mexicana de cartas Pokémon. "
                  f"Escribe SOLO el caption de Instagram (español mexicano) para un carrusel titulado '{theme['title']}' "
                  f"con estas cartas: {cards}. Tono emocionante y de marca. NO inventes precios ni estadísticas. "
                  f"Incluye CTA a hitslabtcg.com y 6-8 hashtags al final. Máximo 400 caracteres antes de los hashtags. "
                  f"Devuelve solo el caption, sin comillas.")
        r = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        t = (r.text or "").strip()
        return t if len(t) > 20 else None
    except Exception as e:
        print("Gemini fallback:", e); return None

def fallback_caption(theme):
    cards = " · ".join(c[1] for c in theme["cards"])
    return (f"✨ {theme['title']} — {cards}.\n\n"
            f"En HITS LAB tienes de todo tipo de Pokémon: sellado, singles, hits y pronto graduadas. "
            f"Las mejores cartas en un solo lugar.\n\n🛒 hitslabtcg.com\n\n"
            f"#Pokemon #PokemonTCG #HitsLab #TCGMexico #CartasPokemon #Coleccionismo")

# ---------- render ----------
def logo_c(img, y, h, cx=W//2):
    lw=int(LOGO.width*h/LOGO.height); r=LOGO.resize((lw,h)); img.paste(r,(cx-lw//2,y),r)

def wrap(dr,t,f,mw):
    o=[]; c=""
    for w in t.split():
        tt=(c+" "+w).strip()
        if dr.textlength(tt,font=f)<=mw: c=tt
        else: o.append(c); c=w
    if c: o.append(c)
    return o

def cover(theme,fn):
    top=(24,16,54); bot=(4,3,12); g=Image.new("RGB",(1,H)); q=g.load()
    for y in range(H):
        t=y/H; q[0,y]=(int(top[0]+(bot[0]-top[0])*t),int(top[1]+(bot[1]-top[1])*t),int(top[2]+(bot[2]-top[2])*t))
    base=g.resize((W,H)).convert("RGBA")
    gl=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(gl).ellipse([300,-150,900,520],fill=theme["glow"])
    base=Image.alpha_composite(base,gl.filter(ImageFilter.GaussianBlur(160)))
    dr=ImageDraw.Draw(base); logo_c(base,90,168)
    def tg(xy,txt,f,fill,gc,bl=22):
        L=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(L).text(xy,txt,font=f,fill=gc,anchor="mm")
        base.alpha_composite(L.filter(ImageFilter.GaussianBlur(bl))); ImageDraw.Draw(base).text(xy,txt,font=f,fill=fill,anchor="mm")
    dr.text((W//2,500),"COLECCIÓN LEYENDA",font=F(30),fill=GOLD,anchor="mm")
    fs=118 if dr.textlength(theme["title"],font=F(118))<=W-120 else 84
    tg((W//2,640),theme["title"],F(fs),WHITE,(150,90,230,255))
    dr.line([W//2-190,720,W//2+190,720],fill=GOLD,width=4)
    for i,ln in enumerate(theme["sub"]):
        dr.text((W//2,790+i*52),ln,font=F(36,False),fill=CTX,anchor="mm")
    dr.text((W//2,H-140),"DESLIZA  →",font=F(34),fill=GOLD,anchor="mm")
    base.convert("RGB").save(fn)

def card_slide(theme,card,idx,total,fn):
    cid,name,setr,note=card
    open("c.png","wb").write(http_get(f"https://images.pokemontcg.io/{cid}_hires.png"))
    ci=Image.open("c.png").convert("RGBA")
    img=Image.new("RGB",(W,H),NAVY).convert("RGBA")
    ch=680; cw=int(ci.width*ch/ci.height); cx,cy=60,290
    gl=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(gl).rectangle([cx-20,cy-20,cx+cw+20,cy+ch+20],fill=GOLD+(70,))
    img=Image.alpha_composite(img,gl.filter(ImageFilter.GaussianBlur(55))); dr=ImageDraw.Draw(img)
    dr.rectangle([0,0,14,H],fill=GOLD)
    lw=int(LOGO.width*100/LOGO.height); r=LOGO.resize((lw,100)); img.paste(r,(52,46),r)
    dr.text((W-60,74),f"{idx} / {total}",font=F(26),fill=GOLD,anchor="ra")
    dr.line([54,178,W-54,178],fill=GOLD,width=2)
    dr.text((60,205),theme["kicker"],font=F(26),fill=GOLD)
    rc=ci.resize((cw,ch)); img.paste(rc,(cx,cy),rc); dr.rectangle([cx-4,cy-4,cx+cw+4,cy+ch+4],outline=GOLD,width=4)
    x0=cx+cw+48; rw=W-56-x0; y=360
    for ln in wrap(dr,name.upper(),F(48),rw): dr.text((x0,y),ln,font=F(48),fill=WHITE); y+=56
    y+=8; dr.text((x0,y),setr,font=F(26),fill=GOLD); y+=58
    for ln in wrap(dr,note,F(29,False),rw): dr.text((x0,y),ln,font=F(29,False),fill=CTX); y+=41
    dr.line([54,H-140,W-54,H-140],fill=GOLD,width=2)
    dr.text((60,H-108),"hitslabtcg.com",font=F(27,False),fill=MUTED)
    img.convert("RGB").save(fn)

def cierre(idx,total,fn):
    img=Image.new("RGB",(W,H),NAVY); dr=ImageDraw.Draw(img)
    dr.rectangle([0,0,14,H],fill=GOLD); dr.text((W-60,66),f"{idx} / {total}",font=F(26),fill=GOLD,anchor="ra")
    logo_c(img,150,175)
    dr.text((W//2,455),"LAS MEJORES CARTAS",font=F(58),fill=WHITE,anchor="mm")
    dr.text((W//2,529),"EN UN SOLO LUGAR",font=F(58),fill=GOLD,anchor="mm")
    for i,ln in enumerate(["Todo tipo de Pokémon:","sellado · singles · hits · pronto graduadas"]):
        dr.text((W//2,630+i*48),ln,font=F(29,False),fill=CTX,anchor="mm")
    dr.rounded_rectangle([W//2-330,790,W//2+330,890],radius=16,fill=GOLD)
    dr.text((W//2,840),"HITSLABTCG.COM",font=F(44),fill=NAVY,anchor="mm")
    dr.text((W//2,960),"@hits_lab",font=F(30),fill=GOLD,anchor="mm")
    img.save(fn)

def ps(idx,total,fn):
    img=Image.new("RGB",(W,H),NAVY); dr=ImageDraw.Draw(img)
    dr.rectangle([0,0,14,H],fill=GOLD); dr.text((W-60,60),f"{idx} / {total}",font=F(26),fill=GOLD,anchor="ra")
    dr.text((W//2,300),"P. D.",font=F(40),fill=MUTED,anchor="mm")
    cxm=W//2; dr.polygon([(cxm+18,380),(cxm-42,520),(cxm-4,520),(cxm-24,620),(cxm+52,470),(cxm+8,470)],fill=GOLD)
    dr.text((W//2,720),"DESBLOQUEA EL JUEGO",font=F(56),fill=WHITE,anchor="mm")
    dr.text((W//2,800),"Al comprar en HITS LAB TCG",font=F(30,False),fill=CTX,anchor="mm")
    dr.text((W//2,880),"HITSLABTCG.COM",font=F(50),fill=GOLD,anchor="mm")
    img.save(fn)

# ---------- host + telegram ----------
def uguu(path):
    for _ in range(3):
        r=subprocess.run(["curl","-s","--max-time","60","-F",f"files[]=@{path}","https://uguu.se/upload.php"],capture_output=True,text=True)
        try: return json.loads(r.stdout)["files"][0]["url"]
        except: pass
    raise RuntimeError("upload fail")

def send_album(urls, caption):
    media=[{"type":"photo","media":u} for u in urls]; media[0]["caption"]=caption
    data=urllib.parse.urlencode({"chat_id":CHAT,"media":json.dumps(media)}).encode()
    urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{TG_TOKEN}/sendMediaGroup",data=data),timeout=60)

# ---------- main ----------
def main():
    theme=pick_theme(); total=6; files=[]
    cover(theme,"car_1.png")
    for i,card in enumerate(theme["cards"]): card_slide(theme,card,i+2,total,f"car_{i+2}.png")
    cierre(5,total,"car_5.png"); ps(6,total,"car_6.png")
    urls=[]
    for i in range(1,7):
        Image.open(f"car_{i}.png").convert("RGB").save(f"car_{i}.jpg","JPEG",quality=90)
        urls.append(uguu(f"car_{i}.jpg"))
    caption=gemini_caption(theme) or fallback_caption(theme)
    caption="🔥 POST DE HOY (borrador, no publicado)\n\n"+caption+'\n\n—\nSi te late, dime VA y lo subo.'
    send_album(urls, caption[:1020])
    print("Enviado a Telegram. Tema:", theme["title"])

if __name__=="__main__":
    main()
