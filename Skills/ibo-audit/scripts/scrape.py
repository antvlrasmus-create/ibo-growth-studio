#!/usr/bin/env python3
"""
ibo-audit: скрапер страниц ibo.ieml.ru → seo/scraped/*.md
Использование:
    python3 scrape.py                                          # дефолтный список
    python3 scrape.py --url https://ibo.ieml.ru/ru/ --name home
Зависимости: pip install httpx beautifulsoup4
"""

import argparse
import sys
import time
from pathlib import Path

try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Установите зависимости: pip install httpx beautifulsoup4")

BASE = "https://ibo.ieml.ru"
OUT_DIR = Path(__file__).resolve().parents[3] / "seo" / "scraped"
REQUEST_DELAY_SEC = 1.0

DEFAULT_PAGES = {
    "home": f"{BASE}/ru/",
    "about": f"{BASE}/ru/o-nas/about/",
    "mba": f"{BASE}/ru/educational_programs/mba/",
    "zakupki": f"{BASE}/ru/educational_programs/zakupki/",
    "appraisa": f"{BASE}/ru/educational_programs/appraisa/",
    "pedagogy": f"{BASE}/ru/educational_programs/pedagogy/",
    "safety": f"{BASE}/ru/educational_programs/safety/",
    "it": f"{BASE}/ru/educational_programs/cit/",
    "economy-management": f"{BASE}/ru/educational_programs/economy-management/",
    "hospitality": f"{BASE}/ru/educational_programs/hospitality/",
    "bas": f"{BASE}/ru/educational_programs/bas/",
    "cultureart": f"{BASE}/ru/educational_programs/cultureart/",
    "psychology": f"{BASE}/ru/educational_programs/psychology/",
    "students": f"{BASE}/ru/educational_programs/students/",
    "online": f"{BASE}/ru/online/",
}


def scrape(url: str, name: str) -> bool:
    try:
        resp = httpx.get(
            url,
            follow_redirects=True,
            timeout=20,
            headers={"User-Agent": "ibo-audit/1.0 (+seo self-check)"},
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "iframe"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        lines = [title, ""]
        seen: set[str] = set()
        for el in soup.find_all(["h1", "h2", "h3", "p", "li"]):
            text = el.get_text(" ", strip=True)
            if text and text not in seen and len(text) > 2:
                seen.add(text)
                lines.append(text)

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = OUT_DIR / f"{name}.md"
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"✅ {name}: {len(lines)} строк → {out_path}")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"🔴 {name}: {e}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Скрапер страниц ibo.ieml.ru")
    parser.add_argument("--url", help="один URL для скрапа")
    parser.add_argument("--name", help="имя выходного файла (без .md)")
    args = parser.parse_args()

    if args.url:
        name = args.name or args.url.rstrip("/").rsplit("/", 1)[-1] or "page"
        scrape(args.url, name)
        return

    for name, url in DEFAULT_PAGES.items():
        scrape(url, name)
        time.sleep(REQUEST_DELAY_SEC)


if __name__ == "__main__":
    main()
