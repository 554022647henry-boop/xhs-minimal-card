# xhs-minimal-card · 极简笔记卡片

白底纯文字风格的小红书卡片生成器，适合长文内容。

![style](https://img.shields.io/badge/style-minimal-black) ![platform](https://img.shields.io/badge/platform-小红书-ff2442)

## 效果

- 白底纯文字，无装饰
- 1080×1440px（标准小红书比例）
- 顶部账号名水印
- **内容自动分页**（CSS 多列布局，按行边界切分，无需手动插入分隔符）
- 支持 `**加粗**` 语法

## 快速开始

### 安装依赖

```bash
pip install playwright pillow
playwright install chromium
```

### 生成卡片

```bash
python scripts/render.py content.txt -b 你的账号名 -o ./output
```

### 内容格式

```text
第一张卡片的内容

可以有多个段落

---

第二张卡片的内容

支持 **加粗文字**
```

## 参数

| 参数 | 说明 | 默认 |
|------|------|------|
| `input` | 内容文本文件路径 | 必填 |
| `-b` | 顶部账号名水印 | 空 |
| `-o` | 输出目录 | 当前目录 |

## 作为 Claude Code Skill 使用

本项目同时是一个 [Claude Code Agent Skill](https://docs.anthropic.com/claude-code)。

将目录放置到 `~/.claude/skills/xhs-minimal-card/` 后，在 Claude Code 中直接输入 `/xhs-minimal-card` 即可启动交互式卡片生成流程。

## 文件结构

```
xhs-minimal-card/
├── SKILL.md          # Claude Code Skill 定义
├── scripts/
│   └── render.py     # 渲染脚本
└── assets/
    └── card.html     # 卡片 HTML 模板
```
