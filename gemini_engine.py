import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from config import AppConfig
from models import LocationData

class GeminiEngine:
    """Omi의 메모리 컨텍스트와 Chaos Logic(위치 기반 Dynamic Temperature)을 통합한 추론 엔진"""
    def __init__(self, config: AppConfig):
        self.config = config

    def calculate_chaos_temperature(self, location: LocationData) -> float:
        """
        [Chaos Logic]
        - Familiar Zone (용인, 판교 등): Temperature = 0.3 (정밀, 분석적, 체계적)
        - Unfamiliar Zone (양평, 하남, 낯선 곳): Temperature = 0.9 (확산적, 직관적, 창의적)
        """
        return 0.3 if location.is_familiar else 0.9

    def collect_recent_context(self) -> str:
        lookback = timedelta(hours=self.config.context_lookback_hours)
        now = datetime.now()
        dates_to_check = [
            now.strftime('%Y-%m-%d'),
            (now - timedelta(days=1)).strftime('%Y-%m-%d')
        ]
        
        collected_lines = []
        for d in dates_to_check:
            p = self.config.vault_dir / f'{d}.md'
            if p.exists():
                try:
                    content = p.read_text(encoding='utf-8')
                    lines = [l for l in content.splitlines() if l.startswith('- **[')]
                    collected_lines.extend(lines)
                except Exception:
                    pass

        recent_items = collected_lines[-40:] if len(collected_lines) > 40 else collected_lines
        return '\n'.join(recent_items) if recent_items else '(최근 기록된 대화 맥락이 없습니다.)'

    def ask(self, user_query: str, location: LocationData) -> str:
        api_key = self.config.gemini_api_key
        if not api_key:
            return 'Gemini API 키가 설정되지 않았습니다. 환경변수 GEMINI_API_KEY를 설정해주세요.'

        temperature = self.calculate_chaos_temperature(location)
        context_stream = self.collect_recent_context()

        system_instruction = f"""너는 사용자의 일상과 영혼을 상시 기록하고 곁에서 지켜보는 AI 동반자 'Soul Scribe (Omi Edition)'이다.
현재 사용자의 시공간 좌표:
- 위도/경도: {location.latitude:.4f}, {location.longitude:.4f}
- 공간 판정: {location.zone_name} (일상 공간 여부: {location.is_familiar})
- 적용된 Chaos Temperature: {temperature}

[지침]
1. 사용자가 이어폰으로 즉각 음성을 청취하므로 마크다운 특수기호나 리스트 태그 없이 자연스럽고 깔끔한 한국어 구어체로 2~4문장으로 임팩트 있게 답하라.
2. 위치가 낯선 미지의 공간(Temp 0.9)일 때는 새로운 아이디어, 직관적 통찰, 모험적인 관점을 열어줘라.
3. 일상 구역(Temp 0.3)일 때는 실용적이고 체계적이며 안정적인 실행 중심 관점으로 답하라.
4. 아래에 제공된 사용자의 최근 Omi 라이프스트림 대화/위치 로그를 바탕으로 맥락을 즉각 꿰뚫어라."""

        prompt = f"""[사용자의 최근 Omi Lifestream 로그]
{context_stream}

[사용자의 방금 전 발화]
{user_query}"""

        endpoint = f'https://generativelanguage.googleapis.com/v1beta/models/{self.config.gemini_model}:generateContent?key={api_key}'
        payload = {
            'system_instruction': {
                'parts': [{'text': system_instruction}]
            },
            'contents': [
                {
                    'role': 'user',
                    'parts': [{'text': prompt}]
                }
            ],
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': 400
            }
        }

        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_data = json.loads(resp.read().decode('utf-8'))
                candidates = resp_data.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts:
                        return parts[0].get('text', '').strip()
                return '응답을 생성하지 못했습니다.'
        except urllib.error.HTTPError as e:
            return f'Gemini API 오류 발생 (코드 {e.code})'
        except Exception as e:
            return f'요청 처리 중 오류: {str(e)}'
