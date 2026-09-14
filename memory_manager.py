import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from config import AppConfig
from models import OmiMemory, TranscriptSegment, LocationData

class MemoryManager:
    """Omi 스타일의 대화 세그먼트 생성 및 Obsidian Vault 무한 누적 동기화기"""
    def __init__(self, config: AppConfig):
        self.config = config
        self.config.vault_dir.mkdir(parents=True, exist_ok=True)
        self.current_memory = OmiMemory(
            id=str(uuid.uuid4())[:8],
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def add_transcript(self, text: str, location: LocationData):
        now_time = datetime.now().strftime("%H:%M:%S")
        seg = TranscriptSegment(start_time=now_time, text=text, location=location)
        self.current_memory.segments.append(seg)
        self.current_memory.location = location

        # Obsidian 일별 마크다운 파일에 실시간 스트림 기록
        self._append_stream_to_file(seg, location)

    def _append_stream_to_file(self, seg: TranscriptSegment, location: LocationData):
        today_str = datetime.now().strftime("%Y-%m-%d")
        md_path = self.config.vault_dir / f"{today_str}.md"

        if not md_path.exists():
            frontmatter = f"""---
title: Soul Scribe Daily Stream ({today_str})
created: {today_str}
type: omi-lifestream-vault
tags: [omi, soul-scribe, obsidian-vault, ai-memories]
---

# 🎙️ Soul Scribe (Omi Stream): {today_str}

"""
            md_path.write_text(frontmatter, encoding="utf-8")

        log_entry = f"- **[{seg.start_time}]** 📍 `[{location.latitude:.4f}, {location.longitude:.4f}]` *({location.zone_name})*\n  - {seg.text}\n"
        with open(md_path, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def append_response(self, query: str, response: str, location: LocationData):
        today_str = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M:%S")
        md_path = self.config.vault_dir / f"{today_str}.md"
        entry = f"- **[{now_time}]** ⚡ **[Soul Scribe / Omi Response]**\n  - *User*: {query}\n  - *AI*: {response}\n"
        with open(md_path, "a", encoding="utf-8") as f:
            f.write(entry)
