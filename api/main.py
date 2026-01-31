from flask import Flask, render_template_string, request, redirect, url_for
import requests
from jinja2 import DictLoader
import json

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
# 2. TEMPLATES HTML (REDESIGNED)
# ==========================================

HTML_BASE = """
<!DOCTYPE html>
<html lang="id" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ALBEDOWIBU-TV{% endblock %}</title>
    <meta property="og:site_name" content="ALBEDOWIBU-TV">
    <meta name="theme-color" content="#0f0f12">
    {% block meta %}{% endblock %}
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.css" />

    <style>
        :root { --primary: #8b5cf6; --secondary: #ec4899; --bg-deep: #0a0a0c; --glass: rgba(20, 20, 30, 0.7); }
        body { background-color: var(--bg-deep); color: #e2e8f0; font-family: 'Outfit', sans-serif; overflow-x: hidden; }
        
        /* Custom NProgress */
        #nprogress .bar { background: linear-gradient(90deg, var(--primary), var(--secondary)) !important; height: 3px !important; }
        #nprogress .peg { box-shadow: 0 0 15px var(--primary), 0 0 5px var(--secondary) !important; }
        
        /* Glass Effect */
        .glass-panel { background: var(--glass); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08); }
        .glass-nav { background: rgba(10, 10, 12, 0.8); backdrop-filter: blur(16px); border-bottom: 1px solid rgba(255,255,255,0.05); }
        
        /* Animations */
        .hover-scale { transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
        .hover-scale:hover { transform: scale(1.03); }
        .fade-in { animation: fadeIn 0.5s ease-out forwards; opacity: 0; transform: translateY(10px); }
        @keyframes fadeIn { to { opacity: 1; transform: translateY(0); } }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #0f0f12; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--primary); }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    
    <nav class="glass-nav sticky top-0 z-50">
        <div class="container mx-auto px-4 lg:px-8 h-16 flex items-center justify-between gap-4">
            <a href="/" class="flex items-center gap-2 group">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-fuchsia-600 flex items-center justify-center text-white shadow-lg shadow-violet-500/20 group-hover:rotate-12 transition">
                    <i class="ri-play-fill font-black"></i>
                </div>
                <span class="text-xl font-bold tracking-tight text-white">ALBEDO<span class="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-fuchsia-400">TV</span></span>
            </a>

            <div class="hidden md:flex items-center gap-1 bg-white/5 p-1 rounded-full border border-white/5">
                <a href="/" class="px-5 py-1.5 rounded-full text-sm font-medium hover:bg-white/10 transition {{ 'text-white bg-white/10' if request.path == '/' else 'text-gray-400' }}">Home</a>
                <a href="/movies" class="px-5 py-1.5 rounded-full text-sm font-medium hover:bg-white/10 transition {{ 'text-white bg-white/10' if request.path == '/movies' else 'text-gray-400' }}">Movies</a>
                <a href="/genres" class="px-5 py-1.5 rounded-full text-sm font-medium hover:bg-white/10 transition {{ 'text-white bg-white/10' if request.path == '/genres' else 'text-gray-400' }}">Genre</a>
                <a href="/favorites" class="px-5 py-1.5 rounded-full text-sm font-medium hover:bg-white/10 transition {{ 'text-white bg-white/10' if request.path == '/favorites' else 'text-gray-400' }}">Koleksi</a>
            </div>

            <form action="/search" method="GET" class="hidden md:flex relative group w-64">
                <input type="text" name="q" placeholder="Cari..." value="{{ search_query if search_query else '' }}"
                       class="w-full bg-slate-900/50 border border-slate-700 text-sm rounded-full py-2 pl-4 pr-10 focus:outline-none focus:border-violet-500 focus:bg-slate-900 transition-all text-white placeholder-slate-500">
                <button type="submit" class="absolute right-3 top-2 text-slate-500 group-focus-within:text-violet-400 hover:text-white transition"><i class="ri-search-2-line"></i></button>
            </form>
            
            <a href="/search?q=" class="md:hidden w-10 h-10 flex items-center justify-center bg-slate-800 rounded-full text-white"><i class="ri-search-2-line"></i></a>
        </div>
    </nav>

    <main class="container mx-auto px-4 lg:px-8 py-6 pb-24 md:pb-12 flex-grow">
        {% block content %}{% endblock %}
    </main>

    <div class="md:hidden fixed bottom-0 left-0 right-0 bg-[#0f0f12]/95 backdrop-blur-xl border-t border-white/5 flex justify-around items-center p-2 z-50 pb-safe">
        <a href="/" class="flex flex-col items-center p-2 text-xs {{ 'text-violet-400' if request.path == '/' else 'text-gray-500' }}">
            <i class="ri-home-5-{{ 'fill' if request.path == '/' else 'line' }} text-xl mb-0.5"></i> Home
        </a>
        <a href="/movies" class="flex flex-col items-center p-2 text-xs {{ 'text-violet-400' if request.path == '/movies' else 'text-gray-500' }}">
            <i class="ri-film-{{ 'fill' if request.path == '/movies' else 'line' }} text-xl mb-0.5"></i> Movie
        </a>
        <a href="/genres" class="flex flex-col items-center p-2 text-xs {{ 'text-violet-400' if request.path == '/genres' else 'text-gray-500' }}">
            <i class="ri-apps-{{ 'fill' if request.path == '/genres' else 'line' }} text-xl mb-0.5"></i> Genre
        </a>
        <a href="/favorites" class="flex flex-col items-center p-2 text-xs {{ 'text-violet-400' if request.path == '/favorites' else 'text-gray-500' }}">
            <i class="ri-heart-3-{{ 'fill' if request.path == '/favorites' else 'line' }} text-xl mb-0.5"></i> Koleksi
        </a>
    </div>

    <footer class="hidden md:block text-center p-8 mt-auto border-t border-white/5 text-slate-600 text-sm">
        <p>&copy; 2026 ALBEDOWIBU-TV. Stream Responsibly.</p>
    </footer>

    <script>
        window.addEventListener('beforeunload', () => NProgress.start());
        document.addEventListener("DOMContentLoaded", () => {
            NProgress.done();
            // History Marker Script
            const history = JSON.parse(localStorage.getItem('watched_episodes') || '[]');
            history.forEach(url => {
                const links = document.querySelectorAll(`a[href*="${url}"]`);
                links.forEach(link => {
                    link.classList.add('opacity-60', 'grayscale');
                    if(link.querySelector('.ep-status')) {
                        link.querySelector('.ep-status').innerHTML = '<span class="text-green-400"><i class="ri-check-double-line"></i> Selesai</span>';
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

<div class="mb-8 fade-in">
{% if search_query %}
    <div class="flex items-center gap-4">
        <a href="/" class="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center transition border border-white/5"><i class="ri-arrow-left-line"></i></a>
        <div>
            <p class="text-xs text-gray-400 uppercase tracking-widest font-bold">Pencarian</p>
            <h1 class="text-3xl font-bold text-white">"{{ search_query }}"</h1>
        </div>
    </div>
{% elif is_movie_page %}
    <div class="p-6 md:p-10 rounded-3xl bg-gradient-to-r from-pink-900/40 to-purple-900/40 border border-white/10 relative overflow-hidden">
        <div class="relative z-10">
            <h1 class="text-3xl md:text-5xl font-extrabold text-white mb-2">Anime Movies</h1>
            <p class="text-gray-300 max-w-lg">Koleksi film anime layar lebar terbaik dengan kualitas tinggi.</p>
        </div>
        <i class="ri-film-fill absolute -right-10 -bottom-10 text-[200px] text-white/5 rotate-12"></i>
    </div>
{% else %}
    {% if current_page == 1 %}
    <div class="p-6 md:p-10 rounded-3xl bg-gradient-to-r from-violet-900/40 to-fuchsia-900/40 border border-white/10 relative overflow-hidden mb-10">
        <div class="relative z-10">
            <div class="flex items-center gap-3 mb-2">
                <span class="bg-violet-500 text-white text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-wider">Premium Access</span>
            </div>
            <h1 class="text-3xl md:text-5xl font-extrabold text-white mb-2">Halo, ALBEDO.</h1>
            <p class="text-gray-300 max-w-lg">Platform streaming anime pribadi tanpa iklan. Update setiap hari dengan server tercepat.</p>
        </div>
        <i class="ri-vip-crown-fill absolute -right-6 -bottom-10 text-[200px] text-white/5 rotate-12"></i>
    </div>
    {% endif %}
    
    <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-white flex items-center gap-2">
            <span class="w-1.5 h-6 bg-gradient-to-b from-violet-500 to-fuchsia-500 rounded-full block"></span>
            {{ 'Terbaru Rilis' if current_page == 1 else 'Arsip Anime' }}
        </h2>
        <span class="text-xs font-mono text-gray-500 bg-white/5 px-2 py-1 rounded">Page {{ current_page }}</span>
    </div>
{% endif %}
</div>

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 md:gap-6 mb-12">
    {% if not data_list and search_query %}
        <div class="col-span-full py-20 text-center">
            <div class="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">👻</div>
            <p class="text-gray-400">Tidak ada hasil ditemukan.</p>
        </div>
    {% endif %}

    {% for anime in data_list %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="group block relative fade-in" style="animation-delay: {{ loop.index0 * 50 }}ms">
        <div class="relative aspect-[3/4] rounded-xl overflow-hidden bg-slate-800 mb-3 shadow-lg shadow-black/50 ring-1 ring-white/5 group-hover:ring-violet-500/50 transition-all duration-300">
            <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover transition duration-500 group-hover:scale-110 group-hover:rotate-1">
            <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-60 group-hover:opacity-80 transition"></div>
            
            <div class="absolute top-2 right-2 flex flex-col items-end gap-1">
                {% if anime.score %}
                <span class="bg-yellow-500 text-black text-[10px] font-black px-2 py-0.5 rounded shadow-lg backdrop-blur-md">★ {{ anime.score }}</span>
                {% endif %}
                {% if anime.lastup == 'Baru di Upload' %}
                <span class="bg-rose-600 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-lg animate-pulse">NEW</span>
                {% endif %}
            </div>

            <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition duration-300">
                <div class="w-12 h-12 rounded-full bg-violet-600/90 backdrop-blur flex items-center justify-center text-white shadow-xl transform scale-50 group-hover:scale-100 transition">
                    <i class="ri-play-fill text-2xl"></i>
                </div>
            </div>
        </div>
        
        <div>
            <h3 class="text-sm md:text-base font-bold text-white truncate group-hover:text-violet-400 transition">{{ anime.judul }}</h3>
            <div class="flex items-center justify-between mt-1">
                {% if anime.lastch %}
                <span class="text-[10px] font-bold text-white/70 bg-white/10 px-1.5 py-0.5 rounded">{{ anime.lastch }}</span>
                {% endif %}
                <span class="text-[10px] text-gray-500">{{ anime.status }}</span>
            </div>
        </div>
    </a>
    {% endfor %}
</div>

{% if data_list|length > 0 %}
<div class="flex justify-center items-center gap-4 border-t border-white/5 pt-8">
    {% if current_page > 1 %}
    <a href="?q={{ search_query }}&page={{ current_page - 1 }}" class="px-6 py-2.5 rounded-full bg-white/5 hover:bg-white/10 text-white text-sm font-bold transition flex items-center gap-2">
        <i class="ri-arrow-left-line"></i> Prev
    </a>
    {% else %}
    <button disabled class="px-6 py-2.5 rounded-full bg-white/5 text-gray-600 text-sm font-bold cursor-not-allowed flex items-center gap-2">
        <i class="ri-arrow-left-line"></i> Prev
    </button>
    {% endif %}

    <div class="h-10 w-10 rounded-full bg-violet-600 text-white flex items-center justify-center font-bold text-sm shadow-lg shadow-violet-500/20">
        {{ current_page }}
    </div>

    <a href="?q={{ search_query }}&page={{ current_page + 1 }}" class="px-6 py-2.5 rounded-full bg-white/5 hover:bg-white/10 text-white text-sm font-bold transition flex items-center gap-2">
        Next <i class="ri-arrow-right-line"></i>
    </a>
</div>
{% endif %}

{% endblock %}
"""

