from flask import Flask, render_template_string, request, redirect, url_for
import requests
from jinja2 import DictLoader
import json
from functools import lru_cache

# ==========================================
# 1. KONFIGURASI
# ==========================================

GENRE_LIST = sorted([
    "Action", "Adventure", "Comedy", "Demons", "Drama", "Ecchi", "Fantasy", 
    "Game", "Harem", "Historical", "Horror", "Josei", "Magic", "Martial Arts", 
    "Mecha", "Military", "Music", "Mystery", "Parody", "Police", "Psychological", 
    "Romance", "Samurai", "School", "Sci-Fi", "Seinen", "Shoujo", "Shoujo Ai", 
    "Shounen", "Shounen Ai", "Slice of Life", "Space", "Sports", "Super Power", 
    "Supernatural", "Thriller", "Vampire", "Yuri", "Isekai"
])

# ==========================================
# 2. TEMPLATES HTML
# ==========================================

HTML_BASE = """
<!DOCTYPE html>
<html lang="id" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ALBEDOWIBU-TV</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    <style>
        body { background-color: #0a0a0a; color: #fff; font-family: sans-serif; }
        ::-webkit-scrollbar { width: 0; }
        .glass { background: rgba(10,10,10,0.95); border-bottom: 1px solid #222; }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    <nav class="glass fixed top-0 w-full z-50 h-16 flex items-center justify-between px-4">
        <a href="/" class="font-black text-xl tracking-tighter">ALBEDO<span class="text-red-600">TV</span></a>
        <div class="hidden md:flex gap-6 text-sm font-bold text-gray-400">
            <a href="/" class="hover:text-white">HOME</a>
            <a href="/movies" class="hover:text-white">MOVIES</a>
            <a href="/genres" class="hover:text-white">GENRE</a>
        </div>
        <form action="/search" class="relative">
            <input name="q" placeholder="Cari..." class="bg-[#222] rounded-full py-1 px-4 text-sm outline-none border border-transparent focus:border-red-600 w-32 focus:w-48 transition-all">
        </form>
    </nav>
    <main class="container mx-auto px-2 pt-20 pb-20 flex-grow">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
"""

HTML_INDEX = """
{% extends "base.html" %}
{% block content %}
<div class="mb-4 flex justify-between items-end border-l-4 border-red-600 pl-3">
    <h1 class="font-bold text-lg uppercase">{{ title }}</h1>
    <span class="text-xs text-gray-500">Page {{ page }}</span>
</div>

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
    {% for item in data %}
    <a href="/anime/{{ item.id }}" class="block bg-[#111] rounded-lg overflow-hidden relative group">
        <div class="aspect-[3/4] relative">
            <img src="{{ item.thumb }}" loading="lazy" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition">
            <div class="absolute bottom-0 w-full p-2 bg-gradient-to-t from-black to-transparent">
                {% if item.episode %}<span class="text-[10px] text-red-400 font-bold block">{{ item.episode }}</span>{% endif %}
                <h3 class="text-xs font-bold text-white truncate">{{ item.title }}</h3>
            </div>
        </div>
    </a>
    {% endfor %}
</div>

{% if data %}
<div class="flex justify-center gap-4 mt-8 pt-4 border-t border-[#222]">
    {% if page > 1 %}
    <a href="?page={{ page - 1 }}&q={{ query }}" class="px-4 py-2 bg-[#222] rounded text-xs font-bold">← PREV</a>
    {% endif %}
    {% if data|length >= 5 %}
    <a href="?page={{ page + 1 }}&q={{ query }}" class="px-4 py-2 bg-red-600 rounded text-xs font-bold">NEXT →</a>
    {% endif %}
</div>
{% endif %}
{% endblock %}
"""

