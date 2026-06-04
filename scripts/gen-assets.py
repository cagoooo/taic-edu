# -*- coding: utf-8 -*-
import os, io
from PIL import Image, ImageDraw, ImageFont, ImageFilter

os.makedirs('assets', exist_ok=True)
BOLD='C:/Windows/Fonts/msjhbd.ttc'
REG ='C:/Windows/Fonts/msjh.ttc'
log=io.open('_assets_log.txt','w',encoding='utf-8')
def L(*a): log.write(' '.join(str(x) for x in a)+'\n')

# palette (matches site)
SEA   =(14,165,183)   # #0ea5b7
SEADP =(10,125,140)   # #0a7d8c
DEEP  =(6,59,76)      # #063b4c
DEEP2 =(4,34,44)      # #04222c
TEAL3 =(14,100,115)   # #0e6473
GOLD  =(244,185,66)
CORAL =(239,111,53)
WHITE =(255,255,255)

def font(path,size): return ImageFont.truetype(path,size)

def lin_grad(w,h,c1,c2,vertical=True):
    base=Image.new('RGB',(w,h),c1)
    top=Image.new('RGB',(w,h),c2)
    mask=Image.new('L',(w,h))
    md=mask.load()
    for y in range(h):
        for x in range(w):
            t=(y/h) if vertical else (x/w)
            md[x,y]=int(255*t)
    base.paste(top,(0,0),mask)
    return base

def diag_grad(w,h,stops):
    # stops: list of (pos0..1, (r,g,b)); diagonal top-left->bottom-right
    img=Image.new('RGB',(w,h))
    px=img.load()
    def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
    def col(t):
        for i in range(len(stops)-1):
            p0,c0=stops[i]; p1,c1=stops[i+1]
            if t<=p1:
                tt=0 if p1==p0 else (t-p0)/(p1-p0)
                return lerp(c0,c1,tt)
        return stops[-1][1]
    for y in range(h):
        for x in range(w):
            t=(x/w*0.5 + y/h*0.5)
            px[x,y]=col(t)
    return img

def rounded_mask(w,h,r):
    m=Image.new('L',(w,h),0)
    d=ImageDraw.Draw(m)
    d.rounded_rectangle([0,0,w-1,h-1],radius=r,fill=255)
    return m

def center_text(draw,cx,cy,text,fnt,fill):
    bb=draw.textbbox((0,0),text,font=fnt)
    w=bb[2]-bb[0]; h=bb[3]-bb[1]
    draw.text((cx-w/2-bb[0], cy-h/2-bb[1]), text, font=fnt, fill=fill)

# ---------- icon (鱻 on teal rounded square) ----------
def make_icon(size, maskable=False):
    s=size*4  # supersample
    g=lin_grad(s,s,SEA,SEADP,vertical=True)
    img=Image.new('RGBA',(s,s),(0,0,0,0))
    if maskable:
        img.paste(g,(0,0))  # full bleed, no rounding
        glyph_ratio=0.52
    else:
        r=int(s*0.22)
        img.paste(g,(0,0),rounded_mask(s,s,r))
        glyph_ratio=0.64
    d=ImageDraw.Draw(img)
    # subtle wave at bottom
    fs=int(s*glyph_ratio)
    f=font(BOLD,fs)
    # vertical optical tweak: 鱻 slightly up
    center_text(d, s/2, s*0.50, '鱻', f, WHITE)
    img=img.resize((size,size), Image.LANCZOS)
    return img

icons={}
for sz in [16,32,48,180,192,512]:
    icons[sz]=make_icon(sz)
icons['m192']=make_icon(192, maskable=True)
icons['m512']=make_icon(512, maskable=True)

icons[180].save('apple-touch-icon.png')
icons[192].save('assets/icon-192.png')
icons[512].save('assets/icon-512.png')
icons['m192'].save('assets/icon-192-maskable.png')
icons['m512'].save('assets/icon-512-maskable.png')
icons[32].save('assets/favicon-32.png')
# favicon.ico multi-size
icons[48].save('favicon.ico', format='ICO', sizes=[(16,16),(32,32),(48,48)])
L('icons done:', os.path.getsize('favicon.ico'),'ico bytes')

# ---------- OG image 1200x630 ----------
W,H=1200,630
og=diag_grad(W,H,[(0.0,TEAL3),(0.55,DEEP),(1.0,DEEP2)])
# glow accents
glow=Image.new('RGBA',(W,H),(0,0,0,0))
gd=ImageDraw.Draw(glow)
gd.ellipse([-160,-200,360,320], fill=GOLD+(46,))
gd.ellipse([W-360,H-300,W+160,H+220], fill=CORAL+(54,))
glow=glow.filter(ImageFilter.GaussianBlur(90))
og=Image.alpha_composite(og.convert('RGBA'), glow).convert('RGB')
d=ImageDraw.Draw(og)

# decorative waves bottom
wave=Image.new('RGBA',(W,H),(0,0,0,0))
wd=ImageDraw.Draw(wave)
import math
for k,(amp,yb,al) in enumerate([(16,560,40),(20,588,28),(24,616,20)]):
    pts=[]
    for x in range(0,W+1,8):
        pts.append((x, yb+amp*math.sin((x/W)*math.pi*4 + k)))
    pts+=[(W,H),(0,H)]
    wd.polygon(pts, fill=WHITE+(al,))
og=Image.alpha_composite(og.convert('RGBA'),wave).convert('RGB')
d=ImageDraw.Draw(og)

PAD=80
# brand chip top-left: small teal rounded square with 鱻 + wordmark
chip=make_icon(64)
og.paste(chip,(PAD,56),chip)
fb_word=font(BOLD,30)
d.text((PAD+64+16, 70), '本土 AI 共學站', font=fb_word, fill=(207,233,236))

# main title
f_title=font(BOLD,82)
d.text((PAD, 150), '把臺灣的語料', font=f_title, fill=WHITE)
d.text((PAD, 250), '變成師生家長的教材', font=f_title, fill=WHITE)
# accent underline
d.rounded_rectangle([PAD, 352, PAD+150, 360], radius=4, fill=GOLD)

# subtitle
f_sub=font(REG,34)
d.text((PAD, 392), '臺灣主權 AI 訓練語料庫 × 石門國小', font=f_sub, fill=(191,224,228))

# stats chips
f_chip=font(BOLD,26)
chips=['9 大教育主題','4554 筆本土語料','開放探索']
x=PAD; y=456
for c in chips:
    bb=d.textbbox((0,0),c,font=f_chip); cw=bb[2]-bb[0]
    d.rounded_rectangle([x,y,x+cw+34,y+50], radius=25, fill=(255,255,255,30) if False else (18,70,84))
    d.text((x+17,y+10), c, font=f_chip, fill=(213,240,243))
    x+=cw+34+14

# bottom credit + url
f_cred=font(REG,24)
d.text((PAD, 556), '桃園市龍潭區石門國民小學 · 阿凱老師', font=f_cred, fill=(150,190,196))
url='cagoooo.github.io/taic-edu'
f_url=font(BOLD,24)
bb=d.textbbox((0,0),url,font=f_url); uw=bb[2]-bb[0]
d.rounded_rectangle([W-PAD-uw-40, 552, W-PAD, 600], radius=24, fill=GOLD)
d.text((W-PAD-uw-20, 562), url, font=f_url, fill=(58,42,5))

og.save('og-image.png')
L('og-image:', os.path.getsize('og-image.png'),'bytes', og.size)
L('all assets generated OK')
log.close()
print('done')
