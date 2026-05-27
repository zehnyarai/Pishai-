import gradio as gr
import os
import subprocess
import requests
import re
import urllib.parse

def fetch_mega_tracks(query, count):
    """استخراج هوشمند لینک‌های صوتی با لایه پشتیبان تضمینی"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    links = []
    cleaned_query = urllib.parse.quote(query)
    
    try:
        url = f"https://musicfa.com/?s={cleaned_query}"
        res = requests.get(url, headers=headers, timeout=7)
        if res.status_code == 200:
            found = re.findall(r'href=[\'"]?(https://dl\.musicfa\.com/[^\'"]+\.mp3)[\'"]?', res.text)
            for l in found:
                if "dem" not in l.lower() and l not in links:
                    links.append(l)
    except:
        pass

    # آرشیو همیشه پایدار برای جلوگیری از خالی ماندن دست لیست صوتی
    backup_pool = [
        "https://dl.nex1music.ir/1402/08/21/Shadmehr%20Aghili%20-%20Tamasha%20[128].mp3",
        "https://dl.nex1music.ir/1402/05/20/Sohrab%20Pakzad%20-%20Mooye%20Anabi%20[128].mp3",
        "https://dl.nex1music.ir/1402/02/04/Mohammad%20Alizadeh%20-%20Khosh%20Mashi%20[128].mp3",
        "https://dl.musicfa.com/music/1400/08/02/Macan%20Band%20-%20Bi%20Ghoghnoos%20(128).mp3",
        "https://dl.musicfa.com/music/1400/11/17/Aron%20Afshar%20-%20Khande%20Hato%20Ghorban%20(128).mp3"
    ]
    
    index = 0
    while len(links) < count and len(links) < 30:
        links.append(backup_pool[index % len(backup_pool)])
        index += 1
            
    return links[:count]

def pishai_mega_mixer(genre_query, song_count, progress=gr.Progress(track_tqdm=True)):
    try:
        song_count = int(song_count)
        output_file = "premeet_mega_remix.mp3"
        
        # پاکسازی امن فایلهای قدیمی
        if os.path.exists(output_file):
            os.remove(output_file)
            
        os.system("rm -f t_*.mp3 mylist.txt")
        
        if not genre_query.strip():
            return None, "❌ نام خواننده یا سبک وارد نشده است."
            
        progress(0.05, desc="🔍 استخراج زنجیره صوتی از دیتابیس...")
        mp3_urls = fetch_mega_tracks(genre_query, song_count)
        
        processed_files = []
        
        # فرآیند دانلود و کات تک‌به‌تک صوتی با آپدیت زنده وضعیت
        for i, url in enumerate(mp3_urls):
            current_pct = 0.1 + (i / len(mp3_urls)) * 0.7
            progress(current_pct, desc=f"📥 در حال پردازش و کات قطعه {i+1} از {len(mp3_urls)}...")
            
            track_name = f"t_{i}.mp3"
            
            # استفاده از ساختار استاندارد شده کامند لاین برای سرور لینوکس
            cmd = f"ffmpeg -y -ss 00:00:45 -t 30 -i \"{url}\" -acodec libmp3lame -ab 128k {track_name}"
            
            try:
                os.system(cmd)
                if os.path.exists(track_name) and os.path.getsize(track_name) > 10000:
                    processed_files.append(track_name)
            except:
                continue

        if len(processed_files) < 1:
            return None, "⚠️ سرور در این لحظه شلوغ است. لطفا مجددا دکمه را بزنید."

        progress(0.85, desc="🎛️ اتصال و همگام‌سازی بیت‌های صوتی ریمیکس...")
        
        # ایجاد لیست متنی الحاق
        with open("mylist.txt", "w") as f:
            for file in processed_files:
                f.write(f"file '{file}'\n")
                
        # ترکیب نهایی قطعات
        concat_cmd = f"ffmpeg -y -f concat -safe 0 -i mylist.txt -acodec libmp3lame -ab 128k {output_file}"
        os.system(concat_cmd)

        # تمیزکاری دیسک پس از اتمام
        os.system("rm -f t_*.mp3 mylist.txt")

        if os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
            return output_file, f"⚡ مگا پادکست شامل {len(processed_files)} قطعه با موفقیت میکس شد!"
        else:
            return None, "❌ خطا در تولید فایل نهایی."

    except Exception as e:
        return None, f"خطای سیستم: {str(e)}"

# 🎨 قالب روشن، شیک، سفید و آبی آسمانی
premeet_sky_theme = gr.themes.Soft(
    primary_hue="blue",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("DM Sans"), "Tahoma", "sans-serif"]
).set(
    body_background_fill="#f3f8fc",
    block_background_fill="#ffffff",
    block_label_text_color="#2563eb",
    input_background_fill="#f8fafc",
    button_primary_background_fill="#3b82f6",
    button_primary_text_color="#ffffff"
)

with gr.Blocks(theme=premeet_sky_theme) as demo:
    gr.Markdown("<h1 style='text-align: center; color: #1e40af; font-family: sans-serif; margin-top: 10px;'>🎛️ Premeet.ai - pishai Studio Pro</h1>")
    gr.Markdown("<p style='text-align: center; color: #64748b;'>موتور هوشمند ساخت پادکست ریمیکس طولانی و زنجیره‌ای ملودی‌ها (تا ۳۰ آهنگ متوالی)</p>")
    
    with gr.Row():
        query = gr.Textbox(label="🔍 خواننده یا تم ریمیکس", value="شادمهر")
        count = gr.Slider(minimum=2, maximum=30, step=1, label="🎚️ تعداد قطعات زنجیره صوتی", value=5)
        
    btn = gr.Button("🚀 ساخت مگا پادکست ریمیکس متصل", variant="primary")
    audio = gr.Audio(label="🎧 فایل ریمیکس نهایی و پیوسته پایش‌آی")
    status = gr.Markdown("وضعیت: آماده پردازش و میکس دسته‌ای آهنگ‌ها")
    
    btn.click(pishai_mega_mixer, [query, count], [audio, status])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
    
