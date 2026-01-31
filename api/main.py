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
# 2. TEMPLATES HTML
# ==========================================

HTML_BASE = """
<!DOCTYPE html>
<html lang="id" class="dark">
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
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">

    <style>
        :root { --primary: #8b5cf6; --secondary: #ec4899; --bg-deep: #0a0a0c; }
        body { background-color: var(--bg-deep); color: #e2e8f0; font-family: 'Outfit', sans-serif; }
        #nprogress .bar { background: linear-gradient(90deg, var(--primary), var(--secondary)) !important; height: 3px !important; }
        .glass-nav { background: rgba(10, 10, 15, 0.85); backdrop-filter: blur(20px); border-bottom: 1px solid rgba(255,255,255,0.05); }
        .card-hover:hover { transform: translateY(-4px); transition: 0.3s; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #475569; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #6366f1; }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    
    <nav class="glass-nav sticky top-0 z-50">
        <div class="container mx-auto px-4 lg:px-8 py-3 flex flex-col md:flex-row justify-between items-center gap-4">
            <div class="flex items-center gap-8 w-full md:w-auto justify-between">
                <a href="/" class="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-fuchsia-500 tracking-tighter">
                    ALBEDO<span class="text-white">TV</span>
                </a>
                <div class="flex gap-4 md:gap-6 text-xs md:text-sm font-bold tracking-wide">
                    <a href="/" class="text-gray-400 hover:text-white transition">BERANDA</a>
                    <a href="/movies" class="text-gray-400 hover:text-white transition">FILM</a>
                    <a href="/favorites" class="text-gray-400 hover:text-white transition hidden md:block">KOLEKSIKU</a>
                    <a href="/genres" class="text-gray-400 hover:text-white transition md:hidden">GENRE</a>
                </div>
            </div>
            <form action="/search" method="GET" class="w-full md:w-1/3 flex relative group">
                <input type="text" name="q" placeholder="Cari anime / genre..." value="{{ search_query if search_query else '' }}"
                       class="w-full py-2 pl-4 pr-10 bg-slate-900/50 border border-slate-700 rounded-full focus:outline-none focus:border-violet-500 focus:bg-slate-900 text-sm transition-all text-white placeholder-slate-500">
                <button type="submit" class="absolute right-3 top-2 text-slate-500 hover:text-white"><i class="ri-search-2-line"></i></button>
            </form>
        </div>
    </nav>

    <main class="container mx-auto px-4 lg:px-8 py-6 pb-20 md:pb-10 flex-grow">
        {% block content %}{% endblock %}
    </main>

    <footer class="border-t border-slate-900 bg-[#08090f] text-center p-8 mt-12 text-slate-600 text-sm">
        <p>&copy; 2026 ALBEDOWIBU-TV. API by Sansekai.</p>
    </footer>

    <script>
        window.addEventListener('beforeunload', () => NProgress.start());
        document.addEventListener("DOMContentLoaded", () => {
            NProgress.done();
            const history = JSON.parse(localStorage.getItem('watched_episodes') || '[]');
            history.forEach(url => {
                const links = document.querySelectorAll(`a[href*="${url}"]`);
                links.forEach(link => {
                    link.classList.add('opacity-60', 'grayscale');
                    if(link.querySelector('.ep-badge')) link.querySelector('.ep-badge').innerHTML = '<i class="ri-check-line text-green-400"></i>';
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
    <div class="mb-8 flex items-center gap-3">
        <a href="/" class="w-10 h-10 rounded-full bg-slate-800 hover:bg-slate-700 flex items-center justify-center transition"><i class="ri-arrow-left-line text-white"></i></a>
        <div>
            <h2 class="text-2xl font-bold text-white">Hasil: "<span class="text-violet-400">{{ search_query }}</span>"</h2>
            <p class="text-xs text-gray-400">Halaman {{ current_page }}</p>
        </div>
    </div>
{% elif is_movie_page %}
    <div class="mb-8 border-l-4 border-pink-500 pl-4 py-1 bg-gradient-to-r from-pink-900/20 to-transparent">
        <h2 class="text-2xl font-bold text-white">Anime Movies</h2>
        <p class="text-xs text-gray-400">Arsip Film Halaman {{ current_page }}</p>
    </div>
{% else %}
    <div class="mb-8 border-l-4 border-violet-500 pl-4 py-1 bg-gradient-to-r from-violet-900/20 to-transparent">
        <h2 class="text-2xl font-bold text-white">
            {% if current_page == 1 %}🔥 Anime Terbaru{% else %}⭐ Rekomendasi Arsip{% endif %}
        </h2>
        <p class="text-xs text-gray-400">Update Halaman {{ current_page }}</p>
    </div>
{% endif %}

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-5 mb-10">
    {% if not data_list and search_query %}
        <div class="col-span-full py-20 text-center text-gray-500 bg-slate-900/50 rounded-2xl border border-dashed border-slate-800">
            <i class="ri-ghost-line text-4xl mb-2"></i>
            <p>Tidak ada hasil ditemukan atau halaman habis.</p>
            {% if current_page > 1 %}
            <a href="/search?q={{ search_query }}&page={{ current_page - 1 }}" class="text-violet-400 underline mt-2 block">Kembali ke halaman {{ current_page - 1 }}</a>
            {% endif %}
        </div>
    {% endif %}

    {% for anime in data_list %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="card-hover bg-slate-800 rounded-xl overflow-hidden shadow-lg block relative group border border-slate-700/50">
        <div class="relative aspect-[3/4] overflow-hidden">
            <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover transition duration-700 group-hover:scale-110">
            <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-transparent opacity-90"></div>
            
            <div class="absolute top-2 right-2 flex flex-col items-end gap-1">
                {% if anime.score %}
                <span class="bg-yellow-500 text-black text-[10px] font-black px-2 py-0.5 rounded shadow-lg">★ {{ anime.score }}</span>
                {% endif %}
            </div>

            <div class="absolute bottom-0 left-0 right-0 p-4">
                {% if anime.lastch %}<p class="text-[10px] text-fuchsia-300 font-bold mb-1">{{ anime.lastch }}</p>{% endif %}
                <h3 class="text-sm font-bold text-white truncate leading-tight group-hover:text-violet-400 transition">{{ anime.judul }}</h3>
            </div>
        </div>
    </a>
    {% endfor %}
</div>

{% if data_list|length > 0 %}
<div class="flex justify-center items-center gap-4 mt-12 pb-8 border-t border-slate-800 pt-8">
    
    {% if current_page > 1 %}
        {% if search_query %}
            <a href="/search?q={{ search_query }}&page={{ current_page - 1 }}" class="btn-nav">← Prev</a>
        {% elif is_movie_page %}
            <a href="/movies?page={{ current_page - 1 }}" class="btn-nav">← Prev</a>
        {% else %}
            <a href="/?page={{ current_page - 1 }}" class="btn-nav">← Prev</a>
        {% endif %}
    {% else %}
        <button disabled class="btn-nav-disabled">← Prev</button>
    {% endif %}

    <span class="text-slate-500 font-mono text-sm border border-slate-800 px-4 py-1 rounded-full">Halaman {{ current_page }}</span>

    {% if search_query %}
        <a href="/search?q={{ search_query }}&page={{ current_page + 1 }}" class="btn-nav-active">Next →</a>
    {% elif is_movie_page %}
        <a href="/movies?page={{ current_page + 1 }}" class="btn-nav-active">Next →</a>
    {% else %}
        <a href="/?page={{ current_page + 1 }}" class="btn-nav-active">Next →</a>
    {% endif %}

</div>

<style>
    .btn-nav { @apply px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-full border border-slate-700 transition flex items-center gap-2; }
    .btn-nav-disabled { @apply px-6 py-2 bg-slate-900 text-slate-700 rounded-full cursor-not-allowed flex items-center gap-2; }
    .btn-nav-active { @apply px-6 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-full transition shadow-lg shadow-violet-900/20 font-bold flex items-center gap-2; }
</style>
{% endif %}

{% endblock %}
"""

