from flask import Flask, Response, redirect, request
from flask import send_file
import subprocess
import re
import os
import json

app = Flask(__name__)

# ===============================
# CONFIGURAÇÕES GERAIS
# ===============================

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

def server_url():
    return os.environ.get(
        "SERVER_URL",
        request.host_url.rstrip("/")
    )

# ===============================
# CANAIS YOUTUBE
# ===============================

CANAIS_YT = {
    "tvassembleia": {
        "name": "TV Assembleia PI",
        "url": "https://www.youtube.com/@tvassembleia-pi/live",
        "group": "YOUTUBE"
    },
    "tv_cancao_nova": {
        "name": "TV Canção Nova",
        "url": "https://www.youtube.com/user/tvcancaonova/live",
        "group": "YOUTUBE"
    }
}

# ===============================
# PLAYLIST M3U ORIGINAL
# ===============================

M3U_CONTENT = """#EXTM3U
#EXTINF:-1 tvg-id="TVAntena10.br" tvg-name="ANTENA 10 HD" tvg-logo="https://i.imgur.com/BqzBsdm.png" group-title="PIAUÍ TV",ANTENA 10 HD
https://video01.logicahost.com.br/a10maisadap/smil:transcoder.smil/chunklist.m3u8

#EXTINF:-1 tvg-id="Cultura.br" tvg-name="TV CULTURA" tvg-logo="https://lo1.in/BR/cultr.png" group-title="PIAUÍ TV",TV CULTURA
https://player-tvcultura.stream.uol.com.br/live/tvcultura_lsd.m3u8
"""

# ===============================
# PARSER M3U
# ===============================

def parse_m3u(content):
    channels = {}
    lines = content.splitlines()

    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            name = line.split(",")[-1].strip()
            key = re.sub(r"[^a-z0-9]", "_", name.lower())

            url = lines[i + 1].strip() if i + 1 < len(lines) else ""

            channels[key] = {
                "id": key,
                "name": name,
                "url": url,
                "tvg_id": re.search(r'tvg-id="([^"]+)"', line).group(1) if 'tvg-id="' in line else key,
                "logo": re.search(r'tvg-logo="([^"]+)"', line).group(1) if 'tvg-logo="' in line else "",
                "group": re.search(r'group-title="([^"]+)"', line).group(1) if 'group-title="' in line else "GERAL",
                "type": "youtube" if "youtube.com" in url else "direct"
            }

    return channels


M3U_CHANNELS = parse_m3u(M3U_CONTENT)

# ===============================
# HOME HTML
# ===============================

@app.route("/")
def index():
    html = "<h1>📺 Servidor IPTV</h1><ul>"

    for k, c in CANAIS_YT.items():
        html += f'<li>{c["name"]} - <a href="/{k}">Assistir</a></li>'

    for k, c in M3U_CHANNELS.items():
        html += f'<li>{c["name"]} - <a href="/{k}">Assistir</a></li>'

    html += '</ul><a href="/playlist.m3u">📋 Playlist M3U</a>'
    return html


# ===============================
# PLAYLIST M3U
# ===============================

@app.route("/playlist.m3u")
def playlist():
    base = server_url()
    out = "#EXTM3U\n\n"

    for k, c in CANAIS_YT.items():
        out += (
            f'#EXTINF:-1 tvg-id="{k}" group-title="{c["group"]}",{c["name"]}\n'
            f'{base}/{k}\n\n'
        )

    for k, c in M3U_CHANNELS.items():
        out += (
            f'#EXTINF:-1 tvg-id="{c["tvg_id"]}" tvg-logo="{c["logo"]}" '
            f'group-title="{c["group"]}",{c["name"]}\n'
            f'{c["url"] if c["type"] == "direct" else base + "/" + k}\n\n'
        )

    return Response(out, mimetype="audio/x-mpegurl")


# ===============================
# STREAM
# ===============================

def yt_stream(url):
    try:
        stream_url = subprocess.check_output(
            ["yt-dlp", "-f", "best", "--get-url", url],
            text=True
        ).splitlines()[0]
        return redirect(stream_url)
    except Exception as e:
        return f"Erro yt-dlp: {e}", 500


@app.route("/<canal>")
def stream(canal):
    if canal in CANAIS_YT:
        return yt_stream(CANAIS_YT[canal]["url"])

    if canal in M3U_CHANNELS:
        ch = M3U_CHANNELS[canal]
        return yt_stream(ch["url"]) if ch["type"] == "youtube" else redirect(ch["url"])

    return "Canal não encontrado", 404


# ===============================
# JSON / HEALTH
# ===============================

@app.route("/channels")
def channels():
    return Response(
        json.dumps(
            list(CANAIS_YT.values()) + list(M3U_CHANNELS.values()),
            ensure_ascii=False,
            indent=2
        ),
        mimetype="application/json"
    )

###########
@app.route("/epg.xml")
def epg():
    return send_file("epg.xml", mimetype="application/xml")
###########

@app.route("/health")
def health():
    return {
        "status": "ok",
        "youtube": len(CANAIS_YT),
        "m3u": len(M3U_CHANNELS)
    }


# ===============================
# MAIN
# ===============================

if __name__ == "__main__":
    print("🚀 IPTV Server ON")
    print(f"📺 http://localhost:{PORT}")
    app.run(host=HOST, port=PORT)