HTML_GENRES = """
{% extends "base.html" %}
{% block title %}Genre - ALBEDOWIBU-TV{% endblock %}
{% block content %}
<div class="max-w-6xl mx-auto fade-in">
    <div class="text-center mb-10">
        <h1 class="text-3xl md:text-4xl font-extrabold text-white mb-2">Jelajahi Genre</h1>
        <p class="text-gray-400">Temukan anime berdasarkan kategori favoritmu.</p>
    </div>
    
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {% for genre in genres %}
        <a href="/search?q={{ genre }}" class="group relative overflow-hidden bg-slate-800 p-4 rounded-xl text-center border border-white/5 hover:border-violet-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-violet-900/20">
            <div class="absolute inset-0 bg-gradient-to-br from-violet-600/0 to-fuchsia-600/0 group-hover:from-violet-600/20 group-hover:to-fuchsia-600/20 transition duration-500"></div>
            <span class="relative z-10 text-sm font-bold text-gray-300 group-hover:text-white">{{ genre }}</span>
        </a>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

HTML_FAVORITES = """
{% extends "base.html" %}
{% block title %}Koleksiku{% endblock %}
{% block content %}
<div class="mb-8 flex items-center gap-4 fade-in">
    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-rose-600 flex items-center justify-center text-white shadow-lg shadow-red-500/30">
        <i class="ri-heart-3-fill text-2xl"></i>
    </div>
    <div>
        <h1 class="text-2xl font-bold text-white">Koleksi Favorit</h1>
        <p class="text-sm text-gray-400">Disimpan secara lokal di perangkat ini.</p>
    </div>
