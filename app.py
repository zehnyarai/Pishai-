import gradio as gr
import yt_dlp
import os
import subprocess

def pishai_unlimited_engine(genre_query, song_count, progress=gr.Progress()):
    try:
        song_count = int(song_count)
        output_file = "pishai_render_podcast.mp3"
        list_file = "concat_list.txt"
        
        os.system("rm -f *.mp3 *.txt *.m4a *.webm")
        
        progress(0.1, desc="در حال جستجوی موزیک‌های مختلف در سراسر اینترنت...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extract_flat': True,
            'default_search': f'ytsearch{song_count}',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(genre_query, download=False)
            entries = search_results.get('entries', [])

        if not entries:
            return None, "❌ هیچ آهنگی پیدا نشد."

        processed_files = []

        for i, entry in enumerate(entries[:song_count]):
            track_name = f"t_{i}.mp3"
            url = entry.get('url') or entry.get('webpage_url')
            if not url: continue
            
            progress((i+1)/(song_count + 1), desc=f"دانلود و کات کردن آهنگ {i+1} از {song_count}...")
            
            cmd = [
                'ffmpeg', '-y', '-ss', '00:00:50', '-t', '40',
                '-i', url, '-acodec', 'libmp3lame', '-ab', '192k',
                '-af', 'afade=t=in:st=0:d=4,afade=t=out:st=36:d=4',
                track_name
            ]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(track_name) and os.path.getsize(track_name) > 10000:
                processed_files.append(track_name)

        if processed_files:
            with open(list_file, "w") as f:
                for file in processed_files: f.write(f"file '{file}'\n")
            
            subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_file, '-c', 'copy', output_file])
            for f in processed_files: os.remove(f)
            if os.path.exists(list_file): os.remove(list_file)
                
            return output_file, f"🔥 پادکست ریمیکس با موفقیت از {len(processed_files)} آهنگ ساخته شد!"
        
        return None, "❌ خطا در پردازش قطعات صوتی."

    except Exception as e:
        return None, f"خطای سرور رندر: {str(e)}"

with gr.Blocks(theme=gr.themes.Default(primary_hue="orange")) as demo:
    gr.Markdown("# 🎛️ Premeet.ai - pishai Studio (Render Edition)")
    with gr.Row():
        query = gr.Textbox(label="سبک موسیقی یا نام خوانندگان", value="ریمیکس شاد جدید")
        count = gr.Number(label="تعداد آهنگ", value=5)
    btn = gr.Button("🚀 ساخت پادکست بدون محدودیت", variant="primary")
    audio = gr.Audio(label="فایل نهایی")
    status = gr.Markdown("وضعیت: آماده")
    
    btn.click(pishai_unlimited_engine, [query, count], [audio, status])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
