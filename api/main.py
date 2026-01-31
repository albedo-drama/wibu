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
# 2. TEMPLATES HTML (CINEMATIC DESIGN)
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
        :root { --primary: #6366f1; --bg-dark: #050507; --glass: rgba(255, 255, 255, 0.03); }
        body { background-color: var(--bg-dark); color: #eef2ff; font-family: 'Plus Jakarta Sans', sans-serif; -webkit-tap-highlight-color: transparent; }
        
        /* Custom NProgress */
        #nprogress .bar { background: linear-gradient(to right, #8b5cf6, #ec4899) !important; height: 3px; }
        #nprogress .peg { box-shadow: 0 0 15px #8b5cf6, 0 0 5px #ec4899; }

        /* Smooth Scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg-dark); }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #8b5cf6; }

        /* Effects */
        .glass-panel { background: var(--glass); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.05); }
        .text-glow { text-shadow: 0 0 20px rgba(139, 92, 246, 0.5); }
        .card-anim { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        .card-anim:hover { transform: translateY(-5px); box-shadow: 0 15px 30px -10px rgba(139, 92, 246, 0.2); }
        .fade-in { animation: fadeIn 0.5s ease-out forwards; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    
    <nav class="fixed top-0 left-0 right-0 z-50 bg-[#050507]/80 backdrop-blur-xl border-b border-white/5 transition-all duration-300">
        <div class="container mx-auto px-4 h-16 flex items-center justify-between">
            <a href="/" class="flex items-center gap-2 group">
                <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-violet-500/20 group-hover:scale-105 transition">
                    <i class="ri-play-fill text-xl"></i>
                </div>
                <span class="text-lg font-bold tracking-tight text-white hidden sm:block">ALBEDO<span class="text-violet-500">TV</span></span>
            </a>

            <form action="/search" method="GET" class="flex-1 max-w-md mx-4 relative group">
                <div class="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                    <i class="ri-search-line text-gray-500 group-focus-within:text-violet-500 transition"></i>
                </div>
                <input type="text" name="q" placeholder="Cari anime..." value="{{ search_query if search_query else '' }}"
                       class="w-full bg-white/5 border border-white/5 rounded-full py-2.5 pl-10 pr-4 text-sm text-white focus:outline-none focus:bg-white/10 focus:border-violet-500/50 transition-all placeholder-gray-600">
            </form>

            <div class="hidden md:flex items-center gap-1 bg-white/5 p-1 rounded-full border border-white/5">
                <a href="/" class="px-4 py-1.5 rounded-full text-xs font-bold transition {{ 'bg-white/10 text-white' if request.path == '/' else 'text-gray-400 hover:text-white' }}">HOME</a>
                <a href="/movies" class="px-4 py-1.5 rounded-full text-xs font-bold transition {{ 'bg-white/10 text-white' if request.path == '/movies' else 'text-gray-400 hover:text-white' }}">FILM</a>
                <a href="/genres" class="px-4 py-1.5 rounded-full text-xs font-bold transition {{ 'bg-white/10 text-white' if request.path == '/genres' else 'text-gray-400 hover:text-white' }}">GENRE</a>
                <a href="/favorites" class="px-4 py-1.5 rounded-full text-xs font-bold transition {{ 'bg-white/10 text-white' if request.path == '/favorites' else 'text-gray-400 hover:text-white' }}">SAVED</a>
            </div>
        </div>
    </nav>

    <div class="md:hidden fixed bottom-0 left-0 right-0 bg-[#0a0a0c]/95 backdrop-blur-xl border-t border-white/5 flex justify-around items-center p-2 z-50 pb-safe">
        <a href="/" class="flex flex-col items-center p-2 rounded-lg {{ 'text-violet-400' if request.path == '/' else 'text-gray-500' }}">
            <i class="ri-home-5-{{ 'fill' if request.path == '/' else 'line' }} text-xl mb-0.5"></i>
            <span class="text-[10px] font-bold">Home</span>
        </a>
        <a href="/genres" class="flex flex-col items-center p-2 rounded-lg {{ 'text-violet-400' if request.path == '/genres' else 'text-gray-500' }}">
            <i class="ri-compass-3-{{ 'fill' if request.path == '/genres' else 'line' }} text-xl mb-0.5"></i>
            <span class="text-[10px] font-bold">Genre</span>
        </a>
        <a href="/history" class="flex flex-col items-center p-2 rounded-lg {{ 'text-violet-400' if request.path == '/history' else 'text-gray-500' }}">
            <i class="ri-history-line text-xl mb-0.5"></i>
            <span class="text-[10px] font-bold">Riwayat</span>
        </a>
        <a href="/favorites" class="flex flex-col items-center p-2 rounded-lg {{ 'text-violet-400' if request.path == '/favorites' else 'text-gray-500' }}">
            <i class="ri-heart-3-{{ 'fill' if request.path == '/favorites' else 'line' }} text-xl mb-0.5"></i>
            <span class="text-[10px] font-bold">Saved</span>
        </a>
    </div>

    <main class="container mx-auto px-4 pt-24 pb-28 md:pb-12 flex-grow fade-in">
        {% block content %}{% endblock %}
    </main>

    <footer class="hidden md:block text-center p-8 mt-auto border-t border-white/5 text-gray-600 text-xs">
        <p>&copy; 2026 ALBEDOWIBU-TV. Stream Responsibly.</p>
    </footer>

    <script>
        window.addEventListener('beforeunload', () => NProgress.start());
        document.addEventListener("DOMContentLoaded", () => {
            NProgress.done();
            // Auto-mark history
            const history = JSON.parse(localStorage.getItem('watched_episodes') || '[]');
            history.forEach(url => {
                const links = document.querySelectorAll(`a[href*="${url}"]`);
                links.forEach(link => {
                    link.classList.add('opacity-60', 'grayscale');
                    const badge = link.querySelector('.ep-badge');
                    if(badge) { badge.innerHTML = '<i class="ri-check-line text-green-400"></i>'; }
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

{% if current_page == 1 and not search_query and not is_movie_page and data_list %}
    {% set featured = data_list[0] %}
    <div class="relative w-full h-[280px] md:h-[400px] rounded-3xl overflow-hidden mb-12 group">
        <div class="absolute inset-0 bg-cover bg-center transition duration-1000 group-hover:scale-105" style="background-image: url('{{ featured.cover }}');"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-[#050507] via-[#050507]/60 to-transparent"></div>
        
        <div class="absolute bottom-0 left-0 p-6 md:p-10 w-full md:w-2/3">
            <span class="inline-block px-3 py-1 mb-3 rounded-md bg-violet-600/90 text-white text-[10px] font-bold tracking-wider uppercase shadow-lg shadow-violet-600/20">
                Terbaru Rilis
            </span>
            <h1 class="text-2xl md:text-5xl font-black text-white mb-2 leading-tight drop-shadow-lg line-clamp-2">
                {{ featured.judul }}
            </h1>
            <p class="text-gray-300 text-xs md:text-sm mb-6 line-clamp-2 md:line-clamp-none opacity-80">
                Episode terbaru {{ featured.lastch }} sudah tersedia. Tonton sekarang dengan kualitas HD tanpa iklan.
            </p>
            <a href="/anime/{{ featured.url if featured.url else featured.id }}" class="inline-flex items-center gap-2 px-6 py-3 bg-white text-black rounded-xl font-bold text-sm hover:bg-gray-200 transition transform hover:scale-105 shadow-xl">
                <i class="ri-play-circle-fill text-xl"></i> TONTON SEKARANG
            </a>
        </div>
    </div>
{% endif %}

<div class="flex items-center justify-between mb-6">
    <h2 class="text-xl font-bold text-white flex items-center gap-2">
        {% if search_query %}
            <span class="text-violet-500">🔍</span> Hasil Pencarian
        {% elif is_movie_page %}
            <span class="text-pink-500">🎬</span> Movies Archive
        {% else %}
            <span class="text-indigo-500">🔥</span> Update Lainnya
        {% endif %}
    </h2>
    
    <div class="flex items-center gap-2 bg-white/5 rounded-full p-1 border border-white/5">
        {% set base = '/search?q=' + (search_query if search_query else '') + '&page=' if search_query else ('/movies?page=' if is_movie_page else '/?page=') %}
        
        {% if current_page > 1 %}
        <a href="{{ base }}{{ current_page - 1 }}" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/10 text-gray-400 hover:text-white transition"><i class="ri-arrow-left-s-line"></i></a>
        {% endif %}
        <span class="text-xs font-mono font-bold text-white px-2">{{ current_page }}</span>
        <a href="{{ base }}{{ current_page + 1 }}" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/10 text-gray-400 hover:text-white transition"><i class="ri-arrow-right-s-line"></i></a>
    </div>
</div>

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
    {% if not data_list %}
        <div class="col-span-full py-32 text-center">
            <div class="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">👻</div>
            <p class="text-gray-500 text-sm">Tidak ada anime ditemukan.</p>
        </div>
    {% endif %}

    {% for anime in data_list %}
    {% if not (current_page == 1 and not search_query and not is_movie_page and loop.index == 1) %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="card-anim group relative block bg-[#111] rounded-2xl overflow-hidden">
        <div class="aspect-[3/4] overflow-hidden relative">
            <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover transition duration-700 group-hover:scale-110">
            <div class="absolute inset-0 bg-gradient-to-t from-[#050507] via-transparent to-transparent opacity-80"></div>
            
            <div class="absolute top-2 right-2 flex flex-col items-end gap-1">
                {% if anime.score %}
                <span class="bg-yellow-500/90 text-black text-[9px] font-black px-2 py-0.5 rounded-md backdrop-blur-md shadow-lg">★ {{ anime.score }}</span>
                {% endif %}
            </div>

            <div class="absolute bottom-0 left-0 right-0 p-4">
                {% if anime.lastch %}
                <p class="text-[9px] text-violet-300 font-bold mb-1 tracking-wider uppercase">{{ anime.lastch }}</p>
                {% endif %}
                <h3 class="text-sm font-bold text-white leading-tight line-clamp-2 group-hover:text-violet-400 transition">{{ anime.judul }}</h3>
            </div>
            
            <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition duration-300 bg-black/20 backdrop-blur-[2px]">
                <div class="w-10 h-10 rounded-full bg-violet-600 text-white flex items-center justify-center shadow-xl transform scale-50 group-hover:scale-100 transition">
                    <i class="ri-play-fill text-lg"></i>
                </div>
            </div>
        </div>
    </a>
    {% endif %}
    {% endfor %}
</div>

{% endblock %}
"""

HTML_GENRES = """
{% extends "base.html" %}
{% block content %}
<div class="max-w-5xl mx-auto text-center">
    <h1 class="text-3xl font-black text-white mb-2">Jelajahi Genre</h1>
    <p class="text-gray-500 text-sm mb-10">Temukan anime favoritmu berdasarkan kategori</p>
    
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {% for genre in genres %}
        <a href="/search?q={{ genre }}" class="py-4 px-2 bg-white/5 hover:bg-violet-600 border border-white/5 hover:border-violet-500/50 rounded-xl transition group">
            <span class="text-xs font-bold text-gray-300 group-hover:text-white tracking-wide">{{ genre }}</span>
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
    <div class="glass-panel rounded-3xl p-6 md:p-10 mb-10 relative overflow-hidden">
        <div class="absolute inset-0 bg-cover bg-center opacity-20 blur-2xl" style="background-image: url('{{ anime.cover }}');"></div>
        <div class="absolute inset-0 bg-gradient-to-r from-[#050507] via-[#050507]/90 to-transparent"></div>
        
        <div class="relative z-10 grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
            
            <div class="md:col-span-3 lg:col-span-3">
                <img src="{{ anime.cover }}" class="w-48 md:w-full rounded-2xl shadow-2xl border border-white/10 mx-auto md:mx-0">
                
                <div class="mt-4 space-y-2">
                    <a href="#eps" class="block w-full py-3 bg-violet-600 hover:bg-violet-700 text-white text-xs font-bold rounded-xl text-center shadow-lg shadow-violet-600/20 transition">
                        MULAI MENONTON
                    </a>
                    <button onclick="toggleFav()" id="fav-btn" class="block w-full py-3 bg-white/5 hover:bg-white/10 text-gray-300 text-xs font-bold rounded-xl border border-white/5 transition">
                        SIMPAN
                    </button>
                </div>
            </div>

            <div class="md:col-span-9 lg:col-span-9 text-center md:text-left">
                <h1 class="text-3xl md:text-5xl font-black text-white mb-4 leading-tight">{{ anime.judul }}</h1>
                
                <div class="flex flex-wrap justify-center md:justify-start gap-3 mb-6">
                    <div class="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 flex items-center gap-2">
                        <i class="ri-star-fill text-yellow-500"></i>
                        <span class="text-xs font-bold">{{ anime.rating }}</span>
                    </div>
                    <div class="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 flex items-center gap-2">
                        <i class="ri-record-circle-line text-green-500"></i>
                        <span class="text-xs font-bold text-gray-300 uppercase">{{ anime.status }}</span>
                    </div>
                    <div class="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 flex items-center gap-2">
                        <i class="ri-film-line text-blue-500"></i>
                        <span class="text-xs font-bold text-gray-300">{{ anime.custom_total_eps }}</span>
                    </div>
                </div>

                <div class="flex flex-wrap justify-center md:justify-start gap-2 mb-6">
                    {% for g in anime.genre %}
                    <a href="/search?q={{ g }}" class="text-[10px] px-3 py-1 rounded-full bg-white/5 hover:bg-white/20 text-gray-400 hover:text-white transition">{{ g }}</a>
                    {% endfor %}
                </div>

                <div class="bg-black/20 backdrop-blur-sm p-5 rounded-2xl border border-white/5 text-sm text-gray-300 leading-7 text-justify">
                    {{ anime.sinopsis }}
                </div>
            </div>
        </div>
    </div>

    <div id="eps" class="pt-4">
        <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-bold text-white border-l-4 border-violet-500 pl-3">Daftar Episode</h3>
            <button onclick="reverseList()" class="text-xs bg-white/5 hover:bg-white/10 px-4 py-2 rounded-lg text-gray-400 hover:text-white transition">⇅ Terlama - Terbaru</button>
        </div>
        
        <div id="chapter-list" class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-3">
            {% for chapter in anime.chapter %}
            <a href="/watch/{{ anime.series_id }}/{{ chapter.url }}" class="group bg-[#111] hover:bg-violet-600 border border-white/5 hover:border-violet-500/50 p-3 rounded-xl text-center transition relative overflow-hidden">
                <span class="block text-[9px] text-gray-500 group-hover:text-violet-200 mb-1 font-mono">{{ chapter.date }}</span>
                <span class="text-sm font-bold text-white">Ep {{ chapter.ch }}</span>
                <span class="ep-badge absolute top-1 right-1 text-[8px]"></span>
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
            if(isFav) { btn.innerText = "TERSIMPAN"; btn.classList.add('bg-red-600','text-white'); btn.classList.remove('bg-white/5','text-gray-300'); }
            else { btn.innerText = "SIMPAN"; btn.classList.remove('bg-red-600','text-white'); btn.classList.add('bg-white/5','text-gray-300'); }
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
    
    <div class="relative bg-black rounded-2xl overflow-hidden shadow-2xl border border-white/10 aspect-video mb-6 group">
        {% if player_url %}
        <iframe src="{{ player_url }}" class="absolute inset-0 w-full h-full z-10" frameborder="0" allowfullscreen></iframe>
        {% else %}
        <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
            <i class="ri-error-warning-line text-4xl text-gray-700 mb-2"></i>
            <p class="text-gray-500 text-xs">Maaf, video belum tersedia di server.</p>
        </div>
        {% endif %}
    </div>

    <div class="glass-panel p-5 rounded-2xl flex flex-col md:flex-row justify-between items-center gap-4">
        
        <div class="flex items-center gap-4">
            <a href="/anime/{{ anime_url }}" class="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/10 transition">
                <i class="ri-arrow-left-line"></i>
            </a>
            <div>
                <h1 class="text-sm font-bold text-white mb-0.5">Sedang Menonton</h1>
                <p class="text-xs text-violet-400 font-medium truncate max-w-[200px]">{{ anime_title }}</p>
            </div>
        </div>

        <div class="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            <span class="text-[10px] font-bold text-green-400 uppercase tracking-wider">AUTO QUALITY HD</span>
        </div>

        <div class="flex gap-2">
            {% if prev_ep %}
            <a href="/watch/{{ anime_url }}/{{ prev_ep.url }}" class="px-5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-bold text-white border border-white/5 transition">Prev</a>
            {% endif %}
            
            {% if next_ep %}
            <a href="/watch/{{ anime_url }}/{{ next_ep.url }}" class="px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 text-xs font-bold text-white shadow-lg shadow-violet-600/20 transition flex items-center gap-2">
                Next <i class="ri-skip-forward-fill"></i>
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

HTML_FAVORITES = """
{% extends "base.html" %}
{% block content %}
<h2 class="text-xl font-bold text-white mb-6 border-l-4 border-violet-500 pl-3">Koleksi Saya</h2>
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

HTML_HISTORY = """
{% extends "base.html" %}
{% block content %}
<div class="flex justify-between items-center mb-6">
    <h2 class="text-xl font-bold text-white border-l-4 border-violet-500 pl-3">Riwayat Tontonan</h2>
    <button onclick="clearHist()" class="text-xs text-red-500 hover:text-red-400 font-bold">HAPUS SEMUA</button>
</div>
<div id="hist-grid" class="flex flex-col gap-3 max-w-3xl mx-auto"></div>
<script>
    const hist = JSON.parse(localStorage.getItem('albedo_history') || '[]');
    if(hist.length === 0) document.getElementById('hist-grid').innerHTML = '<div class="py-20 text-center text-gray-600 text-sm">Belum ada riwayat.</div>';
    hist.reverse().forEach(item => {
        document.getElementById('hist-grid').insertAdjacentHTML('beforeend', `
        <a href="${item.url}" class="flex gap-4 bg-[#111] p-3 rounded-xl border border-white/5 hover:border-violet-500/30 transition group">
            <div class="w-16 h-20 bg-gray-800 rounded-lg overflow-hidden shrink-0"><img src="${item.cover}" class="w-full h-full object-cover group-hover:opacity-80"></div>
            <div class="flex flex-col justify-center">
                <h3 class="text-sm font-bold text-white mb-1 group-hover:text-violet-400">${item.title}</h3>
                <p class="text-xs text-gray-500">${item.date}</p>
                <div class="mt-2 text-[10px] font-bold text-violet-500 flex items-center gap-1"><i class="ri-play-fill"></i> LANJUTKAN</div>
            </div>
        </a>`);
    });
    function clearHist() { if(confirm('Hapus semua?')) { localStorage.removeItem('albedo_history'); location.reload(); } }
</script>
{% endblock %}
"""

# ==========================================
# 3. BACKEND LOGIC (AUTO QUALITY ENGINE)
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

def smart_fetch(endpoint, params=None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, params=params, timeout=12)
        raw = r.json()
        if isinstance(raw, list): return raw
        if 'data' in raw:
            d = raw['data']
            if isinstance(d, list) and len(d) > 0 and 'result' in d[0]: return d[0]['result']
            return d
        return []
    except: return []

def get_best_quality_url(streams):
    if not streams: return None
    best_link = None
    best_score = 0
    # Logic: 1080p > 720p > 480p > 360p. Prefer MP4 over others.
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
    data = smart_fetch('/latest') if page == 1 else smart_fetch('/recommended', params={'page': page})
    return render_template_string(HTML_INDEX, data_list=data, current_page=page, is_movie_page=False, search_query=None)

@app.route('/movies')
def movies():
    page = request.args.get('page', 1, type=int)
    data = smart_fetch('/movie', params={'page': page})
    return render_template_string(HTML_INDEX, data_list=data, current_page=page, is_movie_page=True, search_query=None)

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
    data = smart_fetch('/search', params={'query': q, 'page': page})
    return render_template_string(HTML_INDEX, data_list=data, search_query=q, current_page=page)

@app.route('/anime/<path:url_id>')
def detail(url_id):
    data = smart_fetch('/detail', params={'urlId': url_id})
    if not data: return render_template_string(HTML_DETAIL, error="Tidak ditemukan.")
    anime = data[0]
    eps = anime.get('chapter', [])
    anime['custom_total_eps'] = f"{len(eps)} Eps" if eps else "?"
    if not anime.get('series_id'): anime['series_id'] = url_id
    return render_template_string(HTML_DETAIL, anime=anime)

@app.route('/watch/<path:anime_url>/<path:chapter_url>')
def watch(anime_url, chapter_url):
    title_p = request.args.get('title')
    cover_p = request.args.get('cover')
    vid_data = smart_fetch('/getvideo', params={'chapterUrlId': chapter_url})
    anime_data = smart_fetch('/detail', params={'urlId': anime_url})
    
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
