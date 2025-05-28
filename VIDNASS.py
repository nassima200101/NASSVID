import streamlit as st
import requests
from gtts import gTTS
import base64
import tempfile

# === واجهة التطبيق ===
st.set_page_config(page_title="PixVid Nes - AI Face Talking Tool")
st.title("🧠 PixVid Nes - حول صورة وجه إلى فيديو متكلم")
st.markdown("👧✨ ارفعي صورة، اكتبي النص، وشاهديها تتكلم!")

# === مدخلات المستخدم ===
image_file = st.file_uploader("📸 ارفعي صورة فيها وجه (PNG أو JPG)", type=["png", "jpg", "jpeg"])
text_input = st.text_area("✍️ اكتبي النص اللي تحبي الشخصية تقولو")
lang = st.selectbox("🌐 اختاري اللغة", ["ar", "en"])

if st.button("🎬 أنشئ الفيديو") and image_file and text_input:
    with st.spinner("⏳ جاري تحويل النص إلى صوت..."):
        tts = gTTS(text=text_input, lang=lang)
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_audio.name)

    with open(temp_audio.name, "rb") as f:
        audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    with st.spinner("📤 جاري إرسال الطلب إلى D-ID..."):
        api_key = "bmVsbGFuZXJvMTdAZ21haWwuY29t:UCOl3RVYFJPEojz_UZ_wQ"  # <-- هنا نحط المفتاح من حسابي أو حسابك
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # نحمل الصورة موقتا
        image_bytes = image_file.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        payload = {
            "source_url": f"data:image/jpeg;base64,{image_b64}",
            "script": {
                "type": "audio",
                "audio": f"data:audio/mp3;base64,{audio_b64}"
            }
        }

        response = requests.post("https://api.d-id.com/talks", headers=headers, json=payload)

        if response.status_code == 200:
            talk_id = response.json().get("id")
            st.success("🎉 تم إرسال الفيديو! ننتظر التحميل...")

            # ننتظر حتى الفيديو يجهز
            import time
            for _ in range(30):
                status = requests.get(f"https://api.d-id.com/talks/{talk_id}", headers=headers)
                result = status.json()
                if result.get("result_url"):
                    st.video(result["result_url"])
                    break
                time.sleep(2)
            else:
                st.error("⏳ فات الوقت ولم يتم تجهيز الفيديو بعد. حاولي مرة أخرى!")
        else:
            st.error("❌ حدث خطأ أثناء إرسال الطلب إلى D-ID")