</div>

<div id="fav-grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-5 mb-10"></div>

<div id="empty-state" class="hidden flex flex-col items-center justify-center py-20 text-gray-500 border border-dashed border-white/10 rounded-3xl">
    <div class="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4 text-2xl">💔</div>
    <p class="font-medium">Belum ada anime yang disimpan.</p>
    <a href="/" class="mt-4 text-violet-400 hover:text-violet-300 text-sm font-bold">Cari Anime dulu yuk →</a>
</div>

<script>
    document.addEventListener("DOMContentLoaded", () => {
        const favs = JSON.parse(localStorage.getItem('albedo_favs') || '[]');
        const grid = document.getElementById('fav-grid');
        if (favs.length === 0) document.getElementById('empty-state').classList.remove('hidden');
        else {
            favs.forEach(anime => {
                grid.insertAdjacentHTML('beforeend', `
                <a href="${anime.url}" class="card-hover bg-slate-800 rounded-xl overflow-hidden shadow-lg block relative group border border-slate-700/50">
                    <div class="relative aspect-[3/4] overflow-hidden">
                        <img src="${anime.cover}" class="w-full h-full object-cover">
                        <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-80"></div>
                        <div class="absolute bottom-0 left-0 right-0 p-4">
                            <h3 class="text-sm font-bold text-white truncate">${anime.judul}</h3>
                        </div>
                        <button onclick="removeFav(event, '${anime.url}')" class="absolute top-2 right-2 bg-red-500/90 text-white w-8 h-8 rounded-full flex items-center justify-center shadow-lg hover:bg-red-600 hover:scale-110 transition z-20">
                            <i class="ri-delete-bin-line"></i>
                        </button>
                    </div>
                </a>`);
            });
        }
    });
    function removeFav(e, url) {
        e.preventDefault();
        if(!confirm('Hapus dari koleksi?')) return;
        let favs = JSON.parse(localStorage.getItem('albedo_favs') || '[]');
        localStorage.setItem('albedo_favs', JSON.stringify(favs.filter(f => f.url !== url)));
        location.reload();
    }
