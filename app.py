import streamlit as st
import requests
import time
import base64
import io
from gtts import gTTS

st.set_page_config(page_title="Моя ИИ Студия PRO", page_icon="🎬")

st.title("🎬 Моя ИИ-Студия PRO")
st.write("Профессиональная генерация (Magic Hour).")

tab1, tab2, tab3, tab4 = st.tabs([
    "🖼️ Картинки", 
    "🎬 Видео из текста", 
    "🎞️ Оживить картинку", 
    "🎙️ Озвучка"
])

# --- ВКЛАДКА 1: КАРТИНКИ ---
with tab1:
    st.header("Генерация картинок")
    image_prompt = st.text_input("Опишите картинку (на английском):", key="img_prompt", value="A cute dog dancing in a field of daisies, highly detailed")
    
    if st.button("Нарисовать!"):
        if image_prompt:
            with st.spinner("Magic Hour рисует..."):
                api_key = st.secrets.get("MAGIC_HOUR_API_KEY", "")
                if not api_key:
                    st.error("Ошибка: Добавьте MAGIC_HOUR_API_KEY в Secrets!")
                else:
                    headers = {"Authorization": f"Bearer {api_key}"}
                    # ИСПРАВЛЕНИЕ: Добавлены обязательные поля image_count и style, выбрана модель
                    payload = {
                        "image_count": 1,
                        "model": "z-image-turbo", # Быстрая и качественная модель
                        "aspect_ratio": "16:9",
                        "resolution": "640px",
                        "style": {
                            "prompt": image_prompt,
                            "tool": "general" # Общий стиль
                        }
                    }
                    try:
                        response = requests.post("https://api.magichour.ai/v1/ai-image-generator", json=payload, headers=headers)
                        if response.status_code == 200:
                            res_data = response.json()
                            if res_data.get("status") == "complete":
                                st.image(res_data.get("image_url"), caption="Готово!")
                            else:
                                st.info(f"Задача создана! ID: {res_data.get('project_id')}. Подождите...")
                        else:
                            st.error(f"Ошибка API: {response.text}")
                    except Exception as e:
                        st.error(f"Ошибка: {e}")

# --- ВКЛАДКА 2: ВИДЕО ИЗ ТЕКСТА ---
with tab2:
    st.header("Видео из текста")
    video_prompt = st.text_input("Опишите видео (на английском):", key="vid_prompt", value="A cat surfing on a wave at sunset, cinematic")
    
    if st.button("Создать видео!"):
        if video_prompt:
            with st.spinner("Генерируем..."):
                api_key = st.secrets.get("MAGIC_HOUR_API_KEY", "")
                if not api_key:
                    st.error("Ошибка: Ключ не найден.")
                else:
                    headers = {"Authorization": f"Bearer {api_key}"}
                    payload = {
                        "style": {"prompt": video_prompt},
                        "model": "ltx-2.5",
                        "end_seconds": 5,
                        "aspect_ratio": "16:9",
                        "resolution": "480p"
                    }
                    try:
                        response = requests.post("https://api.magichour.ai/v1/text-to-video", json=payload, headers=headers)
                        if response.status_code == 200:
                            res_data = response.json()
                            if res_data.get("status") == "complete":
                                st.video(res_data.get("video_url"))
                            else:
                                st.info(f"Задача создана! ID: {res_data.get('project_id')}. Подождите немного.")
                        else:
                            st.error(f"Ошибка API: {response.text}")
                    except Exception as e:
                        st.error(f"Ошибка: {e}")

# --- ВКЛАДКА 3: ОЖИВЛЕНИЕ КАРТИНКИ ---
with tab3:
    st.header("Оживление картинки")
    uploaded_file = st.file_uploader("Выберите картинку...", type=["jpg", "jpeg", "png"])
    animation_prompt = st.text_input("Опишите движение:", key="anim_prompt", value="smooth motion, camera slowly zooming in")
    
    if st.button("Оживить!"):
        if uploaded_file is None:
            st.warning("Загрузите картинку.")
        else:
            with st.spinner("Оживляем..."):
                api_key = st.secrets.get("MAGIC_HOUR_API_KEY", "")
                if not api_key:
                    st.error("Ошибка: Ключ не найден.")
                else:
                    try:
                        img_bytes = uploaded_file.read()
                        b64_img = base64.b64encode(img_bytes).decode('utf-8')
                        img_uri = f"data:image/jpeg;base64,{b64_img}"
                        
                        headers = {"Authorization": f"Bearer {api_key}"}
                        payload = {
                            "style": {"prompt": animation_prompt},
                            "model": "ltx-2.5",
                            "end_seconds": 5,
                            "resolution": "480p",
                            "audio": False,
                            "assets": {
                                "image_file_path": img_uri
                            }
                        }
                        
                        response = requests.post("https://api.magichour.ai/v1/image-to-video", json=payload, headers=headers)
                        
                        if response.status_code == 200:
                            res_data = response.json()
                            if res_data.get("status") == "complete":
                                st.video(res_data.get("video_url"))
                            else:
                                st.info(f"Задача создана! ID: {res_data.get('project_id')}. Подождите.")
                        else:
                            st.error(f"Ошибка API: {response.text}")
                    except Exception as e:
                        st.error(f"Ошибка: {e}")

# --- ВКЛАДКА 4: ОЗВУЧКА ---
with tab4:
    st.header("Озвучка текста")
    tts_text = st.text_area("Текст для озвучки:", key="tts_text")
    tts_lang = st.selectbox("Язык", ["ru", "en"], format_func=lambda x: "Русский" if x == "ru" else "Английский")
    
    if st.button("Озвучить!"):
        if not tts_text:
            st.warning("Введите текст.")
        else:
            with st.spinner("Генерируем голос..."):
                try:
                    tts = gTTS(text=tts_text, lang=tts_lang, slow=False)
                    audio_bytes = io.BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    st.success("Готово!")
                    st.audio(audio_bytes, format="audio/mp3")
                except Exception as e:
                    st.error(f"Ошибка: {e}")
