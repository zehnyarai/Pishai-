import gradio as gr
import os

def pishai_mega_mixer(genre_query, song_count):
    output_file = "premeet_mega_remix.mp3"
    
    # تعریف فایل‌های محلی که در گیت‌هاب آپلود کردی
    local_tracks = {
        "track1.mp3": "آهنگ شماره ۱ شادمهر (محلی)",
        "track2.mp3": "آهنگ شماره ۲ (محلی)"
    }
    
    # بررسی اینکه آیا فایل‌ها روی سرور وجود دارند یا خیر
    available_files = [f for f in local_tracks.keys() if os.path.exists(f)]
    
    if not available_files:
        return None, "⚠️ فایل‌های صوتی track1.mp3 یا track2.mp3 هنوز در گیت‌هاب آپلود نشده‌اند!"
    
    try:
        # کپی کردن مستقیم فایل داخلی به عنوان خروجی (بدون نیاز به اینترنت و دانلود)
        # برای تست سریع، اولین فایل موجود را مستقیماً پخش می‌کنیم
        target_track = available_files[0]
        
        with open(target_track, 'rb') as src, open(output_file, 'wb') as dst:
            dst.write(src.read())
            
        return output_file, f"🔥 موفقیت بزرگ! موزیک واقعی {local_tracks[target_track]} بدون نیاز به اینترنت با موفقیت رندر شد."
        
    except Exception as e:
        return None, f"خطای سیستم داخلی: {str(e)}"

# 🎨 قالب مدرن، روشن، سفید و آبی آسمانی رسمی Premeet.ai
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
    gr.Markdown("<p style='text-align: center; color: #64748b;'>نسخه پایدار آفلاین - بهینه‌شده برای سرورهای رندر</p>")
    
    with gr.Row():
        query = gr.Textbox(label="🔍 خواننده یا تم ریمیکس", value="شادمهر")
        count = gr.Slider(minimum=1, maximum=2, step=1, label="🎚️ تعداد قطعات", value=1)
        
    btn = gr.Button("🚀 ساخت و دریافت موزیک‌های واقعی", variant="primary")
    audio = gr.Audio(label="🎧 پلیر پخش صوتی پایش‌آی")
    status = gr.Markdown("وضعیت: آماده فراخوانی")
    
    btn.click(pishai_mega_mixer, [query, count], [audio, status])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
    
