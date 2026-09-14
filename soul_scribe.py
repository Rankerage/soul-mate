import os
import sys
import time
from datetime import datetime
from config import AppConfig
from location_tracker import LocationTracker
from audio_observer import AudioObserver
from memory_manager import MemoryManager
from gemini_engine import GeminiEngine
from tts_speaker import TTSSpeaker
from plugins import WakeWordPlugin

def main():
    print("=" * 65)
    print("🔮 Soul Scribe v1.0.0 (Omi-Powered Autonomous AI Companion)")
    print("=" * 65)

    config = AppConfig()
    
    # 1. 위치 추적기
    location_tracker = LocationTracker(config)
    location_tracker.start()
    print("📍 Location Tracker active.")

    # 2. 오디오 옵저버 및 Omi 메모리 매니저
    observer = AudioObserver(config)
    memory_manager = MemoryManager(config)
    print(f"🎙️ Audio Observer ready. (Obsidian Vault: {config.vault_dir})")

    # 3. Gemini 및 TTS 엔진
    gemini = GeminiEngine(config)
    tts = TTSSpeaker()
    print(f"🧠 Gemini Engine online (Model: {config.gemini_model}).")

    # 4. Omi 플러그인 등록
    wakeword_plugin = WakeWordPlugin(
        wake_words=config.wake_words,
        handler=lambda query, loc: gemini.ask(query, loc)
    )
    print(f"🎯 Omi Trigger Plugins loaded. Wake-words: {config.wake_words}")
    print("=" * 65)
    print("🚀 Soul Scribe 무한 기록 및 청취 루프 시작 (종료: Ctrl+C)\n")

    tts.speak("소울 스크라이브 일점영 버전 가동을 시작합니다.")

    try:
        while True:
            curr_loc = location_tracker.get_latest_location()

            # 1) 오디오 청크 캡처
            wav_path = observer.record_chunk()
            if not wav_path or not wav_path.exists():
                time.sleep(1)
                continue

            # 2) STT 변환
            transcript = observer.transcribe_audio(wav_path)
            if not transcript:
                continue

            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🗣️ [Transcript]: "{transcript}"")

            # 3) Omi Memory & Obsidian Vault 누적
            memory_manager.add_transcript(transcript, curr_loc)

            # 4) Omi 플러그인 이벤트 검사
            if wakeword_plugin.on_transcript(transcript, curr_loc):
                temp = gemini.calculate_chaos_temperature(curr_loc)
                print(f"\n⚡ [OMI WAKE-WORD TRIGGERED] "{transcript}"")
                print(f"🌌 Chaos Logic: Location={curr_loc.zone_name} | Temperature={temp}")
                
                tts.speak("네, 말씀하세요.", wait=True)

                # Gemini 추론
                response = wakeword_plugin.execute(transcript, curr_loc)
                print(f"🤖 [Soul Scribe Response]: {response}")

                # 음성 피드백 & 메모리 기록
                tts.speak(response, wait=True)
                memory_manager.append_response(transcript, response, curr_loc)
                print("--- 스트림 루프 계속 ---\n")

    except KeyboardInterrupt:
        print("\n🛑 Soul Scribe 종료 중...")
        location_tracker.stop()
        tts.speak("소울 스크라이브가 안전하게 종료되었습니다.")
        print("👋 완료.")

if __name__ == '__main__':
    main()
