"""Fetch Wikipedia wikitext infobox + plain intro for titles; saves research/wiki/<title>.json with the page URL. Backs off on 429."""
import json, sys, time, urllib.request, urllib.parse, re, os
UA = {"User-Agent": "swo-pipelines/0.3 (personal research; nig@localhost)"}
def get(params):
    u = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({**params, "format": "json", "redirects": 1})
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40))
def clean(v):
    v = re.sub(r"<ref[^>]*/>|<ref.*?</ref>", "", v)
    v = re.sub(r"\{\{convert\|([\d.,]+)\|([^|}]+)[^}]*\}\}", r"\1 \2", v)
    v = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", v)
    return re.sub(r"<br\s*/?>", "; ", v).strip()
def one(t):
    w = get({"action": "parse", "page": t, "prop": "wikitext"})
    if "parse" not in w: return print("MISSING", t)
    w = w["parse"]; x = get({"action": "query", "prop": "extracts", "exintro": 1, "explaintext": 1, "titles": w["title"]})
    intro = next(iter(x["query"]["pages"].values())).get("extract", ""); box = {}
    m = re.search(r"\{\{Infobox.*?\n\}\}", w["wikitext"]["*"], re.S)
    if m:
        for line in m.group(0).split("\n"):
            mm = re.match(r"\s*\|\s*([\w ]+?)\s*=\s*(.+)", line)
            if mm: box[mm.group(1)] = clean(mm.group(2))
    json.dump({"title": w["title"], "url": "https://en.wikipedia.org/wiki/" + w["title"].replace(" ", "_"), "infobox": box, "intro": intro[:3000]},
              open("research/wiki/" + re.sub(r"[^\w]+", "_", t) + ".json", "w"), indent=1); print("OK", t, "->", w["title"], len(box))
for t in sys.argv[1:]:
    for k in range(4):
        try: one(t); break
        except Exception as e:
            print("FAIL", t, e); time.sleep(30 if "429" in str(e) else 1)
            if "429" not in str(e): break
    time.sleep(5)
