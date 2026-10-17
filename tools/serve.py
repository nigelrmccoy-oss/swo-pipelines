"""Local dev server for SWO-PIPELINES: binds 127.0.0.1 only and refuses /data/private/ and dot-paths to anything but a localhost Host header.
Usage: python3 tools/serve.py [port]   (default 8770). Ctrl-C to stop."""
import http.server, sys, os, functools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class H(http.server.SimpleHTTPRequestHandler):
    def _blocked(self):
        p = self.path.split("?", 1)[0].lower()
        host = (self.headers.get("Host") or "").split(":")[0]
        if "/." in p: return True                      # .git, .env, ...
        if p.startswith("/data/private/") and host not in ("127.0.0.1", "localhost"): return True
        return False
    def do_GET(self):
        if self._blocked(): return self.send_error(404)
        return super().do_GET()
    def do_HEAD(self):
        if self._blocked(): return self.send_error(404)
        return super().do_HEAD()
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8770
srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(H, directory=ROOT))
print(f"serving {ROOT} on http://127.0.0.1:{port}/ (localhost only)", flush=True)
try: srv.serve_forever()
except KeyboardInterrupt: pass