</script>
{% endblock %}
"""

HTML_DETAIL = """
{% extends "base.html" %}
{% block title %}{{ anime.judul }}{% endblock %}
{% block meta %}<meta property="og:image" content="{{ anime.cover }}">{% endblock %}
{% block content %}
{% if error %}
    <div class="text-center py-20 text-red-500">{{ error }}</div>
{% else %}
    <div class="relative w-full h-[300px] md:h-[400px] rounded-3xl overflow-hidden mb-[-100px] md:mb-[-120px] shadow-2xl">
        <div class="absolute inset-0 bg-cover bg-center" style="background-image: url('{{ anime.cover }}');"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-[#0a0a0c] via-[#0a0a0c]/80 to-transparent"></div>
        <div class="absolute inset-0 bg-[#0a0a0c]/40 backdrop-blur-sm"></div>
    </div>

    <div class="relative z-10 px-4 md:px-8">
        <div class="flex flex-col md:flex-row gap-8 items-start">
            <div class="w-40 md:w-64 shrink-0 mx-auto md:mx-0">
                <img src="{{ anime.cover }}" class="w-full rounded-xl shadow-2xl border-4 border-slate-800 ring-1 ring-white/10 hover:scale-[1.02] transition duration-500">
            </div>

            <div class="flex-1 pt-4 md:pt-12 text-center md:text-left w-full">
                <h1 class="text-3xl md:text-5xl font-black text-white mb-4 leading-tight">{{ anime.judul }}</h1>
                
                <div class="flex flex-wrap justify-center md:justify-start gap-3 mb-6">
                    <button id="fav-btn" onclick="toggleFav()" class="px-6 py-2 rounded-full bg-white/10 border border-white/10 hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/50 transition flex items-center gap-2 text-sm font-bold">
                        <i id="fav-icon" class="ri-heart-line text-lg"></i> <span id="fav-text">Simpan</span>
                    </button>
                    <a href="#chapter-list" class="px-6 py-2 rounded-full bg-violet-600 hover:bg-violet-700 text-white font-bold text-sm shadow-lg shadow-violet-500/20 flex items-center gap-2 transition">
                        <i class="ri-play-circle-fill text-lg"></i> Nonton
                    </a>
                </div>

                <div class="flex flex-wrap justify-center md:justify-start gap-2 mb-6 text-xs font-bold uppercase tracking-wide text-gray-400">
                    <span class="px-3 py-1 bg-slate-800 rounded-md border border-slate-700"><i class="ri-star-fill text-yellow-500 mr-1"></i> {{ anime.rating }}</span>
                    <span class="px-3 py-1 bg-slate-800 rounded-md border border-slate-700">{{ anime.status }}</span>
                    <span class="px-3 py-1 bg-slate-800 rounded-md border border-slate-700">{{ anime.custom_total_eps }}</span>
                </div>

                <div class="flex flex-wrap justify-center md:justify-start gap-2 mb-6">
                    {% for g in anime.genre %}
                    <a href="/search?q={{ g }}" class="text-xs px-3 py-1 rounded-full bg-white/5 hover:bg-violet-600 hover:text-white border border-white/10 transition">{{ g }}</a>
                    {% endfor %}
                </div>

                <div class="bg-slate-900/50 p-6 rounded-2xl border border-white/5 text-sm leading-relaxed text-gray-300 text-left">
                    <h3 class="text-white font-bold mb-2 text-xs uppercase tracking-wider">Sinopsis</h3>
                    <p>{{ anime.sinopsis }}</p>
                </div>
            </div>
        </div>
    </div>

    <div class="mt-12">
        <div class="flex justify-between items-center mb-6 px-2">
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
                <i class="ri-list-check text-violet-500"></i> Episode
            </h3>
            <button onclick="reverseList()" class="text-xs font-bold text-gray-400 hover:text-white flex items-center gap-1 transition">
                <i class="ri-arrow-up-down-line"></i> Balik Urutan
            </button>
        </div>
        
        <div id="chapter-list" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {% for chapter in anime.chapter %}
            <a href="/watch/{{ anime.series_id if anime.series_id else 'unknown' }}/{{ chapter.url }}" 
               class="bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-violet-500 p-4 rounded-xl text-center group transition relative overflow-hidden">
                <span class="ep-status block text-[10px] text-gray-500 mb-1 group-hover:text-violet-300">{{ chapter.date }}</span>
                <span class="text-sm font-bold text-white">Ep {{ chapter.ch }}</span>
                <div class="absolute inset-0 bg-violet-500/10 opacity-0 group-hover:opacity-100 transition"></div>
            </a>
            {% endfor %}
        </div>
    </div>

    <script>
        function reverseList() { const list = document.getElementById('chapter-list'); Array.from(list.children).reverse().forEach(item => list.appendChild(item)); }
        
        const animeData = { url: window.location.pathname, cover: '{{ anime.cover }}', judul: '{{ anime.judul|replace("'", "\\'") }}' };
        
        function updateFavBtn() {
            const favs = JSON.parse(localStorage.getItem('albedo_favs') || '[]');
            const isFav = favs.some(f => f.url === animeData.url);
            const btn = document.getElementById('fav-btn'); const icon = document.getElementById('fav-icon'); const txt = document.getElementById('fav-text');
            
            if (isFav) { 
                btn.classList.add('bg-red-500', 'border-red-500', 'text-white');
                btn.classList.remove('bg-white/10', 'border-white/10', 'hover:bg-red-500/20');
                icon.classList.replace('ri-heart-line', 'ri-heart-fill');
                txt.innerText = 'Tersimpan';
            } else { 
                btn.classList.remove('bg-red-500', 'border-red-500', 'text-white');
                btn.classList.add('bg-white/10', 'border-white/10', 'hover:bg-red-500/20');
                icon.classList.replace('ri-heart-fill', 'ri-heart-line');
                txt.innerText = 'Simpan';
            }
        }
        
        function toggleFav() {
            let favs = JSON.parse(localStorage.getItem('albedo_favs') || '[]');
            const idx = favs.findIndex(f => f.url === animeData.url);
            if (idx === -1) favs.push(animeData); else favs.splice(idx, 1);
            localStorage.setItem('albedo_favs', JSON.stringify(favs));
            updateFavBtn();
        }
        updateFavBtn();
    </script>
{% endif %}
{% endblock %}
"""

HTML_WATCH = """
{% extends "base.html" %}
{% block title %}Nonton {{ anime_title }}{% endblock %}
{% block content %}
<div class="max-w-6xl mx-auto">
    <div class="mb-6">
        <a href="/anime/{{ anime_url }}" class="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white transition group">
            <span class="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-violet-600 transition"><i class="ri-arrow-left-line"></i></span>
            <span class="font-medium">Kembali ke Episode List</span>
        </a>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2">
            {% if video %}
            <div class="bg-black rounded-2xl overflow-hidden shadow-2xl shadow-violet-900/10 border border-slate-800 aspect-video relative z-10">
                {% if video.stream and video.stream|length > 0 %}
                <iframe src="{{ video.stream[0].link }}" class="absolute inset-0 w-full h-full" allowfullscreen scrolling="no" frameborder="0"></iframe>
                {% else %}
                <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-6">
                    <i class="ri-error-warning-fill text-4xl text-red-500 mb-2"></i>
                    <p class="text-gray-400 font-medium">Embed Player tidak tersedia.</p>
                </div>
                {% endif %}
            </div>
            
            <div class="mt-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 class="text-xl font-bold text-white">Sedang Menonton</h1>
                    <p class="text-violet-400 text-sm font-medium">{{ anime_title }}</p>
                </div>
                
                <div class="flex gap-2">
                    {% if prev_ep %}
                    <a href="/watch/{{ anime_url }}/{{ prev_ep.url }}" class="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-sm font-bold border border-slate-700 transition flex items-center gap-2">
                        <i class="ri-skip-back-fill"></i> Prev
                    </a>
                    {% endif %}
                    {% if next_ep %}
                    <a href="/watch/{{ anime_url }}/{{ next_ep.url }}" class="px-4 py-2 rounded-lg bg-white text-slate-900 hover:bg-gray-200 text-sm font-bold transition flex items-center gap-2">
                        Next <i class="ri-skip-forward-fill"></i>
                    </a>
                    {% endif %}
                </div>
            </div>
            {% else %}
            <div class="p-10 text-center bg-slate-900 rounded-2xl border border-slate-800">
                <p class="text-red-400 font-bold">Video Error / Belum Rilis.</p>
            </div>
            {% endif %}
        </div>

        <div class="lg:col-span-1">
            <div class="glass-panel p-6 rounded-2xl sticky top-24">
                <h3 class="text-white font-bold mb-4 flex items-center gap-2">
                    <i class="ri-server-line text-violet-500"></i> Server & Kualitas
                </h3>
                
                {% if video and video.stream %}
                <div class="flex flex-col gap-2">
                    {% for s in video.stream %}
                        {% set color = 'bg-slate-800 hover:bg-slate-700 border-slate-700' %}
                        {% if '1080' in s.reso %}{% set color = 'bg-gradient-to-r from-red-900/50 to-red-800/50 border-red-500/30 hover:border-red-500' %}
                        {% elif '720' in s.reso %}{% set color = 'bg-gradient-to-r from-violet-900/50 to-purple-800/50 border-violet-500/30 hover:border-violet-500' %}
                        {% elif '480' in s.reso %}{% set color = 'bg-gradient-to-r from-emerald-900/50 to-green-800/50 border-emerald-500/30 hover:border-emerald-500' %}
                        {% endif %}

                        <a href="{{ s.link }}" target="_blank" class="flex justify-between items-center p-3 rounded-xl border transition group {{ color }}">
                            <div class="flex items-center gap-3">
                                <div class="w-8 h-8 rounded-lg bg-black/20 flex items-center justify-center">
                                    <i class="ri-film-line text-white/70"></i>
                                </div>
                                <div class="flex flex-col">
                                    <span class="text-sm font-bold text-white">{{ s.reso }}</span>
                                    <span class="text-[10px] text-gray-400 uppercase tracking-wider">{{ s.provide }}</span>
                                </div>
                            </div>
                            <i class="ri-external-link-line text-white/30 group-hover:text-white transition"></i>
                        </a>
                    {% endfor %}
                </div>
                <p class="text-xs text-gray-500 mt-4 text-center">Klik untuk membuka player alternatif (Direct Link).</p>
                {% else %}
                <p class="text-gray-500 text-sm">Tidak ada server tersedia.</p>
                {% endif %}
            </div>
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

# ==========================================
# 3. BACKEND ROUTING
# ==========================================

app = Flask(__name__)
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE,
    'index.html': HTML_INDEX,
    'favorites.html': HTML_FAVORITES,
    'genres.html': HTML_GENRES,
    'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH
})