HTML_GENRES = """
{% extends "base.html" %}
{% block title %}Genre - ALBEDOWIBU-TV{% endblock %}
{% block content %}
<div class="max-w-6xl mx-auto text-center">
    <h2 class="text-3xl font-black text-white mb-8">Pilih Genre</h2>
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {% for genre in genres %}
        <a href="/search?q={{ genre }}" class="group bg-slate-800 hover:bg-violet-600 border border-slate-700 hover:border-violet-500 p-4 rounded-xl transition-all shadow-lg">
            <span class="text-gray-300 font-bold group-hover:text-white text-sm">{{ genre }}</span>
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
<div class="mb-8 flex items-center gap-3 border-l-4 border-red-500 pl-4 py-2 bg-gradient-to-r from-red-500/10 to-transparent">
    <h2 class="text-xl font-bold text-white">Koleksi Favorit</h2>
    <p class="text-xs text-gray-400">Tersimpan di browser</p>
</div>
<div id="fav-grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-5 mb-10"></div>
<div id="empty-state" class="hidden flex flex-col items-center justify-center py-20 text-gray-500 bg-slate-900/50 rounded-2xl border border-dashed border-slate-800">
    <i class="ri-heart-add-line text-5xl mb-3"></i><p>Belum ada koleksi.</p>
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
                        <div class="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black to-transparent">
                            <h3 class="text-sm font-bold text-white truncate">${anime.judul}</h3>
                        </div>
                        <button onclick="removeFav(event, '${anime.url}')" class="absolute top-2 right-2 bg-red-500 text-white w-8 h-8 rounded-full flex items-center justify-center shadow-lg hover:bg-red-600 transition z-20"><i class="ri-delete-bin-line"></i></button>
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
    <div class="bg-slate-800/50 backdrop-blur-md rounded-3xl p-6 md:p-8 shadow-2xl border border-white/5 mb-10 flex flex-col md:flex-row gap-8 relative overflow-hidden">
        <div class="absolute inset-0 bg-cover bg-center opacity-10 blur-3xl pointer-events-none" style="background-image: url('{{ anime.cover }}');"></div>
        <div class="w-full md:w-[280px] shrink-0 relative z-10 mx-auto md:mx-0">
            <img src="{{ anime.cover }}" class="w-full rounded-2xl shadow-2xl border border-slate-600/50 group-hover:scale-[1.02] transition duration-500">
        </div>
        <div class="w-full relative z-10">
            <div class="flex flex-col md:flex-row justify-between gap-4 mb-4">
                <h1 class="text-2xl md:text-4xl font-black text-white leading-tight flex-1">{{ anime.judul }}</h1>
                <button id="fav-btn" onclick="toggleFav()" class="shrink-0 flex items-center gap-2 px-4 py-2 rounded-full bg-slate-800 border border-slate-600 text-gray-300 hover:text-red-400 transition font-bold text-xs"><i id="fav-icon" class="ri-heart-line text-lg"></i> <span id="fav-text">SIMPAN</span></button>
            </div>
            <div class="flex flex-wrap gap-2 mb-6 text-xs font-bold uppercase tracking-wide">
                <span class="px-3 py-1 bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 rounded-lg">★ {{ anime.rating }}</span>
                <span class="px-3 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-lg">{{ anime.status }}</span>
                <span class="px-3 py-1 bg-green-500/10 text-green-400 border border-green-500/20 rounded-lg">{{ anime.custom_total_eps }}</span>
            </div>
            <div class="flex flex-wrap gap-2 mb-6">
                {% for g in anime.genre %}
                <a href="/search?q={{ g }}" class="text-xs bg-slate-900/80 hover:bg-violet-600 text-gray-400 hover:text-white px-3 py-1.5 rounded-md border border-slate-700 transition">{{ g }}</a>
                {% endfor %}
            </div>
            <div class="bg-slate-950/40 p-5 rounded-2xl border border-white/5 mb-6 max-h-48 overflow-y-auto custom-scroll">
                <p class="text-gray-300 text-sm leading-7">{{ anime.sinopsis }}</p>
            </div>
            <div class="flex gap-6 text-xs text-gray-500 font-mono">
                <span>{{ anime.author }}</span><span>{{ anime.published }}</span>
            </div>
        </div>
    </div>
    <div class="flex justify-between items-end mb-6 border-b border-slate-800 pb-4">
        <h3 class="text-2xl font-bold text-white tracking-tight">📺 Daftar Episode</h3>
        <button onclick="reverseList()" class="text-xs bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-full border border-slate-700 transition">⇅ Urutkan</button>
    </div>
    <div id="chapter-list" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 pb-12">
        {% for chapter in anime.chapter %}
        <a href="/watch/{{ anime.series_id if anime.series_id else 'unknown' }}/{{ chapter.url }}" class="bg-slate-800 hover:bg-violet-600 border border-slate-700 hover:border-violet-500 p-4 rounded-xl text-center group transition relative overflow-hidden">
            <span class="ep-badge absolute top-2 right-2 text-[10px] text-slate-600 group-hover:text-white">●</span>
            <span class="block text-[10px] text-gray-500 group-hover:text-violet-200 mb-1">{{ chapter.date }}</span>
            <span class="text-sm font-bold text-white">Ep {{ chapter.ch }}</span>
        </a>
        {% endfor %}
    </div>
    <script>
        function reverseList() { const list = document.getElementById('chapter-list'); Array.from(list.children).reverse().forEach(item => list.appendChild(item)); }
        const animeData = { url: window.location.pathname, cover: '{{ anime.cover }}', judul: '{{ anime.judul|replace("'", "\\'") }}' };
        function updateFavBtn() {
            const favs = JSON.parse(localStorage.getItem('albedo_favs') || '[]');
            const isFav = favs.some(f => f.url === animeData.url);
            const btn = document.getElementById('fav-btn'); const icon = document.getElementById('fav-icon'); const txt = document.getElementById('fav-text');
            if (isFav) { btn.classList.replace('text-gray-300', 'text-white'); btn.classList.replace('bg-slate-800', 'bg-red-500'); btn.classList.replace('border-slate-600', 'border-red-500'); icon.classList.replace('ri-heart-line', 'ri-heart-fill'); txt.innerText='TERSIMPAN'; }
            else { btn.classList.replace('text-white', 'text-gray-300'); btn.classList.replace('bg-red-500', 'bg-slate-800'); btn.classList.replace('border-red-500', 'border-slate-600'); icon.classList.replace('ri-heart-fill', 'ri-heart-line'); txt.innerText='SIMPAN'; }
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
        <a href="/anime/{{ anime_url }}" class="text-violet-400 hover:text-white font-bold transition text-sm flex items-center gap-1 w-fit"><i class="ri-arrow-left-line"></i> Kembali</a>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2">
            {% if video %}
            <div class="bg-black rounded-2xl overflow-hidden shadow-2xl border border-slate-800 aspect-video relative z-10 group">
                {% if video.stream and video.stream|length > 0 %}
                <iframe src="{{ video.stream[0].link }}" class="absolute inset-0 w-full h-full" allowfullscreen scrolling="no" frameborder="0"></iframe>
                {% else %}
                <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-6 bg-slate-900"><i class="ri-error-warning-fill text-4xl text-red-500 mb-2"></i><p class="text-gray-300 font-bold">Stream Error</p></div>
                {% endif %}
            </div>
            <div class="mt-6 flex justify-between items-center bg-slate-800 p-4 rounded-xl border border-slate-700">
                <div class="flex gap-2">
                    {% if prev_ep %}
                    <a href="/watch/{{ anime_url }}/{{ prev_ep.url }}" class="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-sm font-bold transition flex items-center gap-1"><i class="ri-skip-back-fill"></i> Prev</a>
                    {% else %}
                    <button disabled class="px-4 py-2 rounded-lg bg-slate-900 text-slate-600 text-sm font-bold cursor-not-allowed">Prev</button>
                    {% endif %}
                    {% if next_ep %}
                    <a href="/watch/{{ anime_url }}/{{ next_ep.url }}" class="px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-700 text-white text-sm font-bold transition flex items-center gap-1 shadow-lg shadow-violet-900/30">Next <i class="ri-skip-forward-fill"></i></a>
                    {% else %}
                    <button disabled class="px-4 py-2 rounded-lg bg-slate-900 text-slate-600 text-sm font-bold cursor-not-allowed">Next</button>
                    {% endif %}
                </div>
                <div class="text-right"><h1 class="text-sm font-bold text-white">Sedang Menonton</h1><p class="text-xs text-violet-400 truncate max-w-[150px]">{{ anime_title }}</p></div>
            </div>
            {% else %}
            <div class="p-10 text-center bg-slate-900 rounded-2xl border border-slate-800"><p class="text-red-400 font-bold">Video Error / Belum Rilis.</p></div>
            {% endif %}
        </div>
        <div class="lg:col-span-1">
            <div class="bg-slate-900/50 backdrop-blur border border-slate-800 p-5 rounded-2xl sticky top-24">
                <h3 class="text-white font-bold mb-4 flex items-center gap-2 text-sm uppercase tracking-wider border-b border-slate-800 pb-2"><i class="ri-server-line text-violet-500"></i> Kualitas Video</h3>
                {% if video and video.stream %}
                <div class="flex flex-col gap-2 max-h-[400px] overflow-y-auto custom-scroll pr-1">
                    {% for s in video.stream %}
                        {% set color_cls = 'border-slate-700 bg-slate-800 text-gray-300 hover:bg-slate-700' %}
                        {% set badge = 'SD' %}
                        {% set badge_color = 'bg-gray-600' %}
                        {% if '1080' in s.reso %}{% set color_cls = 'border-red-500/30 bg-gradient-to-r from-red-900/20 to-transparent text-red-200 hover:border-red-500' %}{% set badge = 'FHD' %}{% set badge_color = 'bg-red-600' %}
                        {% elif '720' in s.reso %}{% set color_cls = 'border-violet-500/30 bg-gradient-to-r from-violet-900/20 to-transparent text-violet-200 hover:border-violet-500' %}{% set badge = 'HD' %}{% set badge_color = 'bg-violet-600' %}
                        {% elif '480' in s.reso %}{% set color_cls = 'border-emerald-500/30 bg-gradient-to-r from-emerald-900/20 to-transparent text-emerald-200 hover:border-emerald-500' %}{% set badge = 'SD' %}{% set badge_color = 'bg-emerald-600' %}
                        {% endif %}
                        <a href="{{ s.link }}" target="_blank" class="flex justify-between items-center p-3 rounded-lg border {{ color_cls }} transition group">
                            <div class="flex items-center gap-3"><span class="{{ badge_color }} text-white text-[10px] font-black px-1.5 py-0.5 rounded shadow">{{ badge }}</span><div class="flex flex-col"><span class="text-sm font-bold">{{ s.reso }}</span><span class="text-[10px] opacity-60 uppercase">{{ s.provide }}</span></div></div><i class="ri-external-link-line opacity-50 group-hover:opacity-100 transition"></i>
                        </a>
                    {% endfor %}
                </div>
                {% else %}
                <p class="text-gray-500 text-xs">Tidak ada server tersedia.</p>
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
# 3. BACKEND ROUTING & LOGIC
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
HEADERS = {'User-Agent': 'ALBEDOTV/9.0', 'Accept': 'application/json'}

def fetch_api(endpoint, params=None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, params=params, timeout=12)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list): return data
        if 'data' in data: return data['data']
        return data
    except: return None

def sort_streams(streams):
    if not streams: return []
    def get_score(s):
        r = s.get('reso', '').lower()
        if '1080' in r: return 4
        if '720' in r: return 3
        if '480' in r: return 2
        if '360' in r: return 1
        return 0
    return sorted(streams, key=get_score, reverse=True)

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
    video_info = None
    if vid and len(vid) > 0:
        video_info = vid[0]
        video_info['stream'] = sort_streams(video_info.get('stream', []))
    
    return render_template_string(
        HTML_WATCH, 
        video=video_info, 
        anime_title=title, 
        anime_url=anime_url, 
        current_url=chapter_url, 
        next_ep=next_ep, 
        prev_ep=prev_ep
    )

if __name__ == '__main__':
    app.run(debug=True)
