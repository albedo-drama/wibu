from flask import Flask, render_template_string, request, redirect, url_for
import requests
from jinja2 import DictLoader
import json
from functools import lru_cache

# ==========================================
# 1. KONFIGURASI APP & CACHE
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
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.css" />

    <style>
        body { background-color: #050505; color: #fff; font-family: 'Poppins', sans-serif; }
        #nprogress .bar { background: #ef4444 !important; height: 3px; }
        .nav-glass { background: rgba(5, 5, 5, 0.9); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.05); }
        .card-anime { transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }
        .card-anime:hover { transform: translateY(-5px); box-shadow: 0 10px 20px -10px rgba(239, 68, 68, 0.3); }
        /* Hide Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #000; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #ef4444; }
    </style>
</head>
<body class="flex flex-col min-h-screen selection:bg-red-600 selection:text-white">
    
    <nav class="nav-glass sticky top-0 z-50 h-16 flex items-center justify-between px-4 md:px-8">
        <a href="/" class="flex items-center gap-2 group">
            <div class="w-8 h-8 bg-gradient-to-br from-red-600 to-rose-700 rounded flex items-center justify-center text-white font-black group-hover:rotate-12 transition shadow-lg shadow-red-900/50">A</div>
            <span class="text-lg md:text-xl font-black tracking-tighter text-white">
                ALBEDO<span class="text-red-600">TV</span>
            </span>
        </a>

        <div class="hidden md:flex gap-6 text-xs font-bold text-gray-400">
            <a href="/" class="hover:text-white transition">BERANDA</a>
            <a href="/movies" class="hover:text-white transition">MOVIES</a>
            <a href="/genres" class="hover:text-white transition">GENRE</a>
            <a href="/favorites" class="hover:text-white transition">KOLEKSI</a>
            <a href="/history" class="hover:text-white transition">RIWAYAT</a>
        </div>

        <form action="/search" method="GET" class="relative group">
            <input type="text" name="q" placeholder="Cari Anime..." value="{{ search_query if search_query else '' }}"
                   class="bg-white/5 border border-white/10 rounded-full py-1.5 pl-4 pr-10 text-xs text-white focus:outline-none focus:border-red-600 w-32 md:w-64 transition-all focus:bg-black">
            <button type="submit" class="absolute right-3 top-1.5 text-gray-500 hover:text-white group-focus-within:text-red-500 transition">
                <i class="ri-search-line"></i>
            </button>
        </form>
    </nav>

    <div class="md:hidden fixed bottom-0 left-0 right-0 bg-black/95 border-t border-white/10 flex justify-around p-3 z-50 pb-5 backdrop-blur-lg">
        <a href="/" class="text-center text-[10px] font-bold text-gray-500 hover:text-white {{ 'text-red-500' if request.path == '/' }}">
            <i class="ri-home-5-fill text-lg block"></i> HOME
        </a>
        <a href="/genres" class="text-center text-[10px] font-bold text-gray-500 hover:text-white {{ 'text-red-500' if request.path == '/genres' }}">
            <i class="ri-layout-grid-fill text-lg block"></i> GENRE
        </a>
        <a href="/favorites" class="text-center text-[10px] font-bold text-gray-500 hover:text-white {{ 'text-red-500' if request.path == '/favorites' }}">
            <i class="ri-heart-3-fill text-lg block"></i> SAVED
        </a>
        <a href="/history" class="text-center text-[10px] font-bold text-gray-500 hover:text-white {{ 'text-red-500' if request.path == '/history' }}">
            <i class="ri-history-line text-lg block"></i> HIST
        </a>
    </div>

    <main class="container mx-auto px-4 py-6 flex-grow pb-24 md:pb-10">
        {% block content %}{% endblock %}
    </main>

    <script>
        window.addEventListener('beforeunload', () => NProgress.start());
        document.addEventListener("DOMContentLoaded", () => NProgress.done());
    </script>
</body>
</html>
"""

HTML_INDEX = """
{% extends "base.html" %}
{% block content %}

<div class="mb-6 flex justify-between items-end border-b border-white/10 pb-4">
    <h1 class="text-xl font-bold text-white uppercase flex items-center gap-2">
        {% if search_query %}
            <i class="ri-search-eye-line text-red-600"></i> Hasil: "{{ search_query }}"
        {% elif is_movie_page %}
            <i class="ri-movie-2-line text-red-600"></i> Daftar Movie
        {% else %}
            <i class="ri-fire-fill text-red-600"></i> Update Terbaru
        {% endif %}
    </h1>
    <span class="text-[10px] bg-white/10 px-2 py-1 rounded text-gray-400">Page {{ current_page }}</span>
</div>

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 md:gap-4">
    {% if not data_list %}
        <div class="col-span-full py-20 text-center bg-white/5 rounded-xl border border-dashed border-white/10">
            <i class="ri-ghost-line text-4xl text-gray-600 mb-2"></i>
            <p class="text-gray-400 text-xs font-bold">TIDAK ADA DATA</p>
            {% if current_page > 1 %}
            <a href="javascript:history.back()" class="inline-block mt-4 px-4 py-2 bg-red-600 rounded text-xs font-bold">Kembali</a>
            {% endif %}
        </div>
    {% endif %}

    {% for anime in data_list %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="card-anime block bg-[#111] rounded-lg overflow-hidden relative group">
        <div class="aspect-[3/4] relative overflow-hidden">
            <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover transition duration-700 group-hover:scale-110 group-hover:opacity-60">
            <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
            
            {% if anime.score %}
            <div class="absolute top-2 right-2 bg-yellow-500 text-black text-[9px] font-black px-1.5 py-0.5 rounded shadow-lg">★ {{ anime.score }}</div>
            {% endif %}
            
            <div class="absolute bottom-0 left-0 right-0 p-3">
                {% if anime.lastch %}
                <span class="bg-red-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded mb-1 inline-block shadow">{{ anime.lastch }}</span>
                {% endif %}
                <h3 class="text-xs md:text-sm font-bold text-gray-100 truncate group-hover:text-red-500 transition">{{ anime.judul }}</h3>
            </div>
            
            <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition duration-300">
                <i class="ri-play-circle-fill text-5xl text-white drop-shadow-lg"></i>
            </div>
        </div>
    </a>
    {% endfor %}
</div>

{% if data_list|length > 0 %}
<div class="flex justify-center items-center gap-3 mt-10 border-t border-white/10 pt-6">
    {% set base = '/search?q=' + (search_query if search_query else '') + '&page=' if search_query else ('/movies?page=' if is_movie_page else '/?page=') %}

    {% if current_page > 1 %}
    <a href="{{ base }}{{ current_page - 1 }}" class="px-5 py-2 bg-[#222] hover:bg-[#333] text-white text-xs font-bold rounded-full transition flex items-center gap-1">
        <i class="ri-arrow-left-s-line"></i> Prev
    </a>
    {% endif %}

    {% if data_list|length >= 10 %}
    <a href="{{ base }}{{ current_page + 1 }}" class="px-5 py-2 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-full transition shadow-lg shadow-red-900/50 flex items-center gap-1">
        Next <i class="ri-arrow-right-s-line"></i>
    </a>
    {% endif %}
</div>
{% endif %}

{% endblock %}
"""

HTML_GENRES = """
{% extends "base.html" %}
{% block content %}
<div class="max-w-5xl mx-auto">
    <h1 class="text-2xl font-black text-center text-white mb-8 tracking-tight">KATEGORI GENRE</h1>
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
        {% for genre in genres %}
        <a href="/search?q={{ genre }}" class="py-3 px-2 bg-[#111] border border-white/5 hover:border-red-600 hover:bg-red-900/20 rounded-lg text-xs font-bold text-gray-400 hover:text-white transition text-center">
            {{ genre }}
        </a>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

HTML_HISTORY = """
{% extends "base.html" %}
{% block title %}Riwayat Nonton{% endblock %}
{% block content %}
<div class="flex justify-between items-center mb-6 border-l-4 border-red-600 pl-4">
    <h2 class="text-xl font-bold text-white">RIWAYAT NONTON</h2>
    <button onclick="clearHistory()" class="text-[10px] text-red-500 hover:text-red-400 underline">Hapus Semua</button>
</div>

<div id="hist-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3"></div>
<div id="empty" class="hidden text-center py-20 text-gray-500 text-sm bg-[#111] rounded-xl">Belum ada riwayat tontonan.</div>

<script>
    const hist = JSON.parse(localStorage.getItem('albedo_history') || '[]');
    if(hist.length === 0) document.getElementById('empty').classList.remove('hidden');
    
    // Urutkan dari yg terbaru (index terakhir ke awal)
    hist.reverse().forEach(item => {
        document.getElementById('hist-grid').insertAdjacentHTML('beforeend', `
        <a href="${item.url}" class="flex gap-3 bg-[#111] p-3 rounded-lg hover:bg-[#1a1a1a] transition group relative">
            <div class="w-16 h-20 shrink-0 rounded overflow-hidden">
                <img src="${item.cover}" class="w-full h-full object-cover group-hover:opacity-80">
            </div>
            <div class="flex flex-col justify-center overflow-hidden">
                <h3 class="text-xs font-bold text-white truncate w-full mb-1 group-hover:text-red-500">${item.title}</h3>
                <p class="text-[10px] text-gray-500">Ditonton: ${item.date}</p>
                <span class="text-[10px] text-red-400 font-bold mt-1">Lanjut Nonton →</span>
            </div>
        </a>`);
    });

    function clearHistory() {
        if(confirm('Hapus semua riwayat?')) {
            localStorage.removeItem('albedo_history');
            location.reload();
        }
    }
</script>
{% endblock %}
"""

HTML_FAVORITES = """
{% extends "base.html" %}
{% block content %}
<h2 class="text-lg font-bold mb-4 border-l-4 border-red-600 pl-3">KOLEKSI SAYA</h2>
<div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3"></div>
<div id="empty" class="hidden text-center py-20 text-gray-500 text-sm bg-[#111] rounded-xl">Belum ada koleksi.</div>
<script>
    const favs = JSON.parse(localStorage.getItem('albedo_favs')||'[]');
    if(favs.length===0) document.getElementById('empty').classList.remove('hidden');
    favs.forEach(a => {
        document.getElementById('grid').insertAdjacentHTML('beforeend', `
        <a href="${a.url}" class="block bg-[#111] rounded-lg overflow-hidden relative group">
            <div class="aspect-[3/4]"><img src="${a.cover}" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition"></div>
            <div class="p-2"><h3 class="text-[10px] font-bold text-gray-300 truncate group-hover:text-red-500">${a.judul}</h3></div>
            <button onclick="rem(event, '${a.url}')" class="absolute top-1 right-1 bg-red-600 text-white w-6 h-6 rounded flex items-center justify-center text-xs shadow hover:scale-110 transition">x</button>
        </a>`);
    });
    function rem(e, u) { e.preventDefault(); if(!confirm('Hapus?'))return; localStorage.setItem('albedo_favs', JSON.stringify(favs.filter(f=>f.url!==u))); location.reload(); }
</script>
{% endblock %}
"""

HTML_DETAIL = """
{% extends "base.html" %}
{% block title %}{{ anime.judul }}{% endblock %}
{% block content %}
{% if error %}
    <div class="text-center py-20 text-red-500 text-xs">{{ error }}</div>
{% else %}
    <div class="relative w-full h-[300px] overflow-hidden rounded-2xl mb-[-100px] shadow-2xl opacity-40">
        <div class="absolute inset-0 bg-cover bg-center blur-md" style="background-image: url('{{ anime.cover }}');"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-[#050505] via-[#050505]/50 to-transparent"></div>
    </div>

    <div class="relative z-10 px-2 md:px-8">
        <div class="flex flex-col md:flex-row gap-6 items-start">
            <img src="{{ anime.cover }}" class="w-40 md:w-60 rounded-xl border-4 border-[#050505] shadow-2xl mx-auto md:mx-0 bg-[#111]">
            
            <div class="flex-1 text-center md:text-left mt-4 md:mt-12">
                <h1 class="text-2xl md:text-4xl font-black text-white mb-2 leading-tight drop-shadow-lg">{{ anime.judul }}</h1>
                
                <div class="flex flex-wrap justify-center md:justify-start gap-2 mb-4 text-[10px] font-bold uppercase text-gray-300">
                    <span class="bg-white/10 px-2 py-1 rounded border border-white/5">★ {{ anime.rating }}</span>
                    <span class="bg-white/10 px-2 py-1 rounded border border-white/5">{{ anime.status }}</span>
                    <span class="bg-white/10 px-2 py-1 rounded border border-white/5">{{ anime.custom_total_eps }}</span>
                </div>

                <div class="flex flex-wrap justify-center md:justify-start gap-1 mb-6">
                    {% for g in anime.genre %}
                    <a href="/search?q={{ g }}" class="text-[10px] px-3 py-1 bg-red-900/20 text-red-400 border border-red-900/30 rounded-full hover:bg-red-600 hover:text-white transition">{{ g }}</a>
                    {% endfor %}
                </div>

                <p class="text-xs text-gray-400 leading-relaxed bg-[#111] p-4 rounded-xl border border-white/5 mb-6 text-justify shadow-inner max-h-40 overflow-y-auto">
                    {{ anime.sinopsis }}
                </p>

                <div class="flex gap-3 justify-center md:justify-start">
                    <button onclick="toggleFav()" id="fav-btn" class="px-6 py-2.5 bg-[#222] hover:bg-[#333] text-white font-bold text-xs rounded-lg transition flex items-center gap-2">
                        <i class="ri-heart-line"></i> <span>KOLEKSI</span>
                    </button>
                    
                    <button onclick="share()" class="px-6 py-2.5 bg-[#222] hover:bg-[#333] text-white font-bold text-xs rounded-lg transition flex items-center gap-2">
                        <i class="ri-share-line"></i> SHARE
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="mt-12 border-t border-white/10 pt-8">
        <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-bold text-white border-l-4 border-red-600 pl-3">DAFTAR EPISODE</h3>
            <button onclick="reverseList()" class="text-[10px] bg-[#222] px-3 py-1 rounded text-gray-400 hover:text-white">⇅ Balik Urutan</button>
        </div>
        
        <div id="chapter-list" class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2 max-h-[600px] overflow-y-auto pr-1 custom-scroll">
            {% for chapter in anime.chapter %}
            <a href="/watch/{{ anime.series_id }}/{{ chapter.url }}?title={{ anime.judul }}&cover={{ anime.cover }}" 
               class="bg-[#111] hover:bg-red-600 border border-white/5 hover:border-red-500 p-2 rounded text-center transition group">
                <span class="block text-[9px] text-gray-500 group-hover:text-red-200 mb-1">{{ chapter.date }}</span>
                <span class="text-xs font-bold text-white group-hover:text-white">Ep {{ chapter.ch }}</span>
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
            if(isFav) { btn.classList.replace('bg-[#222]','bg-red-600'); btn.innerHTML = '<i class="ri-heart-fill"></i> TERSIMPAN'; }
            else { btn.classList.replace('bg-red-600','bg-[#222]'); btn.innerHTML = '<i class="ri-heart-line"></i> KOLEKSI'; }
        }
        function toggleFav() {
            let favs = JSON.parse(localStorage.getItem('albedo_favs')||'[]');
            const idx = favs.findIndex(f=>f.url===animeData.url);
            if(idx===-1) favs.push(animeData); else favs.splice(idx,1);
            localStorage.setItem('albedo_favs', JSON.stringify(favs));
            updateFav();
        }
        function share() {
            if(navigator.share) navigator.share({title: document.title, url: location.href});
            else alert('Link dicopy!');
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
    <div class="mb-4 flex items-center justify-between">
        <a href="/anime/{{ anime_url }}" class="text-[10px] font-bold text-gray-500 hover:text-white flex items-center gap-1">
            <i class="ri-arrow-left-line"></i> KEMBALI
        </a>
        <h1 class="text-xs font-bold text-gray-300 truncate max-w-[200px]">{{ anime_title }}</h1>
    </div>
    
    {% if video %}
        <div class="aspect-video bg-black rounded-xl overflow-hidden mb-6 relative shadow-2xl border border-white/10">
            {% if player_url %}
            <iframe src="{{ player_url }}" class="w-full h-full" frameborder="0" allowfullscreen></iframe>
            {% else %}
            <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-6 bg-[#080808]">
                <i class="ri-error-warning-line text-3xl text-red-600 mb-2"></i>
                <p class="text-gray-400 text-xs font-bold">EMBED TIDAK TERSEDIA</p>
                <p class="text-gray-600 text-[10px] mt-1">Silakan gunakan server di bawah.</p>
            </div>
            {% endif %}
        </div>

        <div class="bg-[#111] p-5 rounded-xl border border-white/5">
            <div class="flex justify-between items-center mb-6">
                <span class="text-[10px] font-bold text-gray-500 uppercase">Navigasi Episode</span>
                <div class="flex gap-2">
                    {% if prev_ep %}
                    <a href="/watch/{{ anime_url }}/{{ prev_ep.url }}?title={{ anime_title }}&cover={{ cover_img }}" class="px-4 py-2 bg-[#222] hover:bg-[#333] rounded text-xs font-bold text-white transition">Prev</a>
                    {% endif %}
                    {% if next_ep %}
                    <a href="/watch/{{ anime_url }}/{{ next_ep.url }}?title={{ anime_title }}&cover={{ cover_img }}" class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-xs font-bold text-white transition shadow-lg shadow-red-900/30">Next</a>
                    {% endif %}
                </div>
            </div>

            <div class="mb-6">
                <p class="text-[10px] font-bold text-gray-500 mb-2 uppercase flex items-center gap-2">
                    <i class="ri-server-line"></i> Server & Resolusi
                </p>
                <div class="flex flex-wrap gap-2">
                    {% for s in video.stream %}
                    <a href="{{ s.link }}" target="_blank" class="px-3 py-2 bg-black border border-white/10 hover:border-red-500 rounded text-[10px] text-gray-300 hover:text-white flex items-center gap-2 transition group">
                        <i class="ri-download-cloud-line group-hover:text-red-500"></i> {{ s.reso }} <span class="opacity-50">({{ s.provide }})</span>
                    </a>
                    {% endfor %}
                </div>
            </div>

            <div class="border-t border-white/10 pt-6">
                <button onclick="loadDisqus()" id="btn-com" class="w-full py-3 bg-[#1a1a1a] hover:bg-[#222] rounded text-xs font-bold text-gray-400 transition">
                    TAMPILKAN KOMENTAR
                </button>
                <div id="disqus_thread" class="mt-4"></div>
            </div>
        </div>
    {% else %}
        <div class="text-center py-20 text-gray-500 text-xs">Video belum rilis.</div>
    {% endif %}
</div>

<script>
    // Save History Logic
    const params = new URLSearchParams(window.location.search);
    const title = params.get('title') || 'Anime';
    const cover = params.get('cover') || '';
    const currentUrl = window.location.pathname + window.location.search;
    
    let history = JSON.parse(localStorage.getItem('albedo_history') || '[]');
    // Remove duplicate if exists
    history = history.filter(h => h.url !== currentUrl);
    // Add to top
    history.push({ title: title, cover: cover, url: currentUrl, date: new Date().toLocaleDateString() });
    // Limit to 20 items
    if(history.length > 20) history.shift();
    
    localStorage.setItem('albedo_history', JSON.stringify(history));

    // Disqus
    function loadDisqus() {
        document.getElementById('btn-com').style.display = 'none';
        var d = document, s = d.createElement('script');
        s.src = 'https://albedowibu.disqus.com/embed.js'; // Placeholder ID
        s.setAttribute('data-timestamp', +new Date());
        (d.head || d.body).appendChild(s);
    }
</script>
{% endblock %}
"""

# ==========================================
# 3. BACKEND LOGIC (CACHE ENABLED)
# ==========================================

app = Flask(__name__)
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE,
    'index.html': HTML_INDEX,
    'genres.html': HTML_GENRES,
    'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH,
    'favorites.html': HTML_FAVORITES,
    'history.html': HTML_HISTORY # NEW Template
})

API_BASE = "https://api.sansekai.my.id/api/anime"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}

# LRU Cache: Menyimpan 128 request terakhir di memori agar cepat
@lru_cache(maxsize=128)
def cached_fetch(endpoint, query_str=None, page=1):
    try:
        # Konversi query string manual ke params
        params = {'page': page}
        if query_str: params['query'] = query_str
        
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, params=params, timeout=10)
        raw = r.json()
        
        if isinstance(raw, list): return raw
        if 'data' in raw:
            d = raw['data']
            if isinstance(d, list) and len(d) > 0 and 'result' in d[0]:
                return d[0]['result']
            return d
        return []
    except: return []

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
    # Gunakan cache fetch
    data = cached_fetch('/latest', page=page) if page == 1 else cached_fetch('/recommended', page=page)
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
    # Detail jarang berubah, tidak perlu cache ketat, tapi boleh jika mau
    # Kita fetch langsung agar selalu update episode baru
    try:
        r = requests.get(f"{API_BASE}/detail", headers=HEADERS, params={'urlId': url_id}, timeout=10)
        raw = r.json()
        data = raw.get('data', [])
    except: data = []
    
    if not data: return render_template_string(HTML_DETAIL, error="Anime tidak ditemukan.")
    anime = data[0]
    eps = anime.get('chapter', [])
    anime['custom_total_eps'] = f"{len(eps)} Eps" if eps else "?"
    if not anime.get('series_id'): anime['series_id'] = url_id
    return render_template_string(HTML_DETAIL, anime=anime)

@app.route('/watch/<path:anime_url>/<path:chapter_url>')
def watch(anime_url, chapter_url):
    # Ambil parameter tambahan dari URL untuk History (Title & Cover)
    title_param = request.args.get('title')
    cover_param = request.args.get('cover')
    
    # Fetch Data Video
    try:
        r_vid = requests.get(f"{API_BASE}/getvideo", headers=HEADERS, params={'chapterUrlId': chapter_url}, timeout=10)
        vid_data = r_vid.json().get('data', [])
    except: vid_data = []

    # Fetch Data Detail (Untuk Navigasi)
    try:
        r_det = requests.get(f"{API_BASE}/detail", headers=HEADERS, params={'urlId': anime_url}, timeout=10)
        anime_data = r_det.json().get('data', [])
    except: anime_data = []
    
    title = anime_data[0].get('judul') if anime_data else (title_param or "Anime")
    cover = anime_data[0].get('cover') if anime_data else (cover_param or "")
    chapters = anime_data[0].get('chapter', []) if anime_data else []
    next_ep, prev_ep = get_nav(chapters, chapter_url)
    
    video_info = vid_data[0] if vid_data else None
    player_url = None
    
    if video_info and 'stream' in video_info:
        for s in video_info['stream']:
            if '.mp4' in s['link'] or 'animekita' in s['link']: player_url = s['link']; break
        if not player_url and video_info['stream']: player_url = video_info['stream'][0]['link']

    return render_template_string(
        HTML_WATCH,
        video=video_info,
        player_url=player_url,
        anime_title=title,
        anime_url=anime_url,
        next_ep=next_ep, 
        prev_ep=prev_ep,
        cover_img=cover # Kirim cover ke template
    )

if __name__ == '__main__':
    app.run(debug=True)