API_BASE = "https://api.sansekai.my.id/api/anime"
HEADERS = {'User-Agent': 'ALBEDOTV/7.0', 'Accept': 'application/json'}

def fetch_api(endpoint, params=None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, params=params, timeout=12)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list): return data
        if 'data' in data: return data['data']
        return data
    except: return None

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
    data = fetch_api('/latest') if page == 1 else fetch_api('/recommended', params={'page': page})
    return render_template_string(HTML_INDEX, data_list=data or [], current_page=page, is_movie_page=False)

@app.route('/movies')
def movies():
    page = request.args.get('page', 1, type=int)
    data = fetch_api('/movie', params={'page': page})
    return render_template_string(HTML_INDEX, data_list=data or [], current_page=page, is_movie_page=True)

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
    if not q: return redirect('/')
    res = fetch_api('/search', params={'query': q, 'page': page})
    clean_res = res[0]['result'] if res and len(res) > 0 and 'result' in res[0] else []
    return render_template_string(HTML_INDEX, data_list=clean_res, search_query=q, current_page=page)

@app.route('/anime/<path:url_id>')
def detail(url_id):
    data = fetch_api('/detail', params={'urlId': url_id})
    if not data: return render_template_string(HTML_DETAIL, error="Data anime tidak ditemukan.")
    anime = data[0]
    eps = anime.get('chapter', [])
    anime['custom_total_eps'] = f"{len(eps)} Episodes" if eps else "?"
    if not anime.get('series_id'): anime['series_id'] = url_id
    return render_template_string(HTML_DETAIL, anime=anime)

@app.route('/watch/<path:anime_url>/<path:chapter_url>')
def watch(anime_url, chapter_url):
    vid = fetch_api('/getvideo', params={'chapterUrlId': chapter_url})
    anime_data = fetch_api('/detail', params={'urlId': anime_url})
    title = anime_data[0].get('judul') if anime_data else "Anime"
    next_ep, prev_ep = get_nav(anime_data[0].get('chapter', []) if anime_data else [], chapter_url)
    
    return render_template_string(HTML_WATCH, video=vid[0] if vid else None, anime_title=title, anime_url=anime_url, current_url=chapter_url, next_ep=next_ep, prev_ep=prev_ep)

if __name__ == '__main__':
    app.run(debug=True)
