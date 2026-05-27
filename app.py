import gradio as gr
import os
import subprocess
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def search_and_get_mp3_links(query, count):
    """جستجوی هوشمند در گوگل برای یافتن لینک‌های مستقیم MP3 از سایت‌های ایرانی"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # جستجو در گوگل با تمرکز روی دانلود موزیک ۱۲۸ یا ۳۲۰
    search_query = f"دانلود آهنگ {query} mp3"
    url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
    
    mp3_links = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # پیدا کردن لینک سایت‌ها از نتایج گوگل
        site_urls = []
        for g in soup.find_all('div', class_='g'):
            anchors = g.find_all('a')
            if anchors and anchors[0].has_attr('href'):
                site_url = anchors[0]['href']
                if "google.com" not in site_url and site_url.startswith("http"):
                    site_urls.append(site_url)
        
        # خزش داخل سایت‌های موزیک پیدا شده برای استخراج لینک مستقیم mp3
        for s_url in site_urls:
            if len(mp3_links) >= count:
                break
            try:
                res = requests.get(s_url, headers=headers, timeout=5)
                # پیدا کردن تمام لینک‌های مستقیم mp3 با کیفیت ۱۲۸ یا ۳۲۰
                links = re.findall(r'href=[\'"]?(https[^\'"]+\.mp3)[\'"]?', res.text)
                
                for link in links:
                    # فیلتر کردن لینک‌های تکراری، دمو یا ریمیکس‌های طولانی پادکستی
                    if link not in mp3_links and "demo" not in link.lower() and "podcast" not in link.lower():
                        mp3_links.append(link)
                        if len(mp3_links) >= count:
                            break
            except:
                continue
    except Exception as e:
        print(f"Google Scraping Error: {e}")
        
    return mp3_links

def pishai_iranian_engine(genre_query, song_count, progress=gr.Progress()):
    try:
        song_count = int(song_count)
        output_file = "pishai_persian_podcast.mp3"
        list_file = "concat_list.txt"
        
        # تمیزکاری فایل‌های قدیمی
        os.system("rm -f *.mp3 *.txt")
        
        progress(0.1, desc="در حال جستجوی هوشمند در سایت‌های موزیک فارسی...")
        mp3_urls = search_and_get_mp3_links(genre_query, song_count)
        
        if not mp3_urls:
            return None, "❌ متأسفانه آهنگ یا خواننده مدنظر در سایت‌های موزیک یافت نشد. عبارت را دقیق‌تر بنویسید."
            
        processed_files = []
        
        # دانلود و برش مستقیم قطعات با FFmpeg (بدون نیاز به پکیج‌های سنگین)
        for i, url in enumerate(mp3_urls):
            progress(0.2 + (i / len(mp3_urls)) * 0.6, desc=f"در حال دانلود و کات کردن آهنگ {i+1} از {len(mp3_urls)}...")
            track_name = f"t_{i}.mp3"
            
            # برش ۳۵ ثانیه‌ای از اواسط آهنگ (دقیقه ۱) با افکت فید این و فید اوت
            cmd = [
                'ffmpeg', '-y', '-ss', '00:01:00', '-t', '35',
                '-i', url, '-acodec', 'libmp3lame', '-ab', '128k',
                '-af', 'afade=t=in:st=0:d=4,afade=t=out:st=31:d=4',
                track_name
            ]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(track_name) and os.path.getsize(track_name) > 10000:
                processed_files.append(track_name)

        # چسباندن و ترکیب نهایی قطعات به همدیگر
        if processed_files:
            progress(0.9, desc="در حال میکس، همگام‌سازی و تولید پادکست...")
            with open(list_file, "w") as f:
                for file in processed_files: 
                    f.write(f"file '{file}'\n")
            
            subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_file, '-c', 'copy', output_file])
            
            # تمیزکاری نهایی سرور
            for f in processed_files:
                try: os.remove(f)
                except: pass
            if os.path.exists(list_file): 
                os.remove(list_file)
                
            return output_file, f"🔥 پادکست ریمیکس Premeet.ai با موفقیت از {len(processed_files)} آهنگ برتر ایرانی ساخته شد!"
        
        return None, "❌ خطا در پردازش فایل‌های صوتی دریافت شده."

    except Exception as e:
        return None, f"خطای سرور رندر: {str(e)}"

# رابط کاربری شیک و بهینه‌شده با تم برندینگ شما
with gr.Blocks(theme=gr.themes.Default(primary_hue="orange", secondary_hue="zinc")) as demo:
    gr.Markdown("# 🎛️ Premeet.ai - pishai Studio (Persian Web Edition)")
    gr.Markdown("بدون نیاز به یوتیوب؛ موتور هوشمند مستقیماً آهنگ‌ها را از سرورهای پرسرعت ایرانی استخراج و ریمیکس می‌کند.")
    
    with gr.Row():
        query = gr.Textbox(label="نام خواننده، قطعه یا سبک (مثال: همایون شجریان، ریمیکس شاد، رضا بهرام)", value="شاد جدید")
        count = gr.Number(label="تعداد قطعات در پادکست", value=3)
        
    btn = gr.Button("🚀 ساخت پادکست ریمیکس فوری", variant="primary")
    audio = gr.Audio(label="شنیدن و دانلود پادکست نهایی")
    status = gr.Markdown("وضعیت: آماده به کار")
    
    btn.click(pishai_iranian_engine, [query, count], [audio, status])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
                    
