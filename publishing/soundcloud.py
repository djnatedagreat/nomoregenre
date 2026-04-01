import base64
import json
import os
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import requests

from utils import load_config

from .provider import PublishingProvider

config = load_config()

_CACHE_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".soundcloud_token_cache.json"))
_REDIRECT_PORT = 8080
_REDIRECT_URI = f"http://localhost:{_REDIRECT_PORT}/callback"


class _CallbackHandler(BaseHTTPRequestHandler):
    code = None

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/callback":
            params = parse_qs(parsed.query)
            _CallbackHandler.code = params.get("code", [None])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization successful! You can close this tab.")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # suppress server logs


class SoundCloudProvider(PublishingProvider):

    def _load_cache(self):
        if os.path.exists(_CACHE_PATH):
            with open(_CACHE_PATH) as f:
                return json.load(f)
        return {}

    def _save_cache(self, cache):
        with open(_CACHE_PATH, "w") as f:
            json.dump(cache, f)

    def _store_tokens(self, account, data):
        cache = self._load_cache()
        cache[account] = {
            "token": data["access_token"],
            "expires_at": time.time() + data.get("expires_in", 3600),
            "refresh_token": data.get("refresh_token"),
        }
        self._save_cache(cache)
        return data["access_token"]

    def _basic_auth(self, client_id, client_secret):
        return base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    def _exchange_code(self, client_id, client_secret, code):
        response = requests.post(
            "https://secure.soundcloud.com/oauth/token",
            headers={"accept": "application/json; charset=utf-8"},
            data={"grant_type": "authorization_code", "client_id": client_id,
                  "client_secret": client_secret, "redirect_uri": _REDIRECT_URI, "code": code},
        )
        response.raise_for_status()
        return response.json()

    def _refresh(self, client_id, client_secret, refresh_token):
        response = requests.post(
            "https://secure.soundcloud.com/oauth/token",
            headers={"accept": "application/json; charset=utf-8",
                     "Authorization": f"Basic {self._basic_auth(client_id, client_secret)}"},
            data={"grant_type": "refresh_token", "client_id": client_id,
                  "client_secret": client_secret, "refresh_token": refresh_token},
        )
        response.raise_for_status()
        return response.json()

    def _authorize(self, account, client_id, client_secret):
        params = urlencode({"client_id": client_id, "redirect_uri": _REDIRECT_URI, "response_type": "code"})
        auth_url = f"https://secure.soundcloud.com/connect?{params}"

        _CallbackHandler.code = None
        server = HTTPServer(("localhost", _REDIRECT_PORT), _CallbackHandler)

        print(f"  Opening browser for SoundCloud authorization...")
        print(f"  If the browser doesn't open, visit: {auth_url}")
        webbrowser.open(auth_url)
        server.handle_request()

        if not _CallbackHandler.code:
            raise Exception("Authorization failed: no code received.")

        data = self._exchange_code(client_id, client_secret, _CallbackHandler.code)
        print("  Authorized and token cached.")
        return self._store_tokens(account, data)

    def _token(self, account):
        cache = self._load_cache()
        entry = cache.get(account, {})

        # Return cached token if still valid (with 60s buffer)
        if entry.get("token") and entry.get("expires_at", 0) > time.time() + 60:
            return entry["token"]

        prefix = f"SOUNDCLOUD_{account.upper()}"
        client_id = config.get(f"{prefix}_CLIENT_ID")
        client_secret = config.get(f"{prefix}_SECRET")

        missing = [k for k, v in [(f"{prefix}_CLIENT_ID", client_id), (f"{prefix}_SECRET", client_secret)] if not v]
        if missing:
            raise Exception(f"Missing SoundCloud credentials in .env: {', '.join(missing)}")

        # Try refresh token before falling back to browser auth
        if entry.get("refresh_token"):
            try:
                data = self._refresh(client_id, client_secret, entry["refresh_token"])
                return self._store_tokens(account, data)
            except Exception:
                pass

        return self._authorize(account, client_id, client_secret)

    def update_sharing(self, external_id, sharing, account=None):
        if not account:
            raise Exception("No account specified. Use --account <name>.")
        token = self._token(account)
        response = requests.put(
            f"https://api.soundcloud.com/tracks/{external_id}",
            headers={"Authorization": f"OAuth {token}"},
            data={"track[sharing]": sharing},
        )
        response.raise_for_status()
        return response.json()

    def publish(self, mp3_path, title, sharing="private", description=None, account=None):
        if not account:
            raise Exception("No account specified. Use --account <name>.")
        print("  Authenticating with SoundCloud...")
        token = self._token(account)
        print("  Authenticated.")

        print("  Uploading to SoundCloud...")
        data = {"track[title]": title, "track[sharing]": sharing}
        if description:
            data["track[description]"] = description

        with open(mp3_path, "rb") as f:
            response = requests.post(
                "https://api.soundcloud.com/tracks",
                headers={"Authorization": f"OAuth {token}"},
                files={"track[asset_data]": f},
                data=data,
            )
        response.raise_for_status()
        data = response.json()
        print(f"  Published: {data['permalink_url']}")
        return {
            "external_id": str(data["id"]),
            "url": data["permalink_url"],
            "urn": data["uri"],
        }
