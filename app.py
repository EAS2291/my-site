import streamlit as st
import requests
import os

st.set_page_config(page_title="Моя ИИ Студия", page_icon="🎨")

st.title("🎨 Моя личная ИИ-Студия")
st.write("Здесь вы можете бесплатно создавать картинки и видео.")

tab1, tab2 = st.tabs(["🖼️ Создать картинку", "🎬 Создать видео"])

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

with tab2:
    st.header("Генерация видео")
    video_prompt = st.text_input("Опишите видео:", key="vid_prompt")
    
    if st.button("Создать видео!"):
        if video_prompt:
            with st.spinner("Отправляем запрос в Agnes AI..."):
                api_key = st.secrets.get("AGNES_API_KEY", "")
                
                if not api_key:
                    st.error("Ошибка: Ключ Agnes не добавлен в настройках сайта.")
                else:
                    headers = {"Authorization": f"Bearer {api_key}"}
                    payload = {
                        "model": "agnes-video-2.0",
                        "prompt": video_prompt,
                        "mode": "text"  # ← Обязательный параметр
                    }
                    try:
                        response = requests.post("https://apihub.agnes-ai.com/v1/videos", json=payload, headers=headers)
                        st.write(f"Статус ответа: {response.status_code}")
                        st.write(f"Ответ сервера: {response.text}")
                    except Exception as e:
                        st.error(f"Ошибка при создании видео: {e}")
        else:
            st.warning("Пожалуйста, напишите описание!")
