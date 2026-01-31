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
    <title>{% block title %}ALBEDOWIBU-TV{% endblock %}</title>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.css" />

    <style>
        :root { --bg-dark: #050505; --primary: #e11d48; }
        body { background-color: var(--bg-dark); color: #e5e5e5; font-family: 'Manrope', sans-serif; -webkit-tap-highlight-color: transparent; }
        #nprogress .bar { background: var(--primary) !important; height: 3px; }
        ::-webkit-scrollbar { width: 0px; background: transparent; }
        .glass-nav { background: rgba(5, 5, 5, 0.95); border-bottom: 1px solid rgba(255,255,255,0.08); }
        .card-anim { transition: transform 0.2s; }
        .card-anim:active { transform: scale(0.96); }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    
    <nav class="glass-nav fixed top-0 left-0 right-0 z-50 h-16 flex items-center justify-between px-4 md:px-8">
        <a href="/" class="flex items-center gap-2 group z-50">
            <span class="text-xl font-black tracking-tighter text-white">ALBEDO<span class="text-red-600">TV</span></span>
        </a>

        <div class="hidden md:flex items-center gap-6 text-xs font-bold text-gray-400 uppercase tracking-widest">
            <a href="/" class="hover:text-white transition hover:text-red-500">Home</a>
            <a href="/movies" class="hover:text-white transition hover:text-red-500">Movies</a>
            <a href="/genres" class="hover:text-white transition hover:text-red-500">Genre</a>
            <a href="/favorites" class="hover:text-white transition hover:text-red-500">Koleksi</a>
        </div>

        <form action="/search" method="GET" class="relative">
            <input type="text" name="q" placeholder="Cari..." value="{{ search_query if search_query else '' }}"
                   class="bg-[#151515] border border-white/10 rounded-full py-2 pl-4 pr-10 text-xs text-white focus:outline-none focus:border-red-600 transition-all w-32 focus:w-48 md:w-64">
            <button type="submit" class="absolute right-3 top-2 text-gray-500 hover:text-white"><i class="ri-search-line"></i></button>
        </form>
    </nav>

    <div class="md:hidden fixed bottom-0 left-0 right-0 bg-[#0a0a0c] border-t border-white/10 flex justify-around p-3 z-50 pb-safe">
        <a href="/" class="flex flex-col items-center {{ 'text-red-500' if request.path == '/' else 'text-gray-500' }}"><i class="ri-home-5-fill text-xl"></i></a>
        <a href="/movies" class="flex flex-col items-center {{ 'text-red-500' if request.path == '/movies' else 'text-gray-500' }}"><i class="ri-film-fill text-xl"></i></a>
        <a href="/genres" class="flex flex-col items-center {{ 'text-red-500' if request.path == '/genres' else 'text-gray-500' }}"><i class="ri-layout-grid-fill text-xl"></i></a>
        <a href="/favorites" class="flex flex-col items-center {{ 'text-red-500' if request.path == '/favorites' else 'text-gray-500' }}"><i class="ri-heart-3-fill text-xl"></i></a>
    </div>

    <main class="container mx-auto px-4 pt-20 pb-24 md:pb-12 flex-grow">
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
               class="w-full bg-[#151515] border border-white/10 rounded-2xl py-4 pl-6 pr-14 text-lg text-white focus:outline-none focus:border-red-600 shadow-2xl transition-all">
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
            `<a href="/search?q=${q}" class="px-4 py-2 bg-[#151515] rounded-lg text-sm text-gray-300 hover:text-white hover:bg-[#222] transition border border-white/5">${q}</a>`);
        });
    }
</script>
{% endblock %}
"""

HTML_INDEX = """
{% extends "base.html" %}
{% block content %}

