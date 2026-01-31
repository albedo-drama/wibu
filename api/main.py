from flask import Flask, render_template_string, request, redirect, url_for
import requests
from jinja2 import DictLoader

# ==========================================
# 1. KONFIGURASI TEMPLATES (HTML + JINJA2)
# ==========================================

HTML_BASE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ALBEDOWIBU-TV{% endblock %}</title>
    
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="ALBEDOWIBU-TV">
    {% block meta %}{% endblock %}

    <script src="https://cdn.tailwindcss.com"></script>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/nprogress/0.2.0/nprogress.min.css" />

    <style>
        body { background-color: #0f0f1a; color: #e2e8f0; }
        /* Custom NProgress Color */
        #nprogress .bar { background: #9333ea !important; height: 3px !important; }
        #nprogress .peg { box-shadow: 0 0 10px #9333ea, 0 0 5px #9333ea !important; }
        
        /* Card & Scrollbar */
        .card:hover { transform: translateY(-5px); transition: 0.3s; }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #1e293b; }
        ::-webkit-scrollbar-thumb { background: #7c3aed; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #6d28d9; }
    </style>
</head>
<body class="font-sans antialiased min-h-screen flex flex-col selection:bg-purple-500 selection:text-white">
    
    <nav class="bg-slate-900/95 backdrop-blur-md border-b border-slate-800 p-4 sticky top-0 z-50 shadow-lg">
        <div class="container mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <div class="flex items-center gap-6 w-full md:w-auto justify-between">
                <a href="/" class="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500 tracking-wider">
                    ALBEDO<span class="text-white">WIBU</span>
                </a>
                <div class="flex gap-4 text-sm font-medium">
                    <a href="/" class="text-gray-300 hover:text-purple-400 transition">Series</a>
                    <a href="/movies" class="text-gray-300 hover:text-pink-400 transition">Movies</a>
                </div>
            </div>
            <form action="/search" method="GET" class="w-full md:w-1/3 flex relative group">
                <input type="text" name="q" placeholder="Cari anime..." value="{{ search_query if search_query else '' }}"
                       class="w-full p-2.5 pl-4 bg-slate-800 border border-slate-700 rounded-l-full focus:outline-none focus:border-purple-500 text-sm transition-colors">
                <button type="submit" class="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-2 rounded-r-full hover:opacity-90 transition font-medium text-white shadow-lg">🔍</button>
            </form>
        </div>
    </nav>

    <main class="container mx-auto p-4 md:p-6 flex-grow">
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-slate-900 text-center p-8 mt-12 border-t border-slate-800">
        <p class="text-slate-500 text-sm">&copy; 2026 ALBEDOWIBU-TV. API by Sansekai.</p>
    </footer>

    <script>
        // Trigger Loading Bar saat pindah halaman
        window.addEventListener('beforeunload', () => { NProgress.start(); });
        document.addEventListener("DOMContentLoaded", function() {
            NProgress.done();
            // Load History
            const history = JSON.parse(localStorage.getItem('watched_episodes') || '[]');
            history.forEach(url => {
                const link = document.querySelector(`a[href*="${url}"]`);
                if (link) {
                    link.classList.add('border-green-500', 'text-green-300');
                    if(link.classList.contains('episode-card')) {
                        link.insertAdjacentHTML('beforeend', '<span class="absolute top-1 right-1 text-green-500 text-xs">✔</span>');
                    }
                }
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
    <div class="flex items-center gap-2 mb-6">
        <a href="/" class="text-gray-400 hover:text-white">Home</a>
        <span class="text-gray-600">/</span>
        <h2 class="text-xl font-bold text-white">Hasil: "{{ search_query }}"</h2>
    </div>
{% elif is_movie_page %}
    <h2 class="text-xl font-bold mb-6 text-pink-400 border-l-4 border-pink-500 pl-3">🎬 Anime Movies (Hal {{ current_page }})</h2>
{% else %}
    {% if current_page == 1 %}
    <div class="mb-10 p-8 bg-slate-800 rounded-2xl shadow-2xl border border-slate-700 relative overflow-hidden">
        <div class="relative z-10">
            <h1 class="text-3xl md:text-4xl font-bold text-white mb-2">Halo, <span class="text-purple-400">ALBEDO</span>.</h1>
            <p class="text-gray-400">Selamat datang kembali.</p>
        </div>
        <div class="absolute -right-20 -top-20 w-80 h-80 bg-purple-600 rounded-full blur-[120px] opacity-20"></div>
    </div>
    {% endif %}
    <h2 class="text-xl font-bold mb-6 text-purple-400 border-l-4 border-purple-500 pl-3">🔥 Baru Rilis (Hal {{ current_page }})</h2>
{% endif %}

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-5 mb-8">
    {% for anime in data_list %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="card bg-slate-800 rounded-xl overflow-hidden shadow-lg block relative group border border-slate-700/50">
        <div class="relative aspect-[3/4]">
            <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover transition duration-500 group-hover:scale-110">
            <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-90"></div>
            {% if anime.score %}
            <div class="absolute top-2 right-2 bg-yellow-500/90 text-white text-[10px] font-bold px-1.5 py-0.5 rounded">★ {{ anime.score }}</div>
            {% endif %}
            <div class="absolute bottom-0 left-0 right-0 p-3">
                {% if anime.lastch %}<p class="text-xs text-purple-300 font-bold mb-1">{{ anime.lastch }}</p>{% endif %}
                <h3 class="text-sm font-semibold text-white truncate">{{ anime.judul }}</h3>
            </div>
        </div>
    </a>
    {% endfor %}
</div>

{% if not search_query %}
<div class="flex justify-center gap-4 mt-8">
    {% if current_page > 1 %}
    <a href="?page={{ current_page - 1 }}" class="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-full border border-slate-700 transition">← Sebelumnya</a>
    {% endif %}
    
    {% if data_list|length > 0 %}
    <a href="?page={{ current_page + 1 }}" class="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-full transition shadow-lg shadow-purple-900/50">Selanjutnya (Hal {{ current_page + 1 }}) →</a>
    {% endif %}
</div>
{% endif %}

{% endblock %}
"""

HTML_DETAIL = """
{% extends "base.html" %}

{% block title %}{{ anime.judul }} - ALBEDOWIBU-TV{% endblock %}

{% block meta %}
<meta property="og:title" content="{{ anime.judul }}">
<meta property="og:description" content="Nonton {{ anime.judul }} Subtitle Indonesia di ALBEDOWIBU-TV. {{ anime.status }} - {{ anime.rating }}">
<meta property="og:image" content="{{ anime.cover }}">
{% endblock %}

{% block content %}
{% if error %}
<div class="text-center py-20 text-red-500">{{ error }}</div>
{% else %}
<div class="bg-slate-800/60 backdrop-blur-sm rounded-2xl p-6 md:p-8 shadow-2xl border border-white/5 relative overflow-hidden mb-8">
    <div class="absolute inset-0 bg-cover bg-center opacity-10 blur-xl" style="background-image: url('{{ anime.cover }}'); transform: scale(1.1);"></div>
    <div class="relative z-10 flex flex-col md:flex-row gap-8">
        <div class="w-full md:w-1/4 max-w-[240px] mx-auto md:mx-0 shrink-0">
            <img src="{{ anime.cover }}" class="w-full rounded-xl shadow-2xl border-2 border-slate-600">
        </div>
        <div class="w-full md:w-3/4">
            <h1 class="text-2xl md:text-4xl font-bold text-white mb-3">{{ anime.judul }}</h1>
            <div class="flex flex-wrap gap-2 mb-6">
                <span class="badge bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 px-3 py-1 rounded-full text-xs font-bold">★ {{ anime.rating }}</span>
                <span class="badge bg-blue-500/20 text-blue-400 border border-blue-500/30 px-3 py-1 rounded-full text-xs font-bold">{{ anime.status }}</span>
                <span class="badge bg-green-500/20 text-green-400 border border-green-500/30 px-3 py-1 rounded-full text-xs font-bold">{{ anime.custom_total_eps }}</span>
            </div>
            <div class="mb-5 flex flex-wrap gap-2">
                {% for g in anime.genre %}
                <a href="/search?q={{ g }}" class="text-xs bg-slate-700 hover:bg-purple-600 text-gray-300 hover:text-white px-3 py-1.5 rounded-lg border border-slate-600">{{ g }}</a>
                {% endfor %}
            </div>
            <p class="text-gray-300 text-sm leading-relaxed bg-slate-900/50 p-4 rounded-xl border border-white/5 max-h-40 overflow-y-auto custom-scroll mb-4">{{ anime.sinopsis }}</p>
        </div>
    </div>
</div>

<div class="relative z-10">
    <div class="flex justify-between items-end mb-4 border-b border-slate-700 pb-2">
        <h3 class="text-xl font-bold text-white">📺 Daftar Episode</h3>
        <button onclick="reverseList()" class="text-xs bg-slate-700 hover:bg-slate-600 text-white px-3 py-1 rounded transition">⇅ Balik Urutan</button>
    </div>
    <div id="chapter-list" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 max-h-[600px] overflow-y-auto pr-2 custom-scroll pb-10">
        {% for chapter in anime.chapter %}
        <a href="/watch/{{ anime.series_id if anime.series_id else 'unknown' }}/{{ chapter.url }}" 
           class="episode-card group bg-slate-800 hover:bg-purple-600 border border-slate-700 hover:border-purple-500 p-3 rounded-lg transition text-center relative">
            <span class="text-[10px] text-gray-500 group-hover:text-purple-200 mb-1 block">{{ chapter.date }}</span>
            <span class="text-sm font-bold text-white">Chapter {{ chapter.ch }}</span>
        </a>
        {% endfor %}
    </div>
</div>
<script>
    function reverseList() {
        const list = document.getElementById('chapter-list');
        const items = Array.from(list.children);
        items.reverse().forEach(item => list.appendChild(item));
    }
</script>
{% endif %}
{% endblock %}
"""

HTML_WATCH = """
{% extends "base.html" %}
{% block title %}Nonton {{ anime_title }} - ALBEDOWIBU-TV{% endblock %}

{% block content %}
<div class="max-w-5xl mx-auto">
    <div class="flex items-center gap-2 mb-4 text-sm text-gray-400 overflow-x-auto whitespace-nowrap pb-2">
        <a href="/anime/{{ anime_url }}" class="text-purple-400 hover:text-white font-bold">← {{ anime_title }}</a>
        <span>/</span>
        <span class="text-white">Nonton</span>
    </div>

    {% if video %}
        <div class="bg-black rounded-xl overflow-hidden shadow-2xl border border-slate-700 mb-6 relative">
            <div class="relative pt-[56.25%]">
                {% if video.stream and video.stream|length > 0 %}
                <iframe src="{{ video.stream[0].link }}" class="absolute top-0 left-0 w-full h-full z-10" allowfullscreen scrolling="no" frameborder="0"></iframe>
                {% else %}
                <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-6">
                    <p class="text-red-500 font-bold mb-2">⚠️ Stream Utama Limit / Error</p>
                    <p class="text-gray-400 text-sm">Gunakan tombol resolusi di bawah.</p>
                </div>
                {% endif %}
            </div>
        </div>

        <div class="bg-slate-800 rounded-xl p-5 shadow-lg border border-slate-700">
            <div class="flex flex-col lg:flex-row justify-between items-center gap-6">
                <div class="flex gap-3 w-full lg:w-auto order-2 lg:order-1">
                    {% if prev_ep %}
                    <a href="/watch/{{ anime_url }}/{{ prev_ep.url }}" class="flex-1 lg:flex-none px-5 py-2.5 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition text-center border border-slate-600">⏪ Prev</a>
                    {% else %}
                    <button disabled class="flex-1 bg-slate-900 text-slate-700 px-5 py-2.5 rounded-lg cursor-not-allowed border border-slate-800">⏪ Prev</button>
                    {% endif %}

                    {% if next_ep %}
                    <a href="/watch/{{ anime_url }}/{{ next_ep.url }}" class="flex-1 lg:flex-none px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold transition text-center shadow-lg shadow-purple-900/50">Next ⏩</a>
                    {% else %}
                    <button disabled class="flex-1 bg-slate-900 text-slate-700 px-5 py-2.5 rounded-lg cursor-not-allowed border border-slate-800">Next ⏩</button>
                    {% endif %}
                </div>
                <div class="flex flex-wrap gap-2 justify-center lg:justify-end w-full lg:w-auto order-1 lg:order-2">
                    <span class="w-full text-center lg:text-right text-xs text-gray-400 mb-1 font-bold uppercase">Pilih Server / Resolusi</span>
                    {% for s in video.stream %}
                    <a href="{{ s.link }}" target="_blank" class="px-4 py-2 bg-slate-900 hover:bg-green-600 border border-slate-600 rounded text-xs text-gray-300 hover:text-white transition flex items-center gap-2 group">
                        <span class="w-2 h-2 rounded-full bg-green-500 group-hover:bg-white transition"></span>
                        <span class="font-bold">{{ s.reso }}</span>
                        <span class="opacity-50 text-[10px] uppercase">({{ s.provide }})</span>
                    </a>
                    {% endfor %}
                </div>
            </div>
        </div>
    {% else %}
        <div class="text-center py-24 bg-slate-800 rounded-2xl border border-slate-700">
            <h2 class="text-xl font-bold text-white mb-2">Video Tidak Tersedia</h2>
            <p class="text-gray-500">Mungkin link rusak atau belum dirilis server.</p>
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
# 2. FLASK & API LOGIC
# ==========================================

app = Flask(__name__)
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE,
    'index.html': HTML_INDEX,
    'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH
})

API_BASE = "https://api.sansekai.my.id/api/anime"
HEADERS = {'User-Agent': 'ALBEDOWIBU-TV/3.0', 'Accept': 'application/json'}

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
    next_ep = chapters[idx - 1] if idx > 0 else None
    prev_ep = chapters[idx + 1] if idx < len(chapters) - 1 else None
    return next_ep, prev_ep

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    # API latest mungkin tidak dukung pagination, tapi recommended dukung
    # Kita pakai recommended saja kalau page > 1 agar tidak error
    if page == 1:
        data = fetch_api('/latest')
    else:
        # Fallback ke recommended untuk page > 1 karena /latest biasanya statis
        data = fetch_api('/recommended', params={'page': page})
        
    return render_template_string(HTML_INDEX, data_list=data or [], current_page=page, is_movie_page=False)

@app.route('/movies')
def movies():
    page = request.args.get('page', 1, type=int)
    # API movie tidak ada dokumentasi pagination yang jelas di snippetmu
    # Tapi kita coba kirim param page, jika tidak didukung API biasanya akan return page 1
    data = fetch_api('/movie', params={'page': page})
    return render_template_string(HTML_INDEX, data_list=data or [], current_page=page, is_movie_page=True)

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
    if not data: return render_template_string(HTML_DETAIL, error="Gagal mengambil data anime.")
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
    chapters = anime_data[0].get('chapter', []) if anime_data else []
    next_ep, prev_ep = get_nav(chapters, chapter_url)
    
    return render_template_string(
        HTML_WATCH, video=vid[0] if vid else None, anime_title=title,
        anime_url=anime_url, current_url=chapter_url, next_ep=next_ep, prev_ep=prev_ep
    )

if __name__ == '__main__':
    app.run(debug=True)
