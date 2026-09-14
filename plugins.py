import time
from typing import Callable, List, Dict, Any
from models import LocationData

class OmiPlugin:
    """Omi의 플러그인/앱 인터페이스를 계승한 실시간 이벤트 리스너"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def on_transcript(self, transcript: str, location: LocationData) -> bool:
        """실시간 음성 인식 스트림 수신 시 호출. 트리거 발생 시 True 반환"""
        return False

    def on_trigger(self, query: str, location: LocationData, context: str) -> str:
        """트리거 감지 시 처리 로직"""
        return ""

class WakeWordPlugin(OmiPlugin):
    def __init__(self, wake_words: List[str], handler: Callable[[str, LocationData], str]):
        super().__init__("SoulScribeGatekeeper", "웨이크워드 감지 및 Gemini 호출 플러그인")
        self.wake_words = wake_words
        self.handler = handler

    def on_transcript(self, transcript: str, location: LocationData) -> bool:
        norm = transcript.replace(" ", "").lower()
        for ww in self.wake_words:
            if ww.replace(" ", "").lower() in norm:
                return True
        return False

    def execute(self, query: str, location: LocationData) -> str:
        return self.handler(query, location)
