import gzip
import shutil
import requests
import xml.etree.ElementTree as ET
from pathlib import Path

# =============================
# CONFIG
# =============================

EPG_SOURCES = [
    "https://m3u4u.com/epg/jq2zy9epr3bwxmgwyxr5",
    "https://m3u4u.com/epg/3wk1y24kx7uzdevxygz7",
    "https://m3u4u.com/epg/782dyqdrqkh1xegen4zp",
    "https://www.open-epg.com/files/brazil1.xml.gz",
    "https://www.open-epg.com/files/brazil2.xml.gz",
    "https://www.open-epg.com/files/brazil3.xml.gz",
    "https://www.open-epg.com/files/brazil4.xml.gz",
    "https://www.open-epg.com/files/portugal1.xml.gz",
    "https://www.open-epg.com/files/portugal2.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_BR1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_PT1.xml.gz"
]

OUTPUT = Path("epg.xml")
TMP = Path("tmp_epg")
TMP.mkdir(exist_ok=True)

# =============================
# CANAIS USADOS (tvg-id)
# =============================

USED_CHANNELS = {
    "TVAntena10.br",
    "Cultura.br",
    "tvassembleia",
    "tv_cancao_nova"
}

# =============================
# DOWNLOAD + MERGE
# =============================

root = ET.Element("tv")

for src in EPG_SOURCES:
    name = src.split("/")[-1]
    gz = TMP / name
    xml = TMP / name.replace(".gz", "")

    print("⬇️", src)
    r = requests.get(src, timeout=60)
    gz.write_bytes(r.content)

    with gzip.open(gz, "rb") as f_in, open(xml, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    tree = ET.parse(xml)
    tv = tree.getroot()

    # Channels
    for ch in tv.findall("channel"):
        if ch.attrib.get("id") in USED_CHANNELS:
            root.append(ch)

    # Programmes
    for pr in tv.findall("programme"):
        if pr.attrib.get("channel") in USED_CHANNELS:
            root.append(pr)

# =============================
# SAVE
# =============================

ET.ElementTree(root).write(
    OUTPUT,
    encoding="utf-8",
    xml_declaration=True
)

print("✅ epg.xml gerado com sucesso")