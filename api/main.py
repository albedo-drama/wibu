from flask import Flask, render_template_string, request, redirect, url_for
import requests
from jinja2 import DictLoader
import json

# ==========================================
# 1. TEMPLATE HTML (UI SEARCH FIXED)
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
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">

    <style>
        body { background-color: #050505; color: #fff; font-family: 'Poppins', sans-serif; }
        .nav-glass { background: rgba(0,0,0,0.9); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.1); }
        .card-anime { transition: transform 0.2s; }
        .card-anime:active { transform: scale(0.95); }
        /* Hide Scrollbar */
        ::-webkit-scrollbar { width: 0px; background: transparent; }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    
    <nav class="nav-glass sticky top-0 z-50 h-16 flex items-center justify-between px-4 md:px-8">
        <a href="/" class="flex items-center gap-2 group">
            <div class="w-8 h-8 bg-red-600 rounded flex items-center justify-center text-white font-black group-hover:rotate-6 transition">A</div>
            <span class="text-lg md:text-xl font-black tracking-tighter text-white">
                ALBEDO<span class="text-red-500">WIBU</span>-TV
            </span>
        </a>

        <div class="hidden md:flex gap-6 text-xs font-bold text-gray-400">
            <a href="/" class="hover:text-white transition">BERANDA</a>
            <a href="/movies" class="hover:text-white transition">MOVIES</a>
            <a href="/genres" class="hover:text-white transition">GENRE</a>
            <a href="/favorites" class="hover:text-white transition">KOLEKSIKU</a>
        </div>

        <form action="/search" method="GET" class="hidden md:block relative">
            <input type="text" name="q" placeholder="Cari Anime..." value="{{ search_query if search_query else '' }}"
                   class="bg-[#1a1a1a] border border-gray-700 rounded-full py-2 pl-4 pr-10 text-xs text-white focus:outline-none focus:border-red-500 w-64 transition-all">
            <button type="submit" class="absolute right-3 top-2 text-gray-400 hover:text-white">
                <i class="ri-search-line"></i>
            </button>
        </form>

        <a href="/search" class="md:hidden w-10 h-10 flex items-center justify-center bg-[#1a1a1a] rounded-full text-white border border-gray-700">
            <i class="ri-search-line"></i>
        </a>
    </nav>

    <div class="md:hidden fixed bottom-0 left-0 right-0 bg-black/95 border-t border-white/10 flex justify-around p-3 z-50 pb-5">
        <a href="/" class="text-center text-[10px] font-bold text-gray-500 hover:text-white">
            <i class="ri-home-5-line text-lg block"></i> HOME
        </a>
        <a href="/movies" class="text-center text-[10px] font-bold text-gray-500 hover:text-white">
            <i class="ri-film-line text-lg block"></i> MOVIE
        </a>
        <a href="/genres" class="text-center text-[10px] font-bold text-gray-500 hover:text-white">
            <i class="ri-apps-line text-lg block"></i> GENRE
        </a>
        <a href="/favorites" class="text-center text-[10px] font-bold text-gray-500 hover:text-white">
            <i class="ri-heart-3-line text-lg block"></i> SAVED
        </a>
    </div>

    <main class="container mx-auto px-4 py-6 flex-grow pb-24 md:pb-10">
        {% block content %}{% endblock %}
    </main>

</body>
</html>
"""

HTML_INDEX = """
{% extends "base.html" %}
{% block content %}

