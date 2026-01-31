from flask import Flask, render_template_string, request, redirect, url_for
import requests
from jinja2 import DictLoader

# ==========================================
# 1. KONFIGURASI & HTML TEMPLATES (DALAM STRING)
# ==========================================

# --- Base Layout (Induk) ---
HTML_BASE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALBEDOWIBU-TV</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0f0f1a; color: #e2e8f0; }
        .card:hover { transform: translateY(-5px); transition: 0.3s; }
        .custom-scroll::-webkit-scrollbar { width: 8px; }
        .custom-scroll::-webkit-scrollbar-track { background: #1e293b; }
        .custom-scroll::-webkit-scrollbar-thumb { background: #9333ea; borderRadius: 4px; }
    </style>
</head>
<body class="font-sans antialiased min-h-screen flex flex-col selection:bg-purple-500 selection:text-white">
    <nav class="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 p-4 sticky top-0 z-50">
        <div class="container mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <a href="/" class="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600 tracking-wider">
                ALBEDO<span class="text-white">WIBU</span>
            </a>
            <form action="/search" method="GET" class="w-full md:w-1/3 flex relative">
                <input type="text" name="q" placeholder="Cari anime..." value="{{ search_query if search_query else '' }}"
                       class="w-full p-2 pl-4 bg-slate-800 border border-slate-700 rounded-l-full focus:outline-none focus:border-purple-500 text-sm transition-colors">
                <button type="submit" class="bg-purple-600 px-6 py-2 rounded-r-full hover:bg-purple-700 transition font-medium">🔍</button>
            </form>
        </div>
    </nav>

    <main class="container mx-auto p-4 md:p-6 flex-grow">
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-slate-900 text-center p-6 mt-12 border-t border-slate-800">
        <p class="text-slate-500 text-sm">&copy; 2026 ALBEDOWIBU-TV. Powered by Sansekai API.</p>
        <p class="text-slate-600 text-xs mt-1">Made with Python & Flask for ALBEDO</p>
    </footer>
</body>
</html>
"""

# --- Home Page ---
HTML_INDEX = """
{% extends "base.html" %}
{% block content %}

{% if search_query %}
    <div class="flex items-center gap-2 mb-6">
        <a href="/" class="text-gray-400 hover:text-white">Home</a>
        <span class="text-gray-600">/</span>
        <h2 class="text-xl font-bold text-white">Hasil: "{{ search_query }}"</h2>
    </div>
{% else %}
    <div class="mb-8 p-6 bg-gradient-to-r from-purple-900 to-slate-900 rounded-2xl shadow-2xl border border-white/10 relative overflow-hidden">
        <div class="relative z-10">
            <h1 class="text-3xl md:text-5xl font-bold text-white mb-2">Streaming Anime Tanpa Iklan</h1>
            <p class="text-purple-200">Update setiap hari, resolusi hemat kuota hingga HD.</p>
        </div>
        <div class="absolute -right-10 -bottom-20 w-64 h-64 bg-purple-500 rounded-full blur-[100px] opacity-20"></div>
    </div>
    <h2 class="text-xl font-bold mb-4 text-purple-400 border-l-4 border-purple-500 pl-3">Baru Diupload</h2>
{% endif %}

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 mb-12">
    {% if not latest and search_query %}
        <p class="col-span-full text-center text-gray-500 py-10">Tidak ditemukan anime dengan kata kunci tersebut.</p>
    {% endif %}

    {% for anime in latest %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="card bg-slate-800 rounded-xl overflow-hidden shadow-lg block relative group border border-slate-700/50 hover:border-purple-500/50">
        <div class="relative aspect-[3/4] overflow-hidden">
            <img src="{{ anime.cover }}" alt="{{ anime.judul }}" class="w-full h-full object-cover transition duration-500 group-hover:scale-110">
            <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-transparent opacity-80"></div>
            <div class="absolute bottom-0 left-0 right-0 p-3">
                <p class="text-xs text-yellow-400 font-bold mb-1">{{ anime.lastch }}</p>
                <h3 class="text-sm font-semibold text-white truncate leading-tight">{{ anime.judul }}</h3>
            </div>
            {% if anime.lastup %}
            <div class="absolute top-2 right-2 bg-red-600 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow">
                NEW
            </div>
            {% endif %}
        </div>
    </a>
    {% endfor %}
</div>

{% if recommended and not search_query %}
<h2 class="text-xl font-bold mb-4 text-pink-400 border-l-4 border-pink-500 pl-3">Rekomendasi</h2>
<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
    {% for anime in recommended %}
    <a href="/anime/{{ anime.url }}" class="card bg-slate-800 rounded-xl overflow-hidden shadow-lg block border border-slate-700/50">
        <div class="relative aspect-[3/4]">
            <img src="{{ anime.cover }}" alt="{{ anime.judul }}" class="w-full h-full object-cover">
            <div class="absolute top-2 right-2 bg-purple-600/90 backdrop-blur text-white text-xs font-bold px-2 py-1 rounded shadow">
                ★ {{ anime.score }}
            </div>
            <div class="absolute bottom-0 inset-x-0 bg-black/80 p-2 text-center">
                 <p class="text-xs text-gray-300">{{ anime.status }}</p>
            </div>
        </div>
        <div class="p-3">
            <h3 class="text-sm font-semibold truncate hover:text-purple-400 transition">{{ anime.judul }}</h3>
        </div>
    </a>
    {% endfor %}
</div>
{% endif %}

{% endblock %}
"""

# --- Detail Page ---
HTML_DETAIL = """
{% extends "base.html" %}
{% block content %}

{% if error %}
<div class="flex flex-col items-center justify-center min-h-[50vh] text-center">
    <div class="text-6xl mb-4">😭</div>
    <h2 class="text-2xl font-bold text-red-400 mb-2">Anime Tidak Ditemukan</h2>
    <p class="text-gray-500 mb-6">{{ error }}</p>
    <a href="/" class="px-6 py-2 bg-slate-700 hover:bg-slate-600 rounded-full text-white transition">Kembali ke Home</a>
</div>
{% else %}
<div class="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 md:p-8 shadow-2xl border border-white/5 relative overflow-hidden">
    <div class="absolute inset-0 bg-cover bg-center opacity-10 blur-xl" style="background-image: url('{{ anime.cover }}'); transform: scale(1.2);"></div>
    
    <div class="relative z-10 flex flex-col md:flex-row gap-8">
        <div class="w-full md:w-1/4 max-w-[250px] mx-auto md:mx-0 shrink-0">
            <img src="{{ anime.cover }}" class="w-full rounded-xl shadow-[0_0_20px_rgba(147,51,234,0.3)] border-2 border-slate-600/50">
        </div>

        <div class="w-full md:w-3/4">
            <h1 class="text-3xl md:text-5xl font-bold text-white mb-3">{{ anime.judul }}</h1>
            
            <div class="flex flex-wrap gap-2 mb-6">
                <span class="bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1">
                    ⭐ {{ anime.rating }}
                </span>
                <span class="bg-blue-500/20 text-blue-400 border border-blue-500/30 text-xs font-bold px-3 py-1 rounded-full">
                    {{ anime.status }}
                </span>
                <span class="bg-green-500/20 text-green-400 border border-green-500/30 text-xs font-bold px-3 py-1 rounded-full">
                    Total: {{ anime.custom_total_eps }}
                </span>
            </div>

            <div class="mb-4">
                <p class="text-gray-400 text-xs mb-1 uppercase tracking-wide">Genre</p>
                <div class="flex flex-wrap gap-2">
                    {% for g in anime.genre %}
                    <a href="/search?q={{ g }}" class="text-xs bg-slate-700 hover:bg-purple-600 text-gray-300 hover:text-white px-2 py-1 rounded transition">
                        {{ g }}
                    </a>
                    {% endfor %}
                </div>
            </div>

            <div class="mb-6">
                <p class="text-gray-400 text-xs mb-1 uppercase tracking-wide">Sinopsis</p>
                <p class="text-gray-300 text-sm leading-relaxed bg-slate-900/50 p-4 rounded-xl border border-white/5 max-h-40 overflow-y-auto custom-scroll">
                    {{ anime.sinopsis }}
                </p>
            </div>
            
            <div class="grid grid-cols-2 gap-y-2 text-sm text-gray-400 border-t border-white/5 pt-4">
                <p>Studio: <span class="text-white">{{ anime.author }}</span></p>
                <p>Rilis: <span class="text-white">{{ anime.published }}</span></p>
            </div>
        </div>
    </div>

    <div class="mt-10 relative z-10">
        <h3 class="text-xl font-bold text-white mb-4 flex items-center gap-2 border-b border-white/10 pb-2">
            📺 Daftar Episode
        </h3>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 max-h-[500px] overflow-y-auto pr-2 custom-scroll">
            {% for chapter in anime.chapter %}
            <a href="/watch/{{ anime.series_id if anime.series_id else 'unknown' }}/{{ chapter.url }}" 
               class="group bg-slate-700/50 hover:bg-purple-600 border border-slate-600/50 hover:border-purple-500 p-3 rounded-lg transition duration-200 text-center flex flex-col justify-center min-h-[70px]">
                <span class="text-[10px] text-gray-400 group-hover:text-purple-200 mb-1">{{ chapter.date }}</span>
                <span class="text-sm font-bold text-white group-hover:scale-105 transition-transform">Chapter {{ chapter.ch }}</span>
            </a>
            {% endfor %}
        </div>
    </div>
</div>
{% endif %}
{% endblock %}
"""

# --- Watch Page ---
HTML_WATCH = """
{% extends "base.html" %}
{% block content %}

<div class="max-w-5xl mx-auto">
    <div class="flex items-center gap-2 mb-4 text-sm overflow-x-auto whitespace-nowrap pb-2">
        <a href="/" class="text-gray-500 hover:text-white">Home</a>
        <span class="text-gray-600">/</span>
        <a href="/anime/{{ anime_url }}" class="text-purple-400 hover:text-white font-medium truncate max-w-[150px] md:max-w-xs">{{ anime_title }}</a>
        <span class="text-gray-600">/</span>
        <span class="text-white">Nonton</span>
    </div>

    {% if video %}
        <div class="bg-black rounded-xl overflow-hidden shadow-2xl border border-slate-700 mb-6 group relative">
            <div class="relative pt-[56.25%] w-full"> {% if video.stream and video.stream|length > 0 %}
                    <iframe src="{{ video.stream[0].link }}" 
                            class="absolute top-0 left-0 w-full h-full z-10" 
                            allowfullscreen 
                            scrolling="no" 
                            frameborder="0"></iframe>
                {% else %}
                    <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-4">
                        <div class="text-4xl mb-2">⚠️</div>
                        <p class="text-red-500 font-bold mb-2">Player Utama Error</p>
                        <p class="text-gray-400 text-sm">Gunakan tombol resolusi di bawah untuk membuka video.</p>
                    </div>
                {% endif %}
            </div>
        </div>

        <div class="bg-slate-800 rounded-xl p-4 md:p-6 shadow-lg border border-slate-700">
            
            <div class="mb-6 border-b border-slate-700 pb-4">
                <h1 class="text-lg md:text-xl font-bold text-white mb-1">Sedang Menonton</h1>
                <p class="text-purple-400 text-sm">{{ anime_title }}</p>
            </div>

            <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
                
                <div class="w-full lg:w-auto order-2 lg:order-1 flex gap-2">
                    {% if prev_ep %}
                    <a href="/watch/{{ anime_url }}/{{ prev_ep.url }}" class="flex-1 lg:flex-none px-6 py-2.5 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition flex items-center justify-center gap-2 border border-slate-600">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
                        Prev
                    </a>
                    {% else %}
                    <button disabled class="flex-1 lg:flex-none px-6 py-2.5 bg-slate-900 text-slate-600 rounded-lg cursor-not-allowed border border-slate-800">Prev</button>
                    {% endif %}

                    {% if next_ep %}
                    <a href="/watch/{{ anime_url }}/{{ next_ep.url }}" class="flex-1 lg:flex-none px-6 py-2.5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-lg font-bold transition flex items-center justify-center gap-2 shadow-lg shadow-purple-900/50">
                        Next
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                    </a>
                    {% else %}
                    <button disabled class="flex-1 lg:flex-none px-6 py-2.5 bg-slate-900 text-slate-600 rounded-lg cursor-not-allowed border border-slate-800">Next</button>
                    {% endif %}
                </div>

                <div class="w-full lg:w-auto order-1 lg:order-2">
                    <div class="flex flex-wrap gap-2 items-center justify-start lg:justify-end">
                        <span class="text-xs text-gray-400 uppercase tracking-wide font-bold mr-1">Download / Alt:</span>
                        {% for s in video.stream %}
                        <a href="{{ s.link }}" target="_blank" class="px-3 py-1.5 bg-slate-900 hover:bg-green-600 border border-slate-600 rounded text-xs text-gray-300 hover:text-white transition flex items-center gap-1">
                            <span class="w-2 h-2 rounded-full bg-green-500"></span>
                            {{ s.reso }} <span class="opacity-50 text-[10px]">({{ s.provide }})</span>
                        </a>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>

    {% else %}
        <div class="text-center py-20 bg-slate-800/50 rounded-2xl border border-red-500/20">
            <div class="text-5xl mb-4">⚠️</div>
            <h2 class="text-2xl font-bold text-white mb-2">Gagal Memuat Video</h2>
            <p class="text-gray-400 mb-6">Mungkin episode ini belum rilis atau API sedang sibuk.</p>
            <a href="/anime/{{ anime_url }}" class="text-purple-400 hover:underline">Kembali ke Halaman Detail</a>
        </div>
    {% endif %}
</div>
{% endblock %}
"""

# ==========================================
# 2. FLASK SETUP & HELPER FUNCTIONS
# ==========================================

app = Flask(__name__)

# Mengatur Jinja loader agar bisa membaca template dari string variables di atas
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE,
    'index.html': HTML_INDEX,
    'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH
})

# API Config
API_BASE = "https://api.sansekai.my.id/api/anime"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ALBEDOWIBU-TV/1.0',
    'Accept': 'application/json'
}

def fetch_api(endpoint, params=None):
    """
    Mengambil data dari API dengan Error Handling.
    Menangani format return yang kadang list, kadang dict 'data'.
    """
    try:
        url = f"{API_BASE}{endpoint}"
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Normalisasi Output API (Karena format API sansekai tidak konsisten)
        if isinstance(data, list): 
            return data
        if 'data' in data: 
            return data['data']
        return data
        
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
        return None

def get_navigation(all_chapters, current_chapter_url):
    """
    Logika Next/Prev.
    Array chapters biasanya urut dari Terbaru (atas) ke Terlama (bawah).
    Jadi: Next Episode (ch lebih besar) = index - 1
          Prev Episode (ch lebih kecil) = index + 1
    """
    if not all_chapters: return None, None

    current_idx = -1
    for i, ch in enumerate(all_chapters):
        if ch.get('url') == current_chapter_url:
            current_idx = i
            break
            
    next_ep = None
    prev_ep = None
    
    if current_idx != -1:
        # Ingat: List urut mundur. 
        # Jika current index 5, maka next eps (lebih baru) ada di index 4
        if current_idx > 0:
            next_ep = all_chapters[current_idx - 1]
            
        # Prev eps (lebih lama) ada di index 6
        if current_idx < len(all_chapters) - 1:
            prev_ep = all_chapters[current_idx + 1]
            
    return next_ep, prev_ep

# ==========================================
# 3. ROUTES (LOGIC)
# ==========================================

@app.route('/')
def home():
    # Ambil Anime Terbaru & Rekomendasi
    latest = fetch_api('/latest')
    recommended = fetch_api('/recommended', params={'page': 1})
    
    return render_template_string(HTML_INDEX, latest=latest or [], recommended=recommended or [])

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query: return redirect(url_for('home'))
    
    raw = fetch_api('/search', params={'query': query})
    results = []
    
    # API search kadang me-return structure nested di dalam 'result'
    if raw and isinstance(raw, list) and len(raw) > 0:
        results = raw[0].get('result', [])
    elif raw and 'data' in raw: # Handle edge case
        results = raw['data']

    return render_template_string(HTML_INDEX, latest=results, search_query=query, recommended=[])

@app.route('/anime/<path:url_id>')
def detail(url_id):
    # Ambil detail anime
    data = fetch_api('/detail', params={'urlId': url_id})
    
    if not data or len(data) == 0:
        return render_template_string(HTML_DETAIL, error="Data anime tidak ditemukan di API.")
        
    anime = data[0]
    
    # Tambahan Data: Hitung manual total episode & range
    chapters = anime.get('chapter', [])
    total_eps = len(chapters)
    if total_eps > 0:
        first = chapters[-1]['ch'] # Episode paling bawah (awal)
        last = chapters[0]['ch']   # Episode paling atas (terbaru)
        anime['custom_total_eps'] = f"{total_eps} Eps ({first}-{last})"
    else:
        anime['custom_total_eps'] = "Unknown"
        
    # Pastikan series_id ada untuk link watch (fallback ke url_id)
    if not anime.get('series_id'):
        anime['series_id'] = url_id

    return render_template_string(HTML_DETAIL, anime=anime)

@app.route('/watch/<path:anime_url>/<path:chapter_url>')
def watch(anime_url, chapter_url):
    # 1. Ambil Video Stream
    stream_data = fetch_api('/getvideo', params={'chapterUrlId': chapter_url})
    video_info = stream_data[0] if stream_data and len(stream_data) > 0 else None
    
    # 2. Ambil Detail Anime (Hanya untuk keperluan Navigasi Next/Prev & Judul)
    anime_data = fetch_api('/detail', params={'urlId': anime_url})
    
    anime_title = "Anime"
    next_ep = None
    prev_ep = None
    
    if anime_data and len(anime_data) > 0:
        details = anime_data[0]
        anime_title = details.get('judul', 'Anime')
        chapters = details.get('chapter', [])
        
        # Hitung Navigasi
        next_ep, prev_ep = get_navigation(chapters, chapter_url)
        
    return render_template_string(
        HTML_WATCH,
        video=video_info,
        anime_title=anime_title,
        anime_url=anime_url,
        next_ep=next_ep,
        prev_ep=prev_ep,
        current_url=chapter_url
    )

# Handler untuk Vercel Serverless
if __name__ == '__main__':
    app.run(debug=True)