<div class="mb-6 flex items-center justify-between border-b border-white/10 pb-4">
    <h2 class="text-lg font-bold text-white uppercase flex items-center gap-2">
        {% if search_query %}
            <span class="text-red-500">🔍</span> Hasil: "{{ search_query }}"
        {% elif is_movie_page %}
            <span class="text-red-500">🎬</span> Anime Movies
        {% else %}
            <span class="text-red-500">🔥</span> Update Terbaru
        {% endif %}
    </h2>
    <span class="text-[10px] bg-[#151515] px-2 py-1 rounded text-gray-500 border border-white/10">Page {{ current_page }}</span>
</div>

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
    {% if not data_list %}
        <div class="col-span-full py-20 text-center bg-[#151515] rounded-2xl border border-dashed border-white/10">
            <p class="text-gray-500 text-sm">Tidak ada hasil ditemukan.</p>
        </div>
    {% endif %}

    {% for anime in data_list %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="card-anim group relative block bg-[#151515] rounded-lg overflow-hidden shadow-lg border border-white/5">
        <div class="aspect-[3/4] overflow-hidden relative">
            <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover transition duration-700 group-hover:scale-110 group-hover:opacity-60">
            <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
            
            {% if anime.rating and anime.rating != 'N/A' %}
            <div class="absolute top-2 right-2 bg-yellow-500 text-black text-[9px] font-black px-1.5 py-0.5 rounded shadow">★ {{ anime.rating }}</div>
            {% elif anime.lastup == 'Baru di Upload' %}
            <div class="absolute top-2 right-2 bg-red-600 text-white text-[9px] font-black px-1.5 py-0.5 rounded shadow animate-pulse">NEW</div>
            {% endif %}
            
            <div class="absolute bottom-0 left-0 right-0 p-3">
                {% if anime.lastch %}
                <span class="text-[9px] font-bold text-red-400 uppercase tracking-wider mb-1 block">{{ anime.lastch }}</span>
                {% endif %}
                <h3 class="text-xs font-bold text-white leading-tight line-clamp-2 group-hover:text-red-500 transition">{{ anime.judul }}</h3>
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
    
    {% if data_list|length >= 10 %}
    <a href="{{ base }}{{ current_page + 1 }}" class="px-6 py-2.5 bg-red-600 hover:bg-red-700 rounded-full text-xs font-bold text-white transition flex items-center gap-2 shadow-lg shadow-red-900/20">Next →</a>
    {% endif %}
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
    <h1 class="text-xl font-black text-center text-white mb-8">PILIH GENRE</h1>
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
        {% for genre in genres %}
        <a href="/search?q={{ genre }}" class="py-3 px-2 bg-[#151515] border border-white/5 hover:border-red-600 hover:bg-red-900/10 rounded-lg text-xs font-bold text-gray-400 hover:text-white transition text-center">
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
        <div class="md:col-span-3 lg:col-span-3">
            <img src="{{ anime.cover }}" class="w-40 md:w-full mx-auto rounded-lg shadow-2xl border border-white/10 mb-4 bg-[#151515]">
            <a href="#eps" class="block w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold text-xs rounded-lg text-center shadow-lg transition mb-2">
                <i class="ri-play-fill mr-1"></i> NONTON
            </a>
            <button onclick="toggleFav()" id="fav-btn" class="block w-full py-3 bg-[#151515] hover:bg-[#222] text-gray-400 font-bold text-xs rounded-lg text-center transition border border-white/5">
                SIMPAN
            </button>
        </div>
        
        <div class="md:col-span-9 lg:col-span-9">
            <h1 class="text-2xl md:text-3xl font-black text-white mb-4 leading-tight">{{ anime.judul }}</h1>
            
            <div class="flex flex-wrap gap-2 mb-6">
                {% if anime.rating and anime.rating != 'N/A' %}
                <span class="bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg text-xs font-bold text-gray-300 flex items-center gap-1">
                    <i class="ri-star-fill text-yellow-500"></i> {{ anime.rating }}
                </span>
                {% endif %}
                <span class="bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg text-xs font-bold text-gray-300">{{ anime.status }}</span>
                <span class="bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg text-xs font-bold text-gray-300">{{ anime.custom_total_eps }}</span>
            </div>

            <div class="flex flex-wrap gap-2 mb-6">
                {% for g in anime.genre %}
                <a href="/search?q={{ g }}" class="text-[10px] px-3 py-1 bg-red-900/10 text-red-400 border border-red-900/20 rounded-full hover:bg-red-600 hover:text-white transition">{{ g }}</a>
                {% endfor %}
            </div>

            <div class="bg-[#151515] p-6 rounded-2xl border border-white/10 relative mt-4">
                <h3 class="text-xs font-bold text-gray-500 mb-3 uppercase tracking-widest flex items-center gap-2"><i class="ri-file-text-line"></i> Sinopsis</h3>
                <div class="text-sm text-gray-300 leading-relaxed text-justify">
                    {{ anime.sinopsis | safe }}
                </div>
            </div>
            
            <div class="mt-6 flex gap-6 text-[10px] text-gray-600 font-mono uppercase">
                <span>{{ anime.author }}</span><span>{{ anime.published }}</span>
            </div>
        </div>
    </div>

    <div id="eps" class="border-t border-white/10 pt-8">
        <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-bold text-white border-l-4 border-red-600 pl-3">DAFTAR EPISODE</h3>
            <button onclick="reverseList()" class="text-[10px] bg-[#151515] hover:bg-[#222] px-3 py-1 rounded text-gray-400 transition">⇅ Balik Urutan</button>
        </div>
        
        <div id="chapter-list" class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-2 max-h-[500px] overflow-y-auto custom-scroll pr-1">
            {% for chapter in anime.chapter %}
            <a href="/watch/{{ anime.series_id }}/{{ chapter.url }}?title={{ anime.judul }}" 
               class="bg-[#151515] hover:bg-red-600 border border-white/5 hover:border-red-500 p-3 rounded-xl text-center transition group">
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
            if(isFav) { btn.innerText = "TERSIMPAN"; btn.classList.add('bg-red-600','text-white'); btn.classList.remove('bg-[#151515]','text-gray-400'); }
            else { btn.innerText = "SIMPAN"; btn.classList.remove('bg-red-600','text-white'); btn.classList.add('bg-[#151515]','text-gray-400'); }
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
        <div id="player-container" class="relative bg-black rounded-xl overflow-hidden mb-6 shadow-2xl border border-white/10 group aspect-video">
            {% if player_url %}
            <iframe id="main-player" src="{{ player_url }}" class="absolute inset-0 w-full h-full" frameborder="0" allowfullscreen allow="autoplay; fullscreen"></iframe>
            {% else %}
            <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-6 bg-[#080808]">
                <p class="text-red-500 text-sm font-bold">STREAM ERROR</p>
                <p class="text-gray-500 text-xs mt-1">Coba episode lain.</p>
            </div>
            {% endif %}
        </div>

        <div class="bg-[#151515] p-5 rounded-xl border border-white/5 flex flex-col md:flex-row justify-between items-center gap-6">
            <div class="text-center md:text-left">
                <h1 class="text-sm font-bold text-white mb-1">Sedang Menonton</h1>
                <p class="text-xs text-red-400 font-medium truncate max-w-[250px]">{{ anime_title }}</p>
                <div class="mt-2 flex items-center gap-2 justify-center md:justify-start">
                    <span class="text-[10px] bg-green-500/10 text-green-400 px-2 py-0.5 rounded border border-green-500/20">AUTO BEST QUALITY</span>
                </div>
            </div>

            <div class="flex gap-2 items-center">
                <button onclick="toggleFullscreen()" class="px-4 py-2.5 bg-[#222] hover:bg-[#333] rounded-lg text-[10px] font-bold text-white border border-white/5 transition flex items-center gap-2">
                    <i class="ri-fullscreen-line"></i> BIOSKOP
                </button>

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
        <div class="text-center py-20 bg-[#151515] rounded-xl border border-white/5 text-xs text-gray-500">Video belum tersedia.</div>
    {% endif %}
</div>

<script>
    function toggleFullscreen() {
        var elem = document.getElementById("player-container");
        if (!document.fullscreenElement) {
            if (elem.requestFullscreen) { elem.requestFullscreen(); }
            else if (elem.webkitRequestFullscreen) { elem.webkitRequestFullscreen(); }
        } else {
            if (document.exitFullscreen) { document.exitFullscreen(); }
        }
    }
    
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
<h2 class="text-lg font-bold mb-4 border-l-4 border-red-600 pl-3">KOLEKSIKU</h2>
<div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3"></div>
<div id="empty" class="hidden text-center py-32 text-gray-600 text-sm">Belum ada anime yang disimpan.</div>
<script>
    const favs = JSON.parse(localStorage.getItem('albedo_favs')||'[]');
    if(favs.length===0) document.getElementById('empty').classList.remove('hidden');
    favs.forEach(a => {
        document.getElementById('grid').insertAdjacentHTML('beforeend', `
        <a href="${a.url}" class="group relative block bg-[#151515] rounded-lg overflow-hidden shadow border border-white/5">
            <div class="aspect-[3/4]"><img src="${a.cover}" class="w-full h-full object-cover group-hover:scale-110 transition duration-500"></div>
            <div class="absolute bottom-0 inset-x-0 p-2 bg-gradient-to-t from-black/90 to-transparent">
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
# 3. BACKEND LOGIC (DATA NORMALIZER)
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
def smart_fetch(endpoint, query_str=None, page=1):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, params={'query':query_str, 'page':page}, timeout=12)
        raw = r.json()
        if isinstance(raw, list): return raw
        if 'data' in raw:
            d = raw['data']
            if isinstance(d, list) and len(d)>0 and 'result' in d[0]: return d[0]['result']
            return d
        return []
    except: return []

# NORMALISASI DATA (PENTING UNTUK RATING)
def normalize_data_list(data_list):
    cleaned = []
    if not data_list: return []
    for item in data_list:
        score = item.get('score') or item.get('rating')
        if not score or score == '?' or score == 'N/A': score = None
        else: score = str(score)
        item['rating'] = score
        cleaned.append(item)
    return cleaned

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
    # GANTI STRATEGI: GUNAKAN /recent AGAR PAGINATION JALAN
    raw_data = smart_fetch('/recent', params={'page': page})
    
    # Jika /recent kosong di page 1 (mungkin error), fallback ke /latest
    if not raw_data and page == 1:
        raw_data = smart_fetch('/latest')
        
    data = normalize_data_list(raw_data)
    return render_template_string(HTML_INDEX, data_list=data, current_page=page, is_movie_page=False, search_query=None)

@app.route('/movies')
def movies():
    page = request.args.get('page', 1, type=int)
    raw_data = smart_fetch('/movie', page=page)
    data = normalize_data_list(raw_data)
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
    raw_data = smart_fetch('/search', query_str=q, page=page)
    data = normalize_data_list(raw_data)
    return render_template_string(HTML_INDEX, data_list=data, search_query=q, current_page=page)

@app.route('/anime/<path:url_id>')
def detail(url_id):
    try:
        r = requests.get(f"{API_BASE}/detail", headers=HEADERS, params={'urlId': url_id}, timeout=10)
        raw = r.json().get('data', [])
        if raw:
            anime = raw[0]
            anime['rating'] = anime.get('score', anime.get('rating', 'N/A'))
            sinopsis = anime.get('sinopsis') or anime.get('synopsis')
            if not sinopsis or sinopsis == 'N/A' or sinopsis.strip() == '':
                sinopsis = "Sinopsis belum tersedia untuk anime ini."
            anime['sinopsis'] = sinopsis
            eps = anime.get('chapter', [])
            anime['custom_total_eps'] = f"{len(eps)} Eps"
            if not anime.get('series_id'): anime['series_id'] = url_id
        else: anime = None
    except: anime = None
    
    if not anime: return render_template_string(HTML_DETAIL, error="Gagal memuat data anime.")
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
