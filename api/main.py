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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ALBEDOWIBU-TV{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.css" />

    <style>
        body { background-color: #0a0a0a; color: #e5e5e5; font-family: 'Inter', sans-serif; }
        #nprogress .bar { background: #ef4444 !important; height: 3px; }
        .card-hover:hover { transform: translateY(-3px); transition: 0.2s ease-in-out; }
        /* Scrollbar */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: #111; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 5px; }
        ::-webkit-scrollbar-thumb:hover { background: #ef4444; }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    
    <nav class="bg-black/90 border-b border-white/5 sticky top-0 z-50 backdrop-blur-md">
        <div class="container mx-auto px-4 h-16 flex items-center justify-between">
            <a href="/" class="text-xl font-black tracking-tighter text-white flex items-center gap-1 group">
                ALBEDO<span class="text-red-600 group-hover:text-white transition">WIBU</span>-TV
            </a>

            <div class="hidden md:flex gap-6 text-xs font-bold text-gray-400">
                <a href="/" class="hover:text-white transition">HOME</a>
                <a href="/movies" class="hover:text-white transition">MOVIES</a>
                <a href="/genres" class="hover:text-white transition">GENRE</a>
                <a href="/favorites" class="hover:text-white transition">KOLEKSIKU</a>
                <a href="/history" class="hover:text-white transition">RIWAYAT</a>
            </div>

            <form action="/search" method="GET" class="relative group">
                <input type="text" name="q" placeholder="Cari..." value="{{ search_query if search_query else '' }}"
                       class="bg-[#151515] border border-white/10 rounded-full py-2 pl-4 pr-10 text-xs text-white focus:outline-none focus:border-red-600 w-32 md:w-56 transition-all focus:bg-black">
                <button type="submit" class="absolute right-3 top-2 text-gray-500 group-focus-within:text-white">
                    <i class="ri-search-line"></i>
                </button>
            </form>
        </div>
        
        <div class="md:hidden fixed bottom-0 left-0 right-0 bg-[#0a0a0a] border-t border-white/10 flex justify-around p-3 z-50 pb-safe">
            <a href="/" class="text-center text-[10px] font-bold text-gray-500 hover:text-white {{ 'text-red-500' if request.path == '/' }}">
                <i class="ri-home-5-line text-lg block mb-0.5"></i> HOME
            </a>
            <a href="/genres" class="text-center text-[10px] font-bold text-gray-500 hover:text-white {{ 'text-red-500' if request.path == '/genres' }}">
                <i class="ri-layout-grid-line text-lg block mb-0.5"></i> GENRE
            </a>
            <a href="/favorites" class="text-center text-[10px] font-bold text-gray-500 hover:text-white {{ 'text-red-500' if request.path == '/favorites' }}">
                <i class="ri-heart-3-line text-lg block mb-0.5"></i> SAVED
            </a>
            <a href="/history" class="text-center text-[10px] font-bold text-gray-500 hover:text-white {{ 'text-red-500' if request.path == '/history' }}">
                <i class="ri-history-line text-lg block mb-0.5"></i> HIST
            </a>
        </div>
    </nav>

    <main class="container mx-auto px-4 py-8 flex-grow pb-24 md:pb-12">
        {% block content %}{% endblock %}
    </main>

    <script>
        window.addEventListener('beforeunload', () => NProgress.start());
        document.addEventListener("DOMContentLoaded", () => {
            NProgress.done();
            const history = JSON.parse(localStorage.getItem('watched_episodes') || '[]');
            history.forEach(url => {
                const links = document.querySelectorAll(`a[href*="${url}"]`);
                links.forEach(link => {
                    link.classList.add('opacity-50', 'grayscale');
                    if(link.querySelector('.ep-title')) {
                        link.querySelector('.ep-title').classList.replace('text-white', 'text-red-500');
                    }
                });
            });
        });
    </script>
</body>
</html>
"""

HTML_INDEX = """
{% extends "base.html" %}
{% block content %}

<div class="mb-6 flex justify-between items-end border-b border-white/5 pb-4">
    <h2 class="text-lg font-bold text-white flex items-center gap-2">
        {% if search_query %}
            <span class="text-red-600">🔍</span> Hasil: "{{ search_query }}"
        {% elif is_movie_page %}
            <span class="text-red-600">🎬</span> Movies
        {% else %}
            <span class="text-red-600">🔥</span> Update Terbaru
        {% endif %}
    </h2>
    <span class="text-[10px] font-mono text-gray-500">Hal {{ current_page }}</span>
</div>

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 md:gap-5">
    {% if not data_list %}
        <div class="col-span-full py-20 text-center bg-[#111] rounded-xl border border-white/5">
            <p class="text-gray-500 text-xs">Tidak ada data ditemukan.</p>
            {% if current_page > 1 %}
            <a href="javascript:history.back()" class="text-red-500 text-xs hover:underline mt-2 inline-block">Kembali</a>
            {% endif %}
        </div>
    {% endif %}

    {% for anime in data_list %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="card-hover block bg-[#111] rounded-lg overflow-hidden relative group border border-white/5">
        <div class="aspect-[3/4] overflow-hidden relative">
            <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover transition duration-500 group-hover:scale-110 group-hover:opacity-60">
            <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
            
            {% if anime.score %}
            <div class="absolute top-1 right-1 bg-yellow-500 text-black text-[9px] font-black px-1.5 py-0.5 rounded shadow">★ {{ anime.score }}</div>
            {% endif %}
            
            <div class="absolute bottom-0 left-0 right-0 p-3">
                {% if anime.lastch %}
                <span class="bg-red-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded mb-1 inline-block">{{ anime.lastch }}</span>
                {% endif %}
                <h3 class="text-xs font-bold text-gray-200 truncate group-hover:text-red-500 transition">{{ anime.judul }}</h3>
            </div>
        </div>
    </a>
    {% endfor %}
</div>

{% if data_list|length > 0 %}
<div class="flex justify-center items-center gap-3 mt-10 pt-6">
    {% set base_link = '/search?q=' + (search_query if search_query else '') + '&page=' if search_query else ('/movies?page=' if is_movie_page else '/?page=') %}
    
    {% if current_page > 1 %}
    <a href="{{ base_link }}{{ current_page - 1 }}" class="px-5 py-2 bg-[#151515] hover:bg-[#222] text-white text-xs font-bold rounded-full transition">← Prev</a>
    {% endif %}
    
    <a href="{{ base_link }}{{ current_page + 1 }}" class="px-5 py-2 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-full transition shadow-lg shadow-red-900/20">Next →</a>
</div>
{% endif %}

{% endblock %}
"""

HTML_GENRES = """
{% extends "base.html" %}
{% block content %}
<div class="max-w-5xl mx-auto">
    <h2 class="text-xl font-bold text-white mb-6 text-center">DAFTAR GENRE</h2>
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
        {% for genre in genres %}
        <a href="/search?q={{ genre }}" class="bg-[#111] hover:bg-red-900/30 border border-white/5 hover:border-red-500/50 py-3 rounded text-center text-xs font-bold text-gray-400 hover:text-white transition">
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
    <div class="text-center py-20 text-red-500 text-xs">{{ error }}</div>
{% else %}
    
    <div class="max-w-6xl mx-auto bg-[#111] rounded-2xl p-6 md:p-8 border border-white/5 mb-8 shadow-2xl">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
            
            <div class="col-span-1">
                <img src="{{ anime.cover }}" class="w-48 md:w-full rounded-lg shadow-2xl border border-white/10 mx-auto">
                
                <div class="mt-4 flex flex-col gap-2">
                    <a href="#chapter-list" class="w-full py-2 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded text-center transition">
                        MULAI NONTON
                    </a>
                    <button onclick="toggleFav()" id="fav-btn" class="w-full py-2 bg-[#222] hover:bg-[#333] text-gray-300 font-bold text-xs rounded transition">
                        SIMPAN
                    </button>
                </div>
            </div>

            <div class="col-span-1 md:col-span-3 text-center md:text-left">
                <h1 class="text-2xl md:text-4xl font-black text-white mb-4 leading-tight">{{ anime.judul }}</h1>
                
                <div class="flex flex-wrap justify-center md:justify-start gap-2 mb-6">
                    <span class="bg-white/5 border border-white/10 px-3 py-1 rounded text-[10px] font-bold text-gray-300">★ {{ anime.rating }}</span>
                    <span class="bg-white/5 border border-white/10 px-3 py-1 rounded text-[10px] font-bold text-gray-300">{{ anime.status }}</span>
                    <span class="bg-white/5 border border-white/10 px-3 py-1 rounded text-[10px] font-bold text-gray-300">{{ anime.custom_total_eps }}</span>
                </div>

                <div class="flex flex-wrap justify-center md:justify-start gap-1 mb-6">
                    {% for g in anime.genre %}
                    <a href="/search?q={{ g }}" class="text-[10px] px-3 py-1 bg-[#1a1a1a] hover:bg-red-600 text-gray-400 hover:text-white rounded transition">{{ g }}</a>
                    {% endfor %}
                </div>

                <div class="bg-black/40 p-4 rounded-lg border border-white/5 text-xs text-gray-400 leading-relaxed text-justify h-48 overflow-y-auto custom-scroll">
                    {{ anime.sinopsis }}
                </div>
                
                <div class="mt-4 flex gap-6 text-[10px] text-gray-600 font-mono uppercase">
                    <span>{{ anime.author }}</span>
                    <span>{{ anime.published }}</span>
                </div>
            </div>
        </div>
    </div>

    <div class="max-w-6xl mx-auto" id="chapter-list-container">
        <div class="flex justify-between items-center mb-4 border-b border-white/5 pb-2">
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
                <span class="w-1 h-4 bg-red-600 rounded-full"></span> EPISODE LIST
            </h3>
            <button onclick="reverseList()" class="text-[10px] bg-[#111] border border-white/5 px-3 py-1 rounded text-gray-400 hover:text-white transition">⇅ Urutan</button>
        </div>
        
        <div id="chapter-list" class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2 max-h-[500px] overflow-y-auto pr-1">
            {% for chapter in anime.chapter %}
            <a href="/watch/{{ anime.series_id }}/{{ chapter.url }}" class="bg-[#111] hover:bg-red-600 border border-white/5 hover:border-red-500 p-2 rounded text-center transition group">
                <span class="block text-[9px] text-gray-500 group-hover:text-red-200 mb-1">{{ chapter.date }}</span>
                <span class="ep-title text-xs font-bold text-white">Ep {{ chapter.ch }}</span>
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
            if(isFav) { btn.innerText = "TERSIMPAN"; btn.classList.add('text-red-500', 'border-red-500'); }
            else { btn.innerText = "SIMPAN"; btn.classList.remove('text-red-500', 'border-red-500'); }
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
    
    <div class="aspect-video bg-black rounded-xl overflow-hidden shadow-2xl border border-white/10 relative z-10 mb-4">
        {% if player_url %}
        <iframe src="{{ player_url }}" class="w-full h-full" frameborder="0" allowfullscreen></iframe>
        {% else %}
        <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-6">
            <p class="text-red-500 font-bold text-sm">STREAM TIDAK TERSEDIA</p>
            <p class="text-gray-500 text-xs mt-1">Coba episode lain.</p>
        </div>
        {% endif %}
    </div>

    <div class="bg-[#111] p-4 rounded-xl border border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
        <div class="text-center md:text-left">
            <h1 class="text-xs font-bold text-gray-400">SEDANG MENONTON</h1>
            <p class="text-sm font-bold text-white truncate max-w-[250px]">{{ anime_title }}</p>
            <p class="text-[10px] text-green-500 mt-1">✓ Kualitas Terbaik (Auto-Selected)</p>
        </div>

        <div class="flex gap-2">
            {% if prev_ep %}
            <a href="/watch/{{ anime_url }}/{{ prev_ep.url }}" class="px-5 py-2 bg-[#222] hover:bg-[#333] rounded text-xs font-bold text-white transition border border-white/5">
                ← Prev
            </a>
            {% endif %}
            
            <a href="/anime/{{ anime_url }}" class="px-5 py-2 bg-[#222] hover:bg-[#333] rounded text-xs font-bold text-gray-400 hover:text-white transition border border-white/5">
                List
            </a>

            {% if next_ep %}
            <a href="/watch/{{ anime_url }}/{{ next_ep.url }}" class="px-5 py-2 bg-red-600 hover:bg-red-700 rounded text-xs font-bold text-white transition shadow-lg shadow-red-900/30">
                Next →
            </a>
            {% endif %}
        </div>
    </div>

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

HTML_HISTORY = """
{% extends "base.html" %}
{% block content %}
<h2 class="text-lg font-bold mb-4 border-l-4 border-red-600 pl-3">RIWAYAT MENONTON</h2>
<div id="hist-grid" class="flex flex-col gap-2"></div>
<div id="empty" class="hidden text-center py-20 text-gray-500 text-xs bg-[#111] rounded-xl">Belum ada riwayat.</div>
<script>
    const hist = JSON.parse(localStorage.getItem('albedo_history') || '[]');
    if(hist.length === 0) document.getElementById('empty').classList.remove('hidden');
    hist.reverse().forEach(item => {
        document.getElementById('hist-grid').insertAdjacentHTML('beforeend', `
        <a href="${item.url}" class="flex items-center gap-4 bg-[#111] p-3 rounded hover:bg-[#1a1a1a] border border-white/5">
            <div class="w-12 h-12 bg-gray-800 rounded overflow-hidden shrink-0"><img src="${item.cover}" class="w-full h-full object-cover"></div>
            <div>
                <h3 class="text-xs font-bold text-white">${item.title}</h3>
                <p class="text-[10px] text-gray-500">${item.date}</p>
            </div>
            <div class="ml-auto text-xs text-red-500 font-bold">LANJUT ▶</div>
        </a>`);
    });
</script>
{% endblock %}
"""

HTML_FAVORITES = """
{% extends "base.html" %}
{% block content %}
<h2 class="text-lg font-bold mb-4 border-l-4 border-red-600 pl-3">KOLEKSIKU</h2>
<div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3"></div>
<script>
    const favs = JSON.parse(localStorage.getItem('albedo_favs')||'[]');
    if(favs.length===0) document.getElementById('grid').innerHTML = '<div class="col-span-full py-20 text-center text-gray-500 text-xs bg-[#111] rounded">Kosong.</div>';
    favs.forEach(a => {
        document.getElementById('grid').insertAdjacentHTML('beforeend', `
        <a href="${a.url}" class="block bg-[#111] rounded overflow-hidden relative group border border-white/5">
            <div class="aspect-[3/4]"><img src="${a.cover}" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition"></div>
            <div class="p-2"><h3 class="text-[10px] font-bold text-gray-300 truncate">${a.judul}</h3></div>
            <button onclick="rem(event, '${a.url}')" class="absolute top-1 right-1 bg-red-600 text-white w-5 h-5 rounded flex items-center justify-center text-[10px]">x</button>
        </a>`);
    });
    function rem(e, u) { e.preventDefault(); if(!confirm('Hapus?'))return; localStorage.setItem('albedo_favs', JSON.stringify(favs.filter(f=>f.url!==u))); location.reload(); }
</script>
{% endblock %}
"""

# ==========================================
# 3. BACKEND LOGIC (AUTO-QUALITY)
# ==========================================

app = Flask(__name__)
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE,
    'index.html': HTML_INDEX,
    'genres.html': HTML_GENRES,
    'favorites.html': HTML_FAVORITES,
    'history.html': HTML_HISTORY,
    'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH
})

API_BASE = "https://api.sansekai.my.id/api/anime"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# CACHE SEDERHANA
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

# LOGIKA PINTAR PILIH RESOLUSI
def get_best_quality_url(streams):
    if not streams: return None
    
    # 1. Cari MP4 (Google/Animekita) - Paling stabil
    # Urutkan berdasarkan resolusi string (hacky way: string comparison 720 > 480 > 360)
    # Kita cari yang mengandung '1080', lalu '720', lalu '480'
    
    best_link = None
    best_score = 0
    
    for s in streams:
        link = s.get('link', '')
        reso = s.get('reso', '')
        score = 0
        
        # Scoring Resolusi
        if '1080' in reso: score = 40
        elif '720' in reso: score = 30
        elif '480' in reso: score = 20
        elif '360' in reso: score = 10
        
        # Bonus Score untuk Provider Stabil (.mp4)
        if '.mp4' in link or 'animekita' in link: score += 5
        
        if score > best_score:
            best_score = score
            best_link = link
            
    # Fallback: Jika tidak ada yang match, ambil link pertama
    if not best_link and streams:
        best_link = streams[0]['link']
        
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
    data = cached_fetch('/latest') if page == 1 else cached_fetch('/recommended', page=page)
    return render_template_string(HTML_INDEX, data_list=data, current_page=page, is_movie_page=False)

@app.route('/movies')
def movies():
    page = request.args.get('page', 1, type=int)
    data = cached_fetch('/movie', page=page)
    return render_template_string(HTML_INDEX, data_list=data, current_page=page, is_movie_page=True)

@app.route('/genres')
def genres():
    return render_template_string(HTML_GENRES, genres=GENRE_LIST)

@app.route('/favorites')
def favorites():
    return render_template_string(HTML_FAVORITES)

@app.route('/history')
def history():
    return render_template_string(HTML_HISTORY)

@app.route('/search')
def search():
    q = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    if not q: return redirect('/')
    data = cached_fetch('/search', query_str=q, page=page)
    return render_template_string(HTML_INDEX, data_list=data, search_query=q, current_page=page)

@app.route('/anime/<path:url_id>')
def detail(url_id):
    try:
        r = requests.get(f"{API_BASE}/detail", headers=HEADERS, params={'urlId': url_id}, timeout=10)
        anime = r.json().get('data', [])[0]
    except: return render_template_string(HTML_DETAIL, error="Gagal mengambil data.")
    
    anime['custom_total_eps'] = f"{len(anime.get('chapter', []))} Eps"
    if not anime.get('series_id'): anime['series_id'] = url_id
    return render_template_string(HTML_DETAIL, anime=anime)

@app.route('/watch/<path:anime_url>/<path:chapter_url>')
def watch(anime_url, chapter_url):
    # Param History
    title_p = request.args.get('title')
    cover_p = request.args.get('cover')

    # Fetch Video
    try:
        r_vid = requests.get(f"{API_BASE}/getvideo", headers=HEADERS, params={'chapterUrlId': chapter_url}, timeout=10)
        vid_data = r_vid.json().get('data', [])
    except: vid_data = []

    # Fetch Detail (Navigasi)
    try:
        r_det = requests.get(f"{API_BASE}/detail", headers=HEADERS, params={'urlId': anime_url}, timeout=10)
        anime_data = r_det.json().get('data', [])
    except: anime_data = []
    
    title = anime_data[0].get('judul') if anime_data else (title_p or "")
    chapters = anime_data[0].get('chapter', []) if anime_data else []
    next_ep, prev_ep = get_nav(chapters, chapter_url)
    
    video_info = vid_data[0] if vid_data else None
    
    # AUTO QUALITY LOGIC: Ambil 1 link terbaik, hiraukan sisanya
    player_url = get_best_quality_url(video_info.get('stream', []) if video_info else [])

    return render_template_string(
        HTML_WATCH,
        video=video_info,
        player_url=player_url, # Hanya 1 URL yang dikirim
        anime_title=title,
        anime_url=anime_url,
        next_ep=next_ep, 
        prev_ep=prev_ep,
        current_url=chapter_url
    )

if __name__ == '__main__':
    app.run(debug=True)
