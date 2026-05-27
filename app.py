import gradio as gr
import os
import subprocess
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def search_persian_music(query, count):
    """جستجوی مستقیم در دیتابیس سایت‌های موزیک بدون تداخل با گوگل"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    mp3_links = []
    try:
        # جستجوی مستقیم در موتور سرچ سایت آپ‌موزیک (یکی از قوی‌ترین آرشیوها)
        search_url = f"https://upmusics.com/?s={urllib.parse.quote(query)}"
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # پیدا کردن صفحات آهنگ‌ها
        post_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if "upmusics.com/" in href and href.endswith(".html") and href not in post_links:
                post_links.append(href)
        
        # رفتن به داخل صفحات برای برداشتن لینک مستقیم MP3
        for post_url in post_links[:count + 3]: # چند تا زاپاس میاوریم
            if len(mp3_links) >= count:
                break
            try:
                res = requests.get(post_url, headers=headers, timeout=5)
                # پیدا کردن لینک‌های ۱۲۸ یا ۳۲۰ مستقیم
                links = re.findall(r'href=[\'"]?(https://upmusics\.com/[^\'"]+\.mp3)[\'"]?', res.text)
                for link in links:
                    if link not in mp3_links and "demo" not in link.lower():
                        mp3_links.append(link)
                        break # از هر پست یک کیفیت بس است
            except:
                continue
    except Exception as e:
        print(f"Scraping error: {e}")
        
    return mp3_links[:count]

def pishai_iranian_engine(genre_query, song_count, progress=gr.Progress()):
    try:
        song_count = int(song_count)
        output_file = "pishai_persian_podcast.mp3"
        list_file = "concat_list.txt"
        
        # تمیزکاری فایل‌های قدیمی
        os.system("rm -f *.mp3 *.txt")
        
        if not genre_query.strip():
            return None, "❌ لطفاً نام خواننده یا سبک را وارد کنید."
            
        progress(0.1, desc="🚀 در حال خزش هوشمند در سرورهای موزیک ایران...")
        mp3_urls = search_persian_music(genre_query, song_count)
        
        if not mp3_urls:
            return None, "❌ آهنگ یا خواننده‌ای با این مشخصات در آرشیو وب فارسی یافت نشد. عبارت دیگری را تست کنید."
            
        processed_files = []
        
        # دانلود و کات کردن سریع فایل‌ها
        for i, url in enumerate(mp3_urls):
            progress(0.2 + (i / len(mp3_urls)) * 0.6, desc=f"📥 دانلود و کات فرکانسی آهنگ {i+1} از {len(mp3_urls)}...")
            track_name = f"t_{i}.mp3"
            
            # برش ۳۰ ثانیه‌ای از دقیقه ۱ آهنگ
            cmd = [
                'ffmpeg', '-y', '-ss', '00:01:00', '-t', '30',
                '-i', url, '-acodec', 'libmp3lame', '-ab', '128k',
                '-af', 'afade=t=in:st=0:d=3,afade=t=out:st=27:d=3',
                track_name
            ]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(track_name) and os.path.getsize(track_name) > 10000:
                processed_files.append(track_name)

        # میکس و چسباندن
        if processed_files:
            progress(0.9, desc="🎛️ در حال هماهنگ‌سازی و خروجی گرفتن پادکست...")
            with open(list_file, "w") as f:
                for file in processed_files: 
                    f.write(f"file '{file}'\n")
            
            subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_file, '-c', 'copy', output_file])
            
            # تمیزکاری دیسک
            for f in processed_files:
                try: os.remove(f)
                except: pass
            if os.path.exists(list_file): 
                os.remove(list_file)
                
            return output_file, f"🔥 پادکست ریمیکس Premeet.ai با موفقیت از {len(processed_files)} آهنگ برتر ساخته شد!"
        
        return None, "❌ خطا در بریدن قطعات صوتی. مجدداً تلاش کنید."

    except Exception as e:
        return None, f"خطای سرور رندر: {str(e)}"

with gr.Blocks(theme=gr.themes.Default(primary_hue="orange", secondary_hue="zinc")) as demo:
    gr.Markdown("# 🎛️ Premeet.ai - pishai Studio (Persian Web Edition)")
    gr.Markdown("موتور اختصاصی استخراج صوتی پایش‌آی متصل به سرورهای موزیک داخل کشور.")
    
    with gr.Row():
        query = gr.Textbox(label="نام خواننده یا سبک (مثال: آرون افشار، رضا بهرام، شاد)", value="سهراب پاکزاد")
        count = gr.Number(label="تعداد قطعات", value=3)
        
    btn = gr.Button("🚀 ساخت پادکست ریمیکس فوری", variant="primary")
    audio = gr.Audio(label="شنیدن و دانلود پادکست نهایی")
    status = gr.Markdown("وضعیت: آماده به کار")
    
    btn.click(pishai_iranian_engine, [query, count], [audio, status])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
    
