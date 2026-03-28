import os
import shutil
import re
import subprocess
import urllib.parse
from datetime import datetime

# ================= 配置区 =================
# 你的 Obsidian 源文件路径
OBSIDIAN_NOTE_DIR = r"F:/Obsidian/repository/Note"
OBSIDIAN_IMG_DIR = r"F:/Obsidian/repository/Note/images" 

# 你的 Hugo 博客实体路径
HUGO_ROOT = r"E:/Github_blog/Sakurarry_blog"
HUGO_POST_DIR = os.path.join(HUGO_ROOT, "content", "posts")
HUGO_IMG_DIR = os.path.join(HUGO_ROOT, "static", "images")
# Hugo 图片的访问前缀
HUGO_IMG_URL_PREFIX = "/images/"
# ==========================================

def extract_title(content, filename):
    """从内容或文件名提取标题"""
    # 尝试从第一个 # 标题提取
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    # 使用文件名作为标题
    return os.path.splitext(filename)[0]

def process_frontmatter(content, filename):
    """处理 frontmatter，转换为 Hugo 格式"""
    title = extract_title(content, filename)
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 检查是否有现有的 frontmatter
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    hugo_frontmatter = f"""---
title: "{title}"
date: {today}
draft: false
tags: []
categories: []
---"""
    
    if match:
        # 有现有 frontmatter，检查是否是 Hugo 格式
        existing_fm = match.group(1)
        # 如果不是 Hugo 格式（没有 title 字段），替换它
        if 'title:' not in existing_fm.lower():
            content = re.sub(frontmatter_pattern, hugo_frontmatter + '\n\n', content, count=1)
        # 如果是 Hugo 格式但缺少必要字段，补充
        elif 'date:' not in existing_fm.lower():
            # 在现有 frontmatter 中添加 date
            new_fm = existing_fm.rstrip() + f"\ndate: {today}\ndraft: false"
            content = re.sub(frontmatter_pattern, f"---\n{new_fm}\n---\n\n", content, count=1)
    else:
        # 没有 frontmatter，添加新的
        content = hugo_frontmatter + "\n\n" + content
    
    return content

def publish_note(note_filename):
    if not note_filename.endswith('.md'):
        note_filename += '.md'

    src_md = os.path.join(OBSIDIAN_NOTE_DIR, note_filename)
    
    # 获取文章名（不含扩展名）作为图片子文件夹名
    article_name = os.path.splitext(note_filename)[0]
    dest_md = os.path.join(HUGO_POST_DIR, note_filename)
    
    # 文章专属图片目录
    article_img_dir = os.path.join(HUGO_IMG_DIR, article_name)

    if not os.path.exists(src_md):
        return False, f"找不到笔记文件：{src_md}"

    with open(src_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 同时匹配标准 Markdown 图片和 Obsidian 双链图片
    md_img_pattern = r'!\[.*?\]\((.*?)\)'
    wiki_img_pattern = r'!\[\[(.*?)(?:\|.*?)?\]\]'
    
    md_images = re.findall(md_img_pattern, content)
    wiki_images = re.findall(wiki_img_pattern, content)
    
    all_images = md_images + wiki_images
    img_count = 0

    # 第一步：搬运图片文件到文章专属文件夹
    copied_imgs = {}
    for img_path in all_images:
        clean_path = urllib.parse.unquote(img_path.split('|')[0].strip())
        img_name = os.path.basename(clean_path)
        
        possible_src_imgs = [
            os.path.join(OBSIDIAN_IMG_DIR, img_name),
            os.path.join(OBSIDIAN_IMG_DIR, clean_path),
            os.path.join(OBSIDIAN_NOTE_DIR, img_name)
        ]
        
        img_found = False
        for src_img in possible_src_imgs:
            if os.path.exists(src_img):
                os.makedirs(article_img_dir, exist_ok=True)
                dest_img = os.path.join(article_img_dir, img_name)
                
                # 检查是否已存在
                if not os.path.exists(dest_img):
                    shutil.copy2(src_img, dest_img)
                
                safe_img_name = urllib.parse.quote(img_name)
                hugo_img_url = f"{HUGO_IMG_URL_PREFIX}{article_name}/{safe_img_name}"
                copied_imgs[clean_path] = hugo_img_url
                img_count += 1
                img_found = True
                break
        
        if not img_found:
            pass  # 静默跳过找不到的图片

    # 第二步：替换图片路径
    def replace_wiki_img(match):
        img_path = match.group(1).split('|')[0].strip()
        clean_path = urllib.parse.unquote(img_path)
        if clean_path in copied_imgs:
            return f"![{os.path.basename(clean_path)}]({copied_imgs[clean_path]})"
        return match.group(0)
    
    content = re.sub(wiki_img_pattern, replace_wiki_img, content)
    
    def replace_md_img(match):
        img_path = match.group(1)
        clean_path = urllib.parse.unquote(img_path)
        if clean_path in copied_imgs:
            return f"![{os.path.basename(clean_path)}]({copied_imgs[clean_path]})"
        return match.group(0)
    
    content = re.sub(md_img_pattern, replace_md_img, content)

    # 第三步：处理 frontmatter（关键修复！）
    content = process_frontmatter(content, note_filename)

    # 第四步：写入目标文件
    os.makedirs(os.path.dirname(dest_md), exist_ok=True)
    with open(dest_md, 'w', encoding='utf-8') as f:
        f.write(content)

    # 第五步：推送到 GitHub
    try:
        os.chdir(HUGO_ROOT)
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"Auto-publish: {note_filename}"], capture_output=True)
        subprocess.run(["git", "push"], check=True, capture_output=True)
        return True, f"发布成功！共处理 {img_count} 张图片"
    except subprocess.CalledProcessError as e:
        return True, f"文件已复制，但推送失败。请手动推送。"

def list_notes():
    """列出所有可发布的笔记"""
    notes = []
    for f in os.listdir(OBSIDIAN_NOTE_DIR):
        if f.endswith('.md') and not f.startswith('.'):
            notes.append(f)
    return notes

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        publish_note(sys.argv[1])
    else:
        print("可用笔记：")
        for note in list_notes():
            print(f"  - {note}")
        print("\n用法: python publish_blog_v2.py <笔记名>")
