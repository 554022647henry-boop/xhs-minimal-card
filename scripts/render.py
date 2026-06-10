#!/usr/bin/env python3
"""
极简笔记风小红书卡片渲染脚本

用法:
    python render.py <文本文件> [选项]

选项:
    -o, --output-dir   输出目录（默认：当前目录）
    -b, --brand        顶部账号名（默认：空）

文本文件格式：
    - 用 --- 分隔多张卡片
    - 支持 **加粗** 语法

依赖:
    pip install playwright
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
except ImportError:
    print("缺少依赖，请运行：pip install playwright && playwright install chromium")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent.parent
TEMPLATE_PATH = SCRIPT_DIR / "assets" / "card.html"


def text_to_html(text: str) -> str:
    """将纯文本转为 HTML 段落，支持 **加粗**"""
    paragraphs = [p.strip() for p in text.strip().split('\n\n') if p.strip()]
    html_parts = []
    for p in paragraphs:
        # 处理 **加粗**
        p = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', p)
        # 段内换行转 <br>
        p = p.replace('\n', '<br>')
        html_parts.append(f'<p>{p}</p>')
    return '\n'.join(html_parts)


def split_cards(content: str) -> list[str]:
    """按 --- 分割卡片"""
    parts = re.split(r'\n---+\n', content)
    return [p.strip() for p in parts if p.strip()]


async def render_card(page, html: str, output_path: Path):
    await page.set_content(html, wait_until='networkidle')
    await page.screenshot(path=str(output_path), clip={'x': 0, 'y': 0, 'width': 1080, 'height': 1440})


async def main(input_file: str, output_dir: str, brand: str):
    content = Path(input_file).read_text(encoding='utf-8')
    cards = split_cards(content)
    template = TEMPLATE_PATH.read_text(encoding='utf-8')

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1080, 'height': 1440})

        for i, card_text in enumerate(cards, 1):
            content_html = text_to_html(card_text)
            page_label = f'{i:02d}' if len(cards) > 1 else ''

            html = template \
                .replace('{{BRAND}}', brand) \
                .replace('{{CONTENT}}', content_html) \
                .replace('{{PAGE}}', page_label)

            out_file = output_path / f'card_{i}.png'
            await render_card(page, html, out_file)
            print(f'[done] {out_file}')

        await browser.close()

    print(f'done: {len(cards)} cards')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='极简笔记风小红书卡片渲染')
    parser.add_argument('input', help='输入文本文件路径')
    parser.add_argument('-o', '--output-dir', default='.', help='输出目录')
    parser.add_argument('-b', '--brand', default='', help='顶部账号名')
    args = parser.parse_args()

    asyncio.run(main(args.input, args.output_dir, args.brand))
