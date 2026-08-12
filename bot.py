import os, math, random, datetime, subprocess, json, urllib.request, urllib.parse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TG_TOKEN   = os.environ["TELEGRAM_TOKEN"].strip()
CHAT       = os.environ["TELEGRAM_CHAT_ID"].strip()
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

W, H = 1080, 1350
GOLD=(239,186,78); NAVY=(7,6,24); WHITE=(247,247,250); MUTED=(150,152,168); CTX=(210,212,224)
BLUE=(58,160,255); RED=(255,80,96); GREEN=(74,222,150); PURPLE=(150,90,230)

def http_get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"hitslab/1"}), timeout=45).read()
def F(sz,b=True):
    p="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p,sz) if os.path.exists(p) else ImageFont.load_default()

open("logo.png","wb").write(http_get("https://chiexfanwfifoyqviyor.supabase.co/storage/v1/object/public/Products/LOGO_FONDO_TRANSPARENTE.png"))
LOGO=Image.open("logo.png").convert("RGBA")

POOL={
 "base1/4":("Charizard","Base Set · 1999","El más buscado de todos los tiempos."),
 "base1/2":("Blastoise","Base Set · 1999","Clásico de la primera generación."),
 "base1/15":("Venusaur","Base Set · 1999","Pieza clave de cualquier colección."),
 "swsh7/215":("Umbreon VMAX","Evolving Skies · Alt Art","La legendaria 'Moonbreon'."),
 "swsh7/211":("Sylveon VMAX","Evolving Skies · Alt Art","Elegancia pura, un fan favorite."),
 "swsh7/209":("Glaceon VMAX","Evolving Skies · Alt Art","Frío y espectacular."),
 "swsh7/218":("Rayquaza VMAX","Evolving Skies · Alt Art","El grial dragón del hobby."),
 "sm115/9":("Charizard-GX","Hidden Fates","De un set de culto."),
 "swsh35/74":("Charizard VMAX","Champion's Path","Rainbow, brillo total."),
}
def cimg(cid):
    open("t.png","wb").write(http_get(f"https://images.pokemontcg.io/{cid}_hires.png"))
    return Image.open("t.png").convert("RGBA")
def wrap(dr,t,f,mw):
    o=[];c=""
    for w in t.split():
        tt=(c+" "+w).strip()
        if dr.textlength(tt,font=f)<=mw:c=tt
        else:o.append(c);c=w
    if c:o.append(c)
    return o
