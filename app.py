import streamlit as st
import requests
import time
import base64
import io
from gtts import gTTS

st.set_page_config(page_title="Моя ИИ Студия", page_icon="🎨")

st.title("🎨 Моя личная ИИ-Студия")
st.write("Здесь вы можете бесплатно создавать картинки, видео и озвучку.")

# Создаем 4 вкладки
tab1, tab2, tab3, tab4 = st.tabs([
    "🖼️ Создать картинку", 
    "🎬 Видео из текста", 
    "🎞️ Оживить картинку", 
    "🎙️ Озвучка"
])

# --- ВКЛАДКА 1: КАРТИНКИ ---
with tab1:
    st.header("Генерация картинок")
    image_prompt = st.text_input("Опишите, что вы хотите увидеть:", key="img_prompt")
    if st.button("Нарисовать!"):
        if image_prompt:
            with st.spinner("Нейросеть рисует..."):
                try:
                    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(image_prompt)}"
                    st.image(url, caption="Ваша картинка готова!")
                except Exception as e:
                    st.error(f"Произошла ошибка: {e}")
        else:
            st.warning("Пожалуйста, напишите описание!")

# --- ВКЛАДКА 2: ВИДЕО ИЗ ТЕКСТА ---
with tab2:
    st.header("Генерация видео по тексту")
    video_prompt = st.text_input("Опишите видео:", key="vid_prompt")
    if st.button("Создать видео!"):
        if video_prompt:
            with st.spinner("Отправляем запрос в Agnes AI..."):
                api_key = st.secrets.get("AGNES_API_KEY", "")
                if not api_key:
                    st.error("Ошибка: Ключ Agnes не найден.")
                else:
                    headers = {"Authorization": f"Bearer {api_key}"}
                    payload = {
                        "model": "agnes-video-2.5-flash",
                        "prompt": video_prompt,
                        "mode": "text",
                        "size": "720P",
                        "seconds": "5"
                    }
                    try:
                        response = requests.post("https://apihub.agnes-ai.com/v1/videos", json=payload, headers=headers)
                        if response.status_code == 200:
                            st.success("Задача создана! Подождите...")
                        else:
                            st.error(f"Ошибка API: {response.text}")
                    except Exception as e:
                        st.error(f"Ошибка: {e}")

# --- ВКЛАДКА 3: ОЖИВЛЕНИЕ КАРТИНКИ (МУЛЬТИКИ) ---
with tab3:
    st.header("Оживление картинки (Image-to-Video)")
    st.write("Загрузите картинку, и нейросеть превратит её в видео.")
    
    uploaded_file = st.file_uploader("Выберите картинку (JPG, PNG)...", type=["jpg", "jpeg", "png"])
    animation_prompt = st.text_input("Опишите движение (например: 'камера медленно приближается, персонаж моргает'):", key="anim_prompt")
    
    if st.button("Оживить!"):
        if uploaded_file is None:
            st.warning("Пожалуйста, загрузите картинку.")
        elif not animation_prompt:
            st.warning("Пожалуйста, опишите движение.")
        else:
            api_key = st.secrets.get("AGNES_API_KEY", "")
            if not api_key:
                st.error("Ошибка: Ключ Agnes не найден.")
            else:
                with st.spinner("Оживляем картинку... Это займет около 1-2 минут."):
                    try:
                        # Превращаем картинку в base64
                        img_bytes = uploaded_file.read()
                        b64_img = base64.b64encode(img_bytes).decode('utf-8')
                        img_uri = f"data:image/jpeg;base64,{b64_img}"
                        
                        headers = {"Authorization": f"Bearer {api_key}"}
                        payload = {
                            "model": "agnes-video-2.5-flash",
                            "prompt": animation_prompt,
                            "mode": "keyframe",
                            "first_frame": img_uri, # Передаем картинку как первый кадр
                            "size": "720P",
                            "seconds": "5"
                        }
                        
                        response = requests.post("https://apihub.agnes-ai.com/v1/videos", json=payload, headers=headers)
                        
                        if response.status_code == 200:
                            video_id = response.json().get("video_id")
                            st.success(f"Задача создана! ID: {video_id}")
                            
                            # Ждем результат
                            status_placeholder = st.empty()
                            video_url = None
                            with st.spinner("Генерируем видео... Пожалуйста, подождите."):
                                for _ in range(30):
                                    time.sleep(2)
                                    status_url = f"https://apihub.agnes-ai.com/agnesapi?video_id={video_id}&model_name=agnes-video-2.5-flash"
                                    status_response = requests.get(status_url, headers=headers)
                                    
                                    if status_response.status_code == 200:
                                        data = status_response.json()
                                        if data.get("status") == "completed":
                                            video_url = data.get("url")
                                            st.success("Видео готово!")
                                            st.video(video_url)
                                            break
                                        elif data.get("status") == "failed":
                                            st.error("Генерация видео не удалась.")
                                            break
                                    status_placeholder.text("Все еще генерируем...")
                        else:
                            st.error(f"Ошибка API: {response.text}")
                    except Exception as e:
                        st.error(f"Ошибка: {e}")

# --- ВКЛАДКА 4: ОЗВУЧКА (TTS) ---
with tab4:
    st.header("Озвучка текста (Text-to-Speech)")
    st.write("Введите текст, и нейросеть озвучит его.")
    
    tts_text = st.text_area("Текст для озвучки:", key="tts_text")
    tts_lang = st.selectbox("Выберите язык", ["ru", "en"], format_func=lambda x: "Русский" if x == "ru" else "Английский")
    
    if st.button("Озвучить!"):
        if not tts_text:
            st.warning("Пожалуйста, введите текст.")
        else:
            with st.spinner("Генерируем голос..."):
                try:
                    # Создаем аудио
                    tts = gTTS(text=tts_text, lang=tts_lang, slow=False)
                    audio_bytes = io.BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    
                    st.success("Голос готов!")
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button(
                        label="Скачать аудио",
                        data=audio_bytes,
                        file_name="voiceover.mp3",
                        mime="audio/mp3"
                    )
                except Exception as e:
                    st.error(f"Ошибка при озвучке: {e}")
