import gradio as gr
import os
import subprocess
import requests
from bs4 import BeautifulSoup
import urllib.parse

def search_fast_sources(query, count):
    """جستجوی بسیار سریع با کنترل دقیق زمان پاسخ سرور (Timeout)"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    mp3_links = []
    
    # لیست منابع با اولویت پایداری و سرعت پاسخ‌دهی بدون کلودفلر
    sources = [
        f"https://nex1music.ir/?s={urllib.parse.quote(query)}",
        f"https://upmusics.com/?s={urllib.parse.quote(query)}"
    ]
    
    for url in sources:
        if len(mp3_links) >= count:
            break
        try:
            # زمان انتظار فقط ۲ ثانیه است تا اگر سایتی بلاک بود، برنامه کند نشود
            res = requests.get(url, headers=headers, timeout=2.5)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.endswith(".mp3") and "preview" not in href.lower() and "demo" not in href.lower():
                        if href not in mp3_links:
                            mp3_links.append(href)
                            if len(mp3_links) >= count:
                                break
        except:
            continue # در صورت بروز هرگونه تاخیر یا خطا، فوراً به منبع بعدی می‌رود
            
    return mp3_links[:count]

def pishai_turbo_engine(genre_query, song_count, progress=gr.Progress()):
    try:
        song_count = int(song_count)
        output_file = "pishai_turbo_remix.mp3"
        
        # پاکسازی دیسک
        os.system("rm -f *.mp3 *.txt")
        
        if not genre_query.strip():
            return None, "❌ لطفاً نام خواننده یا سبک را وارد کنید."
            
        progress(0.1, desc="🔍 خزش برق‌آسا در سرورهای موزیک...")
        mp3_urls = search_fast_sources(genre_query, song_count)
        
        if not mp3_urls:
            return None, f"❌ موزیکی برای '{genre_query}' یافت نشد. نام خواننده را ساده‌تر بنویسید."
            
        processed_files = []
        
        # بهینه‌سازی دانلود: برش از ثانیه ۱۰ برای دانلود فوق‌سریع قطعات
        for i, url in enumerate(mp3_urls):
            progress(0.2 + (i / len(mp3_urls)) * 0.5, desc=f"📥 برش و دریافت فوری قطعه {i+1}...")
            track_name = f"t_{i}.mp3"
            
            # انتقال ss به ابتدای دستور، سرعت استریم و کات FFmpeg را انقلابی می‌کند
            cmd = [
                'ffmpeg', '-y', '-ss', '00:00:15', '-t', '30',
                '-i', url, '-acodec', 'libmp3lame', '-ab', '128k',
                track_name
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(track_name) and os.path.getsize(track_name) > 10000:
                processed_files.append(track_name)

        if not processed_files:
            return None, "❌ خطا در دریافت قطعات موسیقی. مجدداً دکمه را بزنید."

        progress(0.8, desc="🎛️ همگام‌سازی ملودی‌ها و میکس دی‌جی (Crossfade)...")
        
        # ترکیب و میکس فرکانسی ریتمیک قطعات به هم
        inputs_count = len(processed_files)
        if inputs_count == 1:
            os.rename(processed_files[0], output_file)
        elif inputs_count == 2:
            subprocess.run(['ffmpeg', '-y', '-i', processed_files[0], '-i', processed_files[1], '-filter_complex', 'acrossfade=d=3:c1=tri:c2=tri', output_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif inputs_count == 3:
            subprocess.run(['ffmpeg', '-y', '-i', processed_files[0], '-i', processed_files[1], '-i', processed_files[2], '-filter_complex', 'acrossfade=d=3:c1=tri:c2=tri[a1];[a1][2:a]acrossfade=d=3:c1=tri:c2=tri', output_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            with open("concat_list.txt", "w") as f:
                for file in processed_files: f.write(f"file '{file}'\n")
            subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'concat_list.txt', '-c', 'copy', output_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # تمیزکاری فایل‌های موقت
        for f in processed_files:
            try: os.remove(f)
            except: pass
            
        if os.path.exists("concat_list.txt"): 
            os.remove("concat_list.txt")

        return output_file, f"🎵 پادکست ریمیکس ریتمیک و متصل با موفقیت در چند ثانیه ساخته شد!"

    except Exception as e:
        return None, f"خطای موتور میکس: {str(e)}"

# طراحی مدرن با عنوان مشخص تپ توربو
with gr.Blocks(theme=gr.themes.Default(primary_hue="orange", secondary_hue="zinc")) as demo:
    gr.Markdown("# 🎛️ Premeet.ai - pishai DJ Studio (Turbo Edition)")
    gr.Markdown("نسخه بهینه‌شده با سرعت بالا و قابلیت اتصال ریتمیک ملودی‌ها به صورت نرم (Crossfade).")
    
    with gr.Row():
        query = gr.Textbox(label="نام خواننده یا سبک ریمیکس", value="معین")
        count = gr.Slider(minimum=2, maximum=3, step=1, label="تعداد قطعات ریمیکس", value=2)
        
    btn = gr.Button("🚀 تولید و همگام‌سازی فوری ریمیکس", variant="primary")
    audio = gr.Audio(label="پادکست خروجی پایش‌آی")
    status = gr.Markdown("وضعیت: آماده میکس سریع")
    
    btn.click(pishai_turbo_engine, [query, count], [audio, status])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
    