HTML_DETAIL = """
{% extends "base.html" %}
{% block title %}{{ anime.judul }}{% endblock %}
{% block content %}
{% if error %}
    <div class="text-center py-20 text-red-500">{{ error }}</div>
{% else %}
    <div class="flex flex-col md:flex-row gap-6 mb-8">
        <img src="{{ anime.thumb }}" class="w-40 rounded-lg shadow-lg mx-auto md:mx-0 border border-[#333]">
        <div class="flex-1">
            <h1 class="text-2xl font-bold mb-2">{{ anime.judul }}</h1>
            
            <div class="flex flex-wrap gap-2 mb-4 text-[10px] font-bold">
                <span class="bg-[#222] px-2 py-1 rounded text-yellow-500 border border-yellow-500/30">★ {{ anime.skor }}</span>
                
                <span class="bg-[#222] px-2 py-1 rounded border border-white/10">{{ anime.status }}</span>
                
                <span class="bg-[#222] px-2 py-1 rounded border border-white/10">{{ anime.total_episode }}</span>
            </div>
            
            <div class="bg-[#111] p-4 rounded-lg border border-[#222] text-xs text-gray-300 leading-6 text-justify mb-4">
                <strong class="block text-gray-500 mb-1 uppercase tracking-wider">Sinopsis</strong>
                {{ anime.sinopsis | safe }}
            </div>

            <div class="flex gap-2">
                <a href="#eps" class="bg-red-600 px-6 py-2 rounded text-xs font-bold">LIHAT EPISODE</a>
            </div>
        </div>
    </div>

    <div id="eps" class="border-t border-[#222] pt-4">
        <div class="flex justify-between mb-4">
            <h3 class="font-bold border-l-4 border-red-600 pl-2">DAFTAR EPISODE</h3>
            <button onclick="rev()" class="text-[10px] bg-[#222] px-2 rounded">⇅ Balik</button>
        </div>
        <div id="ep-list" class="grid grid-cols-2 md:grid-cols-6 gap-2 max-h-[600px] overflow-y-auto">
            {% for ep in anime.chapter %}
            <a href="/watch/{{ anime.series_id }}/{{ ep.id }}?title={{ anime.judul }}" class="bg-[#111] p-2 rounded text-center hover:bg-red-600 transition group border border-[#222]">
                <span class="text-[9px] text-gray-500 block mb-1 group-hover:text-white">{{ ep.date }}</span>
                <span class="text-xs font-bold">Ep {{ ep.title }}</span>
            </a>
            {% endfor %}
        </div>
    </div>
    <script>function rev(){const l=document.getElementById('ep-list');Array.from(l.children).reverse().forEach(i=>l.appendChild(i))}</script>
{% endif %}
{% endblock %}
"""

HTML_WATCH = """
{% extends "base.html" %}
{% block title %}Nonton {{ title }}{% endblock %}
{% block content %}
<div class="max-w-4xl mx-auto">
    <a href="/anime/{{ anime_id }}" class="text-xs text-gray-500 mb-2 block font-bold">← KEMBALI KE DETAIL</a>
    
    {% if video_url %}
        <div id="player-wrap" class="aspect-video bg-black rounded-lg overflow-hidden mb-4 relative border border-[#333]">
            <iframe src="{{ video_url }}" class="w-full h-full" frameborder="0" allowfullscreen></iframe>
        </div>
        <button onclick="full()" class="w-full py-2 bg-[#222] text-xs font-bold mb-4 rounded border border-[#333]">⛶ MODE BIOSKOP (LANDSCAPE)</button>
    {% else %}
        <div class="py-20 text-center bg-[#111] text-xs text-red-500">Video tidak ditemukan.</div>
    {% endif %}

    <div class="bg-[#111] p-4 rounded border border-[#222]">
        <h1 class="text-xs font-bold text-gray-400 mb-1">SEDANG MEMUTAR</h1>
        <p class="text-sm font-bold text-white mb-4">{{ title }}</p>
        
        <div class="flex gap-2">
            {% if prev %}<a href="/watch/{{ anime_id }}/{{ prev }}?title={{ title }}" class="flex-1 bg-[#222] py-2 text-center rounded text-xs font-bold hover:bg-[#333]">PREV</a>{% endif %}
            {% if next %}<a href="/watch/{{ anime_id }}/{{ next }}?title={{ title }}" class="flex-1 bg-red-600 py-2 text-center rounded text-xs font-bold hover:bg-red-700">NEXT</a>{% endif %}
        </div>
    </div>
</div>
<script>
    function full(){
        const p = document.getElementById('player-wrap');
        if(p.requestFullscreen) p.requestFullscreen();
        else if(p.webkitRequestFullscreen) p.webkitRequestFullscreen();
    }
</script>
{% endblock %}
"""

# ==========================================
# 3. BACKEND LOGIC (STRICT MAPPING)
# ==========================================

app = Flask(__name__)
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE, 'index.html': HTML_INDEX, 'detail.html': HTML_DETAIL, 'watch.html': HTML_WATCH
})

API = "https://api.sansekai.my.id/api/anime"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

@lru_cache(maxsize=64)
def fetch(endpoint, **kwargs):
    try:
        r = requests.get(f"{API}{endpoint}", params=kwargs, headers=HEADERS, timeout=10)
        return r.json()
    except: return None

# --- PARSING LIST (HOME/SEARCH) ---
def parse_list(raw):
    res = []
    if not raw: return []
    
    # Deteksi List vs Dict
    items = raw if isinstance(raw, list) else raw.get('data', [])
    # Deteksi Search Nested
    if isinstance(raw, dict) and 'data' in raw and raw['data']:
        if 'result' in raw['data'][0]: items = raw['data'][0]['result']

    for i in items:
        # ID Extraction
        url = i.get('endpoint') or i.get('url') or i.get('slug') or ''
        # Clean ID
        uid = url.replace('https://otakudesu.cloud/anime/','').replace('/','')
        
        res.append({
            'id': uid,
            'title': i.get('title') or i.get('judul') or 'Anime',
            'thumb': i.get('thumb') or i.get('image') or i.get('cover') or '',
            'episode': i.get('episode') or i.get('last_chapter') or '',
            'rating': i.get('score') or i.get('rating') # Bisa None
        })
    return res

