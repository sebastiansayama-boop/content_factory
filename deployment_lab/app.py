from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def _request_log(self, status):
        cf_ray = self.headers.get("CF-Ray", "-")
        host = self.headers.get("Host", "-")
        print(
            f"request method={self.command} path={self.path} status={status} "
            f"host={host} cf_ray={cf_ray}",
            flush=True,
        )

    def do_GET(self):
        if self.path == "/health":
            body = json.dumps({"status": "ok", "service": "deployment-probe"}).encode()
            self._send(200, body, "application/json; charset=utf-8")
            self._request_log(200)
            return
        if self.path == "/":
            body = b"deployment-probe: OK\n"
            self._send(200, body, "text/plain; charset=utf-8")
            self._request_log(200)
            return
        body = b"not found\n"
        self._send(404, body, "text/plain; charset=utf-8")
        self._request_log(404)

    def do_HEAD(self):
        if self.path == "/health":
            body = json.dumps({"status": "ok", "service": "deployment-probe"}).encode()
            self._send(200, body, "application/json; charset=utf-8")
            self._request_log(200)
            return
        if self.path == "/":
            body = b"deployment-probe: OK\n"
            self._send(200, body, "text/plain; charset=utf-8")
            self._request_log(200)
            return
        body = b"not found\n"
        self._send(404, body, "text/plain; charset=utf-8")
        self._request_log(404)


port = int(os.environ.get("PORT", "10000"))
server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
print(f"deployment-probe listening on 0.0.0.0:{port}", flush=True)
server.serve_forever()
