#!/usr/bin/env python3
"""
ibo-audit: SEO-чекер для ibo.ieml.ru
Проверяет title, description, keywords, H1/H2, canonical, OG-теги.
Использование:
    python3 audit.py                          # дефолтный список страниц
    python3 audit.py <url1> <url2> ...        # конкретные URL
    python3 audit.py --out report.md          # сохранить markdown-отчёт
Зависимости: pip install httpx beautifulsoup4
"""

import argparse
import sys
import time
from dataclasses import dataclass, field
from datetime import date

try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Установите зависимости: pip install httpx beautifulsoup4")

BASE = "https://ibo.ieml.ru"

# Дефолтный список страниц: главная + кластеры + служебные
DEFAULT_PAGES = {
    "Главная": f"{BASE}/ru/",
    "О нас": f"{BASE}/ru/o-nas/about/",
    "MBA": f"{BASE}/ru/educational_programs/mba/",
    "Госзакупки": f"{BASE}/ru/educational_programs/zakupki/",
    "Оценочная деятельность": f"{BASE}/ru/educational_programs/appraisa/",
    "Педагогика": f"{BASE}/ru/educational_programs/pedagogy/",
    "Охрана труда": f"{BASE}/ru/educational_programs/safety/",
    "IT и нейросети": f"{BASE}/ru/educational_programs/cit/",
    "Экономика и менеджмент": f"{BASE}/ru/educational_programs/economy-management/",
    "Гостеприимство": f"{BASE}/ru/educational_programs/hospitality/",
    "БАС": f"{BASE}/ru/educational_programs/bas/",
    "Культура и искусство": f"{BASE}/ru/educational_programs/cultureart/",
    "Психология": f"{BASE}/ru/educational_programs/psychology/",
    "Студентам": f"{BASE}/ru/educational_programs/students/",
    "Онлайн-обучение": f"{BASE}/ru/online/",
}

TITLE_SOFT_LIMIT = 60
TITLE_HARD_LIMIT = 70
DESC_MIN, DESC_MAX = 50, 160
BROKEN_KEYWORD_CHARS = ("{", "}", "$")
REQUEST_DELAY_SEC = 1.0

OK, WARN, CRIT = "✅", "🟡", "🔴"


@dataclass
class PageResult:
    name: str
    url: str
    status_code: int = 0
    title: str = ""
    description: str = ""
    keywords: str = ""
    h1: list = field(default_factory=list)
    h2_count: int = 0
    canonical: str = ""
    og_title: str = ""
    og_description: str = ""
    error: str = ""
    issues: list = field(default_factory=list)


def fetch(url: str) -> PageResult:
    r = PageResult(name="", url=url)
    try:
        resp = httpx.get(
            url,
            follow_redirects=True,
            timeout=20,
            headers={"User-Agent": "ibo-audit/1.0 (+seo self-check)"},
        )
        r.status_code = resp.status_code
        soup = BeautifulSoup(resp.text, "html.parser")

        if soup.title and soup.title.string:
            r.title = soup.title.string.strip()

        def meta(name=None, prop=None):
            tag = soup.find("meta", attrs={"name": name} if name else {"property": prop})
            return (tag.get("content") or "").strip() if tag else ""

        r.description = meta(name="description")
        r.keywords = meta(name="keywords")
        r.og_title = meta(prop="og:title")
        r.og_description = meta(prop="og:description")

        canonical = soup.find("link", attrs={"rel": "canonical"})
        r.canonical = (canonical.get("href") or "").strip() if canonical else ""

        r.h1 = [h.get_text(strip=True) for h in soup.find_all("h1")]
        r.h2_count = len(soup.find_all("h2"))
    except Exception as e:  # noqa: BLE001
        r.error = str(e)
    return r


