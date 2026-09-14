import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List
from models import GeofencePoint

@dataclass
class AppConfig:
    version: str = "1.0.0"
    app_name: str = "Soul Scribe (Omi-Powered)"

    # Gemini API 설정
    gemini_api_key: str = field(
        default_factory=lambda: os.getenv('GEMINI_API_KEY', '')
    )
    gemini_model: str = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')

    # 웨이크워드 및 플러그인 트리거 목록
    wake_words: List[str] = field(
        default_factory=lambda: ['호들아', '해킹해', '호들', '해킹', '영혼아', '소울아', '헤이오미', '오미야']
    )

    # Obsidian 호환 저장 디렉토리
    vault_dir: Path = field(
        default_factory=lambda: Path(os.getenv('SOUL_SCRIBE_VAULT', os.path.expanduser('~/storage/shared/Documents/SoulScribe')))
    )

    # Omi 실시간 오디오 캡처 설정
    audio_chunk_seconds: int = 5
    sample_rate: int = 16000
    temp_audio_path: Path = field(
        default_factory=lambda: Path(os.getenv('TMPDIR', '/tmp')) / 'soul_scribe_chunk.wav'
    )

    # whisper.cpp 온디바이스 엔진 경로
    whisper_bin: str = os.getenv('WHISPER_BIN', os.path.expanduser('~/whisper.cpp/build/bin/whisper-cli'))
    whisper_model: str = os.getenv('WHISPER_MODEL', os.path.expanduser('~/whisper.cpp/models/ggml-tiny.bin'))

    # 위치 추적 주기 (초)
    location_poll_interval: int = 120
    
    # Chaos Geofence (일상 거점)
    familiar_zones: List[GeofencePoint] = field(
        default_factory=lambda: [
            GeofencePoint(name='용인_기흥', lat=37.2754, lon=127.1158, radius_km=5.0),
            GeofencePoint(name='용인_수지', lat=37.3223, lon=127.0975, radius_km=5.0),
            GeofencePoint(name='판교_아지트', lat=37.3948, lon=127.1119, radius_km=3.0),
        ]
    )

    context_lookback_hours: int = 6
    memory_summarize_interval_minutes: int = 15