{% if is_search_page and not search_query %}
    <div class="flex flex-col items-center justify-center min-h-[50vh]">
        <h1 class="text-2xl font-black text-white mb-6">PENCARIAN</h1>
        <form action="/search" method="GET" class="w-full max-w-md relative">
            <input type="text" name="q" placeholder="Ketik judul anime..." autofocus
                   class="w-full bg-[#111] border border-gray-700 rounded-full py-4 pl-6 pr-14 text-white focus:outline-none focus:border-red-500 shadow-xl text-lg">
            <button type="submit" class="absolute right-3 top-2.5 bg-red-600 w-10 h-10 rounded-full flex items-center justify-center text-white hover:bg-red-500 transition">
                <i class="ri-search-line"></i>
            </button>
        </form>
        
        <div class="mt-8 text-center">
            <p class="text-xs text-gray-500 font-bold mb-3 uppercase">Populer</p>
            <div class="flex flex-wrap justify-center gap-2">
                <a href="/search?q=Naruto" class="px-3 py-1 bg-[#111] border border-gray-800 rounded-full text-xs text-gray-400 hover:text-white hover:border-red-500 transition">Naruto</a>
                <a href="/search?q=One Piece" class="px-3 py-1 bg-[#111] border border-gray-800 rounded-full text-xs text-gray-400 hover:text-white hover:border-red-500 transition">One Piece</a>
                <a href="/search?q=Isekai" class="px-3 py-1 bg-[#111] border border-gray-800 rounded-full text-xs text-gray-400 hover:text-white hover:border-red-500 transition">Isekai</a>
                <a href="/search?q=Romance" class="px-3 py-1 bg-[#111] border border-gray-800 rounded-full text-xs text-gray-400 hover:text-white hover:border-red-500 transition">Romance</a>
            </div>
        </div>
    </div>
{% else %}

    <div class="mb-6 border-l-4 border-red-600 pl-4">
        <h1 class="text-xl font-bold text-white uppercase">
            {% if search_query %}
                Hasil: <span class="text-red-500">"{{ search_query }}"</span>
            {% elif is_movie_page %}
                DAFTAR MOVIE
            {% else %}
                UPDATE TERBARU
            {% endif %}
        </h1>
        <p class="text-[10px] text-gray-500 font-mono mt-1">HALAMAN {{ current_page }}</p>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {% if not data_list %}
            <div class="col-span-full py-20 text-center bg-white/5 rounded-xl">
                <i class="ri-ghost-smile-line text-4xl text-gray-600 mb-2"></i>
                <p class="text-gray-400 text-xs font-bold">TIDAK ADA DATA DITEMUKAN</p>
                <p class="text-gray-600 text-[10px]">Mungkin API limit atau kata kunci salah.</p>
                {% if current_page > 1 %}
                <a href="javascript:history.back()" class="inline-block mt-4 px-4 py-2 bg-red-600 rounded text-xs font-bold">Kembali</a>
                {% endif %}
            </div>
        {% endif %}

        {% for anime in data_list %}
        <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="card-anime block bg-[#111] rounded overflow-hidden relative group border border-white/5 hover:border-red-500/50">
            <div class="aspect-[3/4] relative overflow-hidden">
                <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover group-hover:scale-110 transition duration-500 group-hover:opacity-70">
                <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
                
                {% if anime.score %}
                <div class="absolute top-1 right-1 bg-yellow-500 text-black text-[9px] font-black px-1.5 py-0.5 rounded shadow">★ {{ anime.score }}</div>
                {% endif %}
                
                <div class="absolute bottom-0 left-0 right-0 p-2">
                    {% if anime.lastch %}
                    <span class="bg-red-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded mb-1 inline-block">{{ anime.lastch }}</span>
                    {% endif %}
                </div>
            </div>
            
            <div class="p-2">
                <h3 class="text-xs font-bold text-gray-200 truncate group-hover:text-red-500 transition">{{ anime.judul }}</h3>
            </div>
        </a>
        {% endfor %}
    </div>

    {% if data_list|length > 0 %}
    <div class="flex justify-center items-center gap-3 mt-10 border-t border-white/10 pt-6">
        {% set base = '/search?q=' + (search_query if search_query else '') + '&page=' if search_query else ('/movies?page=' if is_movie_page else '/?page=') %}

        {% if current_page > 1 %}
        <a href="{{ base }}{{ current_page - 1 }}" class="px-5 py-2 bg-gray-800 hover:bg-gray-700 text-white text-xs font-bold rounded-full transition">← Prev</a>
        {% endif %}

        <span class="text-xs font-mono text-gray-500 bg-white/5 px-3 py-1 rounded">{{ current_page }}</span>

        {% if data_list|length >= 10 %}
        <a href="{{ base }}{{ current_page + 1 }}" class="px-5 py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-full transition shadow-lg shadow-red-900/50">Next →</a>
        {% endif %}
    </div>
    {% endif %}

