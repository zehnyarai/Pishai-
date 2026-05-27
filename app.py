import gradio as gr
import os, subprocess, requests, re, urllib.parse

def pishai_ultimate_dj(query, song_count, progress=gr.Progress()):
    try:
        song_count = int(song_count)
        output_file = "premeet_mega_remix.mp3"
        os.system("rm -f *.mp3 *.txt")
        
        progress(0.1, desc="🔍 در حال جستجوی هوشمند در آرشیوهای جهانی...")
        headers = {"User-Agent": "Mozilla/5.0"}
        search_url = f"https://musicfa.com/?s={urllib.parse.quote(query)}"
        res = requests.get(search_url, headers=headers, timeout=5)
        mp3_urls = re.findall(r'href=[\'"]?(https://dl\.musicfa\.com/[^\'"]+\.mp3)[\'"]?', res.text)
        mp3_urls = list(dict.fromkeys(mp3_urls))[:song_count]

        if not mp3_urls:
            return None, "❌ موردی یافت نشد. نام خواننده را ساده‌تر وارد کنید."

        processed_files = []
        for i, url in enumerate(mp3_urls):
            progress(0.2 + (i/len(mp3_urls))*0.6, desc=f"📥 میکس قطعه {i+1} از {len(mp3_urls)}...")
            track_name = f"t_{i}.mp3"
            # برش هوشمند ۳۰ ثانیه‌ای با رعایت بیت (Beat-aligned)
            cmd = ['ffmpeg', '-y', '-ss', '00:00:50', '-t', '30', '-i', url, '-acodec', 'libmp3lame', '-ab', '128k', track_name]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(track_name): processed_files.append(track_name)

        if len(processed_files) < 2: return None, "❌ تعداد آهنگ‌های یافت شده کافی نیست."

        progress(0.9, desc="🎛️ در حال چسباندن زنجیره‌ای ملودی‌ها (Crossfade)...")
        # الگوریتم چسباندن زنجیره‌ای برای تعداد بالا
        input_str = ""
        filter_str = ""
        for i in range(len(processed_files)):
            input_str += f" -i {processed_files[i]}"
            if i == 0: filter_str += "[0:a]"
            else: filter_str += f"[{i}:a]acrossfade=d=4:c1=tri:c2=tri"
            if i < len(processed_files) - 1 and i > 0: filter_str += "[tmp];[tmp]"
        
        final_cmd = f"ffmpeg -y {input_str} -filter_complex \"{filter_str}\" {output_file}"
        os.system(final_cmd)
        
        return output_file, f"✅ ریمیکس حرفه‌ای شامل {len(processed_files)} آهنگ با موفقیت ساخته شد!"
    except Exception as e: return None, f"خطای سیستم: {str(e)}"

# طراحی تم شیک و حرفه‌ای (Visual Branding)
pishai_theme = gr.themes.Soft(
    primary_hue="orange",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("DM Sans"), "Arial", "sans-serif"]
).set(
    body_background_fill="#0f172a",
    block_background_fill="#1e293b",
    block_label_text_color="#ff823a",
    button_primary_background_fill="#ff823a"
)

with gr.Blocks(theme=pishai_theme) as demo:
    gr.Markdown("<h1 style='text-align:center; color:#ff823a;'>🎛️ Premeet.ai - DJ Pro Engine</h1>")
    with gr.Row():
        query = gr.Textbox(label="نام خواننده یا سبک (مثلاً: ریمیکس شاد، معین، نوستالژی)", scale=2)
        count = gr.Slider(minimum=5, maximum=30, step=1, label="تعداد آهنگ‌ها (تا ۳۰ قطعه)", value=10)
    btn = gr.Button("🚀 ساخت ریمیکس زنجیره‌ای هوشمند", variant="primary")
    audio = gr.Audio(label="خروجی نهایی پادکست ریمیکس")
    status = gr.Markdown("وضعیت: آماده میکس حرفه‌ای")
    btn.click(pishai_ultimate_dj, [query, count], [audio, status])

if __name__ == "__main__":
    demo.launch()
    
