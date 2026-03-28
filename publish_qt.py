import os
import shutil
import re
import subprocess
import urllib.parse
from datetime import datetime

# ================= 配置区 =================
OBSIDIAN_NOTE_DIR = r"F:/Obsidian/repository/Note"
OBSIDIAN_IMG_DIR = r"F:/Obsidian/repository/Note/images" 
HUGO_ROOT = r"E:/Github_blog/Sakurarry_blog"
HUGO_POST_DIR = os.path.join(HUGO_ROOT, "content", "posts")
HUGO_IMG_DIR = os.path.join(HUGO_ROOT, "static", "images")
HUGO_IMG_URL_PREFIX = "/images/"
# ==========================================

def extract_title(content, filename):
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    return os.path.splitext(filename)[0]

def process_frontmatter(content, filename):
    title = extract_title(content, filename)
    today = datetime.now().strftime("%Y-%m-%d")
    
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    hugo_frontmatter = f"""---
title: "{title}"
date: {today}
draft: false
tags: ["Qt", "C++"]
categories: ["编程"]
---"""
    
    if match:
        existing_fm = match.group(1)
        if 'title:' not in existing_fm.lower():
            content = re.sub(frontmatter_pattern, hugo_frontmatter + '\n\n', content, count=1)
        elif 'date:' not in existing_fm.lower():
            new_fm = existing_fm.rstrip() + f"\ndate: {today}\ndraft: false"
            content = re.sub(frontmatter_pattern, f"---\n{new_fm}\n---\n\n", content, count=1)
    else:
        content = hugo_frontmatter + "\n\n" + content
    
    return content

def publish_note(note_filename):
    if not note_filename.endswith('.md'):
        note_filename += '.md'

    src_md = os.path.join(OBSIDIAN_NOTE_DIR, note_filename)
    article_name = os.path.splitext(note_filename)[0]
    dest_md = os.path.join(HUGO_POST_DIR, note_filename)
    article_img_dir = os.path.join(HUGO_IMG_DIR, article_name)

    if not os.path.exists(src_md):
        print(f"❌ 找不到笔记文件：{src_md}")
        return False

    print(f"🚀 开始处理笔记：{note_filename}")

    with open(src_md, 'r', encoding='utf-8') as f:
        content = f.read()

    md_img_pattern = r'!\[.*?\]\((.*?)\)'
    wiki_img_pattern = r'!\[\[(.*?)(?:\|.*?)?\]\]'
    
    md_images = re.findall(md_img_pattern, content)
    wiki_images = re.findall(wiki_img_pattern, content)
    
    all_images = md_images + wiki_images
    img_count = 0

    copied_imgs = {}
    for img_path in all_images:
        clean_path = urllib.parse.unquote(img_path.split('|')[0].strip())
        img_name = os.path.basename(clean_path)
        
        possible_src_imgs = [
            os.path.join(OBSIDIAN_IMG_DIR, img_name),
            os.path.join(OBSIDIAN_IMG_DIR, clean_path),
            os.path.join(OBSIDIAN_NOTE_DIR, img_name)
        ]
        
        for src_img in possible_src_imgs:
            if os.path.exists(src_img):
                os.makedirs(article_img_dir, exist_ok=True)
                dest_img = os.path.join(article_img_dir, img_name)
                if not os.path.exists(dest_img):
                    shutil.copy2(src_img, dest_img)
                    print(f"  ✅ 复制图片：{img_name}")
                safe_img_name = urllib.parse.quote(img_name)
                hugo_img_url = f"{HUGO_IMG_URL_PREFIX}{article_name}/{safe_img_name}"
                copied_imgs[clean_path] = hugo_img_url
                img_count += 1
                break

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
    content = process_frontmatter(content, note_filename)

    os.makedirs(os.path.dirname(dest_md), exist_ok=True)
    with open(dest_md, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ 文件已写入：{dest_md}")
    print(f"  📊 共处理 {img_count} 张图片")
    return True

def main():
    # 发布两个 Qt 文件
    notes = ["Qt.md", "Qt对象树详解.md"]
    
    for note in notes:
        publish_note(note)
        print()
    
    # 推送到 GitHub
    print("☁️ 正在推送到 GitHub...")
    try:
        os.chdir(HUGO_ROOT)
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Publish Qt articles"], capture_output=True)
        subprocess.run(["git", "push"], check=True, capture_output=True)
        print("🎉 推送成功！")
    except subprocess.CalledProcessError as e:
        print("⚠️ 推送失败，请手动推送")

if __name__ == "__main__":
    main()
