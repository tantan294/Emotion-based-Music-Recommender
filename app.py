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
            return [{'dominant_emotion': 'happy'}]

# Mapping cảm xúc sang SoundCloud playlist (URL thực của Chillhop Music)
EMOTION_PLAYLISTS = {
    'happy':   'https://soundcloud.com/chillhopdotcom/sets/chillhop-essentials-summer',
    'sad':     'https://soundcloud.com/chillhopdotcom/sets/melancholic-chillhop',
    'neutral': 'https://soundcloud.com/chillhopdotcom/sets/chillhop-essentials',
    'angry':   'https://soundcloud.com/chillhopdotcom/sets/late-night-chillhop',
    'fear':    'https://soundcloud.com/chillhopdotcom/sets/nocturnal-chillhop',
    'surprise':'https://soundcloud.com/chillhopdotcom/sets/chillhop-essentials-spring',
    'disgust': 'https://soundcloud.com/chillhopdotcom/sets/chillhop-music'
}

def get_sc_playlist_embed(emotion: str) -> str:
    """Trả về URL embed SoundCloud Widget cho playlist theo cảm xúc."""
    import urllib.parse
    playlist_url = EMOTION_PLAYLISTS.get(emotion, EMOTION_PLAYLISTS['neutral'])
    encoded = urllib.parse.quote(playlist_url, safe='')
    return (
        f"https://w.soundcloud.com/player/?url={encoded}"
        f"&color=%23ff5500&auto_play=false&hide_related=true"
        f"&show_comments=false&show_user=true&show_reposts=false"
        f"&show_teaser=false&visual=false"
    )

def get_sc_search_link(song_name: str, artist_name: str = "") -> str:
    """Trả về URL tìm kiếm bài hát trên SoundCloud (mở tab mới)."""
    import urllib.parse
    query = urllib.parse.quote(f"{song_name} {artist_name}".strip())
    return f"https://soundcloud.com/search?q={query}"

# Cấu hình trang
st.set_page_config(page_title="GenZ Lofi Mood-Sync", page_icon="🎵", layout="wide")

# Mapping cảm xúc sang màu nền (gradient)
emotion_colors = {
    'happy': 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
    'sad': 'linear-gradient(135deg, #1E90FF 0%, #00008B 100%)',
    'neutral': 'linear-gradient(135deg, #5f2c82 0%, #49a09d 100%)',
    'angry': 'linear-gradient(135deg, #FF4500 0%, #8B0000 100%)',
    'fear': 'linear-gradient(135deg, #4A4A4A 0%, #000000 100%)',
    'surprise': 'linear-gradient(135deg, #9370DB 0%, #4B0082 100%)',
    'disgust': 'linear-gradient(135deg, #556B2F 0%, #8B4513 100%)'
}

