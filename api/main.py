from flask import Flask, render_template_string, request, redirect, url_for
import requests
from jinja2 import DictLoader
import json
from functools import lru_cache

# ==========================================
# 1. DATA STATIC
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
# 2. TEMPLATES HTML (UI FIXED)
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
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;700;800&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.css" />

    <style>
        :root { --bg-dark: #050505; --primary: #dc2626; }
        body { background-color: var(--bg-dark); color: #fff; font-family: 'Plus Jakarta Sans', sans-serif; -webkit-tap-highlight-color: transparent; }
        #nprogress .bar { background: var(--primary) !important; height: 3px; }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: #000; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 5px; }
        .glass-nav { background: rgba(5, 5, 5, 0.95); border-bottom: 1px solid rgba(255,255,255,0.1); }
        .line-clamp-4 { display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    
    <nav class="glass-nav fixed top-0 left-0 right-0 z-50 h-16 flex items-center justify-between px-4 md:px-8">
        <a href="/" class="flex items-center gap-2 group z-50">
            <div class="w-8 h-8 rounded bg-red-600 flex items-center justify-center text-white font-black shadow-lg shadow-red-600/20">A</div>
            <span class="text-xl font-black tracking-tighter text-white">ALBEDO<span class="text-red-600">TV</span></span>
        </a>

        <div class="hidden md:flex items-center gap-6 text-xs font-bold text-gray-400 uppercase tracking-widest">
            <a href="/" class="hover:text-white transition">Home</a>
            <a href="/movies" class="hover:text-white transition">Movies</a>
            <a href="/genres" class="hover:text-white transition">Genre</a>
            <a href="/favorites" class="hover:text-white transition">Koleksi</a>
        </div>

        <form action="/search" method="GET" class="hidden md:block relative w-64">
            <input type="text" name="q" placeholder="Cari anime..." value="{{ search_query if search_query else '' }}"
                   class="w-full bg-[#151515] border border-white/10 rounded-full py-2 pl-4 pr-10 text-xs text-white focus:outline-none focus:border-red-600 transition-all">
            <button type="submit" class="absolute right-3 top-2 text-gray-500 hover:text-white"><i class="ri-search-line"></i></button>
        </form>

        <a href="/search" class="md:hidden w-10 h-10 flex items-center justify-center bg-[#151515] rounded-full text-white border border-white/10">
            <i class="ri-search-line"></i>
        </a>
    </nav>

    <div class="md:hidden fixed bottom-0 left-0 right-0 bg-[#0a0a0c] border-t border-white/10 flex justify-around p-3 z-50 pb-safe">
        <a href="/" class="flex flex-col items-center {{ 'text-red-500' if request.path == '/' else 'text-gray-500' }}">
            <i class="ri-home-5-fill text-xl"></i>
        </a>
        <a href="/movies" class="flex flex-col items-center {{ 'text-red-500' if request.path == '/movies' else 'text-gray-500' }}">
            <i class="ri-film-fill text-xl"></i>
        </a>
        <a href="/genres" class="flex flex-col items-center {{ 'text-red-500' if request.path == '/genres' else 'text-gray-500' }}">
            <i class="ri-layout-grid-fill text-xl"></i>
        </a>
        <a href="/favorites" class="flex flex-col items-center {{ 'text-red-500' if request.path == '/favorites' else 'text-gray-500' }}">
            <i class="ri-heart-3-fill text-xl"></i>
        </a>
    </div>

    <main class="container mx-auto px-4 pt-24 pb-24 md:pb-12 flex-grow">
        {% block content %}{% endblock %}
    </main>

    <script>
        window.addEventListener('beforeunload', () => NProgress.start());
        document.addEventListener("DOMContentLoaded", () => NProgress.done());
    </script>
</body>
</html>
"""

HTML_SEARCH_LANDING = """
{% extends "base.html" %}
{% block title %}Pencarian{% endblock %}
{% block content %}
<div class="max-w-xl mx-auto mt-10">
    <h1 class="text-3xl font-black text-white mb-6 text-center">PENCARIAN</h1>
    <form action="/search" method="GET" class="relative group mb-8">
        <input type="text" name="q" placeholder="Ketik judul..." autofocus
               class="w-full bg-[#111] border border-white/10 rounded-2xl py-4 pl-6 pr-14 text-lg text-white focus:outline-none focus:border-red-600 shadow-2xl transition-all">
        <button type="submit" class="absolute right-4 top-4 text-gray-400 group-focus-within:text-red-600"><i class="ri-search-2-line text-2xl"></i></button>
    </form>
    
    <div id="recent-box" class="hidden">
        <div class="flex justify-between items-center mb-3 px-2">
            <span class="text-xs font-bold text-gray-500 uppercase">Riwayat</span>
            <button onclick="localStorage.removeItem('search_history');location.reload()" class="text-xs text-red-500">Hapus</button>
        </div>
        <div id="recent-list" class="flex flex-wrap gap-2"></div>
    </div>
</div>
<script>
    const h = JSON.parse(localStorage.getItem('search_history') || '[]');
    if(h.length > 0) {
        document.getElementById('recent-box').classList.remove('hidden');
        h.slice(0,10).forEach(q => {
            document.getElementById('recent-list').insertAdjacentHTML('beforeend', 
            `<a href="/search?q=${q}" class="px-4 py-2 bg-[#1a1a1d] rounded-lg text-sm text-gray-300 hover:text-white hover:bg-[#222] transition border border-white/5">${q}</a>`);
        });
    }
</script>
{% endblock %}
"""

HTML_INDEX = """
{% extends "base.html" %}
{% block content %}

<div class="mb-6 flex items-center justify-between">
    <h2 class="text-xl font-bold text-white border-l-4 border-red-600 pl-3 uppercase">
        {% if search_query %}Hasil: "{{ search_query }}"
        {% elif is_movie_page %}Anime Movies
        {% else %}Update Terbaru
        {% endif %}
    </h2>
    <span class="text-[10px] bg-[#1a1a1d] px-2 py-1 rounded text-gray-500 border border-white/5">Page {{ current_page }}</span>
</div>

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
    {% if not data_list %}
        <div class="col-span-full py-20 text-center bg-[#111] rounded-2xl border border-dashed border-white/10">
            <p class="text-gray-500 text-sm">Tidak ada hasil ditemukan.</p>
        </div>
    {% endif %}

    {% for anime in data_list %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="group relative block bg-[#111] rounded-xl overflow-hidden shadow-lg border border-white/5 hover:border-red-600/50 transition-all hover:-translate-y-1">
        <div class="aspect-[3/4] overflow-hidden relative">
            <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover transition duration-700 group-hover:scale-110 group-hover:opacity-60">
            <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
            
            {% if anime.score %}
            <div class="absolute top-2 right-2 bg-yellow-500 text-black text-[9px] font-black px-1.5 py-0.5 rounded shadow">★ {{ anime.score }}</div>
            {% endif %}
            
            <div class="absolute bottom-0 left-0 right-0 p-3">
                {% if anime.lastch %}
                <span class="text-[9px] font-bold text-red-400 uppercase tracking-wider mb-1 block">{{ anime.lastch }}</span>
                {% endif %}
                <h3 class="text-sm font-bold text-white truncate group-hover:text-red-500 transition">{{ anime.judul }}</h3>
            </div>
        </div>
    </a>
    {% endfor %}
</div>

{% if data_list|length > 0 %}
<div class="flex justify-center items-center gap-3 mt-12 pt-8 border-t border-white/5">
    {% set base = '/search?q=' + (search_query if search_query else '') + '&page=' if search_query else ('/movies?page=' if is_movie_page else '/?page=') %}
    
    {% if current_page > 1 %}
    <a href="{{ base }}{{ current_page - 1 }}" class="px-6 py-2.5 bg-[#151515] hover:bg-[#222] rounded-full text-xs font-bold text-white transition flex items-center gap-2">← Prev</a>
    {% endif %}
    
    <a href="{{ base }}{{ current_page + 1 }}" class="px-6 py-2.5 bg-red-600 hover:bg-red-700 rounded-full text-xs font-bold text-white transition flex items-center gap-2 shadow-lg shadow-red-900/20">Next →</a>
</div>
{% endif %}

{% if search_query %}
<script>
    const q = "{{ search_query }}";
    let h = JSON.parse(localStorage.getItem('search_history') || '[]');
    if(!h.includes(q)) { h.unshift(q); if(h.length > 15) h.pop(); localStorage.setItem('search_history', JSON.stringify(h)); }
</script>
{% endif %}

{% endblock %}
"""

HTML_GENRES = """
{% extends "base.html" %}
{% block content %}
<div class="max-w-5xl mx-auto">
    <h1 class="text-2xl font-black text-center text-white mb-8">PILIH GENRE</h1>
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
        {% for genre in genres %}
        <a href="/search?q={{ genre }}" class="py-3 px-2 bg-[#111] border border-white/5 hover:border-red-600 hover:bg-red-900/10 rounded-lg text-xs font-bold text-gray-400 hover:text-white transition text-center">
            {{ genre }}
        </a>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

HTML_DETAIL = """
{% extends "base.html" %}
{% block title %}{{ anime.judul }}{% endblock %}
{% block content %}
{% if error %}
    <div class="text-center py-20 text-red-500 text-sm">{{ error }}</div>
{% else %}
    <div class="grid grid-cols-1 md:grid-cols-12 gap-8 mb-10">
        
        <div class="md:col-span-4 lg:col-span-3">
            <img src="{{ anime.cover }}" class="w-48 md:w-full mx-auto rounded-xl shadow-2xl border border-white/10 mb-4">
            
            <a href="#eps" class="block w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold text-xs rounded-xl text-center shadow-lg shadow-red-900/20 transition mb-2">
                <i class="ri-play-fill mr-1"></i> LIHAT EPISODE
            </a>
            <button onclick="toggleFav()" id="fav-btn" class="block w-full py-3 bg-[#1a1a1d] hover:bg-[#222] text-gray-400 font-bold text-xs rounded-xl text-center transition border border-white/5">
                SIMPAN
            </button>
        </div>
        
        <div class="md:col-span-8 lg:col-span-9">
            <h1 class="text-2xl md:text-4xl font-black text-white mb-4 leading-tight">{{ anime.judul }}</h1>
            
            <div class="flex flex-wrap gap-2 mb-6">
                <span class="bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg text-xs font-bold text-gray-300 flex items-center gap-1">
                    <i class="ri-star-fill text-yellow-500"></i> {{ anime.rating }}
                </span>
                <span class="bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg text-xs font-bold text-gray-300">
                    {{ anime.status }}
                </span>
                <span class="bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg text-xs font-bold text-gray-300">
                    {{ anime.custom_total_eps }}
                </span>
            </div>

            <div class="flex flex-wrap gap-2 mb-6">
                {% for g in anime.genre %}
                <a href="/search?q={{ g }}" class="text-[10px] px-3 py-1 bg-red-900/10 text-red-400 border border-red-900/20 rounded-full hover:bg-red-600 hover:text-white transition">{{ g }}</a>
                {% endfor %}
            </div>

            <div class="bg-[#111] p-5 rounded-2xl border border-white/10 relative">
                <h3 class="text-xs font-bold text-gray-500 mb-2 uppercase tracking-widest">Sinopsis</h3>
                <div class="text-sm text-gray-300 leading-7 text-justify max-h-60 overflow-y-auto pr-2 custom-scroll">
                    {% if anime.sinopsis and anime.sinopsis != 'N/A' %}
                        {{ anime.sinopsis | safe }}
                    {% else %}
                        <span class="italic text-gray-600">Deskripsi cerita belum tersedia untuk anime ini.</span>
                    {% endif %}
                </div>
            </div>
            
            <div class="mt-4 flex gap-6 text-[10px] text-gray-600 font-mono uppercase">
                <span>{{ anime.author }}</span>
                <span>{{ anime.published }}</span>
            </div>
        </div>
    </div>

    <div id="eps" class="border-t border-white/10 pt-8">
        <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-bold text-white border-l-4 border-red-600 pl-3">DAFTAR EPISODE</h3>
            <button onclick="reverseList()" class="text-xs bg-[#1a1a1d] hover:bg-[#222] px-4 py-2 rounded-lg text-gray-400 transition">⇅ Balik Urutan</button>
        </div>
        
        <div id="chapter-list" class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-2 max-h-[500px] overflow-y-auto pr-1">
            {% for chapter in anime.chapter %}
            <a href="/watch/{{ anime.series_id }}/{{ chapter.url }}?title={{ anime.judul }}" 
               class="bg-[#111] hover:bg-red-600 border border-white/5 hover:border-red-500 p-3 rounded-lg text-center transition group">
                <span class="block text-[9px] text-gray-500 group-hover:text-red-200 mb-1 font-mono">{{ chapter.date }}</span>
                <span class="text-sm font-bold text-white">Ep {{ chapter.ch }}</span>
            </a>
            {% endfor %}
        </div>
    </div>

    <script>
        const animeData = { url: location.pathname, cover: '{{ anime.cover }}', judul: '{{ anime.judul|replace("'", "") }}' };
        function updateFav() {
            const favs = JSON.parse(localStorage.getItem('albedo_favs')||'[]');
            const isFav = favs.some(f=>f.url===animeData.url);
            const btn = document.getElementById('fav-btn');
            if(isFav) { btn.innerText = "TERSIMPAN"; btn.classList.add('bg-red-600','text-white'); btn.classList.remove('bg-[#1a1a1d]','text-gray-400'); }
            else { btn.innerText = "SIMPAN"; btn.classList.remove('bg-red-600','text-white'); btn.classList.add('bg-[#1a1a1d]','text-gray-400'); }
        }
        function toggleFav() {
            let favs = JSON.parse(localStorage.getItem('albedo_favs')||'[]');
            const idx = favs.findIndex(f=>f.url===animeData.url);
            if(idx===-1) favs.push(animeData); else favs.splice(idx,1);
            localStorage.setItem('albedo_favs', JSON.stringify(favs));
            updateFav();
        }
        function reverseList() { const list = document.getElementById('chapter-list'); Array.from(list.children).reverse().forEach(item => list.appendChild(item)); }
        updateFav();
    </script>
{% endif %}
{% endblock %}
"""

HTML_WATCH = """
{% extends "base.html" %}
{% block title %}Nonton {{ anime_title }}{% endblock %}
{% block content %}
<div class="max-w-5xl mx-auto">
    <a href="/anime/{{ anime_url }}" class="inline-flex items-center gap-2 text-xs font-bold text-gray-500 hover:text-white mb-4 transition">
        <i class="ri-arrow-left-line"></i> KEMBALI
    </a>
    
    {% if video %}
        <div class="aspect-video bg-black rounded-xl overflow-hidden mb-6 relative shadow-2xl border border-white/10 group">
            {% if player_url %}
            <iframe src="{{ player_url }}" class="w-full h-full" frameborder="0" allowfullscreen></iframe>
            {% else %}
            <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-6 bg-[#080808]">
                <p class="text-red-500 text-sm font-bold">STREAM ERROR</p>
                <p class="text-gray-500 text-xs mt-1">Coba episode lain.</p>
            </div>
            {% endif %}
        </div>

        <div class="bg-[#111] p-5 rounded-xl border border-white/5 flex flex-col md:flex-row justify-between items-center gap-6">
            <div class="text-center md:text-left">
                <h1 class="text-sm font-bold text-white mb-1">Sedang Menonton</h1>
                <p class="text-xs text-red-400 font-medium truncate max-w-[250px]">{{ anime_title }}</p>
            </div>

            <div class="flex gap-2">
                {% if prev_ep %}
                <a href="/watch/{{ anime_url }}/{{ prev_ep.url }}?title={{ anime_title }}" class="px-5 py-2.5 bg-[#1a1a1d] hover:bg-[#222] rounded-lg text-xs font-bold text-white transition border border-white/5">Prev</a>
                {% endif %}
                
                {% if next_ep %}
                <a href="/watch/{{ anime_url }}/{{ next_ep.url }}?title={{ anime_title }}" class="px-5 py-2.5 bg-red-600 hover:bg-red-700 rounded-lg text-xs font-bold text-white transition shadow-lg shadow-red-600/20 flex items-center gap-2">
                    Next <i class="ri-arrow-right-line"></i>
                </a>
                {% endif %}
            </div>
        </div>
    {% else %}
        <div class="text-center py-20 bg-[#111] rounded-xl border border-white/5 text-xs text-gray-500">Video belum tersedia.</div>
    {% endif %}
</div>
<script>
    document.addEventListener("DOMContentLoaded", function() {
        const currentUrl = "{{ current_url }}";
        let history = JSON.parse(localStorage.getItem('watched_episodes') || '[]');
        if (!history.includes(currentUrl)) { history.push(currentUrl); localStorage.setItem('watched_episodes', JSON.stringify(history)); }
    });
</script>
{% endblock %}
"""

HTML_FAVORITES = """
{% extends "base.html" %}
{% block content %}
<h2 class="text-xl font-bold text-white mb-6 border-l-4 border-red-600 pl-3">KOLEKSIKU</h2>
<div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3"></div>
<div id="empty" class="hidden text-center py-32 text-gray-600 text-sm">Belum ada anime yang disimpan.</div>
<script>
    const favs = JSON.parse(localStorage.getItem('albedo_favs')||'[]');
    if(favs.length===0) document.getElementById('empty').classList.remove('hidden');
    favs.forEach(a => {
        document.getElementById('grid').insertAdjacentHTML('beforeend', `
        <a href="${a.url}" class="group relative block bg-[#111] rounded-xl overflow-hidden shadow-lg border border-white/5">
            <div class="aspect-[3/4]"><img src="${a.cover}" class="w-full h-full object-cover group-hover:scale-110 transition duration-500"></div>
            <div class="absolute bottom-0 inset-x-0 p-3 bg-gradient-to-t from-black/90 to-transparent">
                <h3 class="text-xs font-bold text-white truncate">${a.judul}</h3>
            </div>
            <button onclick="rem(event, '${a.url}')" class="absolute top-2 right-2 bg-red-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs shadow-lg hover:scale-110 transition z-20">✕</button>
        </a>`);
    });
    function rem(e, u) { e.preventDefault(); if(!confirm('Hapus?'))return; localStorage.setItem('albedo_favs', JSON.stringify(favs.filter(f=>f.url!==u))); location.reload(); }
</script>
{% endblock %}
"""

# ==========================================
# 3. BACKEND LOGIC
# ==========================================

app = Flask(__name__)
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE,
    'index.html': HTML_INDEX,
    'genres.html': HTML_GENRES,
    'favorites.html': HTML_FAVORITES,
    'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH,
    'search_landing.html': HTML_SEARCH_LANDING
})

API_BASE = "https://api.sansekai.my.id/api/anime"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

@lru_cache(maxsize=64)
def cached_fetch(endpoint, query_str=None, page=1):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, params={'query':query_str, 'page':page}, timeout=10)
        raw = r.json()
        if isinstance(raw, list): return raw
        if 'data' in raw:
            d = raw['data']
            if isinstance(d, list) and len(d)>0 and 'result' in d[0]: return d[0]['result']
            return d
        return []
    except: return []

def get_best_quality_url(streams):
    if not streams: return None
    best_link = None
    best_score = 0
    for s in streams:
        link = s.get('link', '')
        reso = s.get('reso', '')
        score = 0
        if '1080' in reso: score = 40
        elif '720' in reso: score = 30
        elif '480' in reso: score = 20
        elif '360' in reso: score = 10
        if '.mp4' in link or 'animekita' in link: score += 5
        if score > best_score:
            best_score = score
            best_link = link
    if not best_link and streams: best_link = streams[0]['link']
    return best_link

def get_nav(chapters, current_url):
    if not chapters: return None, None
    idx = next((i for i, ch in enumerate(chapters) if ch.get('url') == current_url), -1)
    if idx == -1: return None, None
    next_ep = chapters[idx - 1] if idx > 0 else None
    prev_ep = chapters[idx + 1] if idx < len(chapters) - 1 else None
    return next_ep, prev_ep

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    data = cached_fetch('/latest') if page == 1 else cached_fetch('/recommended', params={'page': page})
    return render_template_string(HTML_INDEX, data_list=data, current_page=page, is_movie_page=False, search_query=None)

@app.route('/movies')
def movies():
    page = request.args.get('page', 1, type=int)
    data = cached_fetch('/movie', params={'page': page})
    return render_template_string(HTML_INDEX, data_list=data, current_page=page, is_movie_page=True, search_query=None)

@app.route('/genres')
def genres():
    return render_template_string(HTML_GENRES, genres=GENRE_LIST)

@app.route('/favorites')
def favorites():
    return render_template_string(HTML_FAVORITES)

@app.route('/search')
def search():
    q = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    if not q: return render_template_string(HTML_SEARCH_LANDING)
    data = cached_fetch('/search', query_str=q, page=page)
    return render_template_string(HTML_INDEX, data_list=data, search_query=q, current_page=page)

@app.route('/anime/<path:url_id>')
def detail(url_id):
    try:
        r = requests.get(f"{API_BASE}/detail", headers=HEADERS, params={'urlId': url_id}, timeout=10)
        anime = r.json().get('data', [])[0]
    except: return render_template_string(HTML_DETAIL, error="Tidak ditemukan.")
    
    anime['custom_total_eps'] = f"{len(anime.get('chapter', []))} Eps"
    if not anime.get('series_id'): anime['series_id'] = url_id
    return render_template_string(HTML_DETAIL, anime=anime)

@app.route('/watch/<path:anime_url>/<path:chapter_url>')
def watch(anime_url, chapter_url):
    title_p = request.args.get('title')
    try:
        r_vid = requests.get(f"{API_BASE}/getvideo", headers=HEADERS, params={'chapterUrlId': chapter_url}, timeout=10)
        vid_data = r_vid.json().get('data', [])
    except: vid_data = []

    try:
        r_det = requests.get(f"{API_BASE}/detail", headers=HEADERS, params={'urlId': anime_url}, timeout=10)
        anime_data = r_det.json().get('data', [])
    except: anime_data = []
    
    title = anime_data[0].get('judul') if anime_data else (title_p or "")
    chapters = anime_data[0].get('chapter', []) if anime_data else []
    next_ep, prev_ep = get_nav(chapters, chapter_url)
    video_info = vid_data[0] if vid_data else None
    player_url = get_best_quality_url(video_info.get('stream', []) if video_info else [])

    return render_template_string(
        HTML_WATCH, video=video_info, player_url=player_url,
        anime_title=title, anime_url=anime_url, current_url=chapter_url, next_ep=next_ep, prev_ep=prev_ep
    )

if __name__ == '__main__':
    app.run(debug=True)
