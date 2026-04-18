import streamlit as st
import cv2
import numpy as np
import pandas as pd
import os
import random

try:
    from deepface import DeepFace
    MOCK_MODE = False
except ImportError:
    MOCK_MODE = True
    class DeepFace:
        @staticmethod
        def analyze(img_path, actions=None, enforce_detection=False):
            import time
            time.sleep(1.5) # Giả lập độ trễ xử lý
            emotions = ['happy', 'sad', 'neutral', 'angry', 'fear', 'surprise', 'disgust']
            return [{'dominant_emotion': random.choice(emotions)}]

# Cấu hình trang
st.set_page_config(page_title="GenZ Lofi Mood-Sync", page_icon="🎵", layout="wide")

# Mapping cảm xúc sang từ khóa Vibe/Mood
emotion_mapping = {
    'happy': ['Upbeat', 'Happy', 'Sweet', 'Fresh', 'Fun', 'Groove', 'Sunny', 'Uplifting', 'Tropical', 'Breezy', 'Positive', 'Energetic', 'Playful'],
    'sad': ['Melancholic', 'Emotional', 'Sad', 'Lonely', 'Dark', 'Introspective', 'Longing', 'Bittersweet', 'Moody', 'Overcast', 'Lost', 'Cold'],
    'neutral': ['Calm', 'Relaxed', 'Chill', 'Peaceful', 'Soft', 'Ambient', 'Cozy', 'Warm', 'Smooth', 'Focus', 'Atmospheric', 'Gentle', 'Reflective'],
    'angry': ['Raw', 'Raw / Soulful', 'Gritty', 'Dark', 'Deep', 'Gritty', 'Smoky', 'Storm'],
    'fear': ['Dark', 'Deep', 'Nocturnal', 'Empty', 'Cinematic', 'Atmospheric', 'Misty'],
    'surprise': ['Exotic', 'Adventurous', 'Magical', 'Cosmic', 'Ethereal', 'Unique'],
    'disgust': ['Quirky', 'Smoky', 'Retro', 'Strange']
}

# Mapping cảm xúc sang màu nền (gradient)
emotion_colors = {
    'happy': 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)', # Vàng cam
    'sad': 'linear-gradient(135deg, #1E90FF 0%, #00008B 100%)', # Xanh lam
    'neutral': 'linear-gradient(135deg, #5f2c82 0%, #49a09d 100%)', # Tím Teal
    'angry': 'linear-gradient(135deg, #FF4500 0%, #8B0000 100%)', # Đỏ
    'fear': 'linear-gradient(135deg, #4A4A4A 0%, #000000 100%)', # Đen/Xám đậm
    'surprise': 'linear-gradient(135deg, #9370DB 0%, #4B0082 100%)', # Tím
    'disgust': 'linear-gradient(135deg, #556B2F 0%, #8B4513 100%)' # Xanh rêu/Nâu
}

def set_bg_color(emotion):
    color = emotion_colors.get(emotion, 'linear-gradient(135deg, #2b5876 0%, #4e4376 100%)') # default
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {color};
            background-attachment: fixed;
            transition: background 0.5s ease;
        }}
        .song-card {{
            background: rgba(0, 0, 0, 0.4);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .song-title {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 5px;
        }}
        .song-artist {{
            font-size: 1.1rem;
            color: #e0e0e0;
            margin-bottom: 5px;
        }}
        .song-tag {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 5px 10px;
            font-size: 0.8rem;
            margin-right: 5px;
            color: #fff;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

@st.cache_data
def load_data():
    return pd.read_csv('best_lofi_songs_2025.csv')

def main():
    if "mood" not in st.session_state:
        st.session_state.mood = "neutral"
        
    set_bg_color(st.session_state.mood)
    
    st.markdown("<h1 style='color: white;'>🎧 GenZ Lofi Mood-Sync 2025</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: white; font-size: 1.2rem;'>Mood của bạn hôm nay thế nào? Để AI chọn cho bạn những bài Lofi cực chill nhé!</p>", unsafe_allow_html=True)
    
    # Khởi tạo dataset
    df = load_data()
    
    # Chia giao diện 2 cột
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.markdown("<h2 style='color: white;'>📸 Self-Check</h2>", unsafe_allow_html=True)
        if MOCK_MODE:
            st.warning("⚠️ Môi trường Python không hỗ trợ TensorFlow/DeepFace. Đang chạy ở chế độ giả lập (Mock Mode) để testing UI.")
        
        img_buffer = st.camera_input("Chụp mặt xinh/đẹp trai nào...")
        
        if img_buffer is not None:
            bytes_data = img_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            temp_path = "temp_face.jpg"
            cv2.imwrite(temp_path, cv2_img)
            
            with st.spinner("AI đang check VAR cảm xúc của bạn... 🧙‍♂️"):
                try:
                    result = DeepFace.analyze(temp_path, actions=['emotion'], enforce_detection=False)
                    if isinstance(result, list):
                        result = result[0]
                    dominant_emotion = result['dominant_emotion']
                    st.session_state.mood = dominant_emotion
                    st.success(f"Cảm xúc chẩn đoán: **{dominant_emotion.upper()}** 🎯")
                    os.remove(temp_path)
                    st.rerun()
                except Exception as e:
                    st.error(f"Khó phán đoán quá, thử lại nha: {e}")
            
    with col2:
        st.markdown("<h2 style='color: white;'>🎶 Lofi Vibes For You</h2>", unsafe_allow_html=True)
        if hasattr(st.session_state, 'mood'):
            emotion = st.session_state.mood
            keywords = emotion_mapping.get(emotion, emotion_mapping['neutral'])
            keywords_lower = [k.lower() for k in keywords]
            
            def match_vibe(vibe_str):
                if pd.isna(vibe_str): return False
                vibe_lower = str(vibe_str).lower()
                for kw in keywords_lower:
                    if kw in vibe_lower:
                        return True
                return False
                
            filtered_df = df[df['Vibe/Mood'].apply(match_vibe)]
            
            if len(filtered_df) < 5:
                extra = df[~df.index.isin(filtered_df.index)]
                needed = 5 - len(filtered_df)
                if not extra.empty:
                    extra_sample = extra.sample(n=min(needed, len(extra)))
                    recommended = pd.concat([filtered_df, extra_sample])
                else:
                    recommended = filtered_df
            else:
                recommended = filtered_df.sample(n=5)
                
            st.markdown(f"<h3 style='color: white;'>Mood Hiện Tại: {emotion.upper()}</h3>", unsafe_allow_html=True)
            
            for _, row in recommended.iterrows():
                song_title = row['Song Title']
                artist = row['Artist']
                vibe = row['Vibe/Mood']
                best_for = row['Best For']
                
                html_card = f"""
                <div class="song-card">
                    <div class="song-title">{song_title}</div>
                    <div class="song-artist">👤 {artist}</div>
                    <div style="margin-top: 10px;">
                        <span class="song-tag">✨ {vibe}</span>
                        <span class="song-tag">🎯 {best_for}</span>
                    </div>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
        else:
            st.info("Hãy chụp một bức ảnh để nhận gợi ý nhé!")

if __name__ == '__main__':
    main()
