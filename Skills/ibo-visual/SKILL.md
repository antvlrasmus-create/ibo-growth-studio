# ibo-visual — промпт-шаблоны для генерации обложек ИБОиЦТ

## Назначение
Скилл для генерации обложек статей, анонсов программ и постов соцсетей для **ibo.ieml.ru** в едином фирменном стиле. Единый источник правды по визуалу — `brand/BRAND-GUIDE.md`. Этот скилл переводит бренд-гайд в готовые промпты для генерации изображений.

## Когда использовать
- Обложка для статьи блога или анонса курса
- Карточка программы для соцсетей (1:1)
- Баннер для лендинга или презентации (16:9)
- Иллюстрация для email-рассылки

## Фирменный стиль (из BRAND-GUIDE.md, обязательно)
- **Палитра:** белый / светло-серый фон (#f8f9fa), синий акцент (#2563eb), тёмно-синий (#1e40af), тёмно-серый текст (#1f2937)
- **Графика:** плоская векторная, минимализм, без визуального шума
- **Композиция:** одна главная карточка/сцена, мягкие тени, много воздуха
- **Заголовки:** крупные, русские, читаемые в миниатюре
- **Логотип:** сова с книгой в правом верхнем углу (добавляется постпроцессом, не генерацией)
- **Форматы:** 1:1 (соцсети) или 16:9 (статьи/презентации)

## Базовый промпт (шаблон)

```
Flat vector illustration for an education institute cover, clean light background (#f8f9fa),
primary accent color educational blue (#2563eb), dark blue secondary (#1e40af),
minimalist composition with one central scene, soft shadows, lots of whitespace,
no text, no logos, no watermark, professional academic style, [СЮЖЕТ], [ФОРМАТ]
```

- `[СЮЖЕТ]` — из таблицы кластеров ниже
- `[ФОРМАТ]` — `square 1:1 aspect ratio` или `wide 16:9 aspect ratio`
- Текст заголовка НЕ генерировать в изображении — накладывается поверх версткой

## Сюжеты по кластерам программ

| Кластер | Сюжет для промпта |
|---------|-------------------|
| MBA | confident business leader at a strategy desk with growth charts and chess pieces |
| Госзакупки | official documents, contract with seal, government building silhouette, checklist |
| Оценочная деятельность | magnifying glass over a house model, calculator, property blueprint |
| Педагогика | teacher at a whiteboard with students, books, graduation cap, warm classroom scene |
| Охрана труда | worker in hard hat and safety vest, shield icon, safety checklist |
| IT и нейросети | laptop with neural network visualization, digital shield, circuit patterns |
| Экономика и менеджмент | balanced scales, bar charts, briefcase, organizational diagram |
| Гостеприимство | tour guide with a flag near landmark silhouettes, hotel reception bell, suitcase |
| БАС | quadcopter drone flying over a field, remote controller, flight path lines |
| Культура и искусство | theater masks, open book, museum columns, paint palette |
| Психология | two people in conversation, head silhouette with gears and heart, calm scene |
| Студентам | young students collaborating, speech bubbles, lightbulb, career ladder |

## Готовый пример (MBA, 16:9)

```
Flat vector illustration for an education institute cover, clean light background (#f8f9fa),
primary accent color educational blue (#2563eb), dark blue secondary (#1e40af),
minimalist composition with one central scene, soft shadows, lots of whitespace,
no text, no logos, no watermark, professional academic style,
confident business leader at a strategy desk with growth charts and chess pieces,
wide 16:9 aspect ratio
```

## Запреты (из BRAND-GUIDE.md)
- не смешивать стили на одной обложке
- не перегружать композицию деталями
- не использовать мемы, сленг, неформальный визуал
- не генерировать текст внутри изображения (артефакты кириллицы)
- не использовать фиолетовый/розовый как доминирующие цвета — только синяя палитра
- не ставить логотип на зашумлённый фон

## Workflow
1. Определить кластер и формат (1:1 или 16:9)
2. Собрать промпт: базовый шаблон + сюжет + формат
3. Сгенерировать изображение
4. Наложить заголовок (крупный, тёмно-серый #1f2937 или синий #2563eb) и логотип-сову в правом верхнем углу
5. Проверить читаемость заголовка в миниатюре
6. Сохранять готовые ассеты в `brand/covers/` (создать при первом использовании)
