from flask import Flask, render_template_string, request, redirect, url_for
import requests
from jinja2 import DictLoader
import json
from functools import lru_cache

# ==========================================
# 1. TEMPLATES HTML (HANDLES EVERYTHING)
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
        body { background-color: #050505; color: #fff; font-family: sans-serif; }
        ::-webkit-scrollbar { width: 0px; }
        .glass-nav { background: rgba(10, 10, 10, 0.95); border-bottom: 1px solid #222; }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    <nav class="glass-nav fixed top-0 z-50 w-full h-14 flex items-center justify-between px-4">
        <a href="/" class="font-black text-lg tracking-tighter">ALBEDO<span class="text-red-600">TV</span></a>
        <div class="flex gap-4 text-xs font-bold text-gray-400">
            <a href="/" class="hover:text-white">HOME</a>
            <a href="/movies" class="hover:text-white">MOVIES</a>
            <a href="/genres" class="hover:text-white">GENRE</a>
        </div>
        <a href="/search" class="text-gray-400 hover:text-white"><i class="ri-search-line text-lg"></i></a>
    </nav>
    <main class="pt-20 pb-10 px-2 container mx-auto flex-grow">
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
    <span class="text-[10px] text-gray-500">Page {{ page }}</span>
</div>

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
    {% for item in data %}
    <a href="/anime/{{ item.id }}" class="block bg-[#111] rounded overflow-hidden relative group">
        <div class="aspect-[3/4] relative">
            <img src="{{ item.image }}" loading="lazy" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition">
            {% if item.rating %}
            <div class="absolute top-1 right-1 bg-yellow-500 text-black text-[9px] font-bold px-1 rounded">★ {{ item.rating }}</div>
            {% endif %}
            <div class="absolute bottom-0 inset-x-0 p-2 bg-gradient-to-t from-black to-transparent">
                <span class="text-[9px] text-red-400 font-bold block">{{ item.ep }}</span>
                <h3 class="text-xs font-bold text-white truncate">{{ item.title }}</h3>
            </div>
        </div>
    </a>
    {% endfor %}
</div>

{% if data %}
<div class="flex justify-center gap-4 mt-8">
    {% if page > 1 %}
    <a href="?page={{ page - 1 }}&q={{ query }}" class="px-4 py-2 bg-[#222] rounded text-xs">Prev</a>
    {% endif %}
    <a href="?page={{ page + 1 }}&q={{ query }}" class="px-4 py-2 bg-red-600 rounded text-xs">Next</a>
</div>
{% else %}
<div class="py-20 text-center text-gray-500">Data tidak ditemukan atau API Error.</div>
{% endif %}
{% endblock %}
"""

HTML_DETAIL = """
{% extends "base.html" %}
{% block content %}
{% if error %}
    <div class="text-center py-20 text-red-500">{{ error }}</div>
{% else %}
    <div class="flex flex-col md:flex-row gap-6 mb-8">
        <img src="{{ anime.image }}" class="w-40 rounded-lg shadow-lg mx-auto md:mx-0">
        <div class="flex-1">
            <h1 class="text-2xl font-bold mb-2">{{ anime.title }}</h1>
            <div class="flex flex-wrap gap-2 mb-4 text-[10px] font-bold">
                <span class="bg-[#222] px-2 py-1 rounded text-yellow-500">★ {{ anime.rating }}</span>
                <span class="bg-[#222] px-2 py-1 rounded">{{ anime.status }}</span>
                <span class="bg-[#222] px-2 py-1 rounded">{{ anime.total_ep }}</span>
            </div>
            <div class="bg-[#111] p-4 rounded text-xs text-gray-300 leading-6 text-justify mb-4">
                {{ anime.synopsis | safe }}
            </div>
            <div class="flex flex-wrap gap-2">
                {% for g in anime.genres %}
                <a href="/search?q={{ g }}" class="text-[10px] bg-red-900/30 text-red-300 px-2 py-1 rounded border border-red-900/50">{{ g }}</a>
                {% endfor %}
            </div>
        </div>
    </div>

    <div class="border-t border-white/10 pt-4">
        <div class="flex justify-between mb-4">
            <h3 class="font-bold border-l-4 border-red-600 pl-2">EPISODE</h3>
            <button onclick="rev()" class="text-[10px] bg-[#222] px-2 rounded">⇅ Balik</button>
        </div>
        <div id="eps" class="grid grid-cols-3 md:grid-cols-6 gap-2 max-h-[500px] overflow-y-auto">
            {% for ep in anime.episodes %}
            <a href="/watch/{{ anime.id }}/{{ ep.id }}" class="bg-[#111] p-2 rounded text-center hover:bg-red-600 transition">
                <span class="text-[9px] text-gray-500 block">{{ ep.date }}</span>
                <span class="text-xs font-bold">Ep {{ ep.title }}</span>
            </a>
            {% endfor %}
        </div>
    </div>
    <script>function rev(){const l=document.getElementById('eps');Array.from(l.children).reverse().forEach(i=>l.appendChild(i))}</script>
{% endif %}
{% endblock %}
"""

HTML_WATCH = """
{% extends "base.html" %}
{% block content %}
<div class="max-w-4xl mx-auto">
    <a href="/anime/{{ anime_id }}" class="text-xs text-gray-500 mb-2 block">← KEMBALI</a>
    
    {% if stream_url %}
        <div class="aspect-video bg-black rounded-lg overflow-hidden mb-4 relative" id="player">
            <iframe src="{{ stream_url }}" class="w-full h-full" frameborder="0" allowfullscreen></iframe>
        </div>
        <button onclick="full()" class="w-full py-2 bg-[#222] text-xs font-bold mb-4 rounded">⛶ MODE BIOSKOP (LANDSCAPE)</button>
    {% else %}
        <div class="py-20 text-center bg-[#111] text-xs text-red-500">Stream Error / Tidak ditemukan.</div>
    {% endif %}

    <div class="flex justify-between items-center bg-[#111] p-3 rounded mb-4">
        <h1 class="text-xs font-bold truncate w-1/2">{{ title }}</h1>
        <div class="flex gap-2">
            {% if prev %}<a href="/watch/{{ anime_id }}/{{ prev }}" class="px-3 py-1 bg-[#222] text-[10px] rounded">PREV</a>{% endif %}
            {% if next %}<a href="/watch/{{ anime_id }}/{{ next }}" class="px-3 py-1 bg-red-600 text-[10px] rounded">NEXT</a>{% endif %}
        </div>
    </div>
</div>
<script>
    function full(){
        const p = document.getElementById('player');
        if(p.requestFullscreen) p.requestFullscreen();
        else if(p.webkitRequestFullscreen) p.webkitRequestFullscreen();
    }
</script>
{% endblock %}
"""

HTML_SEARCH = """
{% extends "base.html" %}
{% block content %}
<div class="max-w-lg mx-auto py-10">
    <form action="/search" class="relative">
        <input name="q" placeholder="Cari anime..." value="{{ query }}" class="w-full bg-[#111] py-4 pl-6 pr-12 rounded-full text-white border border-white/10 focus:border-red-600 outline-none">
        <button class="absolute right-4 top-4 text-gray-400"><i class="ri-search-line"></i></button>
    </form>
    {% if not query %}
    <div class="mt-8">
        <h3 class="text-xs font-bold text-gray-500 mb-2">GENRE POPULER</h3>
        <div class="flex flex-wrap gap-2">
            {% for g in ['Action','Romance','Isekai','Fantasy','School'] %}
            <a href="/search?q={{ g }}" class="px-3 py-1 bg-[#111] rounded text-xs text-gray-300 hover:text-white">{{ g }}</a>
            {% endfor %}
        </div>
    </div>
    {% endif %}
</div>
{% endblock %}
"""

HTML_GENRES = """
{% extends "base.html" %}
{% block content %}
<h1 class="text-center font-bold text-xl mb-6">GENRE</h1>
<div class="grid grid-cols-2 md:grid-cols-4 gap-2">
    {% for g in genres %}
    <a href="/search?q={{ g }}" class="py-3 bg-[#111] text-center text-xs font-bold text-gray-400 hover:text-white rounded hover:bg-red-900/20">{{ g }}</a>
    {% endfor %}
</div>
{% endblock %}
"""

# ==========================================
# 3. BACKEND CORE (THE CLEANER)
# ==========================================

app = Flask(__name__)
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE,
    'index.html': HTML_INDEX,
    'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH,
    'search.html': HTML_SEARCH,
    'genres.html': HTML_GENRES
})

API_BASE = "https://api.sansekai.my.id/api/anime"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# --- FUNGSI PEMBERSIH DATA (ANTI ERROR) ---
def clean_anime(item):
    """Mengubah format acak API menjadi format standar ALBEDO-TV"""
    if not isinstance(item, dict): return None
    
    # 1. Ambil Judul
    title = item.get('title') or item.get('judul') or item.get('name') or 'Tanpa Judul'
    
    # 2. Ambil Gambar
    image = item.get('image') or item.get('thumb') or item.get('cover') or item.get('thumbnail') or ''
    
    # 3. Ambil ID/URL
    raw_id = item.get('endpoint') or item.get('url') or item.get('slug') or item.get('id') or ''
    # Bersihkan ID jika bentuknya URL penuh
    clean_id = raw_id.replace('https://otakudesu.cloud/anime/', '').replace('/', '')
    
    # 4. Ambil Rating (Apapun kuncinya)
    rating = item.get('score') or item.get('rating') or item.get('vote_average')
    if not rating or rating == '?' or rating == 'N/A': rating = None
    
    # 5. Ambil Episode
    ep = item.get('episode') or item.get('last_chapter') or '?'
    
    return {
        'title': title,
        'image': image,
        'id': clean_id,
        'rating': rating,
        'ep': ep
    }

def clean_detail(data):
    """Pembersih khusus halaman detail"""
    if not data: return None
    
    title = data.get('judul') or data.get('title')
    image = data.get('cover') or data.get('thumb')
    
    # Sinopsis
    syn = data.get('sinopsis') or data.get('synopsis') or 'Tidak ada sinopsis.'
    
    # Episode List
    raw_eps = data.get('chapter') or data.get('episode_list') or []
    episodes = []
    for e in raw_eps:
        # Bersihkan ID Episode
        e_url = e.get('url') or e.get('endpoint') or ''
        e_id = e_url.replace('https://otakudesu.cloud/episode/', '').replace('/', '')
        episodes.append({
            'title': e.get('ch') or e.get('title') or '?',
            'date': e.get('date') or '',
            'id': e_id
        })
        
    return {
        'title': title,
        'image': image,
        'rating': data.get('score') or data.get('rating') or 'N/A',
        'status': data.get('status') or '?',
        'total_ep': f"{len(episodes)} Eps",
        'synopsis': syn,
        'genres': data.get('genre') or [],
        'episodes': episodes
    }

# --- ROUTES ---

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    # Gunakan /recent agar pagination jalan
    try:
        r = requests.get(f"{API_BASE}/recent", params={'page': page}, headers=HEADERS)
        raw = r.json()
        # Handle list vs dict response
        items = raw if isinstance(raw, list) else raw.get('data', [])
        
        data = [clean_anime(x) for x in items]
        data = [x for x in data if x] # Hapus yang None
    except: data = []
    
    return render_template_string(HTML_INDEX, data=data, title="Update Terbaru", page=page, query="")

@app.route('/movies')
def movies():
    page = request.args.get('page', 1, type=int)
    try:
        r = requests.get(f"{API_BASE}/movie", params={'page': page}, headers=HEADERS)
        raw = r.json()
        items = raw if isinstance(raw, list) else raw.get('data', [])
        data = [clean_anime(x) for x in items]
        data = [x for x in data if x]
    except: data = []
    return render_template_string(HTML_INDEX, data=data, title="Anime Movies", page=page, query="")

@app.route('/search')
def search():
    q = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    if not q: return render_template_string(HTML_SEARCH, query="")
    
    try:
        r = requests.get(f"{API_BASE}/search", params={'query': q}, headers=HEADERS)
        raw = r.json()
        # Logic search Sansekai yang aneh (data -> [0] -> result)
        items = []
        if 'data' in raw:
            d = raw['data']
            if isinstance(d, list) and len(d) > 0 and 'result' in d[0]:
                items = d[0]['result']
            elif isinstance(d, list):
                items = d
        
        data = [clean_anime(x) for x in items]
        data = [x for x in data if x]
    except: data = []
    
    return render_template_string(HTML_INDEX, data=data, title=f"Cari: {q}", page=page, query=q)

@app.route('/genres')
def genres():
    return render_template_string(HTML_GENRES, genres=GENRE_LIST)

@app.route('/favorites')
def favorites():
    return render_template_string(HTML_INDEX, data=[], title="Koleksi (Saved in Browser)", page=1, query="")

@app.route('/anime/<path:uid>')
def detail(uid):
    try:
        r = requests.get(f"{API_BASE}/detail", params={'urlId': uid}, headers=HEADERS)
        raw = r.json()
        raw_data = raw.get('data', [])
        if not raw_data: raise Exception("Empty")
        
        anime = clean_detail(raw_data[0])
        # Inject ID for template
        anime['id'] = uid
        return render_template_string(HTML_DETAIL, anime=anime)
    except Exception as e:
        return render_template_string(HTML_DETAIL, error=f"Error: {e}")

@app.route('/watch/<path:aid>/<path:cid>')
def watch(aid, cid):
    try:
        # Get Video
        r = requests.get(f"{API_BASE}/getvideo", params={'chapterUrlId': cid}, headers=HEADERS)
        vid_data = r.json().get('data', [])
        if not vid_data: raise Exception("No Video")
        
        streams = vid_data[0].get('stream', [])
        
        # AUTO QUALITY LOGIC (BEST)
        url = None
        # Cari 1080/720/480 mp4
        for s in streams:
            if '1080' in s['reso'] and 'mp4' in s['link']: url = s['link']; break
        if not url:
            for s in streams: 
                if '720' in s['reso'] and 'mp4' in s['link']: url = s['link']; break
        if not url and streams: url = streams[0]['link'] # Fallback
        
        # Navigasi (Harus fetch detail dulu)
        r_det = requests.get(f"{API_BASE}/detail", params={'urlId': aid}, headers=HEADERS)
        anime_raw = r_det.json().get('data', [])
        prev, next_ep, title = None, None, "Episode"
        
        if anime_raw:
            eps = anime_raw[0].get('chapter', [])
            title = anime_raw[0].get('judul', 'Anime')
            # Cari index
            idx = -1
            for i, e in enumerate(eps):
                if cid in e.get('url', ''): idx = i; break
            
            if idx != -1:
                if idx < len(eps)-1: 
                    prev_raw = eps[idx+1].get('url')
                    prev = prev_raw.replace('https://otakudesu.cloud/episode/','').replace('/','')
                if idx > 0: 
                    next_raw = eps[idx-1].get('url')
                    next_ep = next_raw.replace('https://otakudesu.cloud/episode/','').replace('/','')

        return render_template_string(HTML_WATCH, stream_url=url, anime_id=aid, title=title, prev=prev, next=next_ep)
        
    except Exception as e:
        return render_template_string(HTML_WATCH, error=str(e), anime_id=aid)

if __name__ == '__main__':
    app.run(debug=True)
