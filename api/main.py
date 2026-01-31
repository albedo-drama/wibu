from flask import Flask, render_template_string, request, redirect, url_for
import requests
from jinja2 import DictLoader
import json
from functools import lru_cache

# ==========================================
# 1. KONFIGURASI APP
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
    <title>{% block title %}ALBEDOWIBU-TV{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    <style>
        body { background-color: #050505; color: #fff; font-family: sans-serif; }
        ::-webkit-scrollbar { width: 0px; }
        .glass { background: rgba(20,20,20,0.9); backdrop-filter: blur(10px); border-bottom: 1px solid #333; }
        .clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    </style>
</head>
<body class="flex flex-col min-h-screen pb-20">
    <nav class="glass fixed top-0 w-full z-50 h-16 flex items-center justify-between px-4">
        <a href="/" class="font-black text-xl tracking-tighter">ALBEDO<span class="text-red-600">TV</span></a>
        <div class="hidden md:flex gap-6 text-sm font-bold text-gray-400">
            <a href="/" class="hover:text-white">HOME</a>
            <a href="/movies" class="hover:text-white">MOVIES</a>
            <a href="/genres" class="hover:text-white">GENRE</a>
        </div>
        <form action="/search" class="relative">
            <input name="q" placeholder="Cari..." value="{{ query|default('') }}" class="bg-[#222] rounded-full py-1 px-4 text-sm outline-none border border-transparent focus:border-red-600 w-32 focus:w-48 transition-all">
        </form>
    </nav>

    <div class="md:hidden fixed bottom-0 w-full bg-[#111] border-t border-[#222] flex justify-around p-3 z-50">
        <a href="/" class="text-2xl text-gray-400 hover:text-red-500"><i class="ri-home-5-fill"></i></a>
        <a href="/movies" class="text-2xl text-gray-400 hover:text-red-500"><i class="ri-film-fill"></i></a>
        <a href="/genres" class="text-2xl text-gray-400 hover:text-red-500"><i class="ri-apps-fill"></i></a>
        <a href="/favorites" class="text-2xl text-gray-400 hover:text-red-500"><i class="ri-heart-3-fill"></i></a>
    </div>

    <main class="container mx-auto px-2 pt-20 flex-grow">
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
    {% if not data %}
        <div class="col-span-full py-20 text-center text-gray-500">Tidak ada data / API Error.</div>
    {% endif %}

    {% for item in data %}
    <a href="/anime/{{ item.id }}" class="block bg-[#111] rounded-lg overflow-hidden relative group">
        <div class="aspect-[3/4] relative">
            <img src="{{ item.image }}" loading="lazy" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition">
            
            {% if item.rating %}
            <div class="absolute top-1 right-1 bg-yellow-500 text-black text-[10px] font-bold px-1 rounded">★ {{ item.rating }}</div>
            {% endif %}
            
            <div class="absolute bottom-0 w-full p-2 bg-gradient-to-t from-black to-transparent">
                {% if item.ep %}<span class="text-[10px] text-red-400 font-bold block">{{ item.ep }}</span>{% endif %}
                <h3 class="text-xs font-bold text-white clamp-2">{{ item.title }}</h3>
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
{% block title %}{{ anime.title }}{% endblock %}
{% block content %}
{% if error %}
    <div class="text-center py-20 text-red-500">{{ error }}</div>
{% else %}
    <div class="flex flex-col md:flex-row gap-6 mb-8">
        <img src="{{ anime.image }}" class="w-40 rounded-lg shadow-lg mx-auto md:mx-0 border border-[#333]">
        <div class="flex-1">
            <h1 class="text-2xl font-bold mb-2">{{ anime.title }}</h1>
            <div class="flex flex-wrap gap-2 mb-4 text-[10px] font-bold">
                <span class="bg-[#222] px-2 py-1 rounded text-yellow-500">★ {{ anime.rating }}</span>
                <span class="bg-[#222] px-2 py-1 rounded">{{ anime.status }}</span>
                <span class="bg-[#222] px-2 py-1 rounded">{{ anime.total_ep }}</span>
            </div>
            
            <div class="bg-[#111] p-4 rounded-lg border border-[#222] text-xs text-gray-300 leading-6 text-justify mb-4">
                {{ anime.synopsis | safe }}
            </div>

            <div class="flex gap-2">
                <a href="#eps" class="bg-red-600 px-6 py-2 rounded text-xs font-bold">LIHAT EPISODE</a>
                <button onclick="save()" id="btn-save" class="bg-[#222] px-6 py-2 rounded text-xs font-bold">SIMPAN</button>
            </div>
        </div>
    </div>

    <div id="eps" class="border-t border-[#222] pt-4">
        <div class="flex justify-between mb-4">
            <h3 class="font-bold border-l-4 border-red-600 pl-2">DAFTAR EPISODE</h3>
            <button onclick="reverse()" class="text-[10px] bg-[#222] px-2 rounded">⇅ Balik</button>
        </div>
        <div id="ep-list" class="grid grid-cols-3 md:grid-cols-6 gap-2 max-h-[500px] overflow-y-auto">
            {% for ep in anime.episodes %}
            <a href="/watch/{{ anime.id }}/{{ ep.id }}" class="bg-[#111] p-2 rounded text-center hover:bg-red-600 transition group border border-[#222]">
                <span class="text-[9px] text-gray-500 block mb-1 group-hover:text-white">{{ ep.date }}</span>
                <span class="text-xs font-bold">Ep {{ ep.title }}</span>
            </a>
            {% endfor %}
        </div>
    </div>

    <script>
        function reverse(){ const l=document.getElementById('ep-list'); Array.from(l.children).reverse().forEach(i=>l.appendChild(i)); }
        // Simple Save Logic
        const id = "{{ anime.id }}";
        const title = "{{ anime.title }}";
        const img = "{{ anime.image }}";
        function save(){
            let f = JSON.parse(localStorage.getItem('albedo_favs')||'[]');
            if(f.some(x=>x.id===id)) { f=f.filter(x=>x.id!==id); alert('Dihapus'); }
            else { f.push({id,title,image:img}); alert('Disimpan'); }
            localStorage.setItem('albedo_favs', JSON.stringify(f));
        }
    </script>
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
        <div id="player-wrapper" class="aspect-video bg-black rounded-lg overflow-hidden relative border border-[#333] mb-4">
            <iframe id="video-frame" src="{{ video_url }}" class="w-full h-full" frameborder="0" allowfullscreen></iframe>
        </div>
        
        <div class="bg-[#111] p-4 rounded border border-[#222] mb-6">
            <div class="flex justify-between items-center mb-4">
                <div>
                    <h1 class="text-xs font-bold text-gray-400">SEDANG MEMUTAR</h1>
                    <p class="text-sm font-bold truncate max-w-[200px]">{{ title }}</p>
                    <span class="text-[10px] text-green-500">● Kualitas Tertinggi (Auto)</span>
                </div>
                <button onclick="full()" class="bg-[#222] px-4 py-2 rounded text-[10px] font-bold border border-[#333] flex items-center gap-1">
                    <i class="ri-fullscreen-line"></i> FULLSCREEN
                </button>
            </div>
            
            <div class="flex gap-2">
                {% if prev %}<a href="/watch/{{ anime_id }}/{{ prev }}" class="flex-1 bg-[#222] py-2 text-center rounded text-xs font-bold hover:bg-[#333]">PREV</a>{% endif %}
                <a href="/anime/{{ anime_id }}" class="flex-1 bg-[#222] py-2 text-center rounded text-xs font-bold hover:bg-[#333]">LIST</a>
                {% if next %}<a href="/watch/{{ anime_id }}/{{ next }}" class="flex-1 bg-red-600 py-2 text-center rounded text-xs font-bold hover:bg-red-700">NEXT</a>{% endif %}
            </div>
        </div>
    {% else %}
        <div class="py-20 text-center bg-[#111] rounded text-red-500 text-xs">Video tidak ditemukan di server.</div>
    {% endif %}
</div>
<script>
    function full(){
        const p = document.getElementById('player-wrapper');
        if(p.requestFullscreen) p.requestFullscreen();
        else if(p.webkitRequestFullscreen) p.webkitRequestFullscreen();
    }
</script>
{% endblock %}
"""

HTML_GENRES = """
{% extends "base.html" %}
{% block content %}
<div class="grid grid-cols-2 md:grid-cols-4 gap-2">
{% for g in genres %}
<a href="/search?q={{ g }}" class="bg-[#111] py-3 text-center text-xs font-bold text-gray-400 hover:text-white rounded border border-[#222]">{{ g }}</a>
{% endfor %}
</div>
{% endblock %}
"""

HTML_FAVORITES = """
{% extends "base.html" %}
{% block content %}
<h1 class="font-bold mb-4 border-l-4 border-red-600 pl-3">KOLEKSIKU</h1>
<div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3"></div>
<script>
    const f = JSON.parse(localStorage.getItem('albedo_favs')||'[]');
    if(f.length===0) document.getElementById('grid').innerHTML='<div class="col-span-full text-center py-10 text-gray-500">Kosong</div>';
    f.forEach(i=>{
        document.getElementById('grid').insertAdjacentHTML('beforeend', `
        <a href="/anime/${i.id}" class="block bg-[#111] rounded overflow-hidden relative">
            <div class="aspect-[3/4]"><img src="${i.image}" class="w-full h-full object-cover"></div>
            <div class="p-2"><h3 class="text-xs font-bold truncate">${i.title}</h3></div>
        </a>`);
    });
</script>
{% endblock %}
"""

# ==========================================
# 3. BACKEND LOGIC (THE PARSER)
# ==========================================

app = Flask(__name__)
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE, 'index.html': HTML_INDEX, 'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH, 'genres.html': HTML_GENRES, 'favorites.html': HTML_FAVORITES
})

API = "https://api.sansekai.my.id/api/anime"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

@lru_cache(maxsize=64)
def fetch(endpoint, **kwargs):
    try:
        r = requests.get(f"{API}{endpoint}", params=kwargs, headers=HEADERS, timeout=10)
        return r.json()
    except: return None

def clean_list(raw_data):
    """Membersihkan list dari Home/Movies/Search"""
    clean = []
    if not raw_data: return []
    
    # Handle variasi struktur
    items = []
    if isinstance(raw_data, list): items = raw_data
    elif isinstance(raw_data, dict):
        if 'data' in raw_data:
            d = raw_data['data']
            if isinstance(d, list):
                # Cek nested search result
                if len(d) > 0 and 'result' in d[0]: items = d[0]['result']
                else: items = d
    
    for i in items:
        # ID Extraction
        raw_url = i.get('endpoint') or i.get('url') or i.get('slug') or ''
        clean_id = raw_url.split('/')[-2] if '/' in raw_url else raw_url
        if not clean_id: continue

        # Rating Logic
        rating = i.get('score') or i.get('rating')
        if not rating or rating == '?' or rating == 'N/A': rating = None

        clean.append({
            'title': i.get('title') or i.get('judul') or 'Anime',
            'image': i.get('thumb') or i.get('image') or i.get('cover') or '',
            'id': clean_id,
            'rating': rating,
            'ep': i.get('episode') or i.get('last_chapter') or ''
        })
    return clean

@app.route('/')
def home():
    p = request.args.get('page', 1, type=int)
    # Gunakan /recent agar Pagination JALAN (Recommended ga jalan paginationnya)
    raw = fetch('/recent', page=p)
    data = clean_list(raw)
    return render_template_string(HTML_INDEX, data=data, title="UPDATE TERBARU", page=p, query="")

@app.route('/movies')
def movies():
    p = request.args.get('page', 1, type=int)
    raw = fetch('/movie', page=p)
    data = clean_list(raw)
    return render_template_string(HTML_INDEX, data=data, title="MOVIES", page=p, query="")

@app.route('/search')
def search():
    q = request.args.get('q', '')
    p = request.args.get('page', 1, type=int)
    if not q: return render_template_string(HTML_INDEX, data=[], title="PENCARIAN", page=1, query="")
    raw = fetch('/search', query=q)
    data = clean_list(raw)
    return render_template_string(HTML_INDEX, data=data, title=f"HASIL: {q}", page=p, query=q)

@app.route('/genres')
def genres(): return render_template_string(HTML_GENRES, genres=GENRE_LIST)

@app.route('/favorites')
def favorites(): return render_template_string(HTML_FAVORITES)

@app.route('/anime/<path:uid>')
def detail(uid):
    raw = fetch('/detail', urlId=uid)
    if not raw or 'data' not in raw or not raw['data']:
        return render_template_string(HTML_DETAIL, error="Data Kosong")
    
    d = raw['data'][0]
    
    # Detail Parsing
    episodes = []
    for e in d.get('chapter', []) or d.get('episode_list', []):
        u = e.get('url') or e.get('endpoint') or ''
        eid = u.split('/')[-2] if '/' in u else u
        episodes.append({'title': e.get('ch') or e.get('title'), 'date': e.get('date'), 'id': eid})
    
    anime = {
        'id': uid,
        'title': d.get('judul') or d.get('title'),
        'image': d.get('cover') or d.get('thumb'),
        'synopsis': d.get('sinopsis') or d.get('synopsis') or "Sinopsis tidak tersedia.",
        'rating': d.get('score') or d.get('rating') or 'N/A',
        'status': d.get('status') or '?',
        'total_ep': f"{len(episodes)} Eps",
        'genres': d.get('genre') or [],
        'episodes': episodes
    }
    return render_template_string(HTML_DETAIL, anime=anime)

@app.route('/watch/<path:aid>/<path:cid>')
def watch(aid, cid):
    # Fetch Video Data
    v_raw = fetch('/getvideo', chapterUrlId=cid)
    # Fetch Detail for Navigation
    d_raw = fetch('/detail', urlId=aid)
    
    # Logic Auto Quality (1080 > 720 > 480)
    video_url = None
    if v_raw and 'data' in v_raw and v_raw['data']:
        streams = v_raw['data'][0].get('stream', [])
        
        # Priority Queue
        best_score = 0
        for s in streams:
            score = 0
            if '1080' in s['reso']: score = 30
            elif '720' in s['reso']: score = 20
            elif '480' in s['reso']: score = 10
            if 'mp4' in s['link'] or 'animekita' in s['link']: score += 5
            
            if score > best_score:
                best_score = score
                video_url = s['link']
        
        if not video_url and streams: video_url = streams[0]['link']

    # Logic Navigation
    prev, next_ep, title = None, None, "Episode"
    if d_raw and 'data' in d_raw:
        eps = d_raw['data'][0].get('chapter', [])
        # Find index
        idx = -1
        for i, e in enumerate(eps):
            if cid in (e.get('url') or ''): idx = i; break
        
        if idx != -1:
            if idx < len(eps)-1: prev = eps[idx+1].get('url', '').split('/')[-2]
            if idx > 0: next_ep = eps[idx-1].get('url', '').split('/')[-2]
            title = f"{d_raw['data'][0].get('judul')} - Ep {eps[idx].get('ch')}"

    return render_template_string(HTML_WATCH, video_url=video_url, anime_id=aid, prev=prev, next=next_ep, title=title)

if __name__ == '__main__':
    app.run(debug=True)
