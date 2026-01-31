from flask import Flask, render_template_string, request, redirect, url_for
import requests
from jinja2 import DictLoader
import json

# ==========================================
# 1. HTML TEMPLATES (MINIMALIS & CLEAN)
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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">

    <style>
        body { background-color: #0a0a0a; color: #e5e5e5; font-family: 'Inter', sans-serif; }
        .card:hover { transform: translateY(-3px); transition: 0.2s; }
        /* Player Control */
        video { outline: none; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #111; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    
    <nav class="bg-black/90 border-b border-white/10 sticky top-0 z-50 backdrop-blur-md">
        <div class="container mx-auto px-4 h-14 flex items-center justify-between">
            <div class="flex items-center gap-6">
                <a href="/" class="text-lg font-black text-white tracking-tighter">ALBEDO<span class="text-indigo-500">TV</span></a>
                <div class="hidden md:flex gap-4 text-xs font-bold text-gray-400">
                    <a href="/" class="hover:text-white transition">HOME</a>
                    <a href="/movies" class="hover:text-white transition">MOVIES</a>
                    <a href="/genres" class="hover:text-white transition">GENRE</a>
                    <a href="/favorites" class="hover:text-white transition">FAVORIT</a>
                </div>
            </div>
            <form action="/search" method="GET" class="relative">
                <input type="text" name="q" placeholder="Cari..." value="{{ search_query if search_query else '' }}"
                       class="bg-white/10 border border-white/10 rounded-md py-1 px-3 text-xs text-white focus:outline-none focus:border-indigo-500 w-32 md:w-48 transition-all">
            </form>
        </div>
        <div class="md:hidden flex justify-around py-2 border-t border-white/5 bg-black text-[10px] font-bold text-gray-500">
            <a href="/" class="hover:text-white">HOME</a>
            <a href="/movies" class="hover:text-white">MOVIES</a>
            <a href="/genres" class="hover:text-white">GENRE</a>
            <a href="/favorites" class="hover:text-white">FAVORIT</a>
        </div>
    </nav>

    <main class="container mx-auto px-4 py-6 flex-grow">
        {% block content %}{% endblock %}
    </main>

    <footer class="border-t border-white/10 bg-black text-center p-6 mt-10 text-gray-600 text-xs">
        <p>&copy; 2026 ALBEDOWIBU-TV</p>
    </footer>
</body>
</html>
"""

HTML_INDEX = """
{% extends "base.html" %}
{% block content %}

<div class="mb-6 flex justify-between items-end">
    <h2 class="text-lg font-bold text-white border-l-4 border-indigo-500 pl-3">
        {% if search_query %}Hasil: {{ search_query }}
        {% elif is_movie_page %}Movies
        {% else %}Terbaru
        {% endif %}
    </h2>
    <span class="text-xs text-gray-500 font-mono">Page {{ current_page }}</span>
</div>

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 md:gap-4">
    {% if not data_list and search_query %}
        <div class="col-span-full py-20 text-center text-gray-500 text-sm">Tidak ada hasil.</div>
    {% endif %}

    {% for anime in data_list %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="card block group relative">
        <div class="relative aspect-[3/4] bg-gray-900 rounded-lg overflow-hidden mb-2">
            <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover group-hover:opacity-80 transition">
            <div class="absolute top-1 right-1 bg-black/80 text-white text-[9px] font-bold px-1.5 py-0.5 rounded backdrop-blur-sm">
                {{ anime.lastch if anime.lastch else 'N/A' }}
            </div>
            {% if anime.score %}
            <div class="absolute bottom-1 left-1 bg-yellow-500 text-black text-[9px] font-bold px-1.5 py-0.5 rounded">★ {{ anime.score }}</div>
            {% endif %}
        </div>
        <h3 class="text-xs md:text-sm font-bold text-gray-200 truncate group-hover:text-indigo-400">{{ anime.judul }}</h3>
    </a>
    {% endfor %}
</div>

{% if data_list|length > 0 %}
<div class="flex justify-center gap-2 mt-8 pt-6 border-t border-white/5">
    {% set base_link = '/search?q=' + search_query + '&page=' if search_query else ('/movies?page=' if is_movie_page else '/?page=') %}
    
    {% if current_page > 1 %}
    <a href="{{ base_link }}{{ current_page - 1 }}" class="px-4 py-1.5 bg-gray-800 hover:bg-gray-700 text-white text-xs rounded border border-gray-700">Prev</a>
    {% endif %}
    
    <a href="{{ base_link }}{{ current_page + 1 }}" class="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs rounded font-bold">Next</a>
</div>
{% endif %}

{% endblock %}
"""

HTML_GENRES = """
{% extends "base.html" %}
{% block title %}Genre{% endblock %}
{% block content %}
<h2 class="text-lg font-bold text-white mb-6 border-l-4 border-indigo-500 pl-3">Daftar Genre</h2>
<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
    {% for genre in genres %}
    <a href="/search?q={{ genre }}" class="bg-gray-900 hover:bg-indigo-900/50 border border-white/5 hover:border-indigo-500/50 py-3 rounded text-center text-xs font-bold text-gray-300 hover:text-white transition">
        {{ genre }}
    </a>
    {% endfor %}
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
    <div class="flex flex-col md:flex-row gap-6 mb-8">
        <div class="w-32 md:w-48 shrink-0 mx-auto md:mx-0">
            <img src="{{ anime.cover }}" class="w-full rounded-lg shadow-lg border border-white/10">
        </div>
        <div class="flex-1 text-center md:text-left">
            <h1 class="text-xl md:text-2xl font-bold text-white mb-2 leading-tight">{{ anime.judul }}</h1>
            
            <div class="flex flex-wrap justify-center md:justify-start gap-2 mb-4 text-[10px] uppercase font-bold text-gray-400">
                <span class="bg-white/5 px-2 py-1 rounded border border-white/5">★ {{ anime.rating }}</span>
                <span class="bg-white/5 px-2 py-1 rounded border border-white/5">{{ anime.status }}</span>
                <span class="bg-white/5 px-2 py-1 rounded border border-white/5">{{ anime.custom_total_eps }}</span>
            </div>

            <div class="bg-white/5 p-3 rounded-lg text-xs text-gray-300 leading-relaxed mb-4 text-justify h-32 overflow-y-auto">
                {{ anime.sinopsis }}
            </div>
            
            <div class="flex justify-center md:justify-start gap-3">
                <button onclick="toggleFav()" id="fav-btn" class="px-4 py-1.5 rounded bg-gray-800 border border-gray-700 text-xs font-bold text-gray-300 hover:bg-gray-700 transition">SIMPAN</button>
            </div>
        </div>
    </div>

    <div class="border-t border-white/10 pt-4">
        <div class="flex justify-between items-center mb-4">
            <h3 class="text-sm font-bold text-white">Episode</h3>
            <button onclick="reverseList()" class="text-[10px] bg-gray-800 px-3 py-1 rounded text-gray-300">⇅ Balik</button>
        </div>
        
        <div id="chapter-list" class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2">
            {% for chapter in anime.chapter %}
            <a href="/watch/{{ anime.series_id if anime.series_id else 'unknown' }}/{{ chapter.url }}" 
               class="bg-gray-900 hover:bg-indigo-600 border border-white/5 p-2 rounded text-center transition group">
                <span class="block text-[10px] text-gray-500 group-hover:text-indigo-200 mb-0.5">{{ chapter.date }}</span>
                <span class="text-xs font-bold text-white">Ep {{ chapter.ch }}</span>
            </a>
            {% endfor %}
        </div>
    </div>

    <script>
        function reverseList() { const list = document.getElementById('chapter-list'); Array.from(list.children).reverse().forEach(item => list.appendChild(item)); }
        // Simple Fav Logic
        const animeData = { url: window.location.pathname, cover: '{{ anime.cover }}', judul: '{{ anime.judul|replace("'", "") }}' };
        function updateBtn() {
            const favs = JSON.parse(localStorage.getItem('favs') || '[]');
            const isFav = favs.some(f => f.url === animeData.url);
            const btn = document.getElementById('fav-btn');
            if(isFav) { btn.innerText = "TERSIMPAN"; btn.classList.add('text-red-400'); }
            else { btn.innerText = "SIMPAN"; btn.classList.remove('text-red-400'); }
        }
        function toggleFav() {
            let favs = JSON.parse(localStorage.getItem('favs') || '[]');
            const idx = favs.findIndex(f => f.url === animeData.url);
            if(idx === -1) favs.push(animeData); else favs.splice(idx, 1);
            localStorage.setItem('favs', JSON.stringify(favs));
            updateBtn();
        }
        updateBtn();
    </script>
{% endif %}
{% endblock %}
"""

HTML_WATCH = """
{% extends "base.html" %}
{% block title %}Nonton {{ anime_title }}{% endblock %}
{% block content %}

<div class="max-w-4xl mx-auto">
    <a href="/anime/{{ anime_url }}" class="text-indigo-400 hover:text-white text-xs font-bold mb-4 inline-block">← KEMBALI</a>

    {% if video %}
        <div class="bg-black rounded-lg overflow-hidden shadow-lg border border-gray-800 mb-4 aspect-video relative">
            {% if player_stream %}
                {% if player_stream.type == 'mp4' %}
                    <video controls autoplay class="w-full h-full">
                        <source src="{{ player_stream.link }}" type="video/mp4">
                        Browser Anda tidak mendukung tag video.
                    </video>
                {% else %}
                    <iframe src="{{ player_stream.link }}" class="w-full h-full" allowfullscreen frameborder="0"></iframe>
                {% endif %}
            {% else %}
                <div class="absolute inset-0 flex items-center justify-center text-red-500 font-bold text-sm">
                    Stream tidak dapat dimuat otomatis.<br>Silakan pilih server di bawah.
                </div>
            {% endif %}
        </div>

        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-gray-900 p-4 rounded-lg border border-white/5">
            <div>
                <h1 class="text-sm font-bold text-white mb-1">Sedang Menonton</h1>
                <p class="text-xs text-gray-400">{{ anime_title }}</p>
            </div>
            
            <div class="flex gap-2">
                {% if prev_ep %}
                <a href="/watch/{{ anime_url }}/{{ prev_ep.url }}" class="px-4 py-1.5 bg-gray-800 hover:bg-gray-700 text-white text-xs font-bold rounded border border-gray-700">Prev</a>
                {% else %}
                <button disabled class="px-4 py-1.5 bg-gray-900 text-gray-700 text-xs font-bold rounded cursor-not-allowed">Prev</button>
                {% endif %}
                
                {% if next_ep %}
                <a href="/watch/{{ anime_url }}/{{ next_ep.url }}" class="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded">Next</a>
                {% else %}
                <button disabled class="px-4 py-1.5 bg-gray-900 text-gray-700 text-xs font-bold rounded cursor-not-allowed">Next</button>
                {% endif %}
            </div>
        </div>

        <div class="mt-6">
            <p class="text-[10px] text-gray-500 font-bold uppercase mb-2">PILIH RESOLUSI</p>
            <div class="flex flex-wrap gap-2">
                {% for s in video.stream %}
                    <a href="{{ s.link }}" target="_blank" class="px-3 py-2 bg-gray-800 hover:bg-indigo-900 border border-gray-700 rounded text-xs text-white transition flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full {{ 'bg-green-500' if '480' in s.reso else ('bg-indigo-500' if '720' in s.reso else 'bg-blue-500') }}"></span>
                        {{ s.reso }} 
                        <span class="opacity-50 text-[9px] uppercase">({{ s.provide }})</span>
                    </a>
                {% endfor %}
            </div>
        </div>

    {% else %}
        <div class="text-center py-20 bg-gray-900 rounded text-gray-500 text-sm">Video Error / Belum Rilis</div>
    {% endif %}
</div>
{% endblock %}
"""

HTML_FAVORITES = """
{% extends "base.html" %}
{% block title %}Favorit{% endblock %}
{% block content %}
<h2 class="text-lg font-bold text-white mb-6 border-l-4 border-red-500 pl-3">Koleksiku</h2>
<div id="fav-grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3"></div>
<div id="empty" class="hidden text-center py-20 text-gray-500 text-sm">Belum ada koleksi.</div>
<script>
    const favs = JSON.parse(localStorage.getItem('favs') || '[]');
    if(favs.length===0) document.getElementById('empty').classList.remove('hidden');
    else {
        favs.forEach(a => {
            document.getElementById('fav-grid').insertAdjacentHTML('beforeend', `
            <a href="${a.url}" class="card block relative">
                <div class="aspect-[3/4] bg-gray-800 rounded mb-2 overflow-hidden"><img src="${a.cover}" class="w-full h-full object-cover"></div>
                <h3 class="text-xs font-bold text-gray-200 truncate">${a.judul}</h3>
            </a>`);
        });
    }
</script>
{% endblock %}
"""

# ==========================================
# 3. LOGIC BACKEND (FIXED PLAYER)
# ==========================================

app = Flask(__name__)
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE,
    'index.html': HTML_INDEX,
    'genres.html': HTML_GENRES, # Pastikan GENRES template di-register
    'favorites.html': HTML_FAVORITES,
    'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH
})

GENRE_LIST = sorted([
    "Action", "Adventure", "Comedy", "Demons", "Drama", "Ecchi", "Fantasy", 
    "Game", "Harem", "Historical", "Horror", "Josei", "Magic", "Martial Arts", 
    "Mecha", "Military", "Music", "Mystery", "Parody", "Police", "Psychological", 
    "Romance", "Samurai", "School", "Sci-Fi", "Seinen", "Shoujo", "Shoujo Ai", 
    "Shounen", "Shounen Ai", "Slice of Life", "Space", "Sports", "Super Power", 
    "Supernatural", "Thriller", "Vampire", "Yuri", "Isekai"
])

API_BASE = "https://api.sansekai.my.id/api/anime"
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}

def fetch_api(endpoint, params=None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, params=params, timeout=10)
        data = r.json()
        if isinstance(data, list): return data
        return data.get('data', [])
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
    data = fetch_api('/latest') if page == 1 else fetch_api('/recommended', params={'page': page})
    return render_template_string(HTML_INDEX, data_list=data or [], current_page=page, is_movie_page=False)

@app.route('/movies')
def movies():
    page = request.args.get('page', 1, type=int)
    data = fetch_api('/movie', params={'page': page})
    return render_template_string(HTML_INDEX, data_list=data or [], current_page=page, is_movie_page=True)

@app.route('/genres')
def genres():
    return render_template_string(HTML_GENRES, genres=GENRE_LIST) # GENRES ROUTE ADDED

@app.route('/favorites')
def favorites():
    return render_template_string(HTML_FAVORITES)

@app.route('/search')
def search():
    q = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    if not q: return redirect('/')
    res = fetch_api('/search', params={'query': q, 'page': page})
    # Fix Search Result Structure
    clean_res = res[0]['result'] if res and len(res) > 0 and 'result' in res[0] else []
    return render_template_string(HTML_INDEX, data_list=clean_res, search_query=q, current_page=page)

@app.route('/anime/<path:url_id>')
def detail(url_id):
    data = fetch_api('/detail', params={'urlId': url_id})
    if not data: return render_template_string(HTML_DETAIL, error="Tidak ditemukan.")
    anime = data[0]
    eps = anime.get('chapter', [])
    anime['custom_total_eps'] = f"{len(eps)} Eps" if eps else "?"
    if not anime.get('series_id'): anime['series_id'] = url_id
    return render_template_string(HTML_DETAIL, anime=anime)

@app.route('/watch/<path:anime_url>/<path:chapter_url>')
def watch(anime_url, chapter_url):
    vid = fetch_api('/getvideo', params={'chapterUrlId': chapter_url})
    anime_data = fetch_api('/detail', params={'urlId': anime_url})
    title = anime_data[0].get('judul') if anime_data else "Anime"
    next_ep, prev_ep = get_nav(anime_data[0].get('chapter', []) if anime_data else [], chapter_url)
    
    video_info = None
    player_stream = None
    
    if vid and len(vid) > 0:
        video_info = vid[0]
        streams = video_info.get('stream', [])
        
        # LOGIKA PLAYER BARU:
        # 1. Cari yang .mp4 / storage.animekita (Paling stabil buat embed)
        # 2. Kalau gak ada, pakai stream pertama
        
        for s in streams:
            if 'animekita' in s['link'] or s['link'].endswith('.mp4'):
                player_stream = {'type': 'mp4', 'link': s['link']}
                break
        
        if not player_stream and streams:
            # Fallback ke link pertama (biasanya pixeldrain)
            # Pixeldrain biasanya butuh /u/ agar bisa embed, coba auto-convert kalau formatnya /api/file
            link = streams[0]['link']
            player_stream = {'type': 'iframe', 'link': link}

    return render_template_string(
        HTML_WATCH, 
        video=video_info,
        player_stream=player_stream, # Kirim stream terpilih ke HTML
        anime_title=title, 
        anime_url=anime_url, 
        current_url=chapter_url, 
        next_ep=next_ep, 
        prev_ep=prev_ep
    )

if __name__ == '__main__':
    app.run(debug=True)
