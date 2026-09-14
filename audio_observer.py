import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from config import AppConfig
from location_tracker import LocationData

class AudioObserver:
    def __init__(self, config: AppConfig):
        self.config = config
        self.config.vault_dir.mkdir(parents=True, exist_ok=True)
        if self.config.temp_audio_path.parent.exists():
            self.config.temp_audio_path.parent.mkdir(parents=True, exist_ok=True)

    def record_chunk(self) -> Optional[Path]:
        out_wav = self.config.temp_audio_path
        if out_wav.exists():
            try:
                out_wav.unlink()
            except OSError:
                pass

        try:
            subprocess.run(
                [
                    'termux-microphone-record',
                    '-f', str(out_wav),
                    '-l', str(self.config.audio_chunk_seconds),
                    '-r', str(self.config.sample_rate),
                    '-e', 'wav'
                ],
                capture_output=True,
                timeout=self.config.audio_chunk_seconds + 3
            )
            time.sleep(self.config.audio_chunk_seconds + 0.5)
            if out_wav.exists() and out_wav.stat().st_size > 1000:
                return out_wav
        except Exception:
            try:
                subprocess.run(['termux-microphone-record', '-q'], capture_output=True)
            except Exception:
                pass
        return None

    def transcribe_audio(self, wav_path: Path) -> str:
        if not os.path.exists(self.config.whisper_bin):
            return ''

        cmd = [
            self.config.whisper_bin,
            '-m', self.config.whisper_model,
            '-f', str(wav_path),
            '-l', 'ko',
            '--no-timestamps',
            '-t', '4',
            '-otxt'
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if res.returncode == 0:
                txt_file = Path(str(wav_path) + '.txt')
                if txt_file.exists():
                    text = txt_file.read_text(encoding='utf-8').strip()
                    txt_file.unlink(missing_ok=True)
                    return self._clean_transcript(text)
                return self._clean_transcript(res.stdout)
        except Exception:
            pass
        return ''

    def _clean_transcript(self, text: str) -> str:
        text = re.sub(r'\[.*?\]', '', text)
        return text.strip()

    def append_to_vault(self, text: str, location: LocationData) -> Path:
        today_str = datetime.now().strftime('%Y-%m-%d')
        now_time_str = datetime.now().strftime('%H:%M:%S')
        md_path = self.config.vault_dir / f'{today_str}.md'

        if not md_path.exists():
            frontmatter = f'''---
title: Soul Scribe Daily Stream ({today_str})
created: {today_str}
type: voice-stream-log
tags: [soul-scribe, lifestream, obsidian-log]
---

# 🎙️ Soul Scribe Daily Log: {today_str}

'''
            md_path.write_text(frontmatter, encoding='utf-8')

        log_entry = f"- **[{now_time_str}]** 📍 `[{location.latitude:.4f}, {location.longitude:.4f}]` *({location.zone_name})*\n  - {text}\n"
        with open(md_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        return md_path
