"""On-display QA: open the app with #tour in Firefox on :0 and grab a screenshot 15 s into each tour step (step name read from the window title).
Usage: python3 tools/shoot_tour.py [prefix] [url]   (default url uses ?nohome so no private data appears in screenshots)"""
import time, subprocess, os, re, sys
from PIL import ImageGrab
prefix = sys.argv[1] if len(sys.argv) > 1 else "tour"
url = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8770/?nohome#tour"
os.makedirs("shots", exist_ok=True)
env = dict(os.environ, DISPLAY=os.environ.get("DISPLAY", ":0"))
subprocess.run(["setsid", "-f", "firefox", "--new-window", url], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def title():
    return subprocess.run("for i in $(xprop -root _NET_CLIENT_LIST | sed 's/.*# //; s/,//g'); do xprop -id $i _NET_WM_NAME; done", shell=True, env=env, capture_output=True, text=True).stdout
seen, k, t0 = set(), 0, time.time()
while time.time() - t0 < 600:
    m = re.search(r"TOUR (ERR )?([\w-]+)[^\n]*", title())
    if m and m.group(2) not in seen:
        seen.add(m.group(2)); time.sleep(15)
        ImageGrab.grab(xdisplay=env["DISPLAY"]).save(f"shots/{prefix}-{k:02d}-{m.group(2)}.png"); print(k, m.group(0), round(time.time() - t0), flush=True); k += 1
        if m.group(2) == "end": break
    time.sleep(0.5)