def logo_c(img,y,h,cx=W//2):
    lw=int(LOGO.width*h/LOGO.height);r=LOGO.resize((lw,h));img.paste(r,(cx-lw//2,y),r)
def bg(accent):
    top=(24,16,54);bt=(4,3,12);g=Image.new("RGB",(1,H));q=g.load()
    for y in range(H):
        t=y/H;q[0,y]=(int(top[0]+(bt[0]-top[0])*t),int(top[1]+(bt[1]-top[1])*t),int(top[2]+(bt[2]-top[2])*t))
    b=g.resize((W,H)).convert("RGBA")
    gl=Image.new("RGBA",(W,H),(0,0,0,0));ImageDraw.Draw(gl).ellipse([250,-180,880,520],fill=accent+(90,))
    return Image.alpha_composite(b,gl.filter(ImageFilter.GaussianBlur(170)))
def pill(dr,cx,y,txt,fill,tcol,f):
    w=dr.textlength(txt,font=f);pad=34
    dr.rounded_rectangle([cx-w/2-pad,y-30,cx+w/2+pad,y+30],radius=30,fill=fill)
    dr.text((cx,y),txt,font=f,fill=tcol,anchor="mm")
def framed(img,ci,x,y,h,glow=GOLD):
    cw=int(ci.width*h/ci.height)
    gl=Image.new("RGBA",(W,H),(0,0,0,0));ImageDraw.Draw(gl).rectangle([x-16,y-16,x+cw+16,y+h+16],fill=glow+(80,))
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(45)))
    rc=ci.resize((cw,h));img.paste(rc,(x,y),rc);ImageDraw.Draw(img).rectangle([x-4,y-4,x+cw+4,y+h+4],outline=GOLD,width=4)
    return cw
def cta(dr,y=1250):
    dr.rounded_rectangle([W//2-330,y,W//2+330,y+96],radius=16,fill=GOLD)
    dr.text((W//2,y+48),"HITSLABTCG.COM",font=F(42),fill=NAVY,anchor="mm")

def f_carta_dia():
    cid=random.choice(list(POOL));name,setr,note=POOL[cid]
    img=bg(GOLD);dr=ImageDraw.Draw(img);logo_c(img,60,90)
    pill(dr,W//2,235,"CARTA DEL DIA",GOLD,NAVY,F(34))
    ci=cimg(cid);framed(img,ci,W//2-int(ci.width*640/ci.height)//2,300,640)
    dr=ImageDraw.Draw(img)
    dr.text((W//2,1010),name.upper(),font=F(58),fill=WHITE,anchor="mm")
    dr.text((W//2,1075),setr,font=F(30,False),fill=GOLD,anchor="mm")
    cta(dr,1170)
    img.convert("RGB").save("out_1.jpg","JPEG",quality=90)
    return ["out_1.jpg"], f"⭐ CARTA DEL DÍA: {name} ({setr}). {note}\n\nEncuéntrala y muchas más en 🛒 hitslabtcg.com\n\n#Pokemon #PokemonTCG #HitsLab #TCGMexico"

def f_cual_prefieres():
    a,b=random.sample(list(POOL),2)
    na=POOL[a][0];nb=POOL[b][0]
    img=bg(PURPLE);dr=ImageDraw.Draw(img);logo_c(img,55,80)
    dr.text((W//2,220),"¿CUÁL PREFIERES?",font=F(66),fill=WHITE,anchor="mm")
    dr.text((W//2,285),"comenta abajo",font=F(32,False),fill=GOLD,anchor="mm")
    ca=cimg(a);cb=cimg(b);h=560
    wa=framed(img,ca,70,420,h,BLUE)
    wb=framed(img,cb,W-70-int(cb.width*h/cb.height),420,h,RED)
    dr=ImageDraw.Draw(img)
    dr.ellipse([W//2-58,690,W//2+58,806],fill=GOLD);dr.text((W//2,748),"VS",font=F(46),fill=NAVY,anchor="mm")
    dr.text((W//2-70-wa//2,1030),na.upper(),font=F(28),fill=BLUE,anchor="mm")
    dr.text((W-70-wb//2,1030),nb.upper(),font=F(28),fill=RED,anchor="mm")
    cta(dr,1150)
    img.convert("RGB").save("out_1.jpg","JPEG",quality=90)
    return ["out_1.jpg"], f"🔥 ¿{na} o {nb}? ¿Cuál te llevas? Dinos en los comentarios 👇\n\nLas dos (y más) en 🛒 hitslabtcg.com\n\n#Pokemon #PokemonTCG #HitsLab #TCGMexico"

FACTS=[
 ("El Charizard del Base Set (1999) lo ilustró Mitsuhiro Arita.","base1/4"),
 ("La 'Moonbreon' es de las alt arts más buscadas del hobby moderno.","swsh7/215"),
 ("El Pikachu Illustrator es considerada la carta Pokémon más valiosa del mundo.",None),
 ("El Rayquaza VMAX Alt Art de Evolving Skies es un grial para los fans del dragón.","swsh7/218"),
 ("Las cartas 1st Edition del Base Set son de las más codiciadas por coleccionistas.","base1/4"),
]
def f_dato():
    fact,cid=random.choice(FACTS)
    img=bg(BLUE);dr=ImageDraw.Draw(img);logo_c(img,60,90)
    pill(dr,W//2,240,"¿SABÍAS QUE...?",BLUE,WHITE,F(34))
    y=360
    if cid:
        ci=cimg(cid);framed(img,ci,W//2-int(ci.width*470/ci.height)//2,330,470);y=880
    dr=ImageDraw.Draw(img)
    for ln in wrap(dr,fact,F(46),900):
        dr.text((W//2,y),ln,font=F(46),fill=WHITE,anchor="mm");y+=62
    cta(dr,1180)
    img.convert("RGB").save("out_1.jpg","JPEG",quality=90)
    return ["out_1.jpg"], f"🧠 DATO CURIOSO: {fact}\n\nMás mundo Pokémon en 🛒 hitslabtcg.com\n\n#Pokemon #PokemonTCG #DatoCurioso #HitsLab #TCGMexico"

def f_top5():
    ranked=[("swsh7/215","Umbreon VMAX"),("swsh7/218","Rayquaza VMAX"),("swsh7/211","Sylveon VMAX"),
            ("swsh7/209","Glaceon VMAX"),("swsh35/74","Charizard VMAX")]
    img=bg(RED);dr=ImageDraw.Draw(img);logo_c(img,55,80)
    dr.text((W//2,200),"TOP 5",font=F(84),fill=GOLD,anchor="mm")
    dr.text((W//2,270),"ALT ARTS QUE TODOS QUIEREN",font=F(34),fill=WHITE,anchor="mm")
    y=340;rh=170
    for i,(cid,nm) in enumerate(ranked):
        ci=cimg(cid);hh=140;cw=int(ci.width*hh/ci.height)
        img.paste(ci.resize((cw,hh)),(150,y+8),ci.resize((cw,hh)))
        dr=ImageDraw.Draw(img)
        dr.text((90,y+rh//2-30),f"#{i+1}",font=F(52),fill=GOLD,anchor="lm")
        dr.text((150+cw+30,y+rh//2-30),nm.upper(),font=F(38),fill=WHITE,anchor="lm")
        y+=rh
    cta(dr,y+10)
    img.convert("RGB").save("out_1.jpg","JPEG",quality=90)
    return ["out_1.jpg"], "🏆 TOP 5 ALT ARTS QUE TODOS QUIEREN. ¿Cuál es tu favorita? 👇\n\nCázalas en 🛒 hitslabtcg.com\n\n#Pokemon #PokemonTCG #AltArt #HitsLab #TCGMexico"

FORMATS=[f_carta_dia,f_cual_prefieres,f_dato,f_top5]

def gemini_caption(fmt_name, default):
    if not GEMINI_KEY: return default
    try:
        from google import genai
        c=genai.Client(api_key=GEMINI_KEY)
        p=(f"Eres el community manager de HITS LAB, tienda mexicana de cartas Pokémon. Reescribe este caption de Instagram "
           f"para el formato '{fmt_name}' en español mexicano, más divertido y viral, con emojis, sin inventar precios ni datos, "
           f"conservando el CTA a hitslabtcg.com y unos hashtags. Base: '{default}'. Devuelve solo el caption.")
        r=c.models.generate_content(model="gemini-2.5-flash",contents=p)
        t=(r.text or "").strip()
        return t if len(t)>20 else default
    except Exception as e:
        print("Gemini fallback:",e);return default

def uguu(path):
    for _ in range(3):
        r=subprocess.run(["curl","-s","--max-time","60","-F",f"files[]=@{path}","https://uguu.se/upload.php"],capture_output=True,text=True)
        try:return json.loads(r.stdout)["files"][0]["url"]
        except:pass
    raise RuntimeError("upload fail")
def send_photo(url,caption):
    data=urllib.parse.urlencode({"chat_id":CHAT,"photo":url,"caption":caption}).encode()
    urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",data=data),timeout=60)

def main():
    fmt=random.choice(FORMATS)
    files,default_cap=fmt()
    cap=gemini_caption(fmt.__name__,default_cap)
    cap="🔥 POST DE HOY (borrador, no publicado)\n\n"+cap+"\n\n—\nSi te late, dime VA y lo subo."
    url=uguu(files[0])
    send_photo(url,cap[:1020])
    print("Enviado:",fmt.__name__)

if __name__=="__main__":
    main()