{% endif %}
{% endblock %}
"""

HTML_GENRES = """
{% extends "base.html" %}
{% block content %}
<div class="max-w-5xl mx-auto text-center">
    <h1 class="text-2xl font-black text-white mb-8 tracking-tight">PILIH GENRE</h1>
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
        {% for genre in genres %}
        <a href="/search?q={{ genre }}" class="py-3 px-2 bg-[#111] border border-white/5 hover:border-red-500 hover:bg-red-900/20 rounded text-xs font-bold text-gray-400 hover:text-white transition">
            {{ genre }}
        </a>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

HTML_DETAIL = """
{% extends "base.html" %}
{% block content %}
{% if error %}
    <div class="text-center py-20 text-red-500 text-xs">{{ error }}</div>
{% else %}
    <div class="relative w-full h-[250px] overflow-hidden rounded-t-2xl md:rounded-2xl mb-[-80px] md:mb-[-100px] shadow-2xl opacity-50">
        <div class="absolute inset-0 bg-cover bg-center blur-sm" style="background-image: url('{{ anime.cover }}');"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-[#050505] to-transparent"></div>
    </div>

    <div class="relative z-10 px-2 md:px-8">
        <div class="flex flex-col md:flex-row gap-6 items-start">
            <img src="{{ anime.cover }}" class="w-32 md:w-56 rounded-lg border-4 border-[#050505] shadow-2xl mx-auto md:mx-0">
            
            <div class="flex-1 text-center md:text-left mt-2">
                <h1 class="text-xl md:text-3xl font-black text-white mb-2 leading-tight">{{ anime.judul }}</h1>
                
                <div class="flex flex-wrap justify-center md:justify-start gap-2 mb-4 text-[10px] font-bold uppercase text-gray-400">
                    <span class="bg-white/10 px-2 py-1 rounded">★ {{ anime.rating }}</span>
                    <span class="bg-white/10 px-2 py-1 rounded">{{ anime.status }}</span>
                    <span class="bg-white/10 px-2 py-1 rounded">{{ anime.custom_total_eps }}</span>
                </div>

                <div class="flex flex-wrap justify-center md:justify-start gap-1 mb-4">
                    {% for g in anime.genre %}
                    <a href="/search?q={{ g }}" class="text-[9px] px-2 py-1 bg-red-900/30 text-red-300 border border-red-900/50 rounded hover:bg-red-600 hover:text-white transition">{{ g }}</a>
                    {% endfor %}
                </div>

                <div class="bg-[#111] p-4 rounded-lg border border-white/5 text-xs text-gray-400 text-justify mb-4 max-h-32 overflow-y-auto">
                    {{ anime.sinopsis }}
                </div>

                <button onclick="toggleFav()" id="fav-btn" class="w-full md:w-auto px-6 py-2 bg-white text-black font-bold text-xs rounded hover:bg-gray-200 transition">
                    SIMPAN KE KOLEKSI
                </button>
            </div>
        </div>
    </div>

    <div class="mt-10 border-t border-white/10 pt-6">
        <div class="flex justify-between items-center mb-4">
            <h3 class="text-sm font-bold text-white">EPISODE</h3>
            <button onclick="reverseList()" class="text-[10px] bg-white/10 px-3 py-1 rounded text-gray-300">⇅ Balik</button>
        </div>
        
        <div id="chapter-list" class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2 max-h-[500px] overflow-y-auto pr-1">
            {% for chapter in anime.chapter %}
            <a href="/watch/{{ anime.series_id }}/{{ chapter.url }}" class="bg-[#111] hover:bg-red-900/50 border border-white/5 hover:border-red-500/50 p-2 rounded text-center transition group">
                <span class="block text-[9px] text-gray-500 mb-1">{{ chapter.date }}</span>
                <span class="text-xs font-bold text-white group-hover:text-red-400">Ep {{ chapter.ch }}</span>
            </a>
            {% endfor %}
        </div>
    </div>

    <script>
        const animeData = { url: location.pathname, cover: '{{ anime.cover }}', judul: '{{ anime.judul|replace("'", "") }}' };
        function updateFav() {
            const favs = JSON.parse(localStorage.getItem('favs')||'[]');
            const isFav = favs.some(f=>f.url===animeData.url);
            const btn = document.getElementById('fav-btn');
            if(isFav) { btn.innerText = "TERSIMPAN"; btn.classList.add('bg-red-600','text-white'); btn.classList.remove('bg-white','text-black'); }
            else { btn.innerText = "SIMPAN KE KOLEKSI"; btn.classList.remove('bg-red-600','text-white'); btn.classList.add('bg-white','text-black'); }
        }
        function toggleFav() {
            let favs = JSON.parse(localStorage.getItem('favs')||'[]');
            const idx = favs.findIndex(f=>f.url===animeData.url);
            if(idx===-1) favs.push(animeData); else favs.splice(idx,1);
            localStorage.setItem('favs', JSON.stringify(favs));
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
{% block content %}
<div class="max-w-4xl mx-auto">
    <a href="/anime/{{ anime_url }}" class="text-[10px] font-bold text-gray-500 hover:text-white mb-2 block">← KEMBALI</a>
    
    {% if video %}
        <div class="aspect-video bg-black rounded overflow-hidden mb-4 relative shadow-lg">
            {% if player_url %}
            <iframe src="{{ player_url }}" class="w-full h-full" frameborder="0" allowfullscreen></iframe>
            {% else %}
            <div class="absolute inset-0 flex items-center justify-center text-gray-500 text-xs flex-col">
                <i class="ri-error-warning-line text-2xl mb-1"></i>
                Stream Utama Error. Pilih Resolusi di Bawah.
            </div>
            {% endif %}
        </div>

        <div class="bg-[#111] p-4 rounded border border-white/5">
            <div class="flex justify-between items-center mb-4">
                <h1 class="text-xs font-bold text-white max-w-[200px] truncate">{{ anime_title }}</h1>
                <div class="flex gap-2">
                    {% if prev_ep %}<a href="/watch/{{ anime_url }}/{{ prev_ep.url }}" class="px-3 py-1 bg-gray-800 rounded text-[10px] font-bold text-white hover:bg-gray-700">PREV</a>{% endif %}
                    {% if next_ep %}<a href="/watch/{{ anime_url }}/{{ next_ep.url }}" class="px-3 py-1 bg-red-600 rounded text-[10px] font-bold text-white hover:bg-red-500">NEXT</a>{% endif %}
                </div>
            </div>

            <p class="text-[9px] font-bold text-gray-500 mb-2 uppercase">DOWNLOAD / SERVER ALTERNATIF</p>
            <div class="flex flex-wrap gap-2">
                {% for s in video.stream %}
                <a href="{{ s.link }}" target="_blank" class="px-3 py-2 bg-black border border-gray-800 hover:border-red-500 rounded text-[10px] text-gray-300 hover:text-white flex items-center gap-2 transition">
                    <i class="ri-download-cloud-line"></i> {{ s.reso }} <span class="opacity-50 text-[9px]">({{ s.provide }})</span>
                </a>
                {% endfor %}
            </div>
        </div>
    {% else %}
        <div class="text-center py-20 text-gray-500 text-xs">Video belum rilis.</div>
    {% endif %}
</div>
{% endblock %}
"""

