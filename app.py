import streamlit as st
import cv2
import numpy as np
import pandas as pd
import os
import random
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

try:
    from deepface import DeepFace
    MOCK_MODE = False
except ImportError:
    MOCK_MODE = True
    class DeepFace:
        @staticmethod
        def analyze(img_path, actions=None, enforce_detection=False):
            time.sleep(1.5) # Giả lập độ trễ xử lý
            emotions = ['happy', 'sad', 'neutral', 'angry', 'fear', 'surprise', 'disgust']
            return [{'dominant_emotion': 'happy'}] # Đã cố định cảm xúc thành 'happy' thay vì random

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
def load_and_cluster_data():
    df = pd.read_csv('spotify-2023.csv', encoding='latin-1', sep=';')
    features = ['danceability_%', 'valence_%', 'energy_%', 'acousticness_%']
    
    # Xử lý missing values
    for col in features:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    X = df[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Sử dụng K-Means chia 5 cụm tâm trạng
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Phân tích các tâm trạng gắn với mỗi cụm
    centroids = df.groupby('cluster')[features].mean()
    cluster_mapping = {}
    for cluster_id in centroids.index:
        c_val = centroids.loc[cluster_id, 'valence_%']
        c_eng = centroids.loc[cluster_id, 'energy_%']
        c_aco = centroids.loc[cluster_id, 'acousticness_%']
        
        assigned_emotions = []
        if c_val >= 55 and c_eng >= 60:
            assigned_emotions.extend(['happy', 'surprise'])
        elif c_val < 45 and c_aco >= 30:
            assigned_emotions.extend(['sad', 'fear'])
        elif c_eng >= 65 and c_val < 50:
            assigned_emotions.extend(['angry', 'disgust'])
        else:
            assigned_emotions.append('neutral')
            
        # Nếu logic heuristics không bắt được, lấy default là neutral
        if not assigned_emotions:
            assigned_emotions.append('neutral')
            
        cluster_mapping[cluster_id] = assigned_emotions
        
    df['assigned_emotions'] = df['cluster'].map(cluster_mapping)
    return df

def main():
    if "mood" not in st.session_state:
        st.session_state.mood = "neutral"
        
    set_bg_color(st.session_state.mood)
    
    st.markdown("<h1 style='color: white;'>🎧 GenZ Lofi Mood-Sync 2025</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: white; font-size: 1.2rem;'>AI Music Clustering Enabled 🤖 - Để AI chọn cho bạn những bài Lofi cực chill nhé!</p>", unsafe_allow_html=True)
    
    # Khởi tạo dataset và cluster
    df = load_and_cluster_data()
    
    # Chia giao diện 2 cột
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.markdown("<h2 style='color: white;'>📸 Self-Check</h2>", unsafe_allow_html=True)
        if MOCK_MODE:
            st.warning("⚠️ Môi trường Python không hỗ trợ TensorFlow/DeepFace. Đang chạy ở chế độ giả lập (Mock Mode) để testing UI.")
        
        img_buffer = st.camera_input("Chụp mặt xinh/đẹp trai nào...")
        
        if img_buffer is not None:
            current_img_hash = hash(img_buffer.getvalue())
            
            if st.session_state.get('last_img_hash') != current_img_hash:
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
                        st.session_state.last_img_hash = current_img_hash
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        st.rerun()
                    except Exception as e:
                        st.session_state.last_img_hash = current_img_hash
                        st.error(f"Khó phán đoán quá, thử lại nha: {e}")
            else:
                st.success(f"Cảm xúc chẩn đoán: **{st.session_state.mood.upper()}** 🎯")
            
    with col2:
        st.markdown("<h2 style='color: white;'>🎶 Lofi Vibes For You</h2>", unsafe_allow_html=True)
        if hasattr(st.session_state, 'mood'):
            emotion = st.session_state.mood
            
            # Lọc bài hát dựa trên Cluster có map với cảm xúc này
            def match_cluster(emotions_list):
                # Nếu neutral, random cả các bài neutral
                if emotion == 'neutral' and 'neutral' in emotions_list:
                    return True
                return emotion in emotions_list
                
            filtered_df = df[df['assigned_emotions'].apply(match_cluster)]
            
            # Fallback nếu không có cluster nào khớp (tránh lỗi rỗng)
            if filtered_df.empty:
                filtered_df = df
            
            # Lấy 5 bài ngẫu nhiên
            recommended = filtered_df.sample(n=min(5, len(filtered_df)))
                
            st.markdown(f"<h3 style='color: white;'>Tâm trạng hiện tại: {emotion.upper()}</h3>", unsafe_allow_html=True)
            
            for _, row in recommended.iterrows():
                song_title = row['track_name']
                artist = row['artist(s)_name']
                dance = row['danceability_%']
                val = row['valence_%']
                energy = row['energy_%']
                streams = row['streams']
                cluster_id = row['cluster']
                
                # Format views cho ngắn gọn
                try:
                    streams_fmt = f"{int(streams):,}"
                except:
                    streams_fmt = streams
                
                html_card = f"""
                <div class="song-card">
                    <div class="song-title">{song_title}</div>
                    <div class="song-artist">👤 {artist}</div>
                    <div style="margin-top: 10px;">
                        <span class="song-tag">💃 Dance: {dance}%</span>
                        <span class="song-tag">⚡ Energy: {energy}%</span>
                        <span class="song-tag">😊 Vibe: {val}%</span>
                        <span class="song-tag" style="background: rgba(255,105,180,0.4);">🎧 Streams: {streams_fmt}</span>
                    </div>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
        else:
            st.info("Hãy chụp một bức ảnh để nhận gợi ý nhé!")

if __name__ == '__main__':
    main()
