#!/usr/bin/env python3
"""
Servidor Local PREXIA con Persistencia Automática en Git.
Sirve todo el portal web y expone endpoints REST para leer y guardar la base de datos
de usuarios/niveles directamente en `data/prexia-users-db.json` y crear commits en Git.

Uso:
  python3 scripts/servidor_prexia_git.py
  Luego abrir: http://localhost:8080/site/pages/plataforma-prexia.html
"""

import http.server
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "prexia-users-db.json"
PORT = int(os.environ.get("PREXIA_PORT", "8080"))


def run_git(args):
    try:
        res = subprocess.run(
            ["git"] + args,
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            timeout=15,
        )
        return {
            "ok": res.returncode == 0,
            "code": res.returncode,
            "stdout": res.stdout.strip(),
            "stderr": res.stderr.strip(),
        }
    except Exception as exc:
        return {"ok": False, "code": -1, "stdout": "", "stderr": str(exc)}


class PrexiaGitHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/api/git-status"):
            branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
            last_commit = run_git(["log", "-1", "--pretty=format:%h · %s (%cr)"])
            status = run_git(["status", "-s", "data/prexia-users-db.json"])
            payload = {
                "ok": True,
                "serverMode": "local-git",
                "branch": branch.get("stdout", "main"),
                "lastCommit": last_commit.get("stdout", ""),
                "dirty": bool(status.get("stdout", "")),
                "dbFile": "data/prexia-users-db.json",
            }
            self._send_json(200, payload)
            return

        if self.path.startswith("/api/db"):
            if DB_PATH.exists():
                data = json.loads(DB_PATH.read_text(encoding="utf-8"))
                self._send_json(200, data)
            else:
                self._send_json(404, {"ok": False, "error": "DB file not found"})
            return

        super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/save-git"):
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length).decode("utf-8")
                body = json.loads(raw)
                db_data = body.get("db")
                commit_msg = body.get(
                    "commitMessage",
                    f"chore(poa): actualizar progreso y niveles PREXIA ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
                )
                do_commit = body.get("commit", True)
                do_push = body.get("push", False)

                if not db_data or "usuarios" not in db_data:
                    self._send_json(400, {"ok": False, "error": "Datos de base de datos inválidos"})
                    return

                DB_PATH.parent.mkdir(parents=True, exist_ok=True)
                DB_PATH.write_text(
                    json.dumps(db_data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )

                git_result = {"savedFile": True, "committed": False, "pushed": False}
                if do_commit:
                    add_res = run_git(["add", "data/prexia-users-db.json"])
                    commit_res = run_git(["commit", "-m", commit_msg])
                    git_result["add"] = add_res
                    git_result["commit"] = commit_res
                    git_result["committed"] = commit_res["ok"]

                    if do_push and commit_res["ok"]:
                        push_res = run_git(["push"])
                        git_result["push"] = push_res
                        git_result["pushed"] = push_res["ok"]

                last_commit = run_git(["log", "-1", "--pretty=format:%h · %s (%cr)"])
                git_result["lastCommit"] = last_commit.get("stdout", "")
                self._send_json(200, {"ok": True, "git": git_result})
            except Exception as exc:
                self._send_json(500, {"ok": False, "error": str(exc)})
            return

        self._send_json(404, {"ok": False, "error": "Ruta no encontrada"})

    def _send_json(self, status_code, payload):
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


if __name__ == "__main__":
    print(f"============================================================")
    print(f" Servidor PREXIA POA + Git activo en: http://localhost:{PORT}")
    print(f" Plataforma: http://localhost:{PORT}/site/pages/plataforma-prexia.html")
    print(f" Base de datos Git: {DB_PATH}")
    print(f"============================================================")
    with http.server.ThreadingHTTPServer(("", PORT), PrexiaGitHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")
            sys.exit(0)