HTML_FAVORITES = """
{% extends "base.html" %}
{% block content %}
<h2 class="text-lg font-bold mb-4 border-l-4 border-red-500 pl-3">Saved Anime</h2>
<div id="grid" class="grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 grid"></div>
<script>
    const favs = JSON.parse(localStorage.getItem('favs')||'[]');
    if(favs.length===0) document.getElementById('grid').innerHTML = '<div class="col-span-full text-center text-gray-500 py-10 text-xs">Kosong.</div>';
    favs.forEach(a => {
        document.getElementById('grid').insertAdjacentHTML('beforeend', `
        <a href="${a.url}" class="block bg-[#111] rounded overflow-hidden relative">
            <div class="aspect-[3/4]"><img src="${a.cover}" class="w-full h-full object-cover opacity-80 hover:opacity-100 transition"></div>
            <div class="p-2"><h3 class="text-[10px] font-bold text-gray-300 truncate">${a.judul}</h3></div>
            <button onclick="rem(event, '${a.url}')" class="absolute top-1 right-1 bg-red-600 text-white w-5 h-5 rounded flex items-center justify-center text-[10px]">x</button>
        </a>`);
    });
    function rem(e, u) { e.preventDefault(); if(!confirm('Hapus?'))return; localStorage.setItem('favs', JSON.stringify(favs.filter(f=>f.url!==u))); location.reload(); }
</script>
{% endblock %}
"""

