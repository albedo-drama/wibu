from flask import Flask, render_template_string, request, redirect, url_for
import requests
from jinja2 import DictLoader
import json

# ==========================================
# 1. KONFIGURASI APP
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
<html lang="id" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ALBEDOWIBU-TV{% endblock %}</title>
    <meta name="theme-color" content="#0a0a0a">
    
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.css" />

    <style>
        body { background-color: #050505; color: #e5e5e5; font-family: 'Outfit', sans-serif; }
        
        /* Custom NProgress */
        #nprogress .bar { background: #6366f1 !important; height: 3px; }
        #nprogress .peg { box-shadow: 0 0 10px #6366f1, 0 0 5px #6366f1; }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #0a0a0a; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #6366f1; }

        /* Utilities */
        .glass { background: rgba(20, 20, 20, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.05); }
        .text-shadow { text-shadow: 0 2px 10px rgba(0,0,0,0.8); }
        .line-clamp-3 { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
        .poster-shadow { box-shadow: 0 0 20px rgba(0,0,0,0.5); }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    
    <nav class="sticky top-0 z-50 bg-black/90 border-b border-white/5 backdrop-blur-md">
        <div class="container mx-auto px-4 h-16 flex items-center justify-between">
            <a href="/" class="text-xl font-black tracking-tighter text-white flex items-center gap-1">
                ALBEDO<span class="text-indigo-500">WIBU</span>
            </a>

            <div class="hidden md:flex gap-6 text-sm font-bold text-gray-400">
                <a href="/" class="hover:text-white transition">HOME</a>
                <a href="/movies" class="hover:text-white transition">MOVIES</a>
                <a href="/genres" class="hover:text-white transition">GENRE</a>
                <a href="/favorites" class="hover:text-white transition">KOLEKSIKU</a>
            </div>

            <form action="/search" method="GET" class="relative group">
                <input type="text" name="q" placeholder="Cari anime..." value="{{ search_query if search_query else '' }}"
                       class="bg-white/5 border border-white/10 rounded-full py-1.5 pl-4 pr-10 text-sm text-white focus:outline-none focus:border-indigo-500 w-32 md:w-56 transition-all focus:w-40 md:focus:w-64">
                <button type="submit" class="absolute right-3 top-1.5 text-gray-500 group-focus-within:text-white">
                    <i class="ri-search-line"></i>
                </button>
            </form>
        </div>
        
        <div class="md:hidden fixed bottom-0 left-0 right-0 bg-black/95 border-t border-white/10 flex justify-around p-3 z-50 backdrop-blur-lg">
            <a href="/" class="flex flex-col items-center text-[10px] font-bold text-gray-400 hover:text-white">
                <i class="ri-home-5-line text-lg mb-0.5"></i> HOME
            </a>
            <a href="/movies" class="flex flex-col items-center text-[10px] font-bold text-gray-400 hover:text-white">
                <i class="ri-film-line text-lg mb-0.5"></i> MOVIES
            </a>
            <a href="/genres" class="flex flex-col items-center text-[10px] font-bold text-gray-400 hover:text-white">
                <i class="ri-layout-grid-line text-lg mb-0.5"></i> GENRE
            </a>
            <a href="/favorites" class="flex flex-col items-center text-[10px] font-bold text-gray-400 hover:text-white">
                <i class="ri-heart-3-line text-lg mb-0.5"></i> SAVED
            </a>
        </div>
    </nav>

    <main class="container mx-auto px-4 py-6 flex-grow pb-24 md:pb-10">
        {% block content %}{% endblock %}
    </main>

    <footer class="hidden md:block border-t border-white/5 bg-black text-center p-8 mt-10 text-gray-600 text-sm">
        <p>&copy; 2026 ALBEDOWIBU-TV. All Rights Reserved.</p>
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
                    link.classList.add('opacity-50', 'grayscale');
                    if(link.querySelector('.ep-title')) link.querySelector('.ep-title').classList.add('text-indigo-400');
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

<div class="flex items-end justify-between mb-6">
    <h2 class="text-xl font-bold text-white flex items-center gap-2">
        {% if search_query %}
            <span class="text-indigo-500">🔍</span> Hasil: "{{ search_query }}"
        {% elif is_movie_page %}
            <span class="text-pink-500">🎬</span> Anime Movies
        {% else %}
            <span class="text-indigo-500">🔥</span> Update Terbaru
        {% endif %}
    </h2>
    <span class="text-xs font-mono text-gray-500 bg-white/5 px-2 py-1 rounded">Page {{ current_page }}</span>
</div>

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 md:gap-5">
    {% if not data_list %}
        <div class="col-span-full py-20 text-center bg-white/5 rounded-xl">
            <i class="ri-emotion-unhappy-line text-4xl text-gray-600 mb-2"></i>
            <p class="text-gray-400 text-sm">Tidak ada anime ditemukan.</p>
            {% if current_page > 1 %}
            <a href="javascript:history.back()" class="text-indigo-400 text-xs mt-2 hover:underline">Kembali</a>
            {% endif %}
        </div>
    {% endif %}

    {% for anime in data_list %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="group relative block bg-[#111] rounded-lg overflow-hidden transition-all hover:-translate-y-1 hover:shadow-lg hover:shadow-indigo-500/20">
        <div class="aspect-[3/4] overflow-hidden relative">
            <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover transition duration-500 group-hover:scale-110 group-hover:opacity-80">
            
            <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-transparent"></div>
            
            <div class="absolute top-2 right-2 flex flex-col items-end gap-1">
                {% if anime.score %}
                <span class="bg-yellow-500 text-black text-[9px] font-black px-1.5 py-0.5 rounded shadow">★ {{ anime.score }}</span>
                {% endif %}
                {% if anime.status %}
                <span class="bg-blue-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded shadow">{{ anime.status }}</span>
                {% endif %}
            </div>

            <div class="absolute bottom-0 left-0 right-0 p-3">
                {% if anime.lastch %}
                <p class="text-[9px] text-indigo-300 font-bold uppercase tracking-wider mb-1">{{ anime.lastch }}</p>
                {% endif %}
                <h3 class="text-xs md:text-sm font-bold text-white truncate group-hover:text-indigo-400 transition">{{ anime.judul }}</h3>
            </div>
        </div>
    </a>
    {% endfor %}
</div>

{% if data_list|length > 0 %}
<div class="flex justify-center items-center gap-4 mt-10 pt-6 border-t border-white/5">
    {% set base_link = '/search?q=' + (search_query if search_query else '') + '&page=' if search_query else ('/movies?page=' if is_movie_page else '/?page=') %}
    
    {% if current_page > 1 %}
    <a href="{{ base_link }}{{ current_page - 1 }}" class="px-5 py-2 bg-white/5 hover:bg-white/10 rounded-full text-xs font-bold text-white transition flex items-center gap-1">
        <i class="ri-arrow-left-s-line"></i> Prev
    </a>
    {% else %}
    <button disabled class="px-5 py-2 bg-white/5 text-gray-600 rounded-full text-xs font-bold cursor-not-allowed">Prev</button>
    {% endif %}

    <a href="{{ base_link }}{{ current_page + 1 }}" class="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-full text-xs font-bold text-white transition flex items-center gap-1 shadow-lg shadow-indigo-500/20">
        Next <i class="ri-arrow-right-s-line"></i>
    </a>
</div>
{% endif %}

{% endblock %}
"""

HTML_GENRES = """
{% extends "base.html" %}
{% block content %}
<div class="max-w-5xl mx-auto">
    <h2 class="text-xl font-bold text-white mb-6 text-center">Pilih Genre</h2>
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
        {% for genre in genres %}
        <a href="/search?q={{ genre }}" class="bg-[#111] hover:bg-indigo-900/40 border border-white/5 hover:border-indigo-500/50 py-3 rounded-lg text-center transition group">
            <span class="text-xs font-bold text-gray-400 group-hover:text-white">{{ genre }}</span>
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
    <div class="relative rounded-2xl overflow-hidden bg-[#111] border border-white/5 mb-8 shadow-2xl">
        <div class="absolute inset-0 bg-cover bg-center opacity-20 blur-xl" style="background-image: url('{{ anime.cover }}');"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-[#0a0a0a]/80 to-transparent"></div>
        
        <div class="relative z-10 p-6 md:p-8 flex flex-col md:flex-row gap-6 md:gap-8 items-start">
            <div class="w-32 md:w-56 shrink-0 mx-auto md:mx-0 shadow-2xl poster-shadow rounded-lg overflow-hidden border border-white/10">
                <img src="{{ anime.cover }}" class="w-full h-auto object-cover">
            </div>
            
            <div class="flex-1 text-center md:text-left w-full">
                <h1 class="text-2xl md:text-4xl font-black text-white mb-2 leading-tight text-shadow">{{ anime.judul }}</h1>
                
                <div class="flex flex-wrap justify-center md:justify-start gap-2 mb-4 text-[10px] font-bold uppercase tracking-wider text-gray-300">
                    <span class="bg-white/10 px-2 py-1 rounded">★ {{ anime.rating }}</span>
                    <span class="bg-white/10 px-2 py-1 rounded">{{ anime.status }}</span>
                    <span class="bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-1 rounded">{{ anime.custom_total_eps }}</span>
                </div>

                <div class="flex flex-wrap justify-center md:justify-start gap-2 mb-6">
                    {% for g in anime.genre %}
                    <a href="/search?q={{ g }}" class="text-[10px] px-2 py-1 rounded border border-white/10 hover:bg-white/10 hover:text-white text-gray-400 transition">{{ g }}</a>
                    {% endfor %}
                </div>

                <p class="text-xs text-gray-300 leading-relaxed bg-black/40 p-4 rounded-lg border border-white/5 backdrop-blur-sm mb-6 line-clamp-3 md:line-clamp-none hover:line-clamp-none transition-all cursor-pointer">
                    {{ anime.sinopsis }}
                </p>

                <button onclick="toggleFav()" id="fav-btn" class="w-full md:w-auto px-6 py-2.5 bg-white text-black hover:bg-gray-200 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2">
                    <i id="fav-icon" class="ri-heart-line text-lg"></i> <span id="fav-text">SIMPAN KE KOLEKSI</span>
                </button>
            </div>
        </div>
    </div>

    <div class="border-t border-white/10 pt-6">
        <div class="flex justify-between items-center mb-4">
            <h3 class="text-sm font-bold text-white flex items-center gap-2"><i class="ri-list-check"></i> EPISODE</h3>
            <button onclick="reverseList()" class="text-[10px] bg-white/5 hover:bg-white/10 px-3 py-1 rounded text-gray-400 hover:text-white transition">⇅ BALIK URUTAN</button>
        </div>
        
        <div id="chapter-list" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 max-h-[500px] overflow-y-auto pr-1">
            {% for chapter in anime.chapter %}
            <a href="/watch/{{ anime.series_id }}/{{ chapter.url }}" class="bg-[#111] hover:bg-indigo-900/30 border border-white/5 hover:border-indigo-500/50 p-3 rounded-lg text-center transition group">
                <span class="text-[9px] text-gray-500 block mb-1">{{ chapter.date }}</span>
                <span class="ep-title text-xs font-bold text-white group-hover:text-indigo-400">Chapter {{ chapter.ch }}</span>
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
            const icon = document.getElementById('fav-icon');
            const txt = document.getElementById('fav-text');
            
            if(isFav) {
                btn.className = "w-full md:w-auto px-6 py-2.5 bg-red-600 hover:bg-red-500 text-white rounded-lg text-xs font-bold transition flex items-center justify-center gap-2";
                icon.className = "ri-heart-fill text-lg";
                txt.innerText = "TERSIMPAN";
            } else {
                btn.className = "w-full md:w-auto px-6 py-2.5 bg-white text-black hover:bg-gray-200 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2";
                icon.className = "ri-heart-line text-lg";
                txt.innerText = "SIMPAN KE KOLEKSI";
            }
        }

        function toggleFav() {
            let favs = JSON.parse(localStorage.getItem('albedo_favs')||'[]');
            const idx = favs.findIndex(f=>f.url===animeData.url);
            if(idx===-1) favs.push(animeData); else favs.splice(idx,1);
            localStorage.setItem('albedo_favs', JSON.stringify(favs));
            updateFav();
        }
        
        function reverseList() {
            const list = document.getElementById('chapter-list');
            Array.from(list.children).reverse().forEach(item => list.appendChild(item));
        }
        
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
    <div class="mb-4">
        <a href="/anime/{{ anime_url }}" class="text-[10px] font-bold text-gray-500 hover:text-white flex items-center gap-1 transition w-fit">
            <i class="ri-arrow-left-s-line text-lg"></i> KEMBALI KE LIST
        </a>
    </div>

    {% if video %}
        <div class="bg-black rounded-xl overflow-hidden shadow-2xl border border-white/10 aspect-video relative z-10 mb-4">
            {% if player_stream %}
                {% if player_stream.type == 'mp4' %}
                    <video controls autoplay class="w-full h-full" poster="https://via.placeholder.com/1280x720/000000/FFFFFF?text=ALBEDO-TV">
                        <source src="{{ player_stream.link }}" type="video/mp4">
                        Browser Anda tidak mendukung.
                    </video>
                {% else %}
                    <iframe src="{{ player_stream.link }}" class="w-full h-full" frameborder="0" allowfullscreen></iframe>
                {% endif %}
            {% else %}
                <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-6 bg-[#050505]">
                    <i class="ri-file-warning-line text-3xl text-red-500 mb-2"></i>
                    <p class="text-gray-400 text-xs font-bold">AUTO-PLAY GAGAL</p>
                    <p class="text-gray-600 text-[10px] mt-1">Silakan pilih server manual di bawah.</p>
                </div>
            {% endif %}
        </div>

        <div class="bg-[#111] border border-white/5 rounded-xl p-4 md:p-6">
            <div class="flex flex-col md:flex-row justify-between items-center gap-4 mb-6 border-b border-white/5 pb-4">
                <div class="text-center md:text-left">
                    <h1 class="text-sm font-bold text-white">Sedang Menonton</h1>
                    <p class="text-xs text-indigo-400 truncate max-w-[200px]">{{ anime_title }}</p>
                </div>
                
                <div class="flex gap-2">
                    {% if prev_ep %}
                    <a href="/watch/{{ anime_url }}/{{ prev_ep.url }}" class="px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-xs font-bold text-white border border-white/5 transition">Prev</a>
                    {% else %}
                    <button disabled class="px-4 py-2 bg-black/20 text-gray-700 rounded-lg text-xs font-bold cursor-not-allowed">Prev</button>
                    {% endif %}
                    
                    {% if next_ep %}
                    <a href="/watch/{{ anime_url }}/{{ next_ep.url }}" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-xs font-bold text-white shadow-lg shadow-indigo-500/20 transition">Next</a>
                    {% else %}
                    <button disabled class="px-4 py-2 bg-black/20 text-gray-700 rounded-lg text-xs font-bold cursor-not-allowed">Next</button>
                    {% endif %}
                </div>
            </div>

            <div>
                <p class="text-[10px] font-bold text-gray-500 mb-3 uppercase tracking-wider">PILIH RESOLUSI & SERVER</p>
                <div class="flex flex-wrap gap-2">
                    {% for s in video.stream %}
                        {# COLOR CODING LOGIC #}
                        {% set btn_cls = "bg-white/5 border-white/5 text-gray-300 hover:bg-white/10" %}
                        {% set dot_cls = "bg-gray-500" %}
                        
                        {% if '1080' in s.reso %}
                            {% set btn_cls = "bg-red-900/20 border-red-500/30 text-red-200 hover:bg-red-900/40" %}
                            {% set dot_cls = "bg-red-500" %}
                        {% elif '720' in s.reso %}
                            {% set btn_cls = "bg-indigo-900/20 border-indigo-500/30 text-indigo-200 hover:bg-indigo-900/40" %}
                            {% set dot_cls = "bg-indigo-500" %}
                        {% elif '480' in s.reso %}
                            {% set btn_cls = "bg-green-900/20 border-green-500/30 text-green-200 hover:bg-green-900/40" %}
                            {% set dot_cls = "bg-green-500" %}
                        {% endif %}

                        <a href="{{ s.link }}" target="_blank" class="px-4 py-2 rounded border text-xs font-bold transition flex items-center gap-2 group {{ btn_cls }}">
                            <span class="w-2 h-2 rounded-full {{ dot_cls }}"></span>
                            {{ s.reso }} 
                            <span class="opacity-50 font-normal uppercase text-[9px] ml-1">({{ s.provide }})</span>
                            <i class="ri-external-link-line opacity-0 group-hover:opacity-100 transition-opacity"></i>
                        </a>
                    {% endfor %}
                </div>
            </div>
        </div>

    {% else %}
        <div class="text-center py-20 bg-white/5 rounded-xl border border-white/5 text-sm text-gray-500">
            Video Error / Belum tersedia.
        </div>
    {% endif %}
</div>
{% endblock %}
"""

HTML_FAVORITES = """
{% extends "base.html" %}
{% block content %}
<h2 class="text-lg font-bold text-white mb-6 border-l-4 border-red-600 pl-3">Koleksi Anime</h2>
<div id="fav-grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3"></div>
<div id="empty" class="hidden text-center py-20 text-gray-500 text-sm bg-white/5 rounded-xl">Belum ada koleksi.</div>
<script>
    const favs = JSON.parse(localStorage.getItem('albedo_favs') || '[]');
    if(favs.length===0) document.getElementById('empty').classList.remove('hidden');
    else {
        favs.forEach(a => {
            document.getElementById('fav-grid').insertAdjacentHTML('beforeend', `
            <a href="${a.url}" class="group relative block bg-[#111] rounded-lg overflow-hidden">
                <div class="aspect-[3/4]"><img src="${a.cover}" class="w-full h-full object-cover group-hover:opacity-80 transition"></div>
                <div class="p-3">
                    <h3 class="text-xs font-bold text-gray-200 truncate">${a.judul}</h3>
                </div>
                <button onclick="rem(event, '${a.url}')" class="absolute top-1 right-1 bg-red-600 text-white w-6 h-6 rounded flex items-center justify-center text-xs shadow-lg hover:scale-110 transition"><i class="ri-delete-bin-line"></i></button>
            </a>`);
        });
    }
    function rem(e, u) {
        e.preventDefault();
        if(!confirm('Hapus dari koleksi?')) return;
        localStorage.setItem('albedo_favs', JSON.stringify(favs.filter(f=>f.url!==u)));
        location.reload();
    }
</script>
{% endblock %}
"""

# ==========================================
# 3. LOGIC BACKEND (SMART FETCH)
# ==========================================

app = Flask(__name__)
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE,
    'index.html': HTML_INDEX,
    'genres.html': HTML_GENRES,
    'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH,
    'favorites.html': HTML_FAVORITES
})

API_BASE = "https://api.sansekai.my.id/api/anime"
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}

def smart_fetch(endpoint, params=None):
    """
    Fungsi Pintar untuk mengambil data dari struktur JSON yang berubah-ubah.
    """
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, params=params, timeout=12)
        raw = r.json()
        
        # 1. Jika kembalian langsung List (biasanya /latest)
        if isinstance(raw, list):
            return raw
            
        # 2. Jika ada key 'data'
        if 'data' in raw:
            data = raw['data']
            # Cek apakah ini hasil Search/Genre yang bersarang?
            # Biasanya: data: [ { jumlah: 5, result: [...] } ]
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                if isinstance(first_item, dict) and 'result' in first_item:
                    return first_item['result'] # INI SOLUSI GENRE KOSONG
            return data
            
        return []
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
        return []

def get_nav(chapters, current_url):
    if not chapters: return None, None
    # Cari index chapter saat ini
    # Asumsi: chapters urut dari Newest (index 0) ke Oldest
    idx = next((i for i, ch in enumerate(chapters) if ch.get('url') == current_url), -1)
    
    if idx == -1: return None, None
    
    next_ep = chapters[idx - 1] if idx > 0 else None # Lebih baru
    prev_ep = chapters[idx + 1] if idx < len(chapters) - 1 else None # Lebih lama
    
    return next_ep, prev_ep

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    # Gunakan /recommended untuk page > 1 agar ada konten
    data = smart_fetch('/latest') if page == 1 else smart_fetch('/recommended', params={'page': page})
    return render_template_string(HTML_INDEX, data_list=data, current_page=page, is_movie_page=False)

@app.route('/movies')
def movies():
    page = request.args.get('page', 1, type=int)
    data = smart_fetch('/movie', params={'page': page})
    return render_template_string(HTML_INDEX, data_list=data, current_page=page, is_movie_page=True)

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
    
    # Panggil fungsi Smart Fetch
    data = smart_fetch('/search', params={'query': q, 'page': page})
    
    return render_template_string(HTML_INDEX, data_list=data, search_query=q, current_page=page)

@app.route('/anime/<path:url_id>')
def detail(url_id):
    data = smart_fetch('/detail', params={'urlId': url_id})
    if not data: return render_template_string(HTML_DETAIL, error="Anime tidak ditemukan.")
    anime = data[0]
    
    # Metadata calculation
    eps = anime.get('chapter', [])
    anime['custom_total_eps'] = f"{len(eps)} Episodes" if eps else "?"
    if not anime.get('series_id'): anime['series_id'] = url_id # Fallback
    
    return render_template_string(HTML_DETAIL, anime=anime)

@app.route('/watch/<path:anime_url>/<path:chapter_url>')
def watch(anime_url, chapter_url):
    # Fetch Data
    vid_data = smart_fetch('/getvideo', params={'chapterUrlId': chapter_url})
    anime_data = smart_fetch('/detail', params={'urlId': anime_url})
    
    title = anime_data[0].get('judul') if anime_data else ""
    chapters = anime_data[0].get('chapter', []) if anime_data else []
    next_ep, prev_ep = get_nav(chapters, chapter_url)
    
    video_info = vid_data[0] if vid_data else None
    player_stream = None
    
    if video_info and 'stream' in video_info:
        streams = video_info['stream']
        
        # 1. Cari MP4 (Prioritas Utama - Native Browser Support)
        for s in streams:
            link = s.get('link', '')
            if '.mp4' in link or 'animekita' in link:
                player_stream = {'type': 'mp4', 'link': link}
                break
        
        # 2. Cari Iframe (Google/Blogger)
        if not player_stream:
            for s in streams:
                if 'google' in s.get('link', ''):
                    player_stream = {'type': 'iframe', 'link': s['link']}
                    break
        
        # 3. Fallback: Pakai link pertama (apapun itu)
        if not player_stream and streams:
            player_stream = {'type': 'iframe', 'link': streams[0]['link']}

    return render_template_string(
        HTML_WATCH,
        video=video_info,
        player_stream=player_stream,
        anime_title=title,
        anime_url=anime_url,
        next_ep=next_ep, 
        prev_ep=prev_ep
    )

if __name__ == '__main__':
    app.run(debug=True)
