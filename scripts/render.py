#!/usr/bin/env python3
"""
极简笔记风小红书卡片渲染脚本
用 CSS 多列布局让浏览器自动按行边界分页，Pillow 切图加水印。

用法:
    python render.py <文本文件> -b <账号名> -o <输出目录>

依赖:
    pip install playwright pillow
    playwright install chromium
"""

import argparse
import asyncio
import re
import sys
import tempfile
from pathlib import Path

try:
    from playwright.async_api import async_playwright
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("请运行: pip install playwright pillow && playwright install chromium")
    sys.exit(1)

CARD_W = 1080
CARD_H = 1440
PAD_X  = 84    # 左右内边距
PAD_TOP = 80   # 上内边距
BRAND_H = 24   # 账号名字体大小
BRAND_MB = 56  # 账号名下边距
PAD_BOT = 72   # 下内边距
PAGENUM_H = 26 # 页码高度
PAGENUM_MT = 40 # 页码上边距

# 内容列宽 = 卡片宽 - 左右padding
COL_W = CARD_W - PAD_X * 2
# 内容区可用高度
CONTENT_H = CARD_H - PAD_TOP - BRAND_H - BRAND_MB - PAD_BOT - PAGENUM_MT - PAGENUM_H


def text_to_html(text: str) -> str:
    paragraphs = [p.strip() for p in text.strip().split('\n\n') if p.strip()]
    parts = []
    for p in paragraphs:
        p = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', p)
        p = p.replace('\n', '<br>')
        parts.append(f'<p>{p}</p>')
    return '\n'.join(parts)


def make_column_html(content_html: str) -> str:
    return f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ background:#fff; }}
.wrap {{
  width: {COL_W}px;
  height: {CONTENT_H}px;
  column-width: {COL_W}px;
  column-fill: auto;
  column-gap: 0;
  font-family: 'Noto Sans SC','PingFang SC',sans-serif;
  font-size: 32px;
  color: #1a1a1a;
  line-height: 1.9;
  font-weight: 400;
}}
.wrap p {{ margin-bottom: 36px; }}
.wrap p:last-child {{ margin-bottom: 0; }}
.wrap strong {{ font-weight:700; color:#111; }}
</style>
</head><body>
<div class="wrap">{content_html}</div>
</body></html>"""


async def render_columns(content_html: str) -> tuple[Image.Image, int]:
    """渲染多列布局，返回截图和列数"""
    html = make_column_html(content_html)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # viewport 设宽一点容纳多列
        page = await browser.new_page(viewport={'width': COL_W * 20, 'height': CONTENT_H})

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False,
                                         mode='w', encoding='utf-8') as f:
            f.write(html)
            tmp = f.name

        await page.goto(f'file:///{tmp}', wait_until='networkidle')
        await page.wait_for_timeout(500)  # 等字体加载

        # 获取实际列数
        col_count = await page.evaluate("""() => {
            const w = document.querySelector('.wrap');
            return Math.round(w.scrollWidth / w.clientWidth);
        }""")

        col_count = max(1, col_count)

        # 截图整个多列区域
        screenshot_bytes = await page.screenshot(
            clip={'x': 0, 'y': 0, 'width': COL_W * col_count, 'height': CONTENT_H}
        )
        await browser.close()

    import os
    os.unlink(tmp)

    img = Image.open(__import__('io').BytesIO(screenshot_bytes))
    return img, col_count


def make_card(col_img: Image.Image, col_idx: int, total: int,
              brand: str) -> Image.Image:
    """把一列内容合成到完整卡片上"""
    card = Image.new('RGB', (CARD_W, CARD_H), '#ffffff')
    draw = ImageDraw.Draw(card)

    # 尝试加载字体，失败用默认
    try:
        font_brand   = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', BRAND_H)
        font_pagenum = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', PAGENUM_H)
    except Exception:
        font_brand   = ImageFont.load_default()
        font_pagenum = ImageFont.load_default()

    # 账号名
    if brand:
        draw.text((PAD_X, PAD_TOP), brand, fill='#c0c0c0', font=font_brand)

    # 粘贴内容列
    content_y = PAD_TOP + BRAND_H + BRAND_MB
    col_x = col_idx * COL_W
    col_crop = col_img.crop((col_x, 0, col_x + COL_W, CONTENT_H))
    card.paste(col_crop, (PAD_X, content_y))

    # 页码
    if total > 1:
        page_label = f'{col_idx + 1:02d}'
        bbox = draw.textbbox((0, 0), page_label, font=font_pagenum)
        text_w = bbox[2] - bbox[0]
        page_x = CARD_W - PAD_X - text_w
        page_y = CARD_H - PAD_BOT - PAGENUM_H
        draw.text((page_x, page_y), page_label, fill='#dddddd', font=font_pagenum)

    return card


async def main(input_file: str, output_dir: str, brand: str):
    content = Path(input_file).read_text(encoding='utf-8')
    content_html = text_to_html(content)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print('渲染中...')
    col_img, total = await render_columns(content_html)

    for i in range(total):
        card = make_card(col_img, i, total, brand)
        out = output_path / f'card_{i+1}.png'
        card.save(out)
        print(f'[done] {out}')

    print(f'done: {total} cards')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('-o', '--output-dir', default='.')
    parser.add_argument('-b', '--brand', default='')
    args = parser.parse_args()
    asyncio.run(main(args.input, args.output_dir, args.brand))
