# 🔮 Soul Scribe v1.0.0 (영혼의 서기)

> **BasedHardware Omi(오픈소스 AI 웨어러블)** 아키텍처를 계승하여 안드로이드 **Termux** 환경에서 일상 음성과 GPS를 Obsidian 마크다운 형식으로 무한 기록하고, 위치 기반 **Chaos Logic(동적 Temperature)**과 Gemini API를 결합하여 이어폰으로 즉각 대답하는 독립형 AI 동반자 시스템.

---

## 🌟 Omi 오픈소스 적극 활용 및 계승 구조

Soul Scribe v1.0.0은 **[BasedHardware/omi](https://github.com/BasedHardware/omi)**의 3대 핵심 철학과 아키텍처를 Termux 환경에 맞추어 완벽히 구현했습니다:

1. **Omi Memory Schema & Lifelogging (`models.py`, `memory_manager.py`)**
   - Omi의 대화 세그멘테이션 및 구조화된 메모리(`OmiMemory`, `TranscriptSegment`) 파이프라인 적용.
   - Obsidian Vault(`YYYY-MM-DD.md`)에 실시간 타임스탬프 + GPS 메타데이터(`[Lat, Lon]`)를 무한 누적 기록.

2. **Omi Realtime Plugin Architecture (`plugins.py`)**
   - Omi의 실시간 오디오/텍스트 플러그인 이벤트 버스 설계.
   - `"호들아"`, `"해킹해"`, `"오미야"`, `"헤이오미"` 등의 웨이크워드 감지 시 플러그인 자동 디스패치.

3. **Chaos Logic Location Aware LLM (`gemini_engine.py`)**
   - Omi의 Context Retrieval 방식을 통해 직전 대화 기록을 자동 수집.
   - **Chaos Logic Geofencing**:
     - 🏢 **일상 공간 (용인, 판교 등)**: `Temperature = 0.3` (정밀, 분석적, 체계적 추론)
     - 🌲 **낯선 미지의 공간 (양평, 하남 등)**: `Temperature = 0.9` (확산적, 직관적, 창의적 추론)

4. **Zero-UI Earphone Feedback (`tts_speaker.py`)**
   - `termux-tts-speak`를 통해 화면을 켜지 않고 이어폰으로 즉각적인 음성 피드백 수신.

---

## 📁 프로젝트 파일 구성

```text
soul-scribe/
├── config.py              # 전역 설정 (Gemini 모델, Geofence 거점, 웨이크워드)
├── models.py              # Omi Memory & Location 데이터 모델
├── location_tracker.py    # termux-location 폴링 및 하버사인 거리 판별기
├── audio_observer.py      # termux-microphone-record & whisper.cpp STT 엔진
├── memory_manager.py      # Omi 스타일 메모리 구조화 및 Obsidian Vault 로거
├── gemini_engine.py       # Chaos Logic Dynamic Temperature & Context LLM
├── plugins.py             # Omi 호환 실시간 플러그인 디스패처
├── tts_speaker.py         # termux-tts-speak 이어폰 음성 출력기
├── soul_scribe.py         # v1.0.0 메인 오케스트레이션 데몬
├── setup_termux.sh        # Termux 환경 원클릭 설치 및 whisper.cpp 빌드 스크립트
├── .gitignore
├── LICENSE (MIT)
└── README.md
```

---

## 🚀 안드로이드 Termux 설치 및 실행 가이드

### 1. 필수 앱 설치 (F-Droid 권장)
- **Termux**
- **Termux:API** (마이크, 위치, 오디오 권한 모두 허용)

### 2. 원클릭 환경 구축
```bash
# 1) 저장소 클론 (또는 파일 복사)
git clone https://github.com/<your-username>/soul-scribe.git
cd soul-scribe

# 2) 권한 부여 및 원클릭 빌드 실행
chmod +x setup_termux.sh
./setup_termux.sh
```

### 3. 백그라운드 상시 구동
```bash
# 화면 꺼짐 방지 및 백그라운드 절전 해제
termux-wake-lock

# Gemini API Key 등록
export GEMINI_API_KEY="AIzaSy..."

# Soul Scribe v1.0.0 데몬 실행
python soul_scribe.py
```

---

## 🧪 로컬 테스트 및 검증

```bash
python -c "
from config import AppConfig
from location_tracker import LocationTracker
from gemini_engine import GeminiEngine
from models import LocationData

config = AppConfig()
gemini = GeminiEngine(config)

loc_home = LocationData(latitude=37.2754, longitude=127.1158, is_familiar=True, zone_name='용인')
loc_wild = LocationData(latitude=37.4912, longitude=127.4875, is_familiar=False, zone_name='양평')

assert gemini.calculate_chaos_temperature(loc_home) == 0.3
assert gemini.calculate_chaos_temperature(loc_wild) == 0.9
print('✅ Soul Scribe v1.0.0 Chaos Logic & Omi Engine Test Passed!')
"
```

---

## 📄 라이선스
MIT License (Inspired by BasedHardware/omi)
