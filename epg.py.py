import gzip
import shutil
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import re

# =============================
# CONFIG
# =============================

EPG_SOURCES = [
    {"url": "https://www.open-epg.com/files/brazil1.xml.gz", "priority": 1},
    {"url": "https://epgshare01.online/epgshare01/epg_ripper_BR1.xml.gz", "priority": 2},
    {"url": "https://www.open-epg.com/files/portugal1.xml.gz", "priority": 3}
]

OUTPUT = Path("epg.xml")
TMP = Path("tmp_epg")
TMP.mkdir(exist_ok=True)

# =============================
# CANAIS DA SUA PLAYLIST
# =============================

USED_CHANNELS = {
    "TVAntena10.br": "ANTENA 10 HD",
    "Cultura.br": "TV CULTURA",
    "tvassembleia": "TV ASSEMBLEIA PI",
    "tv_cancao_nova": "TV CANÇÃO NOVA"
}

# =============================
# NORMALIZAÇÃO
# =============================

def norm(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())

USED_NORM = {norm(v): k for k, v in USED_CHANNELS.items()}

# =============================
# MERGE INTELIGENTE
# =============================

root = ET.Element("tv")
added_channels = set()
added_programs = set()

for src in sorted(EPG_SOURCES, key=lambda x: x["priority"]):
    print("⬇️", src["url"])

    gz = TMP / src["url"].split("/")[-1]
    xml = gz.with_suffix("")

    r = requests.get(src["url"], timeout=60)
    gz.write_bytes(r.content)

    with gzip.open(gz, "rb") as f_in, open(xml, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    tree = ET.parse(xml)
    tv = tree.getroot()

    # CHANNELS
    for ch in tv.findall("channel"):
        cid = ch.attrib.get("id")
        cname = ch.findtext("display-name", "")

        match = None
        if cid in USED_CHANNELS:
            match = cid
        else:
            n = norm(cname)
            match = USED_NORM.get(n)

        if match and match not in added_channels:
            ch.attrib["id"] = match
            root.append(ch)
            added_channels.add(match)

    # PROGRAMMES
    for pr in tv.findall("programme"):
        cid = pr.attrib.get("channel")
        start = pr.attrib.get("start")
        title = pr.findtext("title", "")

        if cid not in added_channels:
            continue

        key = f"{cid}-{start}-{title}"
        if key in added_programs:
            continue

        pr.attrib["channel"] = cid
        root.append(pr)
        added_programs.add(key)

# =============================
# SAVE FINAL
# =============================

ET.ElementTree(root).write(
    OUTPUT,
    encoding="utf-8",
    xml_declaration=True
)

print("✅ epg.xml combinado gerado com sucesso")