import gradio as gr
import yt_dlp
import os
import subprocess

def pishai_unlimited_engine(genre_query, song_count, progress=gr.Progress()):
    try:
        song_count = int(song_count)
        output_file = "pishai_render_podcast.mp3"
        list_file = "concat_list.txt"
        
        # پاکسازی فایل‌های صوتی احتمالی قبلی
        os.system("rm -f *.mp3 *.txt *.m4a *.webm")
        
        progress(0.1, desc="در حال جستجوی موزیک‌های مختلف در سراسر اینترنت...")
        
        # تنظیمات جستجوی بسیار ساده و بدون تداخل با سرور
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'default_search': 'ytsearch', # موتور جستجوی استاندارد یوتیوب
        }
        
        search_term = f"{genre_query} music"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # جستجو برای یافتن ۲۰ نتیجه اولیه تا دستمان برای انتخاب باز باشد
            search_results = ydl.extract_info(f"ytsearch20:{search_term}", download=False)
            entries = search_results.get('entries', [])

        if not entries:
            return None, "❌ هیچ آهنگی در دیتابیس پیدا نشد. لطفاً عبارت دیگری را سرچ کنید."

        processed_files = []
        downloaded_count = 0

        # چرخیدن روی نتایج پیدا شده تا به تعداد درخواستی کاربر برسیم
        for entry in entries:
            if downloaded_count >= song_count:
                break
                
            if not entry: 
                continue
                
            url = entry.get('url') or entry.get('webpage_url')
            if not url or "shorts" in url: # رد کردن ویدیوهای کوتاه شورتز یوتیوب
                continue
                
            track_name = f"t_{downloaded_count}.mp3"
            progress(0.2 + (downloaded_count / song_count) * 0.6, desc=f"دانلود و کات کردن آهنگ {downloaded_count + 1} از {song_count}...")
            
            # کات کردن مستقیم ۳۰ ثانیه از آهنگ بدون دانلود کل فایل
            cmd = [
                'ffmpeg', '-y', '-ss', '00:00:40', '-t', '30',
                '-i', url, '-acodec', 'libmp3lame', '-ab', '128k',
                '-af', 'afade=t=in:st=0:d=3,afade=t=out:st=27:d=3',
                track_name
            ]
            
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # بررسی اینکه فایل با موفقیت ایجاد شده و خالی نیست
            if os.path.exists(track_name) and os.path.getsize(track_name) > 10000:
                processed_files.append(track_name)
                downloaded_count += 1

        # چسباندن قطعات دانلود شده
        if processed_files:
            progress(0.9, desc="در حال ترکیب و میکس نهایی پادکست...")
            with open(list_file, "w") as f:
                for file in processed_files: 
                    f.write(f"file '{file}'\n")
            
            subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_file, '-c', 'copy', output_file])
            
            # تمیزکاری دیسک سرور
            for f in processed_files: 
                try: os.remove(f)
                except: pass
            if os.path.exists(list_file): 
                os.remove(list_file)
                
            return output_file, f"🔥 پادکست ریمیکس با موفقیت از {len(processed_files)} آهنگ متفاوت ساخته شد!"
        
        return None, "❌ سرور نتوانست قطعات صوتی را استخراج کند. نام یک خواننده مشخص را تست کنید."

    except Exception as e:
        return None, f"خطای سرور رندر: {str(e)}"

with gr.Blocks(theme=gr.themes.Default(primary_hue="orange")) as demo:
    gr.Markdown("# 🎛️ Premeet.ai - pishai Studio (Render Edition)")
    with gr.Row():
        query = gr.Textbox(label="سبک موسیقی یا نام خوانندگان", value="شاد نوستالژی")
        count = gr.Number(label="تعداد آهنگ", value=3)
    btn = gr.Button("🚀 ساخت پادکست بدون محدودیت", variant="primary")
    audio = gr.Audio(label="فایل نهایی")
    status = gr.Markdown("وضعیت: آماده")
    
    btn.click(pishai_unlimited_engine, [query, count], [audio, status])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
