"""On-display QA: open the app with #tour in Firefox on :0 and grab a screenshot 15 s into each tour step (step name read from the window title)."""
import time, subprocess, os, re
from PIL import ImageGrab
env = dict(os.environ, DISPLAY=":0")
subprocess.run("setsid -f firefox --new-window 'http://localhost:8770/?v=03b#tour' >/dev/null 2>&1", shell=True, env=env)
def title():
    return subprocess.run("for i in $(xprop -root _NET_CLIENT_LIST | sed 's/.*# //; s/,//g'); do xprop -id $i _NET_WM_NAME; done", shell=True, env=env, capture_output=True, text=True).stdout
    return subprocess.run(["xprop", "-id", w, "WM_NAME"], env=env, capture_output=True, text=True).stdout
seen, k, t0 = set(), 0, time.time()
while time.time() - t0 < 600:
    m = re.search(r"TOUR (ERR )?([\w-]+)[^\n]*", title())
    if m and m.group(2) not in seen:
        seen.add(m.group(2)); time.sleep(15)
        ImageGrab.grab(xdisplay=":0").save(f"shots/v03-{k:02d}-{m.group(2)}.png"); print(k, m.group(0), round(time.time() - t0), flush=True); k += 1
        if m.group(2) == "end": break
    time.sleep(0.5)
