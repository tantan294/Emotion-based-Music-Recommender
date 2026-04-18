# 🎧 Báo Cáo Dự Án: GenZ Lofi Mood-Sync 2025

**Mô tả:**
Dự án "GenZ Lofi Mood-Sync 2025" là một ứng dụng Web tương tác thông minh, kết hợp giữa lĩnh vực Trí Tuệ Nhân Tạo (Computer Vision) và Khai phá Dữ liệu (Data Mining). Ứng dụng tự động nhận diện khuôn mặt và cảm xúc của người dùng qua luồng ảnh chụp Camera, từ đó đưa ra các gợi ý bài hát Lofi phù hợp nhất để đồng điệu với tâm trạng hiện tại.

---

## 1. Cấu Trúc Hệ Thống & Các Module Chính

Hệ thống được chia thành 3 phần xử lý chức năng chính:

### 📸 1.1. Module Computer Vision (Nhận diện cảm xúc)
- **Công nghệ**: OpenCV (`cv2`) và DeepFace.
- **Quy trình hoạt động**: 
  - Giao diện web thu nhận ảnh chụp từ người dùng thông qua Camera (Sử dụng widget `st.camera_input`).
  - Bức ảnh dạng nhị phân lấy từ web được giải mã qua OpenCV và đưa vào mô hình học sâu (Deep Convolutional Neural Networks) của DeepFace để phân tích đặc điểm khuôn mặt.
  - Trích xuất ra "Cảm xúc chủ đạo" (Dominant Emotion) gồm các trạng thái: Happy, Sad, Neutral, Angry, Fear, Surprise, Disgust.
- *Lưu ý: Để đảm bảo tính linh hoạt, hệ thống được lập trình với cơ chế Mock Mode dự phòng. Trường hợp thiết bị gặp lỗi cài đặt thư viện lõi ML, nó sẽ chuyển sang chế độ fallback để duy trì luồng giao diện người dùng trơn tru nhất.*

### 🎶 1.2. Module Data Mapping & Recommendation (Gợi ý bài hát)
- **Dữ liệu**: Bộ dataset gốc `best_lofi_songs_2025.csv`.
- **Công nghệ**: Pandas.
- **Quy trình hoạt động**:
  - Xây dựng một từ điển ánh xạ thông minh (Mapping Keyword Dictionary) liên kết giữa các cảm xúc sinh ra từ DeepFace với các trường "Vibe/Mood" của bài hát (VD: `Happy` được map với keyword `Upbeat, Sweet, Fresh`; `Sad` khớp với `Melancholic, Emotional, Noir`).
  - Tích hợp Pandas để duyệt mảng, lọc (`filter`) toàn bộ dữ liệu âm nhạc có thẻ từ khóa tương ứng với loại cảm xúc đang có.
  - Áp dụng thuật toán trích xuất ngẫu nhiên 5 ca khúc trong nhóm được chỉ định (`sample(5)`), giúp mang lại tập kết quả Recommendation luôn mới mẻ, đặc biệt, không nhàm chán vào mỗi lần tương tác.

### 💻 1.3. Module Web Interface (Giao diện Web GenZ)
- **Công nghệ**: Streamlit.
- **Quy trình hoạt động**:
  - Thiết kế Dashboard dạng chia cột hiện đại: Cột Camera (bên trái) và Cột kết quả Playlist (bên phải).
  - Tích hợp kỹ thuật Dynamic UI: Hình nền của ứng dụng (Background Layout) không cố định mà là một thành phần động. Tôi đã sử dụng custom css injection để nội suy biến từ Model logic sang dải Gradient cá tính (mô phỏng lại trạng thái người dùng). Ví dụ: Màu Vàng cam Gradient cho niềm vui, Xanh lam tĩnh lặng cho sự buồn bã, hoặc Tím Neon cho bất ngờ.
  - Giao diện thể hiện thông tin Card của bài hát với hiệu ứng mờ kính (Glassmorphism), hiển thị đầy đủ tên bài, tên nghệ sĩ, và bối cảnh nghe nhạc thích hợp nhất (Best For).

---

## 2. Công Cụ & Môi Trường Yêu Cầu (Dependencies)
- Ngôn ngữ: Python 3.10+
- Quản lý giao diện: `streamlit`
- Xử lý ảnh và cấu trúc mảng: `opencv-python-headless`, `numpy`
- Lõi trí tuệ nhân tạo (Nhận diện cảm xúc): `deepface`
- Thư viện khai phá, lọc, và điều hướng dữ liệu: `pandas`

---

## 3. Hướng Dẫn Cài Đặt và Sử Dụng

**Bước 1: Cài đặt thư viện**
Chạy câu lệnh sau trong Terminal (hoặc Command Prompt) tại cùng thư mục dự án:
```bash
pip install -r requirements.txt
```

**Bước 2: Khởi động Web App**
Khởi động Local Server ảo của Streamlit để render ứng dụng lên Web Browser:
```bash
python -m streamlit run app.py
```

**Bước 3: Trải nghiệm thực tế**
- Khi trình duyệt tải xong (thường tại địa chỉ `localhost:8501`), ứng dụng sẽ yêu cầu quyền mở Camera hệ thống -> Bấm Đồng Ý / Allow.
- Tạo một tư thế hoặc biểu cảm thật ngầu và ấn chụp.
- Đợi màn hình phân tích trong giây lát. Hệ thống sẽ thay đổi toàn bộ không gian màu tổng thể, phân tích chính xác xem bạn đang Happy, Sad, hay Neutral... và ngay lập tức tổng hợp top 5 bản Lofi đang chờ bạn thưởng thức!
