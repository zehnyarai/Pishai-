import gradio as gr
import os
import subprocess
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def search_smart_google_links(query, count):
    """استخراج مستقیم و بسیار سریع لینک‌های mp3 با دور زدن ساختار امنیتی سایت‌ها"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # سرچ متمرکز برای یافتن مستقیم فایل‌های صوتی ۱۲۸ یا ۳۲۰ روی وب فارسی
    search_url = f"https://www.google.com/search?q=site:ir+دانلود+آهنگ+{urllib.parse.quote(query)}+mp3"
    mp3_links = []
    
    try:
        response = requests.get(search_url, headers=headers, timeout=4)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # استخراج لینک‌های خام بدون وارد شدن مستقیم به سایت‌ها (جلوگیری از بلاک شدن آی‌پي)
        all_text = str(soup)
        links = re.findall(r'(https?://[^\s\'"]+\.mp3)', all_text)
        
        for link in links:
            if "preview" not in link.lower() and "demo" not in link.lower():
                if link not in mp3_links:
                    mp3_links.append(link)
                    if len(mp3_links) >= count + 2: # دریافت چند لینک زاپاس
                        break
    except:
        pass
        
    # اگر گوگل به آی‌پی سرور رندر حساس شد، از موتور پشتیبان نکسوان به روش امن استفاده کن
    if not mp3_links:
        try:
            res = requests.get(f"https://nex1music.ir/?s={urllib.parse.quote(query)}", headers=headers, timeout=3)
            mp3_links = list(set(re.findall(r'(https://dl\.nex1music\.ir/[^\s\'"]+\.mp3)', res.text)))
        except:
            pass

    return mp3_links[:count]

def pishai_super_turbo_engine(genre_query, song_count, progress=gr.Progress()):
    try:
        song_count = int(song_count)
        output_file = "pishai_final_master.mp3"
        
        # تمیزکاری دیسک سرور رندر
        os.system("rm -f *.mp3 *.txt")
        
        if not genre_query.strip():
            return None, "❌ لطفاً نام خواننده یا سبک را وارد کنید."
            
        progress(0.1, desc="🔍 استخراج موازی لینک‌های صوتی با موتور هوشمند...")
        mp3_urls = search_smart_google_links(genre_query, song_count)
        
        if not mp3_urls:
            return None, f"❌ موزیکی برای '{genre_query}' یافت نشد. لطفاً کلمه کلیدی را ساده‌تر کنید (مثال: شاد، معین)."
            
        processed_files = []
        
        # دانلود و کات همزمان با تکنیک سریع Stream
        for i, url in enumerate(mp3_urls):
            progress(0.2 + (i / len(mp3_urls)) * 0.5, desc=f"⚡ رندر صوتی و کات ریتمیک قطعه {i+1}...")
            track_name = f"t_{i}.mp3"
            
            # انتقال دستور برش صوتی به ابتدای فایل (ثانیه ۱۵) حجم دانلود را ناچیز و سرعت را نجومی می‌کند
            cmd = [
                'ffmpeg', '-y', '-t', '30', '-headers', 'User-Agent: Mozilla/5.0\r\n',
                '-ss', '00:00:15', '-i', url, '-acodec', 'libmp3lame', '-ab', '128k',
                track_name
            ]
            
            # اجرای دستور با حداکثر مهلت دانلود سریع
            try:
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=12)
                if os.path.exists(track_name) and os.path.getsize(track_name) > 15000:
                    processed_files.append(track_name)
            except subprocess.TimeoutExpired:
                continue # اگر سروری کند بود، معطلش نکن و برو بعدی

        if not processed_files:
            return None, "❌ سرورهای مبدا با تاخیر مواجه شدند. لطفاً مجدداً دکمه ساخت را بزنید."

        progress(0.8, desc="🎛️ اعمال افکت Crossfade و میکس نهایی ملودی‌ها...")
        
        # ترکیب صوتی دی‌جی ریمیکس با افکت محو شدن تدریجی ملودی‌ها در هم
        inputs_count = len(processed_files)
        if inputs_count == 1:
            os.rename(processed_files[0], output_file)
        elif inputs_count == 2:
            subprocess.run(['ffmpeg', '-y', '-i', processed_files[0], '-i', processed_files[1], '-filter_complex', 'acrossfade=d=3:c1=tri:c2=tri', output_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(['ffmpeg', '-y', '-i', processed_files[0], '-i', processed_files[1], '-i', processed_files[2], '-filter_complex', 'acrossfade=d=3:c1=tri:c2=tri[a1];[a1][2:a]acrossfade=d=3:c1=tri:c2=tri', output_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # حذف فایلهای اضافه برای بهینه‌سازی دیسک داکر
        for f in processed_files:
            try: os.remove(f)
            except: pass

        return output_file, f"🔥 پادکست میکس‌شده ریتمیک Premeet.ai با موفقیت آماده دانلود است!"

    except Exception as e:
        return None, f"خطای پردازش سرور: {str(e)}"

with gr.Blocks(theme=gr.themes.Default(primary_hue="orange", secondary_hue="zinc")) as demo:
    gr.Markdown("# 🎛️ Premeet.ai - pishai Studio (Turbo DJ v3)")
    gr.Markdown("نسخه فوق‌سریع و هوشمند ریمیکس زنجیره‌ای ملودی‌ها بدون تاخیر سرور.")
    
    with gr.Row():
        query = gr.Textbox(label="نام خواننده یا سبک موسیقی (فارسی یا انگلیسی)", value="معین")
        count = gr.Slider(minimum=2, maximum=3, step=1, label="تعداد قطعات پادکست ریمیکس", value=2)
        
    btn = gr.Button("🚀 ساخت پادکست ریمیکس فوری", variant="primary")
    audio = gr.Audio(label="فایل پادکست میکس‌شده نهایی")
    status = gr.Markdown("وضعیت: آماده میکس فوق‌سریع")
    
    btn.click(pishai_super_turbo_engine, [query, count], [audio, status])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
        
