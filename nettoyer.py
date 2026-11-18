"""nettoyer.py - Efface les releases (videos) dont l'heure d'effacement est passee (18/11/2026)."""
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

API = f"https://api.github.com/repos/{os.environ['DEPOT']}"
ENTETES = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json",
           "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "nettoyage-videos"}


def appel(methode, url):
    req = urllib.request.Request(url, method=methode, headers=ENTETES)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            texte = r.read().decode("utf-8")
            return json.loads(texte) if texte else {}
    except urllib.error.HTTPError as e:
        if e.code in (404, 422):
            return {}
        raise


def main():
    maintenant = datetime.now(timezone.utc)
    effaces = 0
    for rel in appel("GET", f"{API}/releases?per_page=100") or []:
        try:
            quand = json.loads(rel.get("body") or "{}").get("supprimer_apres")
        except ValueError:
            continue
        if quand and datetime.fromisoformat(quand.replace("Z", "+00:00")) < maintenant:
            appel("DELETE", f"{API}/releases/{rel['id']}")
            appel("DELETE", f"{API}/git/refs/tags/{rel['tag_name']}")
            effaces += 1
            print(f"efface : {rel.get('name')}")
    print(f"{effaces} video(s) effacee(s).")


if __name__ == "__main__":
    main()
