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

    with open(src_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 同时匹配标准 Markdown 图片和 Obsidian 双链图片
    md_images = re.findall(r'!\[.*?\]\((.*?)\)', content)
    wiki_images = re.findall(r'!\[\[(.*?)\]\]', content)
    
    all_images = md_images + wiki_images
    img_count = 0

    for img_path in all_images:
        # 清理路径：处理 URL 编码 (如 %20 变空格)，去掉可能存在的标题
        clean_path = urllib.parse.unquote(img_path.split(' ')[0])
        img_name = os.path.basename(clean_path)
        
        # 尝试在图片目录和根目录中寻找图片
        possible_src_imgs = [
            os.path.join(OBSIDIAN_IMG_DIR, img_name),
            os.path.join(OBSIDIAN_NOTE_DIR, img_name) # 防止图片其实存在外层
        ]
        
        img_found = False
        for src_img in possible_src_imgs:
            if os.path.exists(src_img):
                dest_img = os.path.join(HUGO_IMG_DIR, img_name)
                shutil.copy2(src_img, dest_img)
                img_count += 1
                print(f"  ✅ 成功搬运图片：{img_name}")
                img_found = True
                break
        
        if not img_found:
             print(f"  ⚠️ 警告：在本地找不到图片实体文件：{img_name}")

    shutil.copy2(src_md, dest_md)
    print(f"✅ 笔记已搬运至 E 盘！(共包含 {img_count} 张图片)")

    print("☁️ 正在将代码推送到 GitHub...")
    try:
        os.chdir(HUGO_ROOT)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Auto-publish: {note_filename}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "push"], check=True)
        print("🎉 自动发布成功！请去 GitHub Pages 检查网页。")
    except subprocess.CalledProcessError as e:
        print(f"❌ 推送失败，错误码: {e.returncode}")
        print("💡 提示：既然开启了 TUN 模式，请确保 Mihomo 处于 'Rule' 模式，并且节点处于可用状态。")

if __name__ == "__main__":
    # 请把名字换成你那篇带图片的测试笔记
    publish_note("test.md")
