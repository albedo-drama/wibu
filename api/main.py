from flask import Flask, render_template_string, request, redirect, url_for
import requests
from jinja2 import DictLoader
import json

# ==========================================
# 1. KONFIGURASI & DATA STATIS
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
# 2. TEMPLATES HTML (JINJA2)
# ==========================================

HTML_BASE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ALBEDOWIBU-TV{% endblock %}</title>
    <meta property="og:site_name" content="ALBEDOWIBU-TV">
    {% block meta %}{% endblock %}
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.css" />
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">

    <style>
        body { background-color: #0b0c15; color: #e2e8f0; font-family: 'Inter', sans-serif; }
        
        /* Custom Loading Bar */
        #nprogress .bar { background: linear-gradient(to right, #8b5cf6, #ec4899) !important; height: 3px !important; }
        #nprogress .peg { box-shadow: 0 0 10px #ec4899, 0 0 5px #8b5cf6 !important; }
        
        /* Glassmorphism */
        .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.05); }
        .glass-nav { background: rgba(11, 12, 21, 0.85); backdrop-filter: blur(16px); border-bottom: 1px solid rgba(255,255,255,0.05); }
        
        /* Utilities */
        .card-hover:hover { transform: translateY(-4px); box-shadow: 0 10px 30px -10px rgba(139, 92, 246, 0.3); }
        .text-gradient { background: linear-gradient(to right, #a78bfa, #f472b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        
        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #475569; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #6366f1; }
    </style>
</head>
<body class="min-h-screen flex flex-col selection:bg-fuchsia-500 selection:text-white">
    
    <nav class="glass-nav sticky top-0 z-50 transition-all duration-300">
        <div class="container mx-auto px-4 py-3 flex flex-col md:flex-row justify-between items-center gap-4">
            <div class="flex items-center gap-8 w-full md:w-auto justify-between">
                <a href="/" class="text-2xl font-black tracking-tighter flex items-center gap-2 group">
                    <i class="ri-movie-2-fill text-fuchsia-500 group-hover:rotate-12 transition"></i>
                    <span>ALBEDO<span class="text-fuchsia-500">TV</span></span>
                </a>
                
                <div class="hidden md:flex gap-6 text-sm font-bold tracking-wide">
                    <a href="/" class="text-gray-400 hover:text-white hover:text-gradient transition">BERANDA</a>
                    <a href="/movies" class="text-gray-400 hover:text-white hover:text-gradient transition">FILM</a>
                    <a href="/favorites" class="text-gray-400 hover:text-white hover:text-gradient transition flex items-center gap-1">
                        KOLEKSIKU <span class="text-fuchsia-500 text-xs">❤</span>
                    </a>
                </div>
            </div>

            <div class="flex md:hidden gap-4 text-xs font-bold w-full justify-center border-b border-slate-800 pb-2">
                <a href="/" class="text-gray-300">BERANDA</a>
                <a href="/movies" class="text-gray-300">FILM</a>
                <a href="/favorites" class="text-fuchsia-400">KOLEKSIKU ❤</a>
            </div>

            <form action="/search" method="GET" class="w-full md:w-1/3 flex relative group">
                <i class="ri-search-line absolute left-3 top-2.5 text-gray-500 group-focus-within:text-fuchsia-500 transition"></i>
                <input type="text" name="q" placeholder="Cari judul anime..." value="{{ search_query if search_query else '' }}"
                       class="w-full py-2 pl-10 pr-4 bg-slate-900/50 border border-slate-700 rounded-full focus:outline-none focus:border-fuchsia-500 focus:bg-slate-900 text-sm transition-all text-gray-200 placeholder-gray-600">
            </form>
        </div>
    </nav>

    <main class="container mx-auto px-4 py-6 flex-grow">
        {% block content %}{% endblock %}
    </main>

    <footer class="border-t border-slate-900 bg-[#08090f] text-center p-8 mt-12 text-slate-500 text-sm">
        <p class="mb-2">&copy; 2026 ALBEDOWIBU-TV</p>
        <p class="text-xs opacity-50">Dibuat khusus untuk ALBEDO dengan Python & Flask.</p>
    </footer>

    <script>
        // Loading Indicator
        window.addEventListener('beforeunload', () => NProgress.start());
        document.addEventListener("DOMContentLoaded", () => {
            NProgress.done();
            // History Logic
            const history = JSON.parse(localStorage.getItem('watched_episodes') || '[]');
            history.forEach(url => {
                const links = document.querySelectorAll(`a[href*="${url}"]`);
                links.forEach(link => {
                    link.classList.add('opacity-70', 'grayscale-[0.5]');
                    const badge = link.querySelector('.ep-badge');
                    if(badge) {
                        badge.innerText = 'DITONTON';
                        badge.classList.replace('text-slate-500', 'text-green-500');
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

{% if search_query %}
    <div class="mb-8 flex items-center gap-3 animate-fade-in">
        <a href="/" class="w-8 h-8 flex items-center justify-center rounded-full bg-slate-800 hover:bg-slate-700 transition"><i class="ri-arrow-left-line"></i></a>
        <h2 class="text-2xl font-bold text-white">Hasil Pencarian: "<span class="text-fuchsia-400">{{ search_query }}</span>"</h2>
    </div>
{% elif is_movie_page %}
    <div class="mb-8 flex items-center gap-3 border-l-4 border-pink-500 pl-4 py-2 bg-gradient-to-r from-pink-500/10 to-transparent rounded-r-xl">
        <i class="ri-film-line text-2xl text-pink-500"></i>
        <div>
            <h2 class="text-xl font-bold text-white">Layar Lebar & Movie</h2>
            <p class="text-xs text-gray-400">Arsip Halaman {{ current_page }}</p>
        </div>
    </div>
{% else %}
    <div class="mb-8 flex items-center gap-3 border-l-4 border-violet-500 pl-4 py-2 bg-gradient-to-r from-violet-500/10 to-transparent rounded-r-xl">
        <i class="ri-fire-fill text-2xl text-violet-500"></i>
        <div>
            <h2 class="text-xl font-bold text-white">
                {% if current_page == 1 %}Sedang Tayang (Ongoing){% else %}Arsip Rekomendasi{% endif %}
            </h2>
            <p class="text-xs text-gray-400">Update Terbaru Halaman {{ current_page }}</p>
        </div>
    </div>
{% endif %}

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-5 mb-10">
    {% if not data_list and search_query %}
        <div class="col-span-full flex flex-col items-center justify-center py-20 text-gray-500 bg-slate-900/50 rounded-2xl border border-dashed border-slate-800">
            <i class="ri-ghost-line text-4xl mb-2"></i>
            <p>Anime tidak ditemukan.</p>
        </div>
    {% endif %}

    {% for anime in data_list %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="card-hover bg-slate-800 rounded-xl overflow-hidden shadow-lg block relative group border border-slate-700/50 transition-all duration-300">
        <div class="relative aspect-[3/4] overflow-hidden">
            <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover transition duration-700 group-hover:scale-110 group-hover:brightness-110">
            <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-90"></div>
            
            <div class="absolute top-2 right-2 flex flex-col gap-1 items-end">
                {% if anime.score %}
                <span class="bg-yellow-500/90 backdrop-blur text-black text-[10px] font-black px-2 py-0.5 rounded shadow-lg flex items-center gap-1">
                    <i class="ri-star-fill text-[8px]"></i> {{ anime.score }}
                </span>
                {% endif %}
            </div>

            <div class="absolute bottom-0 left-0 right-0 p-4">
                {% if anime.lastch %}
                <p class="text-[10px] text-fuchsia-300 font-bold mb-1 uppercase tracking-wider bg-fuchsia-500/20 w-fit px-2 rounded">{{ anime.lastch }}</p>
                {% endif %}
                <h3 class="text-sm font-bold text-white truncate leading-tight group-hover:text-fuchsia-400 transition">{{ anime.judul }}</h3>
            </div>
        </div>
    </a>
    {% endfor %}
</div>

{% if not search_query %}
<div class="flex justify-center items-center gap-4 mt-12 pb-8 border-t border-slate-800 pt-8">
    {% if current_page > 1 %}
    <a href="?page={{ current_page - 1 }}" class="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-full border border-slate-700 transition flex items-center gap-2">
        <i class="ri-arrow-left-s-line"></i> Halaman Sebelumnya
    </a>
    {% endif %}
    
    <a href="?page={{ current_page + 1 }}" class="px-6 py-2.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:opacity-90 text-white rounded-full transition shadow-lg shadow-fuchsia-900/20 font-bold flex items-center gap-2">
        Halaman Berikutnya <i class="ri-arrow-right-s-line"></i>
    </a>
</div>
{% endif %}
{% endblock %}
"""

HTML_FAVORITES = """
{% extends "base.html" %}
{% block title %}Koleksiku - ALBEDOWIBU-TV{% endblock %}
{% block content %}

<div class="mb-8 flex items-center gap-3 border-l-4 border-red-500 pl-4 py-2 bg-gradient-to-r from-red-500/10 to-transparent rounded-r-xl">
    <i class="ri-heart-3-fill text-2xl text-red-500"></i>
    <div>
        <h2 class="text-xl font-bold text-white">Koleksi Favorit</h2>
        <p class="text-xs text-gray-400">Daftar anime yang kamu simpan</p>
    </div>
</div>

<div id="fav-grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-5 mb-10">
    </div>

<div id="empty-state" class="hidden flex flex-col items-center justify-center py-20 text-gray-500 bg-slate-900/50 rounded-2xl border border-dashed border-slate-800">
    <i class="ri-heart-add-line text-5xl mb-3 text-slate-700"></i>
    <p class="font-medium">Belum ada koleksi.</p>
    <p class="text-sm">Tekan tombol hati di halaman anime untuk menyimpan.</p>
    <a href="/" class="mt-4 px-4 py-2 bg-slate-800 rounded-lg hover:bg-slate-700 text-sm transition text-white">Cari Anime</a>
</div>

<script>
    document.addEventListener("DOMContentLoaded", () => {
        const favs = JSON.parse(localStorage.getItem('albedo_favs') || '[]');
        const grid = document.getElementById('fav-grid');
        const empty = document.getElementById('empty-state');

        if (favs.length === 0) {
            empty.classList.remove('hidden');
        } else {
            favs.forEach(anime => {
                const html = `
                <a href="${anime.url}" class="card-hover bg-slate-800 rounded-xl overflow-hidden shadow-lg block relative group border border-slate-700/50 transition-all duration-300">
                    <div class="relative aspect-[3/4] overflow-hidden">
                        <img src="${anime.cover}" class="w-full h-full object-cover">
                        <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-90"></div>
                        <div class="absolute bottom-0 left-0 right-0 p-4">
                            <h3 class="text-sm font-bold text-white truncate leading-tight group-hover:text-fuchsia-400 transition">${anime.judul}</h3>
                        </div>
                        <button onclick="removeFav(event, '${anime.url}')" class="absolute top-2 right-2 bg-red-500 text-white w-8 h-8 rounded-full flex items-center justify-center shadow-lg hover:bg-red-600 transition z-20">
                            <i class="ri-delete-bin-line"></i>
                        </button>
                    </div>
                </a>`;
                grid.insertAdjacentHTML('beforeend', html);
            });
        }
    });

    function removeFav(e, url) {
        e.preventDefault(); // Prevent navigating
        if(!confirm('Hapus dari koleksi?')) return;
        
        let favs = JSON.parse(localStorage.getItem('albedo_favs') || '[]');
        favs = favs.filter(f => f.url !== url);
        localStorage.setItem('albedo_favs', JSON.stringify(favs));
        location.reload();
    }
</script>
{% endblock %}
"""

HTML_GENRES = """
{% extends "base.html" %}
{% block title %}Genre - ALBEDOWIBU-TV{% endblock %}
{% block content %}
<div class="max-w-6xl mx-auto">
    <div class="text-center mb-10">
        <h2 class="text-3xl font-black text-white tracking-tight mb-2">Jelajahi Genre</h2>
        <p class="text-slate-400 text-sm">Pilih kategori anime favoritmu</p>
    </div>
    
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {% for genre in genres %}
        <a href="/search?q={{ genre }}" class="group bg-slate-800 hover:bg-gradient-to-br hover:from-violet-600 hover:to-fuchsia-600 border border-slate-700 hover:border-transparent p-4 rounded-xl transition-all duration-300 flex items-center justify-center text-center shadow-lg active:scale-95">
            <span class="text-gray-300 font-bold group-hover:text-white text-sm">{{ genre }}</span>
        </a>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

HTML_DETAIL = """
{% extends "base.html" %}
{% block title %}{{ anime.judul }}{% endblock %}
{% block meta %}<meta property="og:image" content="{{ anime.cover }}">{% endblock %}

{% block content %}
{% if error %}
    <div class="text-center py-20 text-red-500 bg-slate-900 rounded-2xl border border-red-900/30">{{ error }}</div>
{% else %}
    <div class="glass rounded-3xl p-6 md:p-8 shadow-2xl mb-10 flex flex-col md:flex-row gap-8 relative overflow-hidden">
        <div class="absolute inset-0 bg-cover bg-center opacity-10 blur-3xl pointer-events-none" style="background-image: url('{{ anime.cover }}');"></div>
        
        <div class="w-full md:w-[280px] shrink-0 relative z-10 mx-auto md:mx-0 group">
            <img src="{{ anime.cover }}" class="w-full rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] border border-slate-600/50 group-hover:scale-[1.02] transition duration-500">
        </div>
        
        <div class="w-full relative z-10">
            <div class="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-4">
                <h1 class="text-2xl md:text-3xl font-black text-white leading-tight flex-1">{{ anime.judul }}</h1>
                
                <button id="fav-btn" onclick="toggleFav()" class="shrink-0 flex items-center gap-2 px-4 py-2 rounded-full bg-slate-800 border border-slate-600 text-gray-300 hover:bg-slate-700 hover:text-red-400 transition active:scale-95">
                    <i id="fav-icon" class="ri-heart-line text-xl"></i>
                    <span id="fav-text" class="text-xs font-bold">FAVORIT</span>
                </button>
            </div>
            
            <div class="flex flex-wrap gap-2 mb-6">
                <span class="bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 px-3 py-1 rounded-lg text-xs font-bold flex items-center gap-1"><i class="ri-star-fill"></i> {{ anime.rating }}</span>
                <span class="bg-blue-500/10 text-blue-400 border border-blue-500/20 px-3 py-1 rounded-lg text-xs font-bold">{{ anime.status }}</span>
                <span class="bg-green-500/10 text-green-400 border border-green-500/20 px-3 py-1 rounded-lg text-xs font-bold">{{ anime.custom_total_eps }}</span>
            </div>

            <div class="flex flex-wrap gap-2 mb-6">
                {% for g in anime.genre %}
                <a href="/search?q={{ g }}" class="text-xs bg-slate-900/80 hover:bg-fuchsia-600 text-slate-400 hover:text-white px-3 py-1.5 rounded-md border border-slate-700 transition">{{ g }}</a>
                {% endfor %}
            </div>

            <div class="bg-slate-950/40 p-5 rounded-2xl border border-white/5 mb-6 max-h-48 overflow-y-auto custom-scroll">
                <p class="text-gray-300 text-sm leading-7">{{ anime.sinopsis }}</p>
            </div>
            
            <div class="flex flex-col sm:flex-row gap-4 sm:gap-8 text-xs text-gray-500 font-mono border-t border-white/5 pt-4">
                <span><i class="ri-building-line"></i> {{ anime.author }}</span>
                <span><i class="ri-calendar-line"></i> {{ anime.published }}</span>
            </div>
        </div>
    </div>

    <div class="glass p-6 rounded-3xl border border-slate-800">
        <div class="flex justify-between items-center mb-6">
            <h3 class="text-xl font-bold text-white flex items-center gap-2"><i class="ri-list-check"></i> Daftar Episode</h3>
            <button onclick="reverseList()" class="text-xs bg-slate-800 hover:bg-slate-700 text-gray-300 px-4 py-2 rounded-full border border-slate-700 transition flex items-center gap-2">
                <i class="ri-arrow-up-down-line"></i> Balik Urutan
            </button>
        </div>
        
        <div id="chapter-list" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {% for chapter in anime.chapter %}
            <a href="/watch/{{ anime.series_id if anime.series_id else 'unknown' }}/{{ chapter.url }}" 
               class="bg-slate-900/80 hover:bg-violet-600 border border-slate-700 hover:border-violet-500 p-4 rounded-xl text-center group transition duration-300 relative overflow-hidden active:scale-95">
                <span class="ep-badge absolute top-2 right-2 text-[8px] font-bold text-slate-600 group-hover:text-white/70">BELUM</span>
                <span class="block text-[10px] text-gray-500 group-hover:text-violet-200 mb-1">{{ chapter.date }}</span>
                <span class="text-sm font-bold text-white">Chapter {{ chapter.ch }}</span>
            </a>
            {% endfor %}
        </div>
    </div>

    <script>
        // Sort
        function reverseList() {
            const list = document.getElementById('chapter-list');
            Array.from(list.children).reverse().forEach(item => list.appendChild(item));
        }

        // Favorites Logic
        const animeData = {
            url: window.location.pathname,
            cover: '{{ anime.cover }}',
            judul: '{{ anime.judul|replace("'", "\\'") }}' // Escape quote
        };

        function updateFavBtn() {
            const favs = JSON.parse(localStorage.getItem('albedo_favs') || '[]');
            const isFav = favs.some(f => f.url === animeData.url);
            const btn = document.getElementById('fav-btn');
            const icon = document.getElementById('fav-icon');
            
            if (isFav) {
                btn.classList.add('bg-red-500/10', 'text-red-500', 'border-red-500/50');
                btn.classList.remove('text-gray-300', 'bg-slate-800');
                icon.classList.replace('ri-heart-line', 'ri-heart-fill');
            } else {
                btn.classList.remove('bg-red-500/10', 'text-red-500', 'border-red-500/50');
                btn.classList.add('text-gray-300', 'bg-slate-800');
                icon.classList.replace('ri-heart-fill', 'ri-heart-line');
            }
        }

        function toggleFav() {
            let favs = JSON.parse(localStorage.getItem('albedo_favs') || '[]');
            const index = favs.findIndex(f => f.url === animeData.url);
            
            if (index === -1) {
                favs.push(animeData);
            } else {
                favs.splice(index, 1);
            }
            
            localStorage.setItem('albedo_favs', JSON.stringify(favs));
            updateFavBtn();
        }

        // Init
        updateFavBtn();
    </script>
{% endif %}
{% endblock %}
"""

HTML_WATCH = """
{% extends "base.html" %}
{% block title %}Nonton {{ anime_title }}{% endblock %}
{% block content %}

<div class="max-w-5xl mx-auto">
    <div class="mb-6 flex flex-col gap-2">
        <a href="/anime/{{ anime_url }}" class="text-violet-400 hover:text-white font-bold transition text-sm flex items-center gap-1 w-fit">
            <i class="ri-arrow-left-line"></i> Kembali ke {{ anime_title }}
        </a>
        <h1 class="text-xl md:text-2xl font-black text-white">Sedang Menonton</h1>
    </div>

    {% if video %}
        <div class="bg-black rounded-2xl overflow-hidden shadow-[0_0_40px_rgba(139,92,246,0.15)] border border-slate-800 mb-6 aspect-video relative group">
            {% if video.stream and video.stream|length > 0 %}
            <iframe src="{{ video.stream[0].link }}" class="absolute inset-0 w-full h-full z-10" allowfullscreen scrolling="no" frameborder="0"></iframe>
            {% else %}
            <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-6 bg-slate-900">
                <i class="ri-error-warning-fill text-4xl text-red-500 mb-2"></i>
                <p class="text-gray-300 font-bold">Stream Embed tidak tersedia.</p>
                <p class="text-gray-500 text-sm mt-1">Silakan pilih server alternatif di bawah.</p>
            </div>
            {% endif %}
        </div>

        <div class="glass p-5 rounded-2xl border border-slate-700 shadow-xl">
            
            <div class="flex flex-col md:flex-row justify-between items-center gap-6 mb-6 pb-6 border-b border-slate-700/50">
                <div class="flex gap-3 w-full md:w-auto">
                    {% if prev_ep %}
                    <a href="/watch/{{ anime_url }}/{{ prev_ep.url }}" class="flex-1 px-5 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold transition text-center text-sm border border-slate-700 flex items-center justify-center gap-2">
                        <i class="ri-skip-back-fill"></i> Eps Sebelumnya
                    </a>
                    {% else %}
                    <button disabled class="flex-1 px-5 py-3 bg-slate-900 text-slate-600 rounded-xl font-bold text-center text-sm cursor-not-allowed border border-slate-800 flex items-center justify-center gap-2">
                        <i class="ri-skip-back-line"></i> Eps Sebelumnya
                    </button>
                    {% endif %}

                    {% if next_ep %}
                    <a href="/watch/{{ anime_url }}/{{ next_ep.url }}" class="flex-1 px-5 py-3 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:opacity-90 text-white rounded-xl font-bold transition text-center text-sm shadow-lg shadow-fuchsia-900/30 flex items-center justify-center gap-2">
                        Eps Berikutnya <i class="ri-skip-forward-fill"></i>
                    </a>
                    {% else %}
                    <button disabled class="flex-1 px-5 py-3 bg-slate-900 text-slate-600 rounded-xl font-bold text-center text-sm cursor-not-allowed border border-slate-800 flex items-center justify-center gap-2">
                        Eps Berikutnya <i class="ri-skip-forward-line"></i>
                    </button>
                    {% endif %}
                </div>
                
                <div class="text-right hidden md:block">
                    <p class="text-xs text-slate-500 font-mono">SERVER UTAMA</p>
                    <p class="text-sm font-bold text-violet-400">PIXELDRAIN / MIX</p>
                </div>
            </div>

            <div>
                <p class="text-xs text-gray-400 font-bold uppercase tracking-widest mb-3 flex items-center gap-2">
                    <i class="ri-download-cloud-2-line"></i> Opsi Download / Alternatif
                </p>
                <div class="flex flex-wrap gap-3">
                    {% for s in video.stream %}
                        {# Color Logic #}
                        {% set btn_cls = 'bg-slate-800 hover:bg-slate-700 border-slate-600 text-gray-300' %}
                        {% if '1080' in s.reso %}{% set btn_cls = 'bg-red-900/30 hover:bg-red-600 border-red-500/50 text-red-200 hover:text-white' %}
                        {% elif '720' in s.reso %}{% set btn_cls = 'bg-fuchsia-900/30 hover:bg-fuchsia-600 border-fuchsia-500/50 text-fuchsia-200 hover:text-white' %}
                        {% elif '480' in s.reso %}{% set btn_cls = 'bg-emerald-900/30 hover:bg-emerald-600 border-emerald-500/50 text-emerald-200 hover:text-white' %}
                        {% endif %}

                        <a href="{{ s.link }}" target="_blank" 
                           class="{{ btn_cls }} border px-4 py-2 rounded-lg transition flex items-center gap-2 group text-xs font-bold">
                            <i class="ri-film-line"></i> {{ s.reso }}
                            <span class="opacity-50 font-normal ml-1">({{ s.provide }})</span>
                        </a>
                    {% endfor %}
                </div>
            </div>
        </div>
    {% else %}
        <div class="text-center py-24 bg-slate-900/50 rounded-2xl border border-slate-800">
            <i class="ri-file-damage-line text-4xl text-slate-600 mb-2"></i>
            <h2 class="text-lg font-bold text-white mb-1">Video Tidak Tersedia</h2>
            <p class="text-gray-500 text-sm">Server belum merilis video ini atau link rusak.</p>
        </div>
    {% endif %}
</div>

<script>
    // Auto-save history
    document.addEventListener("DOMContentLoaded", function() {
        const currentUrl = "{{ current_url }}";
        let history = JSON.parse(localStorage.getItem('watched_episodes') || '[]');
        if (!history.includes(currentUrl)) {
            history.push(currentUrl);
            localStorage.setItem('watched_episodes', JSON.stringify(history));
        }
    });
</script>
{% endblock %}
"""

# ==========================================
# 3. BACKEND & ROUTING
# ==========================================

app = Flask(__name__)
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE,
    'index.html': HTML_INDEX,
    'favorites.html': HTML_FAVORITES, # New Template
    'genres.html': HTML_GENRES,
    'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH
})

API_BASE = "https://api.sansekai.my.id/api/anime"
HEADERS = {'User-Agent': 'ALBEDOTV/6.0', 'Accept': 'application/json'}

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
    if not q: return redirect('/')
    res = fetch_api('/search', params={'query': q})
    clean_res = res[0]['result'] if res and len(res) > 0 and 'result' in res[0] else []
    return render_template_string(HTML_INDEX, data_list=clean_res, search_query=q)

@app.route('/anime/<path:url_id>')
def detail(url_id):
    data = fetch_api('/detail', params={'urlId': url_id})
    if not data: return render_template_string(HTML_DETAIL, error="Data anime tidak ditemukan.")
    anime = data[0]
    eps = anime.get('chapter', [])
    anime['custom_total_eps'] = f"{len(eps)} Episode" if eps else "?"
    if not anime.get('series_id'): anime['series_id'] = url_id
    return render_template_string(HTML_DETAIL, anime=anime)

@app.route('/watch/<path:anime_url>/<path:chapter_url>')
def watch(anime_url, chapter_url):
    vid = fetch_api('/getvideo', params={'chapterUrlId': chapter_url})
    anime_data = fetch_api('/detail', params={'urlId': anime_url})
    title = anime_data[0].get('judul') if anime_data else "Anime"
    next_ep, prev_ep = get_nav(anime_data[0].get('chapter', []) if anime_data else [], chapter_url)
    
    return render_template_string(
        HTML_WATCH, 
        video=vid[0] if vid else None, 
        anime_title=title, 
        anime_url=anime_url, 
        current_url=chapter_url, 
        next_ep=next_ep, 
        prev_ep=prev_ep
    )

if __name__ == '__main__':
    app.run(debug=True)
