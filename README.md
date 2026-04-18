# 🎧 Mood-Sync 2025

**Mô tả:**
Mood-Sync 2025 là một ứng dụng Web tương tác thông minh, kết hợp giữa **Trí Tuệ Nhân Tạo (Computer Vision)**, **Khai phá Dữ liệu (Data Mining)** và tích hợp nền tảng âm nhạc. Ứng dụng tự động nhận diện khuôn mặt và cảm xúc của người dùng qua ảnh chụp Camera, từ đó đưa ra các gợi ý bài hát phù hợp nhất với tâm trạng hiện tại, kèm nút nghe trực tiếp trên **Spotify** và **SoundCloud**.

---

## 1. Cấu Trúc Hệ Thống & Các Module Chính

Hệ thống được chia thành 3 phần xử lý chức năng chính:

### 📸 1.1. Module Computer Vision (Nhận diện cảm xúc)
- **Công nghệ**: OpenCV (`cv2`) và DeepFace.
- **Quy trình hoạt động**:
  - Giao diện web thu nhận ảnh chụp từ người dùng thông qua Camera (`st.camera_input`).
  - Ảnh được giải mã qua OpenCV và đưa vào mô hình học sâu (Deep CNN) của DeepFace để phân tích đặc điểm khuôn mặt.
  - Trích xuất ra **Cảm xúc chủ đạo (Dominant Emotion)** gồm: `Happy`, `Sad`, `Neutral`, `Angry`, `Fear`, `Surprise`, `Disgust`.
  - Toàn bộ giao diện (màu nền gradient, danh sách nhạc) thay đổi tức thời theo cảm xúc vừa được phát hiện.
- **Cơ chế đồng bộ**: Sử dụng **image hashing** để phát hiện ảnh mới, tránh xử lý lại và đảm bảo "Cảm xúc chẩn đoán" và "Tâm trạng hiện tại" luôn khớp nhau.
- *Mock Mode: Nếu thiết bị không hỗ trợ DeepFace, hệ thống tự động chuyển sang chế độ fallback để duy trì giao diện.*

### 🎶 1.2. Module Data Mining & AI Recommendation (Gợi ý bài hát)
- **Dữ liệu**: Bộ dataset thực tế `spotify-2023.csv` (gồm ~950 bài hát nổi bật nhất năm 2023 từ Kaggle, với các thuộc tính âm nhạc định lượng).
- **Công nghệ**: `pandas`, `scikit-learn` (KMeans Clustering, StandardScaler).
- **Quy trình hoạt động**:
  - Hệ thống sử dụng thuật toán **K-Means Clustering** (5 cụm) để phân nhóm toàn bộ dữ liệu âm nhạc dựa trên 4 chỉ số âm học: `danceability_%`, `valence_%`, `energy_%`, `acousticness_%`.
  - Mỗi cụm (cluster) được tự động gán nhãn cảm xúc thông qua phân tích các giá trị centroid (VD: Cluster có `valence cao + energy cao` → `happy/surprise`; `valence thấp + acousticness cao` → `sad/fear`).
  - Khi cảm xúc người dùng được phát hiện, hệ thống lọc ra đúng cụm nhạc phù hợp và **sample ngẫu nhiên 5 bài** từ cụm đó để gợi ý.
  - Kết quả được **cache theo session** để tránh reload bài hát mỗi lần màn hình tự render lại.

### 💻 1.3. Module Web Interface (Giao diện Web)
- **Công nghệ**: Streamlit, HTML/CSS tùy chỉnh.
- **Quy trình hoạt động**:
  - Dashboard 2 cột: Cột Camera (trái) và Cột Playlist (phải).
  - **Dynamic Background**: Hình nền gradient thay đổi theo từng cảm xúc (Vàng cam → vui vẻ, Xanh lam → buồn bã, Tím neon → bất ngờ...).
  - **Glassmorphism Card**: Mỗi bài hát được hiển thị dạng thẻ kính mờ với tên bài, nghệ sĩ và các chỉ số âm nhạc.
  - **Nút nghe nhạc đa nền tảng**: Mỗi thẻ bài hát có 2 nút:
    - 🔊 **SoundCloud** (màu cam) — Tìm & nghe bài hát trực tiếp trên SoundCloud.
    - 🎧 **Spotify** (màu xanh lá) — Tìm & nghe bài hát trực tiếp trên Spotify.
  - Không yêu cầu API key hay tài khoản Premium để sử dụng tính năng nhạc.

---

## 2. Công Cụ & Môi Trường Yêu Cầu (Dependencies)

| Thư viện | Mục đích |
|---|---|
| `streamlit` | Giao diện web |
| `opencv-python-headless` | Xử lý ảnh camera |
| `numpy` | Xử lý mảng nhị phân |
| `deepface` | Nhận diện cảm xúc khuôn mặt (AI) |
| `pandas` | Xử lý & lọc dữ liệu âm nhạc |
| `scikit-learn` | Thuật toán KMeans Clustering |

---

## 3. Dataset

- **File**: `spotify-2023.csv`
- **Nguồn**: [Kaggle - Most Streamed Spotify Songs 2023](https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023)
- **Nội dung**: ~950 bài hát phổ biến nhất 2023, gồm các cột: tên bài hát, nghệ sĩ, lượt stream, và các chỉ số âm nhạc định lượng (`danceability_%`, `valence_%`, `energy_%`, `acousticness_%`...).

---

## 4. Hướng Dẫn Cài Đặt và Sử Dụng

**Bước 1: Cài đặt thư viện**
```bash
pip install -r requirements.txt
```

**Bước 2: Khởi động ứng dụng**
```bash
python -m streamlit run app.py
```

**Bước 3: Trải nghiệm**
1. Trình duyệt mở tại `http://localhost:8501` (hoặc cổng được chỉ định).
2. Bấm **Allow** để cho phép truy cập camera.
3. Tạo một biểu cảm rồi ấn chụp ảnh.
4. Hệ thống phân tích cảm xúc → đổi màu nền → gợi ý Top 5 bài hát phù hợp.
5. Bấm nút **🔊 SoundCloud** hoặc **🎧 Spotify** để nghe bài hát đó ngay lập tức!

---

## 5. Kiến Trúc Hệ Thống (Tóm tắt)

```
Camera Input (Streamlit)
        ↓
  OpenCV Decode
        ↓
  DeepFace.analyze()  →  dominant_emotion (7 loại)
        ↓
  KMeans Cluster Filter (scikit-learn)
        ↓
  Sample 5 bài hát từ cluster phù hợp
        ↓
  Hiển thị Card + Nút Spotify/SoundCloud
        ↓
  Dynamic Background theo cảm xúc (CSS Gradient)
```