def set_bg_color(emotion):
    color = emotion_colors.get(emotion, 'linear-gradient(135deg, #2b5876 0%, #4e4376 100%)')
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
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .song-title {{
            font-size: 1.3rem;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 4px;
        }}
        .song-artist {{
            font-size: 1rem;
            color: #e0e0e0;
            margin-bottom: 10px;
        }}
        .song-tag {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 4px 10px;
            font-size: 0.78rem;
            margin-right: 5px;
            margin-bottom: 8px;
            color: #fff;
        }}
        .spotify-player {{
            border-radius: 12px;
            margin-top: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

@st.cache_data
def load_and_cluster_data():
    # Thử đọc với utf-8 trước, fallback về cp1252 nếu lỗi
    try:
        df = pd.read_csv('spotify-2023.csv', encoding='utf-8', sep=';')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv('spotify-2023.csv', encoding='cp1252', sep=';')
        except UnicodeDecodeError:
            df = pd.read_csv('spotify-2023.csv', encoding='latin-1', sep=';')
    
    # Làm sạch các cột text - loại bỏ ký tự lỗi còn sót lại
    for col in ['track_name', 'artist(s)_name']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x.encode('utf-8', errors='replace').decode('utf-8') if isinstance(x, str) else x)
    features = ['danceability_%', 'valence_%', 'energy_%', 'acousticness_%']
    
    for col in features:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    X = df[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
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
            
        if not assigned_emotions:
            assigned_emotions.append('neutral')
            
        cluster_mapping[cluster_id] = assigned_emotions
        
    df['assigned_emotions'] = df['cluster'].map(cluster_mapping)
    return df

def main():
    if "mood" not in st.session_state:
        st.session_state.mood = "neutral"
        
    set_bg_color(st.session_state.mood)
    
    st.markdown("<h1 style='color: white;'>🎧 Mood-Sync 2025</h1>", unsafe_allow_html=True)
    
    df = load_and_cluster_data()
    
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.markdown("<h2 style='color: white;'>📸 Self-Check</h2>", unsafe_allow_html=True)
        if MOCK_MODE:
            st.warning("⚠️ Đang chạy ở chế độ giả lập (Mock Mode).")
        
        img_buffer = st.camera_input("Chụp một bức ảnh thật đẹp nhé...")
        
        if img_buffer is not None:
            current_img_hash = hash(img_buffer.getvalue())
            
            if st.session_state.get('last_img_hash') != current_img_hash:
                bytes_data = img_buffer.getvalue()
                cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                
                temp_path = "temp_face.jpg"
                cv2.imwrite(temp_path, cv2_img)
                
                with st.spinner("Bípppppp, check quả VAR cảm xúc của bạn... 🧙‍♂️"):
                    try:
                        result = DeepFace.analyze(temp_path, actions=['emotion'], enforce_detection=False)
                        if isinstance(result, list):
                            result = result[0]
                        dominant_emotion = result['dominant_emotion']
                        st.session_state.mood = dominant_emotion
                        st.session_state.last_img_hash = current_img_hash
                        # Xoá cache nhạc khi đổi cảm xúc
                        st.session_state.pop('cached_tracks', None)
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        st.rerun()
                    except Exception as e:
                        st.session_state.last_img_hash = current_img_hash
                        st.error(f"Khó phán đoán quá, thử lại nha: {e}")
            else:
                st.success(f"Cảm xúc chẩn đoán: **{st.session_state.mood.upper()}** 🎯")
            
    with col2:
        st.markdown("<h2 style='color: white;'>🎶 Vibes For You</h2>", unsafe_allow_html=True)
        if hasattr(st.session_state, 'mood'):
            emotion = st.session_state.mood
            
            def match_cluster(emotions_list):
                if emotion == 'neutral' and 'neutral' in emotions_list:
                    return True
                return emotion in emotions_list
                
            filtered_df = df[df['assigned_emotions'].apply(match_cluster)]
            
            if filtered_df.empty:
                filtered_df = df
            
            # Cache danh sách bài hát
            if 'cached_tracks' not in st.session_state or st.session_state.get('cached_mood') != emotion:
                recommended = filtered_df.sample(n=min(5, len(filtered_df)))
                st.session_state.cached_tracks = recommended
                st.session_state.cached_mood = emotion
            else:
                recommended = st.session_state.cached_tracks
                
            st.markdown(f"<h3 style='color: white;'>Tâm trạng: {emotion.upper()} — Top 5 Picks 🔥</h3>", unsafe_allow_html=True)
            
            # Danh sách bài hát với nút tìm trên SoundCloud
            for _, row in recommended.iterrows():
                song_title = row['track_name']
                artist = row['artist(s)_name']
                dance = row['danceability_%']
                val = row['valence_%']
                energy = row['energy_%']
                streams = row['streams']
                
                try:
                    streams_fmt = f"{int(streams):,}"
                except:
                    streams_fmt = streams
                
                sc_link = get_sc_search_link(song_title, artist)
                
                import urllib.parse
                sp_query = urllib.parse.quote(f"{song_title} {artist}")
                sp_link = f"https://open.spotify.com/search/{sp_query}"
                
                html_card = f"""
                <div class="song-card">
                    <div class="song-title">🎵 {song_title}</div>
                    <div class="song-artist">👤 {artist}</div>
                    <div style="margin-bottom: 10px;">
                        <span class="song-tag">💃 Dance: {dance}%</span>
                        <span class="song-tag">⚡ Energy: {energy}%</span>
                        <span class="song-tag">😊 Vibe: {val}%</span>
                        <span class="song-tag" style="background: rgba(255,85,0,0.5);">🎧 {streams_fmt}</span>
                    </div>
                    <a href="{sc_link}" target="_blank"
                       style="display:inline-block; background:#ff5500; color:white;
                              padding:7px 16px; border-radius:20px; text-decoration:none;
                              font-size:0.85rem; font-weight:bold; margin-right:8px;">
                        🔊 SoundCloud
                    </a>
                    <a href="{sp_link}" target="_blank"
                       style="display:inline-block; background:#1DB954; color:white;
                              padding:7px 16px; border-radius:20px; text-decoration:none;
                              font-size:0.85rem; font-weight:bold;">
                        🎧 Spotify
                    </a>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
        else:
            st.info("Hãy chụp một bức ảnh để nhận gợi ý nhé!")

if __name__ == '__main__':
    main()
