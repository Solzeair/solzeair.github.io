import os
import shutil
import re
import subprocess
import urllib.parse

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

    # 获取文章名（去掉 .md 后缀），用于创建图片子文件夹
    article_name = os.path.splitext(note_filename)[0]
    article_img_dir = os.path.join(HUGO_IMG_DIR, article_name)
    article_img_url_prefix = f"{HUGO_IMG_URL_PREFIX}{article_name}/"
    print(f"   📁 图片将保存到: {article_img_dir}")

    with open(src_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 同时匹配标准 Markdown 图片和 Obsidian 双链图片
    md_img_pattern = r'!\[.*?\]\((.*?)\)'
    wiki_img_pattern = r'!\[\[(.*?)(?:\|.*?)?\]\]'
    
    md_images = re.findall(md_img_pattern, content)
    wiki_images = re.findall(wiki_img_pattern, content)
    
    all_images = md_images + wiki_images
    img_count = 0

    print(f"\n🔍 发现图片：")
    print(f"   Markdown 格式图片: {len(md_images)} 个")
    print(f"   Obsidian 双链图片: {len(wiki_images)} 个")

    # 第一步：搬运图片文件，并记录已成功搬运的图片名
    copied_imgs = {}  # 键：原图片路径，值：Hugo 访问路径
    
    for img_path in all_images:
        clean_path = urllib.parse.unquote(img_path.split('|')[0].strip())
        img_name = os.path.basename(clean_path)
        
        print(f"\n--- 处理图片: {img_name} ---")
        
        # 尝试在图片目录和根目录中寻找图片
        possible_src_imgs = [
            os.path.join(OBSIDIAN_IMG_DIR, img_name),
            os.path.join(OBSIDIAN_IMG_DIR, clean_path),
            os.path.join(OBSIDIAN_NOTE_DIR, img_name),
            os.path.join(OBSIDIAN_NOTE_DIR, clean_path)
        ]
        
        img_found = False
        for i, src_img in enumerate(possible_src_imgs, 1):
            print(f"   尝试路径 [{i}]: {src_img}")
            if os.path.exists(src_img):
                # 创建文章专属的图片目录
                os.makedirs(article_img_dir, exist_ok=True)
                dest_img = os.path.join(article_img_dir, img_name)
                
                # 检查目标文件是否已存在
                if os.path.exists(dest_img):
                    print(f"   ⚠️ 图片已存在，跳过复制: {img_name}")
                else:
                    shutil.copy2(src_img, dest_img)
                    print(f"   ✅ 复制成功！文件大小: {os.path.getsize(dest_img)} bytes")
                
                # 记录 Hugo 访问路径（使用文章专属路径）
                safe_img_name = urllib.parse.quote(img_name)
                hugo_img_url = f"{article_img_url_prefix}{safe_img_name}"
                copied_imgs[clean_path] = hugo_img_url
                img_count += 1
                print(f"   📍 Hugo URL: {hugo_img_url}")
                img_found = True
                break
        
        if not img_found:
            print(f"   ❌ 警告：找不到图片文件: {img_name}")

    # 第二步：替换笔记中的图片路径
    print(f"\n📝 开始替换图片路径...")
    
    # 替换 Obsidian 双链图片 ![[]] 为 Markdown 图片格式
    def replace_wiki_img(match):
        img_path = match.group(1).split('|')[0].strip()
        clean_path = urllib.parse.unquote(img_path)
        if clean_path in copied_imgs:
            new_path = copied_imgs[clean_path]
            print(f"   替换: ![[{img_path}]] -> ![]({new_path})")
            return f"![{os.path.basename(clean_path)}]({new_path})"
        else:
            return match.group(0)
    
    content = re.sub(wiki_img_pattern, replace_wiki_img, content)
    
    # 替换标准 Markdown 图片的本地路径
    def replace_md_img(match):
        img_path = match.group(1)
        clean_path = urllib.parse.unquote(img_path)
        if clean_path in copied_imgs:
            new_path = copied_imgs[clean_path]
            print(f"   替换: ![]({img_path}) -> ![]({new_path})")
            return f"![{os.path.basename(clean_path)}]({new_path})"
        else:
            return match.group(0)
    
    content = re.sub(md_img_pattern, replace_md_img, content)

    # 第三步：写入替换后的笔记内容到 Hugo 目录
    with open(dest_md, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n💾 写入目标文件: {dest_md}")
    print(f"✅ 笔记已搬运至 E 盘！(共包含 {img_count} 张图片，已替换路径)")

    # 第四步：推送至 GitHub
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
