import os
import shutil
import re
import subprocess
import urllib.parse
import datetime  # 新增：用于获取系统时间

# ================= 配置区 =================
# 你的 Obsidian 源文件路径
OBSIDIAN_NOTE_DIR = r"F:/Obsidian/repository/Note"
OBSIDIAN_IMG_DIR = r"F:/Obsidian/repository/Note/images" 

# 你的 Hugo 博客实体路径
HUGO_ROOT = r"E:/Github_blog/Sakurarry_blog"
HUGO_POST_DIR = os.path.join(HUGO_ROOT, "content", "posts")
HUGO_IMG_DIR = os.path.join(HUGO_ROOT, "static", "images")
# Hugo 图片的访问前缀（根据你的博客域名/路径调整，默认 /images/ 即可）
HUGO_IMG_URL_PREFIX = "/images/"
# ==========================================

def publish_note(note_filename):
    if not note_filename.endswith('.md'):
        note_filename += '.md'

    src_md = os.path.join(OBSIDIAN_NOTE_DIR, note_filename)
    dest_md = os.path.join(HUGO_POST_DIR, note_filename)

    if not os.path.exists(src_md):
        print(f"❌ 找不到笔记文件：{src_md}")
        return

    print(f"🚀 开始处理笔记：{note_filename} ...")
    print(f"   源文件：{src_md}")
    print(f"   目标文件：{dest_md}")

    # 获取文章名（去掉 .md 后缀），用于创建图片子文件夹和生成标题
    article_name = os.path.splitext(note_filename)[0]
    article_img_dir = os.path.join(HUGO_IMG_DIR, article_name)
    article_img_url_prefix = f"{HUGO_IMG_URL_PREFIX}{article_name}/"
    print(f"   📁 图片将保存到: {article_img_dir}")

    with open(src_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # ====== 图像处理部分 (保持你优秀的逻辑不变) ======
    md_img_pattern = r'!\[.*?\]\((.*?)\)'
    wiki_img_pattern = r'!\[\[(.*?)(?:\|.*?)?\]\]'
    
    md_images = re.findall(md_img_pattern, content)
    wiki_images = re.findall(wiki_img_pattern, content)
    all_images = md_images + wiki_images
    img_count = 0

    print(f"\n🔍 发现图片：")
    print(f"   Markdown 格式图片: {len(md_images)} 个")
    print(f"   Obsidian 双链图片: {len(wiki_images)} 个")

    copied_imgs = {}
    for img_path in all_images:
        clean_path = urllib.parse.unquote(img_path.split('|')[0].strip())
        img_name = os.path.basename(clean_path)
        
        possible_src_imgs = [
            os.path.join(OBSIDIAN_IMG_DIR, img_name),
            os.path.join(OBSIDIAN_IMG_DIR, clean_path),
            os.path.join(OBSIDIAN_NOTE_DIR, img_name),
            os.path.join(OBSIDIAN_NOTE_DIR, clean_path)
        ]
        
        img_found = False
        for i, src_img in enumerate(possible_src_imgs, 1):
            if os.path.exists(src_img):
                os.makedirs(article_img_dir, exist_ok=True)
                dest_img = os.path.join(article_img_dir, img_name)
                
                if not os.path.exists(dest_img):
                    shutil.copy2(src_img, dest_img)
                
                safe_img_name = urllib.parse.quote(img_name)
                hugo_img_url = f"{article_img_url_prefix}{safe_img_name}"
                copied_imgs[clean_path] = hugo_img_url
                img_count += 1
                img_found = True
                break
        
    def replace_wiki_img(match):
        img_path = match.group(1).split('|')[0].strip()
        clean_path = urllib.parse.unquote(img_path)
        if clean_path in copied_imgs:
            new_path = copied_imgs[clean_path]
            return f"![{os.path.basename(clean_path)}]({new_path})"
        return match.group(0)
    
    content = re.sub(wiki_img_pattern, replace_wiki_img, content)
    
    def replace_md_img(match):
        img_path = match.group(1)
        clean_path = urllib.parse.unquote(img_path)
        if clean_path in copied_imgs:
            new_path = copied_imgs[clean_path]
            return f"![{os.path.basename(clean_path)}]({new_path})"
        return match.group(0)
    
    content = re.sub(md_img_pattern, replace_md_img, content)


    # ====== 新增：智能处理 Front Matter ======
    print(f"\n⚙️ 检查并补全 Front Matter 元数据...")
    # 获取当前 ISO 格式的时间，带时区 (Hugo 完美支持)
    current_time = datetime.datetime.now().astimezone().isoformat('T', 'seconds')
    
    # 匹配开头是否有 --- 包裹的区域
    fm_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.search(fm_pattern, content, flags=re.DOTALL)

    if match:
        print("   ✅ 检测到现有 Front Matter，正在检查缺失字段...")
        fm_content = match.group(1)
        fm_lines = fm_content.split('\n')
        
        # 检查是否缺失关键字段
        has_title = any(line.strip().startswith('title:') for line in fm_lines)
        has_date = any(line.strip().startswith('date:') for line in fm_lines)
        has_draft = any(line.strip().startswith('draft:') for line in fm_lines)
        
        new_fm_lines = fm_lines.copy()
        if not has_title:
            new_fm_lines.append(f'title: "{article_name}"')
            print("   ➕ 自动补充字段: title")
        if not has_date:
            new_fm_lines.append(f'date: {current_time}')
            print("   ➕ 自动补充字段: date")
        if not has_draft:
            new_fm_lines.append(f'draft: false')
            print("   ➕ 自动补充字段: draft")
            
        # 重新拼接替换
        new_fm_text = "---\n" + "\n".join(new_fm_lines) + "\n---\n"
        content = re.sub(fm_pattern, new_fm_text, content, count=1, flags=re.DOTALL)
    else:
        print("   ⚠️ 未检测到 Front Matter，正在自动生成...")
        new_fm_text = f"---\ntitle: \"{article_name}\"\ndate: {current_time}\ndraft: false\n---\n"
        content = new_fm_text + content


    # ====== 写入并推送到 GitHub ======
    with open(dest_md, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n💾 写入目标文件: {dest_md}")

    print("\n☁️ 正在将代码推送到 GitHub...")
    try:
        os.chdir(HUGO_ROOT)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Auto-publish: {note_filename}"], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "push"], check=True)
        print("🎉 自动发布成功！请去 GitHub Pages 检查网页。")
    except subprocess.CalledProcessError as e:
        print(f"❌ 推送失败，错误码: {e.returncode}")
        print("💡 提示：请检查网络连接和 Git 配置。")

if __name__ == "__main__":
    publish_note("test.md")
