import subprocess
import shutil

class TTSSpeaker:
    def __init__(self, language: str = 'ko-KR', rate: float = 1.15, pitch: float = 1.0):
        self.language = language
        self.rate = str(rate)
        self.pitch = str(pitch)
        self.has_termux_tts = shutil.which('termux-tts-speak') is not None

    def speak(self, text: str, wait: bool = True):
        if not text:
            return

        print(f'\n🔊 [TTS 출력] {text}')
        
        if self.has_termux_tts:
            cmd = [
                'termux-tts-speak',
                '-l', self.language,
                '-r', self.rate,
                '-p', self.pitch,
                text
            ]
            try:
                if wait:
                    subprocess.run(cmd, timeout=30)
                else:
                    subprocess.Popen(cmd)
            except Exception as e:
                print(f'TTS 실행 에러: {e}')
