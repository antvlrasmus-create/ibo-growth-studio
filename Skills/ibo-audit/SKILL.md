# ibo-audit — автоматический SEO-чекер для ibo.ieml.ru

## Назначение
Скилл для аудита страниц сайта **ibo.ieml.ru**: проверяет мета-теги (title, description, keywords), структуру заголовков (H1/H2), ищет типовые проблемы (дубли title, сломанные keywords с символом `{`, отсутствие description) и сверяет с эталонами из `seo/SEO-TEMPLATES.md`.

## Когда использовать
- Появились новые страницы на сайте → прогнать аудит
- Разработчики внедрили мета-теги из `seo/IMPLEMENTATION-GUIDE.md` → проверить внедрение
- Периодическая проверка (раз в месяц), нет ли регрессий
- Нужно спарсить контент страниц для анализа → `scripts/scrape.py`

## Скрипты

### 1. `scripts/audit.py` — SEO-аудит страниц

```bash
# аудит дефолтного списка страниц (12 кластеров + служебные)
python3 Skills/ibo-audit/scripts/audit.py

# аудит конкретных URL
python3 Skills/ibo-audit/scripts/audit.py https://ibo.ieml.ru/ru/ https://ibo.ieml.ru/ru/educational_programs/mba/

# сохранить отчёт в markdown
python3 Skills/ibo-audit/scripts/audit.py --out seo/SEO-AUDIT-REPORT-NEW.md
```

Что проверяет для каждой страницы:
| Проверка | Критерий | Статус при нарушении |
|----------|----------|----------------------|
| Title есть | не пустой | 🔴 |
| Title длина | ≤ 60 символов (мягкий лимит 70) | 🟡 |
| Title дубль | не совпадает с title главной / других страниц | 🔴 |
| Meta description | есть, 50–160 символов | 🔴 нет / 🟡 длина |
| Keywords | есть, без мусорных символов (`{`, `}`, `$`) | 🔴 сломаны / 🟡 нет |
| H1 | ровно один | 🔴 0 или >1 |
| H2 | ≥ 2 на контентных страницах | 🟡 |
| Canonical | присутствует | 🟡 |
| OG-теги | og:title, og:description | 🟡 |

Вывод: таблица в консоль + (опционально) markdown-отчёт в формате `seo/SEO-AUDIT-REPORT.md`.

### 2. `scripts/scrape.py` — скрапер страниц

```bash
# спарсить дефолтный список в seo/scraped/
python3 Skills/ibo-audit/scripts/scrape.py

# спарсить конкретный URL с именем файла
python3 Skills/ibo-audit/scripts/scrape.py --url https://ibo.ieml.ru/ru/o-nas/about/ --name about
```

Сохраняет текст страницы (title + видимый контент) в `seo/scraped/{name}.md`. Big output — всегда в `seo/scraped/`, не в корень.

## Зависимости
```bash
pip install httpx beautifulsoup4
```

## Правила
- Отчёты сохранять в `seo/`, скрап — в `seo/scraped/`
- Эталонные мета-теги — в `seo/SEO-TEMPLATES.md`; при расхождении факта с эталоном указывать оба значения
- После аудита обновить `NEXT-STEPS.md` (дата, итог, что дальше)
- Не DDOS-ить сайт: пауза ≥ 1 сек между запросами (заложено в скриптах)