# ==========================================
# 2. LOGIC BACKEND
# ==========================================

app = Flask(__name__)
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE,
    'index.html': HTML_INDEX,
    'genres.html': HTML_GENRES,
    'favorites.html': HTML_FAVORITES,
    'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH
})

GENRES = sorted(["Action", "Adventure", "Comedy", "Demons", "Drama", "Ecchi", "Fantasy", "Game", "Harem", "Historical", "Horror", "Josei", "Magic", "Martial Arts", "Mecha", "Military", "Music", "Mystery", "Parody", "Police", "Psychological", "Romance", "Samurai", "School", "Sci-Fi", "Seinen", "Shoujo", "Shounen", "Slice of Life", "Space", "Sports", "Super Power", "Supernatural", "Thriller", "Vampire", "Isekai"])

API_BASE = "https://api.sansekai.my.id/api/anime"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def smart_fetch(endpoint, params=None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, params=params, timeout=12)
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
    data = smart_fetch('/latest') if page == 1 else smart_fetch('/recommended', params={'page': page})
    return render_template_string(HTML_INDEX, data_list=data, current_page=page, is_movie_page=False, search_query=None, is_search_page=False)

@app.route('/movies')
def movies():
    page = request.args.get('page', 1, type=int)
    data = smart_fetch('/movie', params={'page': page})
    return render_template_string(HTML_INDEX, data_list=data, current_page=page, is_movie_page=True, search_query=None, is_search_page=False)

@app.route('/genres')
def genres():
    return render_template_string(HTML_GENRES, genres=GENRES)

@app.route('/favorites')
def favorites():
    return render_template_string(HTML_FAVORITES)

@app.route('/search')
def search():
    q = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    
    # JIKA Q KOSONG => TAMPILKAN PAGE SEARCH KHUSUS (HTML_INDEX akan handle ini)
    if not q:
        return render_template_string(HTML_INDEX, is_search_page=True, search_query=None, data_list=[])
    
    data = smart_fetch('/search', params={'query': q, 'page': page})
    return render_template_string(HTML_INDEX, data_list=data, search_query=q, current_page=page, is_movie_page=False, is_search_page=True)

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
    vid_data = smart_fetch('/getvideo', params={'chapterUrlId': chapter_url})
    anime_data = smart_fetch('/detail', params={'urlId': anime_url})
    title = anime_data[0].get('judul') if anime_data else ""
    chapters = anime_data[0].get('chapter', []) if anime_data else []
    next_ep, prev_ep = get_nav(chapters, chapter_url)
    video_info = vid_data[0] if vid_data else None
    player_url = None
    if video_info and 'stream' in video_info:
        for s in video_info['stream']:
            if '.mp4' in s['link'] or 'animekita' in s['link']: player_url = s['link']; break
        if not player_url and video_info['stream']: player_url = video_info['stream'][0]['link']
    return render_template_string(HTML_WATCH, video=video_info, player_url=player_url, anime_title=title, anime_url=anime_url, next_ep=next_ep, prev_ep=prev_ep)

if __name__ == '__main__':
    app.run(debug=True)
