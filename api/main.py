from flask import Flask, render_template_string, request, redirect, url_for
import requests
from jinja2 import DictLoader

# ==========================================
# 1. TEMPLATES HTML & DATA
# ==========================================

GENRE_LIST = sorted([
    "Action", "Adventure", "Comedy", "Demons", "Drama", "Ecchi", "Fantasy", 
    "Game", "Harem", "Historical", "Horror", "Josei", "Magic", "Martial Arts", 
    "Mecha", "Military", "Music", "Mystery", "Parody", "Police", "Psychological", 
    "Romance", "Samurai", "School", "Sci-Fi", "Seinen", "Shoujo", "Shoujo Ai", 
    "Shounen", "Shounen Ai", "Slice of Life", "Space", "Sports", "Super Power", 
    "Supernatural", "Thriller", "Vampire", "Yuri", "Isekai"
])

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

    <style>
        body { background-color: #0f0f1a; color: #e2e8f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        #nprogress .bar { background: #d946ef !important; height: 3px !important; } 
        #nprogress .peg { box-shadow: 0 0 10px #d946ef, 0 0 5px #d946ef !important; }
        .card-hover:hover { transform: translateY(-5px); }
        .glass-nav { background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(255,255,255,0.05); }
        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #1e293b; }
        ::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 10px; }
    </style>
