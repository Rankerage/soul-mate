#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "============================================="
echo "🔮 Soul Scribe Termux 원클릭 환경 설치 스크립트"
echo "============================================="

# 1. Termux 패키지 업데이트 및 기본 빌드 도구 설치
pkg update -y
pkg install -y termux-api python git clang cmake make ffmpeg sox libsndfile

# 2. Termux 저장소 접근 권한 요청
termux-setup-storage

# 3. Python 필수 라이브러리 설치
pip install --upgrade pip

# 4. whisper.cpp 초경량 온디바이스 STT 빌드
cd $HOME
if [ ! -d "whisper.cpp" ]; then
    echo "📥 whisper.cpp 클론 중..."
    git clone https://github.com/ggerganov/whisper.cpp.git
fi

cd whisper.cpp
echo "⚙️ whisper.cpp 컴파일 중 (ARM64 최적화)..."
cmake -B build
cmake --build build --config Release -j$(nproc)

# 5. 한국어 인식용 ggml tiny 모델 다운로드 (약 75MB)
echo "📥 Whisper Tiny 모델 다운로드 중..."
bash ./models/download-ggml-model.sh tiny

# 6. 환경변수 및 디렉토리 설정
mkdir -p ~/storage/shared/Documents/SoulScribe

echo ""
echo "============================================="
echo "✅ Soul Scribe 환경 설정 완료!"
echo ""
echo "[실행 전 준비사항]"
echo "1. Gemini API 키 등록:"
echo "   export GEMINI_API_KEY=\"your_gemini_api_key_here\""
echo "2. Termux 배터리 최적화 해제 및 Wake-lock 적용:"
echo "   termux-wake-lock"
echo "3. Soul Scribe 실행:"
echo "   python soul_scribe.py"
echo "============================================="
