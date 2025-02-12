# 🎬 Video Subtitle Generator  

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repo-blue?style=flat&logo=github)](https://github.com/AhmadShayan1112/Video-subtitle-generator)  

## 📌 Overview  
The **Video Subtitle Generator** is a **Streamlit-based application** that:  
✅ **Transcribes video audio** using **Whisper AI**  
✅ **Translates subtitles** into multiple languages  
✅ **Generates topic-based summaries** via **Gemini AI**  
✅ **Adds subtitles & dubbed audio** to videos  
✅ **Exports results** in **SRT, MP4, and MP3 formats**  

This tool is ideal for content creators, educators, and multilingual audiences.  

---

## 🚀 Features  
🔹 **Automatic Speech-to-Text** (Whisper AI)  
🔹 **Multi-Language Subtitle Translation**  
🔹 **Topic Detection & Summarization** (Gemini AI)  
🔹 **Subtitles Embedding in Videos** (FFmpeg)  
🔹 **Voice Dubbing in Another Language** (gTTS)  
🔹 **Supports Multiple Formats** (MP4, MKV, AVI, MOV)  

---

## 🛠️ Installation  

### **1️⃣ Clone the Repository**  
```sh
git clone https://github.com/AhmadShayan1112/Video-subtitle-generator.git
cd Video-subtitle-generator
```

### **2️⃣ Install Dependencies**  
Ensure you have **Python 3.8+** installed. Then, install required packages:  
```sh
pip install -r requirements.txt
```

### **3️⃣ Run the App**  
```sh
streamlit run app.py
```

---

## 📂 File Structure  
```
📁 Video-subtitle-generator
│── 📄 app.py                 # Main Streamlit app  
│── 📄 requirements.txt       # Dependencies  
│── 📁 models                 # Whisper model (if needed)  
│── 📁 temp                   # Temporary files  
│── 📁 outputs                # Generated subtitles, videos, audio files  
```

---

## 🔧 Usage  
1️⃣ **Upload a video** (MP4, MKV, AVI, MOV)  
2️⃣ **Enter the target language code** (e.g., `es` for Spanish, `fr` for French)  
3️⃣ The app will **transcribe, translate, summarize, and add subtitles**  
4️⃣ **Download results**: Translated SRT, subtitled video, or dubbed video  

---

## 🛑 Requirements  
- Python 3.8+  
- Streamlit  
- OpenAI Whisper  
- FFmpeg  
- Deep Translator  
- Google Generative AI  
- gTTS (Google Text-to-Speech)  

---

## 🤝 Contributing  
Contributions are welcome! Feel free to open an issue or submit a pull request.  

---

## 📬 Contact  
For any queries, reach out at:  
📧 **ahmadshayan1112@example.com**  
🌍 [GitHub Profile](https://github.com/AhmadShayan1112)  

