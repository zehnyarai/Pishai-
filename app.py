import gradio as gr
import os
import subprocess
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def search_open_iranian_source(query, count):
    """جستجوی پرسرعت در دیتابیس‌های باز صوتی بدون فیلتر و ضد مسدودسازی"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    mp3_links = []
    
    try:
        # استفاده از موتور سرچ موزیکفا (یکی از پایدارترین سرورهای دانلود باز)
        search_url = f"https://musicfa.com/?s={urllib.parse.quote(query)}"
        res = requests.get(search_url, headers=headers, timeout=4)
        if res.status_code == 200:
            # استخراج مستقیم لینک‌های mp3 کیفیت عالی با ریجکس جهت افزایش سرعت
            links = re.findall(r'href=[\'"]?(https://dl\.musicfa\.com/[^\'"]+\.mp3)[\'"]?', res.text)
            for link in links:
                if "dem" not in link.lower() and link not in mp3_links:
                    mp3_links.append(link)
                    if len(mp3_links) >= count:
                        break
    except:
        pass
        
    return mp3_links

def pishai_seamless_engine(genre_query, song_count, progress=gr.Progress()):
    try:
        song_count = int(song_count)
        output_file = "pishai_seamless_remix.mp3"
        
        # پاکسازی صددرصد فایل‌های موقت قدیمی
        os.system("rm -f *.mp3 *.txt")
        
        if not genre_query.strip():
            return None, "❌ لطفاً نام خواننده یا سبک را وارد کنید."
            
        progress(0.1, desc="🔍 جستجو در آرشیو بدون فیلتر موزیک فارسی...")
        mp3_urls = search_open_iranian_source(genre_query, song_count)
        
        if not mp3_urls:
            return None, f"❌ آهنگ یا خواننده‌ای برای '{genre_query}' یافت نشد. لطفاً نام را ساده‌تر وارد کنید (مثال: شادمهر)."
            
        processed_files = []
        
        # دانلود و کات فرکانسی همزمان
        for i, url in enumerate(mp3_urls):
            progress(0.2 + (i / len(mp3_urls)) * 0.5, desc=f"⚡ دریافت و آماده‌سازی قطعه ملودیک {i+1}...")
            track_name = f"t_{i}.mp3"
            
            # برش ۳۰ ثانیه‌ای هوشمند از اوج آهنگ (ثانیه ۴۰)
            cmd = [
                'ffmpeg', '-y', '-ss', '00:00:40', '-t', '30',
                '-i', url, '-acodec', 'libmp3lame', '-ab', '128k',
                track_name
            ]
            
            try:
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
                if os.path.exists(track_name) and os.path.getsize(track_name) > 10000:
                    processed_files.append(track_name)
            except:
                continue

        if not processed_files:
            return None, "❌ خطای موقت شبکه سرور. لطفاً دوباره دکمه را بزنید."

        progress(0.8, desc="🎛️ اتصال ریتمیک ملودی‌ها به صورت زنجیره‌ای...")
        
        # اتصال روان با فیلتر کراس‌فید (میکس دی‌جی ۳ ثانیه‌ای)
        inputs_count = len(processed_files)
        if inputs_count == 1:
            os.rename(processed_files[0], output_file)
        elif inputs_count == 2:
            subprocess.run(['ffmpeg', '-y', '-i', processed_files[0], '-i', processed_files[1], '-filter_complex', 'acrossfade=d=3:c1=tri:c2=tri', output_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(['ffmpeg', '-y', '-i', processed_files[0], '-i', processed_files[1], '-i', processed_files[2], '-filter_complex', 'acrossfade=d=3:c1=tri:c2=tri[a1];[a1][2:a]acrossfade=d=3:c1=tri:c2=tri', output_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # تمیزکاری دیسک
        for f in processed_files:
            try: os.remove(f)
            except: pass

        return output_file, f"🎵 ریمیکس ریتمیک و زنجیره‌ای Premeet.ai با موفقیت ساخته شد!"

    except Exception as e:
        return None, f"خطای پردازشگر: {str(e)}"

# طراحی بهینه شده متناسب با خواست کاربر
with gr.Blocks(theme=gr.themes.Default(primary_hue="orange", secondary_hue="zinc")) as demo:
    gr.Markdown("# 🎛️ Premeet.ai - pishai Studio (Seamless Mix)")
    gr.Markdown("موتور میکس ریتمیک متصل به دیتابیس‌های پایدار و بدون فیلتر وب فارسی.")
    
    with gr.Row():
        query = gr.Textbox(label="نام خواننده یا سبک ریمیکس", value="شادمهر")
        count = gr.Slider(minimum=2, maximum=3, step=1, label="تعداد آهنگ‌ها", value=2)
        
    btn = gr.Button("🚀 ساخت ریمیکس متصل و روان", variant="primary")
    audio = gr.Audio(label="پادکست خروجی پایش‌آی")
    status = gr.Markdown("وضعیت: آماده میکس")
    
    btn.click(pishai_seamless_engine, [query, count], [audio, status])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
        
