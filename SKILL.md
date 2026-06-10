# xhs-minimal-card · 极简笔记卡片

白底纯文字风格，内容自动分页（CSS 多列布局，不截断行）。

## 使用流程

收到请求后：

1. **询问账号名称**（如果用户没提）：「你的小红书账号名称是什么？」
2. 将用户内容**原文**保存为 `.txt` 文件，不修改任何措辞
3. 运行渲染脚本
4. 告知输出路径和卡片数量

## 渲染命令

```bash
python scripts/render.py <内容文件> -b <账号名> -o <输出目录>
```

示例：
```bash
python scripts/render.py content.txt -b 商分账号 -o ./output
```

## 格式说明

- 段落之间空一行
- `**加粗**` 语法生效
- 内容自动按行边界分页，无需手动插入分隔符

## 依赖

```bash
pip install playwright pillow
playwright install chromium
```