def analyze(results: list[PageResult]) -> None:
    # дубли title считаем по всей выборке
    title_counts: dict[str, int] = {}
    for r in results:
        if r.title:
            title_counts[r.title] = title_counts.get(r.title, 0) + 1

    for r in results:
        if r.error:
            r.issues.append(f"{CRIT} ошибка запроса: {r.error}")
            continue
        if r.status_code != 200:
            r.issues.append(f"{CRIT} HTTP {r.status_code}")

        # title
        if not r.title:
            r.issues.append(f"{CRIT} title отсутствует")
        else:
            if title_counts.get(r.title, 0) > 1:
                r.issues.append(f"{CRIT} title-дубль ({title_counts[r.title]} страниц)")
            if len(r.title) > TITLE_HARD_LIMIT:
                r.issues.append(f"{WARN} title длинный: {len(r.title)} симв. (лимит {TITLE_SOFT_LIMIT})")
            elif len(r.title) > TITLE_SOFT_LIMIT:
                r.issues.append(f"{WARN} title {len(r.title)} симв. (мягкий лимит {TITLE_SOFT_LIMIT})")

        # description
        if not r.description:
            r.issues.append(f"{CRIT} нет meta description")
        elif not (DESC_MIN <= len(r.description) <= DESC_MAX):
            r.issues.append(f"{WARN} description {len(r.description)} симв. (норма {DESC_MIN}–{DESC_MAX})")

        # keywords
        if not r.keywords:
            r.issues.append(f"{WARN} нет keywords")
        elif any(ch in r.keywords for ch in BROKEN_KEYWORD_CHARS):
            r.issues.append(f"{CRIT} keywords сломаны (мусорные символы): «{r.keywords[:40]}»")

        # заголовки
        if len(r.h1) == 0:
            r.issues.append(f"{CRIT} нет H1")
        elif len(r.h1) > 1:
            r.issues.append(f"{CRIT} H1×{len(r.h1)} — должен быть один")
        if r.h2_count < 2:
            r.issues.append(f"{WARN} мало H2 ({r.h2_count})")

        # canonical / OG
        if not r.canonical:
            r.issues.append(f"{WARN} нет canonical")
        if not r.og_title or not r.og_description:
            r.issues.append(f"{WARN} неполные OG-теги")


def print_console(results: list[PageResult]) -> None:
    for r in results:
        status = OK if not r.issues else (CRIT if any(CRIT in i for i in r.issues) else WARN)
        print(f"\n{status} {r.name or r.url}")
        print(f"   URL: {r.url}")
        if r.title:
            print(f"   Title ({len(r.title)}): {r.title[:80]}")
        h1_preview = r.h1[0][:60] if r.h1 else "—"
        print(f"   H1×{len(r.h1)} «{h1_preview}» | H2×{r.h2_count}")
        for issue in r.issues:
            print(f"   {issue}")
        if not r.issues:
            print(f"   {OK} проблем не найдено")


def write_markdown(results: list[PageResult], path: str) -> None:
    lines = [
        f"# SEO-Аудит — ibo.ieml.ru",
        "",
        f"**Дата:** {date.today().strftime('%d.%m.%Y')}  ",
        f"**Метод:** ibo-audit (httpx + BeautifulSoup), {len(results)} страниц  ",
        "**SEO-шаблон:** [SEO-TEMPLATES.md](SEO-TEMPLATES.md)",
        "",
        "---",
        "",
        "## Технический аудит (meta-теги)",
        "",
        "| # | Страница | URL | Title (len) | H1 | H2 | Desc | Keywords | Проблемы |",
        "|---|----------|-----|-------------|----|----|------|----------|----------|",
    ]
    for i, r in enumerate(results, 1):
        title_cell = f"{len(r.title)} симв." if r.title else "❌ нет"
        desc_cell = f"{OK} {len(r.description)}" if r.description else "❌ нет"
        if not r.keywords:
            kw_cell = "❌ нет"
        elif any(ch in r.keywords for ch in BROKEN_KEYWORD_CHARS):
            kw_cell = "❌ сломаны"
        else:
            kw_cell = OK
        issues_cell = "; ".join(r.issues) if r.issues else OK
        rel = r.url.replace(BASE, "")
        lines.append(
            f"| {i} | {r.name or '—'} | `{rel}` | {title_cell} | ×{len(r.h1)} | ×{r.h2_count} | {desc_cell} | {kw_cell} | {issues_cell} |"
        )

    crit_total = sum(1 for r in results if any(CRIT in i for i in r.issues))
    lines += [
        "",
        f"**Итог:** {crit_total}/{len(results)} страниц с критическими проблемами.",
        "",
        "Эталонные мета-теги для внедрения: `seo/SEO-TEMPLATES.md`, инструкции: `seo/IMPLEMENTATION-GUIDE.md`.",
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nОтчёт сохранён: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="SEO-аудит страниц ibo.ieml.ru")
    parser.add_argument("urls", nargs="*", help="URL для проверки (по умолчанию — дефолтный список)")
    parser.add_argument("--out", help="путь для markdown-отчёта")
    args = parser.parse_args()

    if args.urls:
        pages = {url: url for url in args.urls}
    else:
        pages = DEFAULT_PAGES

    results: list[PageResult] = []
    for name, url in pages.items():
        print(f"→ {url}", flush=True)
        r = fetch(url)
        r.name = name if name != url else ""
        results.append(r)
        time.sleep(REQUEST_DELAY_SEC)

    analyze(results)
    print_console(results)
    if args.out:
        write_markdown(results, args.out)


if __name__ == "__main__":
    main()