# --- ROUTES ---

@app.route('/')
def home():
    p = request.args.get('page', 1, type=int)
    # Pake /recent biar bisa Next Page
    data = parse_list(fetch('/recent', page=p))
    return render_template_string(HTML_INDEX, data=data, title="UPDATE TERBARU", page=p, query="")

@app.route('/movies')
def movies():
    p = request.args.get('page', 1, type=int)
    data = parse_list(fetch('/movie', page=p))
    return render_template_string(HTML_INDEX, data=data, title="MOVIES", page=p, query="")

@app.route('/genres')
def genres():
    return render_template_string(HTML_INDEX, data=[], title="GENRE (Pilih di Search)", page=1, query="")

@app.route('/search')
def search():
    q = request.args.get('q','')
    p = request.args.get('page', 1, type=int)
    if not q: return render_template_string(HTML_INDEX, data=[], title="PENCARIAN", page=1, query="")
    
    data = parse_list(fetch('/search', query=q))
    return render_template_string(HTML_INDEX, data=data, title=f"HASIL: {q}", page=p, query=q)

@app.route('/anime/<path:uid>')
def detail(uid):
    raw = fetch('/detail', urlId=uid)
    if not raw or 'data' not in raw or not raw['data']:
        return render_template_string(HTML_DETAIL, error="Data Kosong")
    
    d = raw['data'][0]
    
    # PARSING KHUSUS DETAIL (SESUAI KEY API)
    # Total Episode kadang namanya 'total_episode', kadang manual count
    tot_ep = d.get('total_episode')
    chapters = []
    
    # Parse Episode
    raw_eps = d.get('chapter') or d.get('episode_list') or []
    for e in raw_eps:
        u = e.get('url') or e.get('endpoint') or ''
        eid = u.replace('https://otakudesu.cloud/episode/','').replace('/','')
        chapters.append({'id': eid, 'title': e.get('ch') or e.get('title'), 'date': e.get('date')})
    
    if not tot_ep: tot_ep = f"{len(chapters)} Eps"

    anime = {
        'series_id': uid,
        'judul': d.get('judul') or d.get('title'),
        'thumb': d.get('cover') or d.get('thumb') or d.get('image'),
        'skor': d.get('skor') or d.get('score') or d.get('rating') or 'N/A', # AMBIL SKOR
        'status': d.get('status') or '?',
        'total_episode': tot_ep, # AMBIL TOTAL EPISODE
        'sinopsis': d.get('sinopsis') or 'Sinopsis tidak tersedia.', # AMBIL SINOPSIS
        'chapter': chapters
    }
    return render_template_string(HTML_DETAIL, anime=anime)

@app.route('/watch/<path:aid>/<path:cid>')
def watch(aid, cid):
    title = request.args.get('title', 'Anime')
    # Fetch Video
    v_raw = fetch('/getvideo', chapterUrlId=cid)
    # Fetch Detail (Buat navigasi)
    d_raw = fetch('/detail', urlId=aid)
    
    # 1. Cari Link Terbaik
    url = None
    if v_raw and 'data' in v_raw:
        streams = v_raw['data'][0].get('stream', [])
        # Prioritas: 1080 > 720 > 480
        best_score = 0
        for s in streams:
            sc = 0
            if '1080' in s['reso']: sc = 30
            elif '720' in s['reso']: sc = 20
            elif '480' in s['reso']: sc = 10
            if 'mp4' in s['link'] or 'animekita' in s['link']: sc += 5
            
            if sc > best_score:
                best_score = sc
                url = s['link']
        if not url and streams: url = streams[0]['link']

    # 2. Navigasi
    prev, next_ep = None, None
    if d_raw and 'data' in d_raw:
        eps = d_raw['data'][0].get('chapter', [])
        idx = -1
        for i, e in enumerate(eps):
            if cid in (e.get('url') or ''): idx = i; break
        
        if idx != -1:
            if idx < len(eps)-1: 
                prev = eps[idx+1].get('url','').replace('https://otakudesu.cloud/episode/','').replace('/','')
            if idx > 0: 
                next_ep = eps[idx-1].get('url','').replace('https://otakudesu.cloud/episode/','').replace('/','')

    return render_template_string(HTML_WATCH, video_url=url, anime_id=aid, prev=prev, next=next_ep, title=title)

if __name__ == '__main__':
    app.run(debug=True)
