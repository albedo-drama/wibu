from flask import Flask, render_template_string, request, redirect, url_for
import requests
from jinja2 import DictLoader

# ==========================================
# 1. TEMPLATES HTML (Advanced Features)
# ==========================================

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
        .visited-link { opacity: 0.6; filter: grayscale(100%); }
        /* Scrollbar Halus */
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
                       class="w-full p-2.5 pl-4 bg-slate-800 border border-slate-700 rounded-l-full focus:outline-none focus:border-purple-500 text-sm transition-colors group-hover:bg-slate-800/80">
                <button type="submit" class="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-2 rounded-r-full hover:opacity-90 transition font-medium text-white shadow-lg shadow-purple-900/50">🔍</button>
            </form>
        </div>
    </nav>

    <main class="container mx-auto p-4 md:p-6 flex-grow">
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-slate-900 text-center p-8 mt-12 border-t border-slate-800">
        <p class="text-slate-500 text-sm">&copy; 2026 ALBEDOWIBU-TV. API by Sansekai.</p>
        <p class="text-slate-600 text-xs mt-2">Developed specially for ALBEDO</p>
    </footer>
    
    <script>
        // Global Script: Menandai link yang sudah dikunjungi (History Lokal)
        document.addEventListener("DOMContentLoaded", function() {
            const history = JSON.parse(localStorage.getItem('watched_episodes') || '[]');
            history.forEach(url => {
                const link = document.querySelector(`a[href*="${url}"]`);
                if (link) {
                    link.classList.add('border-green-500', 'text-green-300'); // Ganti style jika sudah ditonton
                    const badge = document.createElement('span');
                    badge.innerText = '✔';
                    badge.className = 'absolute top-1 right-1 text-green-500 text-xs font-bold';
                    if(link.classList.contains('episode-card')) link.appendChild(badge);
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
        <h2 class="text-xl font-bold text-white">Hasil Pencarian: "<span class="text-purple-400">{{ search_query }}</span>"</h2>
    </div>
{% elif is_movie_page %}
    <h2 class="text-xl font-bold mb-6 text-pink-400 border-l-4 border-pink-500 pl-3 flex items-center gap-2">
        🎬 Anime Movies Terbaru
    </h2>
{% else %}
    <div class="mb-10 p-8 bg-slate-800 rounded-2xl shadow-2xl border border-slate-700 relative overflow-hidden">
        <div class="relative z-10">
            <h1 class="text-3xl md:text-4xl font-bold text-white mb-2">Halo, <span class="text-purple-400">ALBEDO</span>.</h1>
            <p class="text-gray-400">Selamat datang kembali. Mau nonton apa hari ini?</p>
        </div>
        <div class="absolute -right-20 -top-20 w-80 h-80 bg-purple-600 rounded-full blur-[120px] opacity-20"></div>
    </div>
    
    <h2 class="text-xl font-bold mb-6 text-purple-400 border-l-4 border-purple-500 pl-3">🔥 Baru Rilis (Ongoing)</h2>
{% endif %}

<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-5 mb-12">
    {% if not data_list and search_query %}
        <div class="col-span-full text-center py-20">
            <p class="text-6xl mb-4">😶</p>
            <p class="text-gray-500">Maaf, anime tidak ditemukan.</p>
        </div>
    {% endif %}

    {% for anime in data_list %}
    <a href="/anime/{{ anime.url if anime.url else anime.id }}" class="card bg-slate-800 rounded-xl overflow-hidden shadow-lg block relative group border border-slate-700/50 hover:border-purple-500/50 transition-all duration-300">
        <div class="relative aspect-[3/4] overflow-hidden">
            <img src="{{ anime.cover }}" loading="lazy" alt="{{ anime.judul }}" class="w-full h-full object-cover transition duration-500 group-hover:scale-110">
            
            <div class="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent opacity-90"></div>
            
            <div class="absolute top-2 right-2 flex flex-col gap-1 items-end">
                {% if anime.score %}
                <span class="bg-yellow-500/90 text-white text-[10px] font-bold px-1.5 py-0.5 rounded shadow">★ {{ anime.score }}</span>
                {% endif %}
                {% if anime.lastup == 'Baru di Upload' %}
                <span class="bg-red-600/90 text-white text-[10px] font-bold px-1.5 py-0.5 rounded shadow animate-pulse">NEW</span>
                {% endif %}
            </div>

            <div class="absolute bottom-0 left-0 right-0 p-3">
                {% if anime.lastch %}
                <p class="text-xs text-purple-300 font-bold mb-1">{{ anime.lastch }}</p>
                {% endif %}
                <h3 class="text-sm font-semibold text-white truncate leading-tight group-hover:text-purple-400 transition">{{ anime.judul }}</h3>
            </div>
        </div>
    </a>
    {% endfor %}
</div>

{% if recommended and not search_query and not is_movie_page %}
<h2 class="text-xl font-bold mb-6 text-blue-400 border-l-4 border-blue-500 pl-3">⭐ Rekomendasi Musim Ini</h2>
<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-5">
    {% for anime in recommended %}
    <a href="/anime/{{ anime.url }}" class="card bg-slate-800 rounded-xl overflow-hidden shadow-lg block border border-slate-700/50">
        <div class="relative aspect-[3/4]">
            <img src="{{ anime.cover }}" loading="lazy" class="w-full h-full object-cover">
            <div class="absolute bottom-0 inset-x-0 bg-black/80 p-2 text-center backdrop-blur-sm">
                 <p class="text-xs text-gray-300">{{ anime.status }}</p>
            </div>
        </div>
        <div class="p-3">
            <h3 class="text-sm font-semibold truncate text-gray-200">{{ anime.judul }}</h3>
        </div>
    </a>
    {% endfor %}
</div>
{% endif %}

{% endblock %}
"""

HTML_DETAIL = """
{% extends "base.html" %}
{% block content %}

{% if error %}
<div class="text-center py-20">
    <h2 class="text-2xl font-bold text-red-500">{{ error }}</h2>
    <a href="/" class="text-purple-400 underline mt-4 block">Kembali ke Home</a>
</div>
{% else %}
<div class="bg-slate-800/60 backdrop-blur-sm rounded-2xl p-6 md:p-8 shadow-2xl border border-white/5 relative overflow-hidden mb-8">
    <div class="absolute inset-0 bg-cover bg-center opacity-10 blur-xl" style="background-image: url('{{ anime.cover }}'); transform: scale(1.1);"></div>
    
    <div class="relative z-10 flex flex-col md:flex-row gap-8">
        <div class="w-full md:w-1/4 max-w-[240px] mx-auto md:mx-0 shrink-0">
            <img src="{{ anime.cover }}" class="w-full rounded-xl shadow-2xl border-2 border-slate-600">
        </div>
        <div class="w-full md:w-3/4">
            <h1 class="text-2xl md:text-4xl font-bold text-white mb-3 leading-tight">{{ anime.judul }}</h1>
            
            <div class="flex flex-wrap gap-2 mb-6">
                <span class="badge bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 px-3 py-1 rounded-full text-xs font-bold">★ {{ anime.rating }}</span>
                <span class="badge bg-blue-500/20 text-blue-400 border border-blue-500/30 px-3 py-1 rounded-full text-xs font-bold">{{ anime.status }}</span>
                <span class="badge bg-green-500/20 text-green-400 border border-green-500/30 px-3 py-1 rounded-full text-xs font-bold">{{ anime.custom_total_eps }}</span>
            </div>

            <div class="mb-5">
                <p class="text-gray-500 text-[10px] uppercase font-bold tracking-wider mb-2">GENRE</p>
                <div class="flex flex-wrap gap-2">
                    {% for g in anime.genre %}
                    <a href="/search?q={{ g }}" class="text-xs bg-slate-700 hover:bg-purple-600 text-gray-300 hover:text-white px-3 py-1.5 rounded-lg transition border border-slate-600">
                        {{ g }}
                    </a>
                    {% endfor %}
                </div>
            </div>

            <div class="bg-slate-900/50 p-4 rounded-xl border border-white/5 max-h-40 overflow-y-auto custom-scroll mb-4">
                <p class="text-gray-300 text-sm leading-relaxed">{{ anime.sinopsis }}</p>
            </div>
            
            <div class="text-xs text-gray-500 flex flex-wrap gap-4">
                <p>Studio: <span class="text-gray-300">{{ anime.author }}</span></p>
                <p>Rilis: <span class="text-gray-300">{{ anime.published }}</span></p>
            </div>
        </div>
    </div>
</div>

<div class="relative z-10">
    <div class="flex justify-between items-end mb-4 border-b border-slate-700 pb-2">
        <h3 class="text-xl font-bold text-white flex items-center gap-2">
            📺 Daftar Episode
        </h3>
        <button onclick="reverseList()" class="text-xs bg-slate-700 hover:bg-slate-600 text-white px-3 py-1 rounded transition flex items-center gap-1">
            ⇅ Balik Urutan
        </button>
    </div>

    <div id="chapter-list" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 max-h-[600px] overflow-y-auto pr-2 custom-scroll pb-10">
        {% for chapter in anime.chapter %}
        <a href="/watch/{{ anime.series_id if anime.series_id else 'unknown' }}/{{ chapter.url }}" 
           class="episode-card group bg-slate-800 hover:bg-purple-600 border border-slate-700 hover:border-purple-500 p-3 rounded-lg transition duration-200 text-center flex flex-col justify-center min-h-[70px] relative">
            <span class="text-[10px] text-gray-500 group-hover:text-purple-200 mb-1">{{ chapter.date }}</span>
            <span class="text-sm font-bold text-white">Chapter {{ chapter.ch }}</span>
        </a>
        {% endfor %}
    </div>
</div>

<script>
    // Fitur Sortir Episode
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
{% block content %}

<div class="max-w-5xl mx-auto">
    <div class="flex items-center gap-2 mb-4 text-sm text-gray-400 overflow-x-auto whitespace-nowrap pb-2">
        <a href="/anime/{{ anime_url }}" class="text-purple-400 hover:text-white font-bold">← {{ anime_title }}</a>
        <span>/</span>
        <span class="text-white">Menonton</span>
    </div>

    {% if video %}
        <div class="bg-black rounded-xl overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.5)] border border-slate-700 mb-6 relative group">
            <div class="relative pt-[56.25%]">
                {% if video.stream and video.stream|length > 0 %}
                <iframe src="{{ video.stream[0].link }}" 
                        class="absolute top-0 left-0 w-full h-full z-10" 
                        allowfullscreen scrolling="no" frameborder="0"></iframe>
                {% else %}
                <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-6">
                    <p class="text-red-500 font-bold mb-2 text-lg">⚠️ Stream Error / Limit</p>
                    <p class="text-gray-400 text-sm">Coba klik tombol 'Direct Link' di bawah ini.</p>
                </div>
                {% endif %}
            </div>
        </div>

        <div class="bg-slate-800 rounded-xl p-5 shadow-lg border border-slate-700">
            <div class="flex flex-col lg:flex-row justify-between items-center gap-6">
                
                <div class="flex gap-3 w-full lg:w-auto order-2 lg:order-1">
                    {% if prev_ep %}
                    <a href="/watch/{{ anime_url }}/{{ prev_ep.url }}" class="flex-1 bg-slate-700 hover:bg-slate-600 text-white px-5 py-2.5 rounded-lg font-medium transition text-center border border-slate-600">
                        ⏪ Prev
                    </a>
                    {% else %}
                    <button disabled class="flex-1 bg-slate-900 text-slate-700 px-5 py-2.5 rounded-lg cursor-not-allowed border border-slate-800">⏪ Prev</button>
                    {% endif %}

                    {% if next_ep %}
                    <a href="/watch/{{ anime_url }}/{{ next_ep.url }}" class="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-5 py-2.5 rounded-lg font-bold transition text-center shadow-lg shadow-purple-900/50">
                        Next ⏩
                    </a>
                    {% else %}
                    <button disabled class="flex-1 bg-slate-900 text-slate-700 px-5 py-2.5 rounded-lg cursor-not-allowed border border-slate-800">Next ⏩</button>
                    {% endif %}
                </div>

                <div class="flex flex-wrap gap-2 justify-center lg:justify-end w-full lg:w-auto order-1 lg:order-2">
                    <span class="w-full text-center lg:text-right text-xs text-gray-400 mb-1 font-bold tracking-widest uppercase">Pilih Resolusi</span>
                    {% for s in video.stream %}
                    <a href="{{ s.link }}" target="_blank" class="px-4 py-2 bg-slate-900 hover:bg-green-600 border border-slate-600 rounded text-xs text-gray-300 hover:text-white transition flex items-center gap-2 group">
                        <span class="w-2 h-2 rounded-full bg-green-500 group-hover:bg-white transition"></span>
                        <span class="font-bold">{{ s.reso }}</span>
                        {% if s.provide %}<span class="opacity-50 border-l border-gray-600 pl-2 ml-1">{{ s.provide }}</span>{% endif %}
                    </a>
                    {% endfor %}
                </div>
            </div>
        </div>

    {% else %}
        <div class="text-center py-24 bg-slate-800 rounded-2xl border border-slate-700">
            <h2 class="text-3xl mb-2">😵</h2>
            <h2 class="text-xl font-bold text-white mb-2">Video Tidak Tersedia</h2>
            <p class="text-gray-500">Mungkin link rusak atau belum dirilis oleh server.</p>
        </div>
    {% endif %}
</div>

<script>
    // Simpan history tontonan saat halaman dimuat
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
# 2. FLASK & LOGIC
# ==========================================

app = Flask(__name__)
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE,
    'index.html': HTML_INDEX,
    'detail.html': HTML_DETAIL,
    'watch.html': HTML_WATCH
})

API_BASE = "https://api.sansekai.my.id/api/anime"
HEADERS = {'User-Agent': 'ALBEDOWIBU-TV/2.0', 'Accept': 'application/json'}

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
    # idx-1 = Newer (Next in logic if array is DESC), idx+1 = Older (Prev)
    # Tapi label tombolnya: "Next Episode" (Angka chapter naik)
    # Biasanya list: [Ch 10, Ch 9, ... Ch 1]
    # Jika kita di Ch 9 (idx 1), Next Ep adalah Ch 10 (idx 0), Prev Ep adalah Ch 8 (idx 2)
    next_ep = chapters[idx - 1] if idx > 0 else None
    prev_ep = chapters[idx + 1] if idx < len(chapters) - 1 else None
    return next_ep, prev_ep

# --- ROUTES ---

@app.route('/')
def home():
    latest = fetch_api('/latest')
    recom = fetch_api('/recommended', params={'page': 1})
    return render_template_string(HTML_INDEX, data_list=latest or [], recommended=recom or [], is_movie_page=False)

@app.route('/movies')
def movies():
    data = fetch_api('/movie')
    return render_template_string(HTML_INDEX, data_list=data or [], recommended=[], is_movie_page=True)

@app.route('/search')
def search():
    q = request.args.get('q')
    if not q: return redirect('/')
    res = fetch_api('/search', params={'query': q})
    # Handle weird search API structure
    if res and isinstance(res, list) and len(res) > 0 and 'result' in res[0]:
        clean_res = res[0]['result']
    else:
        clean_res = []
    return render_template_string(HTML_INDEX, data_list=clean_res, search_query=q)

@app.route('/anime/<path:url_id>')
def detail(url_id):
    data = fetch_api('/detail', params={'urlId': url_id})
    if not data: return render_template_string(HTML_DETAIL, error="Gagal mengambil data anime.")
    anime = data[0]
    
    # Custom Metadata
    eps = anime.get('chapter', [])
    anime['custom_total_eps'] = f"{len(eps)} Episodes" if eps else "Unknown"
    if not anime.get('series_id'): anime['series_id'] = url_id # Fallback
    
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
