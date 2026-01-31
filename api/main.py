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
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;700;800&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.css" />

    <style>
        :root { --bg-dark: #050507; --primary: #7c3aed; }
        body { background-color: var(--bg-dark); color: #eef2ff; font-family: 'Plus Jakarta Sans', sans-serif; -webkit-tap-highlight-color: transparent; }
        #nprogress .bar { background: #d946ef !important; height: 3px; }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: #0a0a0c; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 5px; }
        .glass-nav { background: rgba(5, 5, 7, 0.85); backdrop-filter: blur(16px); border-bottom: 1px solid rgba(255,255,255,0.05); }
        .search-glow:focus-within { box-shadow: 0 0 20px rgba(124, 58, 237, 0.3); border-color: #7c3aed; }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    
    <nav class="glass-nav fixed top-0 left-0 right-0 z-50">
        <div class="container mx-auto px-4 h-16 flex items-center justify-between gap-4">
            <a href="/" class="flex items-center gap-2 group shrink-0">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-fuchsia-600 flex items-center justify-center text-white shadow-lg shadow-violet-500/20">
                    <i class="ri-play-mini-fill text-xl"></i>
                </div>
                <span class="text-lg font-bold tracking-tight text-white hidden sm:block">ALBEDO<span class="text-violet-500">TV</span></span>
            </a>

            <form action="/search" method="GET" class="hidden md:flex flex-1 max-w-lg relative group transition-all duration-300">
                <div class="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                    <i class="ri-search-line text-gray-500 group-focus-within:text-violet-500 transition"></i>
                </div>
                <input type="text" name="q" placeholder="Cari anime..." value="{{ search_query if search_query else '' }}"
                       class="w-full bg-[#151518] border border-white/5 rounded-full py-2.5 pl-10 pr-12 text-sm text-white focus:outline-none focus:bg-[#1a1a1d] search-glow transition-all placeholder-gray-600">
            </form>

            <div class="hidden md:flex items-center gap-6 text-sm font-bold text-gray-400">
                <a href="/" class="hover:text-white transition">HOME</a>
                <a href="/movies" class="hover:text-white transition">MOVIES</a>
                <a href="/genres" class="hover:text-white transition">GENRE</a>
                <a href="/favorites" class="hover:text-white transition">SAVED</a>
            </div>

            <a href="/search" class="md:hidden w-10 h-10 flex items-center justify-center bg-white/5 rounded-full text-white">
                <i class="ri-search-2-line"></i>
            </a>
        </div>
    </nav>

    <div class="md:hidden fixed bottom-0 left-0 right-0 bg-[#0a0a0c]/95 backdrop-blur-xl border-t border-white/5 flex justify-around items-center p-2 z-50 pb-safe">
        <a href="/" class="flex flex-col items-center p-2 {{ 'text-violet-400' if request.path == '/' else 'text-gray-500' }}">
            <i class="ri-home-5-{{ 'fill' if request.path == '/' else 'line' }} text-xl"></i>
        </a>
        <a href="/genres" class="flex flex-col items-center p-2 {{ 'text-violet-400' if request.path == '/genres' else 'text-gray-500' }}">
            <i class="ri-compass-3-{{ 'fill' if request.path == '/genres' else 'line' }} text-xl"></i>
        </a>
        <a href="/favorites" class="flex flex-col items-center p-2 {{ 'text-violet-400' if request.path == '/favorites' else 'text-gray-500' }}">
            <i class="ri-heart-3-{{ 'fill' if request.path == '/favorites' else 'line' }} text-xl"></i>
        </a>
        <a href="/history" class="flex flex-col items-center p-2 {{ 'text-violet-400' if request.path == '/history' else 'text-gray-500' }}">
            <i class="ri-history-line text-xl"></i>
        </a>
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
{% block title %}Pencarian - ALBEDO TV{% endblock %}
{% block content %}
<div class="max-w-2xl mx-auto flex flex-col justify-center min-h-[60vh]">
    
    <div class="text-center mb-8">
        <h1 class="text-3xl md:text-4xl font-black text-white mb-2">Mau Nonton Apa?</h1>
        <p class="text-gray-500">Cari judul anime, movie, atau genre favoritmu.</p>
    </div>

    <form action="/search" method="GET" class="relative group mb-10">
        <div class="absolute inset-y-0 left-4 flex items-center pointer-events-none">
            <i class="ri-search-line text-2xl text-gray-500 group-focus-within:text-violet-500 transition"></i>
        </div>
        <input type="text" name="q" placeholder="Ketik judul anime..." autofocus autocomplete="off"
               class="w-full bg-[#111] border border-white/10 rounded-2xl py-4 pl-14 pr-4 text-lg text-white focus:outline-none focus:border-violet-500 focus:bg-[#151518] shadow-2xl transition-all placeholder-gray-600">
        <button type="submit" class="absolute right-3 top-3 bg-violet-600 w-10 h-10 rounded-xl flex items-center justify-center hover:bg-violet-500 text-white transition">
            <i class="ri-arrow-right-line"></i>
        </button>
    </form>

    <div id="recent-box" class="hidden mb-8">
        <div class="flex justify-between items-center mb-3 px-1">
            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider">Riwayat Pencarian</h3>
            <button onclick="clearSearchHist()" class="text-xs text-red-500 hover:text-red-400">Hapus</button>
        </div>
        <div id="recent-list" class="flex flex-wrap gap-2"></div>
    </div>

    <div>
        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 px-1">Pencarian Populer</h3>
        <div class="flex flex-wrap gap-2">
            <a href="/search?q=One Piece" class="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/5 rounded-full text-sm text-gray-300 hover:text-white transition">One Piece</a>
            <a href="/search?q=Naruto" class="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/5 rounded-full text-sm text-gray-300 hover:text-white transition">Naruto</a>
            <a href="/search?q=Solo Leveling" class="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/5 rounded-full text-sm text-gray-300 hover:text-white transition">Solo Leveling</a>
            <a href="/search?q=Isekai" class="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/5 rounded-full text-sm text-gray-300 hover:text-white transition">Isekai</a>
            <a href="/search?q=Romance" class="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/5 rounded-full text-sm text-gray-300 hover:text-white transition">Romance</a>
        </div>
    </div>

</div>

<script>
    // Load Search History
    const history = JSON.parse(localStorage.getItem('search_history') || '[]');
    const box = document.getElementById('recent-box');
    const list = document.getElementById('recent-list');

    if (history.length > 0) {
        box.classList.remove('hidden');
        history.slice(0, 8).forEach(q => {
            list.insertAdjacentHTML('beforeend', `
                <a href="/search?q=${q}" class="px-3 py-1.5 bg-[#1a1a1d] hover:bg-[#252529] border border-white/5 rounded-lg text-xs text-gray-300 hover:text-violet-400 transition flex items-center gap-2">
                    <i class="ri-history-line text-gray-600"></i> ${q}
                </a>
            `);
        });
    }

    function clearSearchHist() {
        localStorage.removeItem('search_history');
        location.reload();
    }
</script>
{% endblock %}
"""

HTML_INDEX = """
{% extends "base.html" %}
{% block content %}

{% if search_query %}
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 border-b border-white/5 pb-6">
        <div class="flex items-center gap-4">
            <a href="/search" class="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center transition border border-white/5">
                <i class="ri-arrow-left-line text-white"></i>
            </a>
            <div>
                <p class="text-xs text-gray-500 font-bold uppercase tracking-wider mb-0.5">Hasil Pencarian</p>
                <h1 class="text-2xl font-black text-white">"{{ search_query }}"</h1>
            </div>
        </div>
        <form action="/search" method="GET" class="relative w-full md:w-64">
            <input type="text" name="q" placeholder="Cari lagi..." 
                   class="w-full bg-[#151518] border border-white/10 rounded-full py-2 pl-4 pr-10 text-xs text-white focus:outline-none focus:border-violet-500 transition-all">
            <button type="submit" class="absolute right-3 top-1.5 text-gray-500 hover:text-white"><i class="ri-search-line"></i></button>
        </form>
    </div>
    
    <script>
        const q = "{{ search_query }}";
        if(q) {
            let h = JSON.parse(localStorage.getItem('search_history') || '[]');
            if(!h.includes(q)) {
                h.unshift(q);
                if(h.length > 10) h.pop();
                localStorage.setItem('search_history', JSON.stringify(h));
            }
        }
    </script>
{% elif is_movie_page %}
    <div class="mb-8 flex items-center gap-3">
        <span class="p-2 rounded-lg bg-pink-500/10 text-pink-500"><i class="ri-film-fill text-2xl"></i></span>
        <div><h1 class="text-2xl font-bold text-white">Anime Movies</h1><p class="text-xs text-gray-400">Arsip Film Halaman {{ current_page }}</p></div>
    </div>
{% else %}
    <div class="mb-8 flex items-center gap-3">
        <span class="p-2 rounded-lg bg-violet-500/10 text-violet-500"><i class="ri-fire-fill text-2xl"></i></span>
        <div><h1 class="text-2xl font-bold text-white">Update Terbaru</h1><p class="text-xs text-gray-400">Halaman {{ current_page }}</p></div>
    </div>
{% endif %}

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
    {% if not data_list %}
        <div class="col-span-full py-24 text-center bg-[#111] rounded-2xl border border-dashed border-white/10">
            <i class="ri-ghost-line text-4xl text-gray-600 mb-2"></i>
            <p class="text-gray-400 text-sm font-bold">Tidak ada hasil ditemukan.</p>
            <p class="text-gray-600 text-xs mt-1">Coba kata kunci lain atau periksa ejaan.</p>
        </div>
    {% endif %}

    {% for anime in data_list %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="group relative block bg-[#111] rounded-xl overflow-hidden transition-all hover:-translate-y-2 hover:shadow-xl hover:shadow-violet-500/10 border border-white/5">
        <div class="aspect-[3/4] overflow-hidden relative">
            <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover transition duration-700 group-hover:scale-110 group-hover:opacity-60">
            <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-transparent"></div>
            
            <div class="absolute top-2 right-2 flex flex-col items-end gap-1">
                {% if anime.score %}
                <span class="bg-yellow-500 text-black text-[9px] font-black px-1.5 py-0.5 rounded shadow">★ {{ anime.score }}</span>
                {% endif %}
            </div>

            <div class="absolute bottom-0 left-0 right-0 p-3">
                {% if anime.lastch %}
                <span class="text-[9px] font-bold text-violet-300 uppercase tracking-wider mb-1 block">{{ anime.lastch }}</span>
                {% endif %}
                <h3 class="text-sm font-bold text-white leading-tight line-clamp-2 group-hover:text-violet-400 transition">{{ anime.judul }}</h3>
            </div>
        </div>
    </a>
    {% endfor %}
</div>

{% if data_list|length > 0 %}
<div class="flex justify-center items-center gap-3 mt-12 pt-8 border-t border-white/5">
    {% set base = '/search?q=' + (search_query if search_query else '') + '&page=' if search_query else ('/movies?page=' if is_movie_page else '/?page=') %}
    
    {% if current_page > 1 %}
    <a href="{{ base }}{{ current_page - 1 }}" class="px-5 py-2.5 bg-[#151515] hover:bg-[#222] rounded-full text-xs font-bold text-white transition flex items-center gap-2">
        <i class="ri-arrow-left-s-line"></i> Prev
    </a>
    {% endif %}
    
    <span class="text-xs font-mono text-gray-500">Page {{ current_page }}</span>

    <a href="{{ base }}{{ current_page + 1 }}" class="px-5 py-2.5 bg-violet-600 hover:bg-violet-700 rounded-full text-xs font-bold text-white transition flex items-center gap-2 shadow-lg shadow-violet-500/20">
        Next <i class="ri-arrow-right-s-line"></i>
    </a>
</div>
{% endif %}

{% endblock %}
"""

HTML_GENRES = """
{% extends "base.html" %}
{% block content %}
<div class="max-w-6xl mx-auto text-center">
    <h1 class="text-3xl font-black text-white mb-8 tracking-tight">KATEGORI GENRE</h1>
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
        {% for genre in genres %}
        <a href="/search?q={{ genre }}" class="py-4 px-2 bg-[#111] border border-white/5 hover:border-violet-500 hover:bg-violet-900/10 rounded-xl text-xs font-bold text-gray-400 hover:text-white transition shadow-sm hover:shadow-lg hover:shadow-violet-500/10">
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
        <div class="md:col-span-3">
            <img src="{{ anime.cover }}" class="w-48 md:w-full mx-auto rounded-xl shadow-2xl border border-white/10">
            <a href="#chapter-list" class="block w-full mt-4 py-3 bg-violet-600 hover:bg-violet-700 text-white font-bold text-xs rounded-xl text-center shadow-lg transition">
                MULAI MENONTON
            </a>
            <button onclick="toggleFav()" id="fav-btn" class="block w-full mt-2 py-3 bg-[#1a1a1d] hover:bg-[#222] text-gray-400 font-bold text-xs rounded-xl text-center transition">
                SIMPAN
            </button>
        </div>
        
        <div class="md:col-span-9">
            <h1 class="text-2xl md:text-4xl font-black text-white mb-4 leading-tight">{{ anime.judul }}</h1>
            
            <div class="flex flex-wrap gap-3 mb-6 text-xs font-bold text-gray-300">
                <span class="bg-[#1a1a1d] border border-white/5 px-3 py-1.5 rounded-lg flex items-center gap-1"><i class="ri-star-fill text-yellow-500"></i> {{ anime.rating }}</span>
                <span class="bg-[#1a1a1d] border border-white/5 px-3 py-1.5 rounded-lg">{{ anime.status }}</span>
                <span class="bg-[#1a1a1d] border border-white/5 px-3 py-1.5 rounded-lg">{{ anime.custom_total_eps }}</span>
            </div>

            <div class="flex flex-wrap gap-2 mb-6">
                {% for g in anime.genre %}
                <a href="/search?q={{ g }}" class="text-[10px] px-3 py-1 bg-violet-900/20 text-violet-300 border border-violet-500/20 rounded-full hover:bg-violet-600 hover:text-white transition">{{ g }}</a>
                {% endfor %}
            </div>

            <p class="text-sm text-gray-400 leading-7 bg-[#111] p-5 rounded-2xl border border-white/5 mb-6 text-justify">
                {{ anime.sinopsis }}
            </p>
            
            <div class="flex gap-6 text-xs text-gray-600 font-mono uppercase">
                <span>{{ anime.author }}</span>
                <span>{{ anime.published }}</span>
            </div>
        </div>
    </div>

    <div id="chapter-list-container" class="border-t border-white/5 pt-8">
        <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-bold text-white border-l-4 border-violet-500 pl-3">DAFTAR EPISODE</h3>
            <button onclick="reverseList()" class="text-xs bg-[#1a1a1d] hover:bg-[#222] px-4 py-2 rounded-lg text-gray-400 transition">⇅ Balik Urutan</button>
        </div>
        
        <div id="chapter-list" class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-2 max-h-[500px] overflow-y-auto custom-scroll pr-1">
            {% for chapter in anime.chapter %}
            <a href="/watch/{{ anime.series_id }}/{{ chapter.url }}?title={{ anime.judul }}" 
               class="bg-[#111] hover:bg-violet-600 border border-white/5 hover:border-violet-500/50 p-3 rounded-xl text-center transition group">
                <span class="block text-[9px] text-gray-500 group-hover:text-violet-200 mb-1 font-mono">{{ chapter.date }}</span>
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
            if(isFav) { btn.innerText = "TERSIMPAN"; btn.classList.add('bg-violet-600','text-white'); btn.classList.remove('bg-[#1a1a1d]','text-gray-400'); }
            else { btn.innerText = "SIMPAN"; btn.classList.remove('bg-violet-600','text-white'); btn.classList.add('bg-[#1a1a1d]','text-gray-400'); }
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
        <div class="aspect-video bg-black rounded-2xl overflow-hidden mb-6 relative shadow-2xl border border-white/10 group">
            {% if player_url %}
            <iframe src="{{ player_url }}" class="w-full h-full" frameborder="0" allowfullscreen></iframe>
            {% else %}
            <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-6 bg-[#080808]">
                <p class="text-red-500 text-sm font-bold">STREAM ERROR</p>
                <p class="text-gray-500 text-xs mt-1">Coba episode lain atau tunggu update.</p>
            </div>
            {% endif %}
        </div>

        <div class="bg-[#111] p-5 rounded-2xl border border-white/5 flex flex-col md:flex-row justify-between items-center gap-6">
            <div class="text-center md:text-left">
                <h1 class="text-sm font-bold text-white mb-1">Sedang Menonton</h1>
                <p class="text-xs text-violet-400 font-medium truncate max-w-[250px]">{{ anime_title }}</p>
                <div class="mt-2 flex items-center gap-2 justify-center md:justify-start">
                    <span class="text-[10px] bg-green-500/10 text-green-400 px-2 py-0.5 rounded border border-green-500/20">AUTO HD</span>
                </div>
            </div>

            <div class="flex gap-2">
                {% if prev_ep %}
                <a href="/watch/{{ anime_url }}/{{ prev_ep.url }}?title={{ anime_title }}" class="px-5 py-2.5 bg-[#1a1a1d] hover:bg-[#222] rounded-xl text-xs font-bold text-white transition border border-white/5">Prev</a>
                {% endif %}
                
                {% if next_ep %}
                <a href="/watch/{{ anime_url }}/{{ next_ep.url }}?title={{ anime_title }}" class="px-5 py-2.5 bg-violet-600 hover:bg-violet-700 rounded-xl text-xs font-bold text-white transition shadow-lg shadow-violet-600/20 flex items-center gap-2">
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
        const title = "{{ anime_title }}";
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
    <button onclick="if(confirm('Hapus semua?')){localStorage.removeItem('albedo_history');location.reload()}" class="text-xs text-red-500 hover:text-red-400 font-bold">HAPUS SEMUA</button>
</div>
<div id="hist-list" class="flex flex-col gap-2 max-w-2xl mx-auto"></div>
<script>
    // Logic History
    // Note: History tontonan perlu ditangkap saat nonton. Saya update script Watch untuk simpan detail.
    // Untuk sekarang kita tampilkan riwayat pencarian dulu atau placeholder.
    document.getElementById('hist-list').innerHTML = '<div class="py-20 text-center text-gray-500 text-sm">Fitur Riwayat Episode sedang dimutakhirkan.</div>';
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
    'search_landing.html': HTML_SEARCH_LANDING, # NEW TEMPLATE
    'genres.html': HTML_GENRES,
    'favorites.html': HTML_FAVORITES,
    'history.html': HTML_HISTORY,
    'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH
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
    data = cached_fetch('/movie', page=page)
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
    
    # JIKA QUERY KOSONG -> BUKA HALAMAN LANDING SEARCH
    if not q:
        return render_template_string(HTML_SEARCH_LANDING)
    
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