</head>
<body class="min-h-screen flex flex-col selection:bg-fuchsia-600 selection:text-white">
    
    <nav class="glass-nav p-4 sticky top-0 z-50">
        <div class="container mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <div class="flex items-center gap-8 w-full md:w-auto justify-between">
                <a href="/" class="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-fuchsia-500 tracking-tighter">
                    ALBEDO<span class="text-white">TV</span>
                </a>
                <div class="flex gap-6 text-sm font-bold tracking-wide">
                    <a href="/" class="text-gray-400 hover:text-white transition hover:scale-105">HOME</a>
                    <a href="/movies" class="text-gray-400 hover:text-white transition hover:scale-105">MOVIES</a>
                    <a href="/genres" class="text-gray-400 hover:text-white transition hover:scale-105">GENRE</a>
                </div>
            </div>
            <form action="/search" method="GET" class="w-full md:w-1/3 flex relative group">
                <input type="text" name="q" placeholder="Cari anime..." value="{{ search_query if search_query else '' }}"
                       class="w-full py-2.5 px-5 bg-slate-800/80 border border-slate-700 rounded-full focus:outline-none focus:border-violet-500 text-sm transition-all group-hover:bg-slate-800">
                <button type="submit" class="absolute right-1 top-1 bottom-1 bg-violet-600 px-4 rounded-full hover:bg-violet-700 text-white transition">🔍</button>
            </form>
        </div>
    </nav>

    <main class="container mx-auto p-4 md:p-6 flex-grow">
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-slate-950 text-center p-8 mt-12 border-t border-slate-900 text-slate-600 text-sm">
        <p>&copy; 2026 ALBEDOWIBU-TV. Serverless Python App.</p>
    </footer>

    <script>
        window.addEventListener('beforeunload', () => NProgress.start());
        document.addEventListener("DOMContentLoaded", () => {
            NProgress.done();
            // History Marker
            const history = JSON.parse(localStorage.getItem('watched_episodes') || '[]');
            history.forEach(url => {
                const links = document.querySelectorAll(`a[href*="${url}"]`);
                links.forEach(link => {
                    link.classList.add('opacity-60', 'grayscale');
                    if(link.querySelector('.ep-badge')) link.querySelector('.ep-badge').innerText = '✔';
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
        <a href="/" class="text-gray-500 hover:text-white transition">🏠</a> <span class="text-gray-600">/</span>
        <h2 class="text-2xl font-bold text-white">Hasil: "<span class="text-violet-400">{{ search_query }}</span>"</h2>
    </div>
{% elif is_movie_page %}
    <div class="mb-8 border-l-4 border-pink-500 pl-4 bg-gradient-to-r from-pink-500/10 to-transparent p-2 rounded-r-xl">
        <h2 class="text-2xl font-bold text-white">🎬 Anime Movies <span class="text-slate-500 text-sm ml-2">Page {{ current_page }}</span></h2>
    </div>
{% else %}
    <div class="mb-8 border-l-4 border-violet-500 pl-4 bg-gradient-to-r from-violet-500/10 to-transparent p-2 rounded-r-xl">
        <h2 class="text-2xl font-bold text-white">
            {% if current_page == 1 %}🔥 Anime Terbaru{% else %}⭐ Rekomendasi{% endif %}
            <span class="text-slate-500 text-sm ml-2">Page {{ current_page }}</span>
        </h2>
    </div>
{% endif %}

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-5 mb-10">
    {% if not data_list and search_query %}
        <div class="col-span-full text-center py-20 text-gray-500 bg-slate-800/50 rounded-2xl">Tidak ada hasil ditemukan.</div>
    {% endif %}

    {% for anime in data_list %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="card-hover bg-slate-800 rounded-xl overflow-hidden shadow-xl block relative group border border-slate-700/50 transition-all duration-300">
        <div class="relative aspect-[3/4] overflow-hidden">
            <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover transition duration-500 group-hover:scale-110">
            <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent opacity-90"></div>
            
            <div class="absolute top-2 right-2 flex flex-col gap-1 items-end">
                {% if anime.score %}
                <span class="bg-yellow-500 text-black text-[10px] font-black px-2 py-0.5 rounded shadow-lg">★ {{ anime.score }}</span>
                {% endif %}
                {% if anime.lastup == 'Baru di Upload' %}
                <span class="bg-red-600 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-lg animate-pulse">NEW</span>
                {% endif %}
            </div>

            <div class="absolute bottom-0 left-0 right-0 p-4">
                {% if anime.lastch %}<p class="text-xs text-fuchsia-400 font-bold mb-1">{{ anime.lastch }}</p>{% endif %}
                <h3 class="text-sm font-bold text-white truncate leading-tight group-hover:text-violet-400 transition">{{ anime.judul }}</h3>
            </div>
        </div>
    </a>
    {% endfor %}
</div>

{% if not search_query %}
<div class="flex justify-center items-center gap-4 mt-12 pb-8 border-t border-slate-800 pt-8">
    {% if current_page > 1 %}
    <a href="?page={{ current_page - 1 }}" class="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-full border border-slate-700 transition">← Back</a>
    {% endif %}
    <span class="text-slate-500 font-mono text-sm border border-slate-800 px-4 py-1 rounded-full">Page {{ current_page }}</span>
    <a href="?page={{ current_page + 1 }}" class="px-6 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-full transition shadow-lg shadow-violet-900/30">Next →</a>
</div>
{% endif %}
{% endblock %}
"""

HTML_GENRES = """
{% extends "base.html" %}
{% block title %}Genre - ALBEDOWIBU-TV{% endblock %}
{% block content %}
<div class="max-w-6xl mx-auto">
    <h2 class="text-3xl font-black text-white mb-8 text-center tracking-tight">📂 Pilih Genre Anime</h2>
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {% for genre in genres %}
        <a href="/search?q={{ genre }}" class="group bg-slate-800 hover:bg-violet-600 border border-slate-700 hover:border-violet-500 p-4 rounded-xl transition-all duration-300 flex items-center justify-center text-center shadow-lg">
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
    <div class="text-center py-20 text-red-500">{{ error }}</div>
{% else %}
    <div class="bg-slate-800/50 backdrop-blur-md rounded-3xl p-6 md:p-8 shadow-2xl border border-white/5 mb-10 flex flex-col md:flex-row gap-8 relative overflow-hidden">
        <div class="absolute inset-0 bg-cover bg-center opacity-10 blur-3xl" style="background-image: url('{{ anime.cover }}');"></div>
        
        <div class="w-full md:w-[280px] shrink-0 relative z-10 mx-auto md:mx-0">
            <img src="{{ anime.cover }}" class="w-full rounded-2xl shadow-[0_0_30px_rgba(0,0,0,0.5)] border-4 border-slate-700/50">
        </div>
        
        <div class="w-full relative z-10">
            <h1 class="text-2xl md:text-4xl font-black text-white mb-4 leading-tight">{{ anime.judul }}</h1>
            
            <div class="flex flex-wrap gap-2 mb-6">
                <span class="bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 px-3 py-1 rounded-lg text-xs font-bold">★ {{ anime.rating }}</span>
                <span class="bg-blue-500/20 text-blue-400 border border-blue-500/30 px-3 py-1 rounded-lg text-xs font-bold">{{ anime.status }}</span>
                <span class="bg-green-500/20 text-green-400 border border-green-500/30 px-3 py-1 rounded-lg text-xs font-bold">{{ anime.custom_total_eps }}</span>
            </div>

            <div class="flex flex-wrap gap-2 mb-6">
                {% for g in anime.genre %}
                <a href="/search?q={{ g }}" class="text-xs bg-slate-900 hover:bg-violet-600 text-gray-400 hover:text-white px-3 py-1.5 rounded-md border border-slate-700 transition">{{ g }}</a>
                {% endfor %}
            </div>

            <div class="bg-slate-950/50 p-5 rounded-2xl border border-white/5 mb-6 max-h-48 overflow-y-auto custom-scroll">
                <p class="text-gray-300 text-sm leading-7">{{ anime.sinopsis }}</p>
            </div>
            
            <div class="flex gap-6 text-xs text-gray-500 font-mono">
                <span>STUDIO: {{ anime.author }}</span>
                <span>RILIS: {{ anime.published }}</span>
            </div>
        </div>
    </div>

    <div class="flex justify-between items-end mb-6 border-b border-slate-800 pb-4">
        <h3 class="text-2xl font-bold text-white tracking-tight">📺 Episode List</h3>
        <button onclick="reverseList()" class="text-xs bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-full border border-slate-700 transition">⇅ Oldest - Newest</button>
    </div>
    
    <div id="chapter-list" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 pb-12">
        {% for chapter in anime.chapter %}
        <a href="/watch/{{ anime.series_id if anime.series_id else 'unknown' }}/{{ chapter.url }}" 
           class="bg-slate-800 hover:bg-violet-600 border border-slate-700 hover:border-violet-500 p-4 rounded-xl text-center group transition duration-300 relative overflow-hidden">
            <span class="ep-badge absolute top-1 right-2 text-[8px] text-slate-500 group-hover:text-white/50">●</span>
            <span class="block text-[10px] text-gray-500 group-hover:text-violet-200 mb-1">{{ chapter.date }}</span>
            <span class="text-sm font-bold text-white">Chapter {{ chapter.ch }}</span>
        </a>
        {% endfor %}
    </div>

    <script>
        function reverseList() {
            const list = document.getElementById('chapter-list');
            Array.from(list.children).reverse().forEach(item => list.appendChild(item));
        }
    </script>
{% endif %}
{% endblock %}
"""

HTML_WATCH = """
{% extends "base.html" %}
{% block title %}Nonton {{ anime_title }}{% endblock %}
{% block content %}

<div class="max-w-5xl mx-auto">
    <div class="mb-4 text-sm text-gray-400 flex items-center gap-2">
        <a href="/anime/{{ anime_url }}" class="text-violet-400 hover:text-white font-bold transition">← {{ anime_title }}</a>
        <span class="opacity-30">/</span>
        <span class="text-white">Player</span>
    </div>

    {% if video %}
        <div class="bg-black rounded-2xl overflow-hidden shadow-2xl border border-slate-800 mb-6 aspect-video relative group">
            {% if video.stream and video.stream|length > 0 %}
            <iframe src="{{ video.stream[0].link }}" class="absolute inset-0 w-full h-full z-10" allowfullscreen scrolling="no" frameborder="0"></iframe>
            {% else %}
            <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-6">
                <p class="text-red-500 font-bold mb-2 text-2xl">⚠️</p>
                <p class="text-gray-400">Stream Embed tidak tersedia.</p>
                <p class="text-gray-500 text-sm mt-2">Silakan pilih server di bawah.</p>
            </div>
            {% endif %}
        </div>

        <div class="bg-slate-800 p-5 rounded-2xl border border-slate-700 shadow-xl">
            
            <div class="flex justify-between items-center mb-6 pb-6 border-b border-slate-700/50">
                <div class="flex gap-3 w-full md:w-auto">
                    {% if prev_ep %}
                    <a href="/watch/{{ anime_url }}/{{ prev_ep.url }}" class="flex-1 px-5 py-2.5 bg-slate-700 hover:bg-slate-600 text-white rounded-xl font-bold transition text-center text-sm">❮ Prev</a>
                    {% else %}
                    <button disabled class="flex-1 px-5 py-2.5 bg-slate-900 text-slate-600 rounded-xl font-bold text-center text-sm cursor-not-allowed">❮ Prev</button>
                    {% endif %}

                    {% if next_ep %}
                    <a href="/watch/{{ anime_url }}/{{ next_ep.url }}" class="flex-1 px-5 py-2.5 bg-violet-600 hover:bg-violet-700 text-white rounded-xl font-bold transition text-center text-sm shadow-lg shadow-violet-900/30">Next ❯</a>
                    {% else %}
                    <button disabled class="flex-1 px-5 py-2.5 bg-slate-900 text-slate-600 rounded-xl font-bold text-center text-sm cursor-not-allowed">Next ❯</button>
                    {% endif %}
                </div>
            </div>

            <div>
                <p class="text-xs text-gray-400 font-bold uppercase tracking-widest mb-3">PILIH RESOLUSI & SERVER</p>
                <div class="flex flex-wrap gap-3">
                    {% for s in video.stream %}
                        {# LOGIKA WARNA TOMBOL BERDASARKAN RESOLUSI #}
                        {% set btn_color = 'bg-slate-700 hover:bg-slate-600 border-slate-600' %}
                        {% if '1080' in s.reso %}
                            {% set btn_color = 'bg-red-600 hover:bg-red-500 border-red-500 shadow-red-900/20' %}
                        {% elif '720' in s.reso %}
                            {% set btn_color = 'bg-fuchsia-600 hover:bg-fuchsia-500 border-fuchsia-500 shadow-fuchsia-900/20' %}
                        {% elif '480' in s.reso %}
                            {% set btn_color = 'bg-emerald-600 hover:bg-emerald-500 border-emerald-500 shadow-emerald-900/20' %}
                        {% elif '360' in s.reso %}
                            {% set btn_color = 'bg-blue-600 hover:bg-blue-500 border-blue-500 shadow-blue-900/20' %}
                        {% endif %}

                        <a href="{{ s.link }}" target="_blank" 
                           class="{{ btn_color }} border px-4 py-2 rounded-lg text-white transition shadow-md flex items-center gap-2 group">
                            <span class="font-black text-sm">{{ s.reso }}</span>
                            <span class="text-[10px] opacity-70 border-l border-white/20 pl-2 uppercase font-mono">{{ s.provide }}</span>
                            <span class="text-xs opacity-0 group-hover:opacity-100 transition-opacity">↗</span>
                        </a>
                    {% endfor %}
                </div>
                <p class="text-[10px] text-gray-500 mt-3 italic">*Klik tombol resolusi di atas jika player utama tidak jalan. Warna merah/ungu = HD.</p>
            </div>
        </div>
    {% else %}
        <div class="text-center py-24 bg-slate-800 rounded-2xl border border-slate-700">
            <h2 class="text-2xl font-bold text-white mb-2">Video Tidak Tersedia</h2>
            <p class="text-gray-500">Mungkin belum rilis atau API sedang down.</p>
        </div>
    {% endif %}
</div>

<script>
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
# 2. LOGIC BACKEND
# ==========================================

app = Flask(__name__)
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE,
    'index.html': HTML_INDEX,
    'genres.html': HTML_GENRES,
    'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH
})

API_BASE = "https://api.sansekai.my.id/api/anime"
HEADERS = {'User-Agent': 'ALBEDOTV/5.0', 'Accept': 'application/json'}

def fetch_api(endpoint, params=None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, params=params, timeout=15)
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
    # Assuming DESC order (Newest -> Oldest)
    next_ep = chapters[idx - 1] if idx > 0 else None
    prev_ep = chapters[idx + 1] if idx < len(chapters) - 1 else None
    return next_ep, prev_ep

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    # Trik: Home page 1 pake /latest, Page > 1 pake /recommended biar infinite scroll feel-nya dapet
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
    if not data: return render_template_string(HTML_DETAIL, error="Gagal load data anime.")
    anime = data[0]
    # Metadata Processing
    eps = anime.get('chapter', [])
    anime['custom_total_eps'] = f"{len(eps)} Episodes" if eps else "?"
    if not anime.get('series_id'): anime['series_id'] = url_id
    return render_template_string(HTML_DETAIL, anime=anime)

@app.route('/watch/<path:anime_url>/<path:chapter_url>')
def watch(anime_url, chapter_url):
    vid = fetch_api('/getvideo', params={'chapterUrlId': chapter_url})
    anime_data = fetch_api('/detail', params={'urlId': anime_url})
    
    title = "Anime"
    next_ep, prev_ep = None, None
    if anime_data:
        title = anime_data[0].get('judul')
        next_ep, prev_ep = get_nav(anime_data[0].get('chapter', []), chapter_url)
        
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
