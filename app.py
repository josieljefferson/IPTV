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

M3U_CONTENT = """#EXTM3U url-tvg="https://m3u4u.com/epg/jq2zy9epr3bwxmgwyxr5, https://m3u4u.com/epg/3wk1y24kx7uzdevxygz7, https://m3u4u.com/epg/782dyqdrqkh1xegen4zp, https://www.open-epg.com/files/brazil1.xml.gz, https://www.open-epg.com/files/brazil2.xml.gz, https://www.open-epg.com/files/brazil3.xml.gz, https://www.open-epg.com/files/brazil4.xml.gz, https://www.open-epg.com/files/portugal1.xml.gz, https://www.open-epg.com/files/portugal2.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_BR1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_PT1.xml.gz"

#PLAYLISTV: pltv-logo="https://cdn-icons-png.flaticon.com/256/25/25231.png" pltv-name="☆Josiel Jefferson☆" pltv-description="Playlist GitLab And GitHub Pages" pltv-cover="https://images.icon-icons.com/2407/PNG/512/gitlab_icon_146171.png" pltv-author="☆Josiel Jefferson☆" pltv-site="https://josieljefferson12.github.io/josieljefferson12.github.io.oficial" pltv-email="josielluz@proton.me"

#EXTINF:-1 tvg-id="SBT(Portuguese).br" tvg-name="NOVO PORTAL DO CADASTRO ÚNICO E INFORMAÇÕES" tvg-logo="https://imgur.com/DsFAXXo.png" group-title="CADASTRO ÚNICO",NOVO PORTAL DO CADASTRO ÚNICO E INFORMAÇÕES
https://files.catbox.moe/6nxf2w.mp4

#EXTINF:-1 tvg-id="SBT(Portuguese).br" tvg-name="WORKSHOP INSTRUÇÕES BÁSICAS PARA GESTÃO MUNICIPAL DO CADASTRO ÚNICO 1" tvg-logo="https://imgur.com/DsFAXXo.png" group-title="CADASTRO ÚNICO",WORKSHOP INSTRUÇÕES BÁSICAS PARA GESTÃO MUNICIPAL DO CADASTRO ÚNICO 1
https://files.catbox.moe/ewz9rd.mp4

#EXTINF:-1 tvg-id="SBT(Portuguese).br" tvg-name="WORKSHOP INSTRUÇÕES BÁSICAS PARA GESTÃO MUNICIPAL DO CADASTRO ÚNICO 2" tvg-logo="https://imgur.com/DsFAXXo.png" group-title="CADASTRO ÚNICO",WORKSHOP INSTRUÇÕES BÁSICAS PARA GESTÃO MUNICIPAL DO CADASTRO ÚNICO 2
https://files.catbox.moe/5hdnwb.mp4

#EXTINF:-1 tvg-id="SBT(Portuguese).br" tvg-name="WORKSHOP INSTRUÇÕES BÁSICAS PARA GESTÃO MUNICIPAL DO CADASTRO ÚNICO 3" tvg-logo="https://imgur.com/DsFAXXo.png" group-title="CADASTRO ÚNICO",WORKSHOP INSTRUÇÕES BÁSICAS PARA GESTÃO MUNICIPAL DO CADASTRO ÚNICO 3
https://files.catbox.moe/d0vp9o.mp4

#EXTINF:-1 tvg-id="SBT(Portuguese).br" tvg-name="VEJA O QUE ACONTECE SE LIGAR O IDR, DPS E DISJUNTOR GERAL NA SEQUÊNCIA ERRADA" tvg-logo="https://imgur.com/HqWfDQ2.png" group-title="ELETRICIDADE",DPS E DISJUNTOR GERAL NA SEQUÊNCIA ERRADA
https://files.catbox.moe/u3jfz4.mp4

#EXTINF:-1 tvg-id="SBT(Portuguese).br" tvg-name="ESSA É A SOLUÇÃO QUANDO NÃO TEM ATERRAMENTO ELÉTRICO NA RESIDÊNCIA. ( ATERRAMENTO TNC-S )" tvg-logo="https://imgur.com/HqWfDQ2.png" group-title="ELETRICIDADE",ESSA É A SOLUÇÃO QUANDO NÃO TEM ATERRAMENTO ELÉTRICO NA RESIDÊNCIA. ( ATERRAMENTO TNC-S )
https://files.catbox.moe/yb00ur.mp4

#EXTINF:-1 tvg-id="SBT(Portuguese).br" tvg-name="FAÇA ISSO PARA INSTALAR DPS EM QUADROS ANTIGOS SEM ATERRAMENTO" tvg-logo="https://imgur.com/HqWfDQ2.png" group-title="ELETRICIDADE",FAÇA ISSO PARA INSTALAR DPS EM QUADROS ANTIGOS SEM ATERRAMENTO
https://files.catbox.moe/en3wf2.mp4

#EXTINF:-1 tvg-id="SBT(Portuguese).br" tvg-name="FAÇA ISSO QUANDO NÃO TIVER ATERRAMENTO ELÉTRICO NA RESIDÊNCIA (ATERRAMENTO SEM HASTES)" tvg-logo="https://imgur.com/HqWfDQ2.png" group-title="ELETRICIDADE",FAÇA ISSO QUANDO NÃO TIVER ATERRAMENTO ELÉTRICO NA RESIDÊNCIA (ATERRAMENTO SEM HASTES)
https://files.catbox.moe/6xw08a.mp4

#EXTINF:-1 tvg-id="SBT(Portuguese).br" tvg-name="QUADRO SEM ATERRAMENTO VEJA COM FAZER SEM QUEBRAR PAREDES" tvg-logo="https://imgur.com/HqWfDQ2.png" group-title="ELETRICIDADE",QUADRO SEM ATERRAMENTO VEJA COM FAZER SEM QUEBRAR PAREDES
https://files.catbox.moe/bn8ppt.mp4

#EXTINF:-1 tvg-id="SBT(Portuguese).br" tvg-name="VOCÊ DEVE LIGAR O NEUTRO NO TERRA! MESMO QUE O QUADRO (QDC) NÃO TENHA IDR NEM DPS" tvg-logo="https://imgur.com/HqWfDQ2.png" group-title="ELETRICIDADE",VOCÊ DEVE LIGAR O NEUTRO NO TERRA! MESMO QUE O QUADRO (QDC) NÃO TENHA IDR NEM DPS
https://files.catbox.moe/6uespv.mp4

#EXTINF:-1 tvg-id="TVAntena10(Portuguese).br" tvg-name="ANTENA 10 HD" tvg-logo="https://i.imgur.com/BqzBsdm.png" group-title="PIAUÍ TV",ANTENA 10 HD
https://video01.logicahost.com.br/a10maisadap/smil:transcoder.smil/chunklist_w2123538353_b1396000.m3u8

#EXTINF:-1 tvg-id="RedeTV(Portuguese).br" tvg-name="O DIA TV" tvg-logo="https://i.imgur.com/xbPIEDD.png" group-title="PIAUÍ TV",O DIA TV
https://6836041ea1117.streamlock.net/tvodia/tvodia/chunklist_w753321210.m3u8

#EXTINF:-1 tvg-id="RedeTV(Portuguese).br" tvg-name="O DIA TV" tvg-logo="https://i.imgur.com/xbPIEDD.png" group-title="PIAUÍ TV",O DIA TV OFICIAL
https://6836041ea1117.streamlock.net/tvodia/tvodia/chunklist_w183304090.m3u8

#EXTINF:-1 tvg-id="CancaoNova(Portuguese).br" tvg-name="RÁDIO CANÇÃO NOVA - CACHOEIRA PAULISTA 89.1" tvg-logo="https://d2i9ujkx0lgi9s.cloudfront.net/account1-i1/embed/860/thumb_17627_thumbnail__836x1280px__radio_cancao_nova_-_cachoeira_paulista_89.1-poster-1696429235.png" group-title="PIAUÍ TV",RÁDIO CANÇÃO NOVA - CACHOEIRA PAULISTA 89.1
https://streaming.fox.srv.br/stream/8074

#EXTINF:-1 tvg-id="CancaoNova(Portuguese).br" tvg-name="RÁDIO CANÇÃO NOVA - CACHOEIRA PAULISTA 89.1" tvg-logo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQKz_ESX35P5Irwj18dscgpIpt1-R9NmOUYjpTaAiyY6YpnystW6ceOzcQ&s=10" group-title="PIAUÍ TV",RÁDIO CANÇÃO NOVA - CACHOEIRA PAULISTA 89.1
https://5c65286fc6ace.streamlock.net/cancaonova/radiocnova_720p/chunklist_w1982794369.m3u8

#EXTINF:-1 tvg-id="CancaoNova(Portuguese).br" tvg-name="RÁDIO CANÇÃO NOVA 96.3MHZ - CACHOEIRA PAULISTA" tvg-logo="https://d2i9ujkx0lgi9s.cloudfront.net/account1-i1/embed/1818/thumb_17627_thumbnail__836x1280px__radio_cancao_nova_-_cachoeira_paulista_96.3-poster-1696430015.png" group-title="PIAUÍ TV",RÁDIO CANÇÃO NOVA 96.3MHZ - CACHOEIRA PAULISTA
https://streaming.fox.srv.br/stream/8104

#EXTINF:-1 tvg-id="CancaoNova(Portuguese).br" tvg-name="TV CANÇÃO NOVA" tvg-logo="https://upload.wikimedia.org/wikipedia/pt/3/3f/Logotipo_da_TV_Can%C3%A7%C3%A3o_Nova.png" group-title="PIAUÍ TV",TV CANÇÃO NOVA
https://www.youtube.com/user/tvcancaonova/live

#EXTINF:-1 tvg-id="CancaoNova(src01).pt" tvg-name="TV CANÇÃO NOVA PT" tvg-logo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRNSVzyD-TnBiJSUeVfuMz4Qn5eMtxDKuluBLeddUP290Xe7WOdrtC2q_XZ&s=10" group-title="PIAUÍ TV",TV CANÇÃO NOVA PT
https://5c65286fc6ace.streamlock.net/cancaonova/CancaoNova.stream_720p/chunklist_w785649869.m3u8

#EXTINF:-1 tvg-id="TVCidadeVerde(Portuguese).br" tvg-name="TV CIDADE VERDE" tvg-logo="https://cdn.tvcidadeverde.com.br/storage/webdisco/logos/371d174f303942df3b554b0e5985c8d4.png" group-title="PIAUÍ TV",TV CIDADE VERDE
https://televisaocidadeverde.brasilstream.com.br/hls/televisaocidadeverde/index.m3u8

#EXTINF:-1 tvg-id="SBT(Portuguese).br" tvg-name="TV CIDADE VERDE PICOS" tvg-logo="https://i.imgur.com/rkGbMJL.png" group-title="PIAUÍ TV",TV CIDADE VERDE PICOS
https://stmv1.transmissaodigital.com/tvcidadeverde/tvcidadeverde/chunklist_w1496024979.m3u8

#EXTINF:-1 tvg-id="SBT(Portuguese).br" tvg-name="TV CIDADE VERDE PICOS FHD" tvg-logo="https://i.imgur.com/rkGbMJL.png" group-title="PIAUÍ TV",TV CIDADE VERDE PICOS FHD
https://stmv1.transmissaodigital.com/tvcidadeverde/tvcidadeverde/chunklist_w685970594.m3u8

#EXTINF:-1 tvg-id="SBT(Portuguese).br" tvg-name="TV CIDADE VERDE TERESINA" tvg-logo="https://i.imgur.com/rkGbMJL.png" group-title="PIAUÍ TV",TV CIDADE VERDE TERESINA
https://stmv1.transmissaodigital.com/cidadeverdenovo/cidadeverdenovo/chunklist_w1115557601.m3u8

#EXTINF:-1 tvg-id="SBT(Portuguese).br" tvg-name="TV CIDADE VERDE TERESINA HD" tvg-logo="https://i.imgur.com/rkGbMJL.png" group-title="PIAUÍ TV",TV CIDADE VERDE TERESINA HD
https://stmv1.transmissaodigital.com/cidadeverdenovo/cidadeverdenovo/chunklist_w1094170448.m3u8

#EXTINF:-1 tvg-id="Cultura(Portuguese).br" tvg-name="TV CULTURA" tvg-logo="https://lo1.in/BR/cultr.png" group-title="PIAUÍ TV",TV CULTURA
https://player-tvcultura.stream.uol.com.br/live/tvcultura_lsd.m3u8

#EXTINF:-1 tvg-id="TVAntena10(Portuguese).br" tvg-name="TV GALLO" tvg-logo="https://i.imgur.com/Go7equc.png" group-title="PIAUÍ TV",TV GALLO
https://5c483b9d1019c.streamlock.net/8202/8202/chunklist_w974707802.m3u8
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