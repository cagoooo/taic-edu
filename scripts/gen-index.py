# -*- coding: utf-8 -*-
# 產出全量精簡搜尋索引 taic_index.json（4554 筆，懶載入用）
# 短鍵：i=id n=name a=agency o=open(1/0) k=keywords u=use g=grade t=theme(可省略)
import json, io, os

SRC = 'C:/Users/smes/Downloads/dataset_metadata_export_all_20260604.json'
OUT = 'H:/TW/taic_index.json'
data = json.load(io.open(SRC, 'r', encoding='utf-8'))
K = list(data[0].keys())
ID, NM, DESC, KW, SIZE, LIC, OPN, AG = K[0], K[1], K[2], K[3], K[4], K[5], K[6], K[7]

# ---- A1 標籤（與站上一致）----
GLOBAL_NEG_TAG = []
def tag(name, kw):
    t = (name or '') + ' ' + (kw or '')
    if any(w in t for w in ['繪本','童謠','故事集','有聲','漫畫','動畫','圖畫','詩詞','歌謠','一個故事','冒險','童書']):
        return '學生共讀', '低中年級'
    if any(w in t for w in ['辭典','詞典','字典','語料庫','音語料','詞彙']):
        return '教師備課', '全年段'
    if any(w in t for w in ['導覽','圖鑑','教材','教案','學習','解說','典藏','手冊','指引','專書','介紹','導論','素養','讀本','選輯','目錄']):
        return '課堂素材', '中高年級'
    if any(w in t for w in ['報告','白皮書','研究','計畫','統計','年報','分析','評估','調查','規劃','考察','簡報','政策','綱要','成果','專案','作業','法制','實錄','公報','文獻','檔案']):
        return '教師備課', '高年級↑'
    return '課堂素材', '全年段'

# ---- 主題分類（與精選目錄同一套評分，best-match）----
GLOBAL_NEG = ['出國報告','出國計畫','出席','參訪','考察報告','年報','簡訊','雙月刊','研究案','委託','工程進度',
              '可行性','研析','期末報告','期中報告','定稿報告','作業要點','為民服務白皮書','侵退','漂砂','水理',
              '校修','維運','容量手冊','監理','立法研究','法制','補強','耐震','發掘','人骨','成果展架']
T = [
 ('ocean', ['海洋教育','海洋素養','海洋生物','海洋是','潮汐','珊瑚','海岸','海廢','海龜','鯨豚','濕地','與海','海洋文化','海洋導論','紅樹林'], ['國家海洋研究院','海洋保育署']),
 ('language', ['臺語','台語','閩南語','客語','客家','族語','原住民族語','辭典','詞典','詞彙','諺語','童謠','古文詩詞','繪本','歌謠'], ['臺灣音樂館','客家委員會']),
 ('art', ['美術','工藝','傳統藝術','典藏','展','攝影','陶','漆器','竹','繪畫','版畫','美感','文物','唐卡','書法','戲曲','偶戲','導覽手冊'], ['國立臺灣美術館','國立臺灣工藝研究發展中心','國立傳統藝術中心','臺灣音樂館','國立故宮博物院']),
 ('nature', ['生態','物種','植物','昆蟲','鳥類','蝴蝶','森林','步道','地質','火山','星空','保育','生物多樣','賞鳥','花期','解說','圖鑑','濕地'], ['內政部國家公園署','林業及自然保育署']),
 ('family', ['家庭教育','親職','給家長','給家長的手冊','性別平等','多元家庭','青春同行','身體的主人','情感','家人關係','上學了','親子','繪本'], []),
 ('traffic', ['交通安全','道路安全','行人','自行車','兒童','通學','號誌','人本','行車安全','旅安','步行','路口安全','交通教育'], []),
 ('media', ['媒體素養','數位素養','假訊息','網路霸凌','資安','個資','詐騙','遊戲','人工智慧','數位時代','防騙','旅安手冊'], []),
 ('history', ['歷史','史前','古蹟','燈塔','老街','移民','新住民','地名','故事','導覽手冊','文化資產','在地','艾爾摩莎','館藏','時代'], ['國立臺灣史前文化博物館','國立臺灣歷史博物館','國立臺灣文學館']),
 ('life', ['生命教育','生涯','夢想','祖父母','祖孫','樂齡','故事集','繪本','感人故事','志工手冊','一個人一個故事'], []),
]
def best_theme(name, kw, ag):
    n = name or ''; a = ag or ''; k = kw or ''
    if any(x in n for x in GLOBAL_NEG): return None
    best, bestsc = None, 0
    for key, nk, ak in T:
        sc = 4*sum(1 for w in nk if w in n) + 2*sum(1 for w in nk if w in k) + (5 if any(x in a for x in ak) else 0)
        if sc > bestsc: best, bestsc = key, sc
    return best if bestsc >= 4 else None   # 門檻：避免亂分

items = []
for d in data:
    name = str(d.get(NM, '')).strip()
    ag = str(d.get(AG, '')).strip()
    kw = str(d.get(KW, '')).strip()
    if kw in ('無', 'None'): kw = ''
    u, g = tag(name, kw)
    rec = {
        'i': d.get(ID, ''),
        'n': name[:90],
        'a': ag[:40],
        'o': 1 if str(d.get(OPN, '')) == 'Y' else 0,
        'u': u, 'g': g,
    }
    if kw: rec['k'] = kw[:50]
    th = best_theme(name, kw, ag)
    if th: rec['t'] = th
    items.append(rec)

from collections import Counter
opn = Counter(r['o'] for r in items)
out = {
    'meta': {'total': len(items), 'open': opn.get(1, 0), 'restricted': opn.get(0, 0), 'export_date': '2026-06-04'},
    'items': items,
}
json.dump(out, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('done', len(items), 'items;', round(os.path.getsize(OUT) / 1024, 1), 'KB')
print('themed:', sum(1 for r in items if 't' in r), '| open:', opn.get(1, 0))
