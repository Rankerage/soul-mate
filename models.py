from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

@dataclass
class GeofencePoint:
    name: str
    lat: float
    lon: float
    radius_km: float = 3.0

@dataclass
class LocationData:
    latitude: float
    longitude: float
    altitude: float = 0.0
    accuracy: float = 0.0
    provider: str = 'unknown'
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    is_familiar: bool = False
    zone_name: str = '낯선 미지의 공간'

@dataclass
class TranscriptSegment:
    start_time: str
    text: str
    location: LocationData

@dataclass
class OmiMemory:
    """BasedHardware Omi 오픈소스 구조를 계승한 구조화된 라이프스트림 메모리 모델"""
    id: str
    created_at: str
    segments: List[TranscriptSegment] = field(default_factory=list)
    summary: str = ""
    action_items: List[str] = field(default_factory=list)
    location: Optional[LocationData] = None
    chaos_temperature: float = 0.3
    category: str = "daily-conversation"

    def to_markdown(self) -> str:
        loc_str = f"[{self.location.latitude:.4f}, {self.location.longitude:.4f}] ({self.location.zone_name})" if self.location else "Unknown"
        lines = [
            f"### 🧠 Omi Memory Segment: `{self.id}`",
            f"- **Timestamp**: {self.created_at}",
            f"- **Location**: 📍 `{loc_str}`",
            f"- **Chaos Temp**: `{self.chaos_temperature}`",
            f"- **Summary**: {self.summary if self.summary else '(실시간 스트림 누적 중)'}",
        ]
        if self.action_items:
            lines.append("- **Action Items**:")
            for item in self.action_items:
                lines.append(f"  - [ ] {item}")
        lines.append("- **Transcripts**:")
        for seg in self.segments:
            lines.append(f"  - `[{seg.start_time}]` {seg.text}")
        lines.append("")
        return "\n".join(lines)
