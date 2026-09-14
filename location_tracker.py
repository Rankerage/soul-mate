import json
import math
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Optional, Tuple
from config import AppConfig
from models import LocationData, GeofencePoint

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c

class LocationTracker:
    """Termux-location 연동 및 Chaos Geofence 평가기"""
    def __init__(self, config: AppConfig):
        self.config = config
        self.current_location: Optional[LocationData] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _poll_loop(self):
        while self._running:
            loc = self._fetch_termux_location()
            if loc:
                self.current_location = loc
            time.sleep(self.config.location_poll_interval)

    def _fetch_termux_location(self) -> Optional[LocationData]:
        try:
            result = subprocess.run(
                ['termux-location', '-p', 'network', '-r', 'once'],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                lat = float(data.get('latitude', 0.0))
                lon = float(data.get('longitude', 0.0))
                acc = float(data.get('accuracy', 0.0))
                prov = data.get('provider', 'network')
                
                is_familiar, zone_name = self._evaluate_geofence(lat, lon)
                return LocationData(
                    latitude=lat,
                    longitude=lon,
                    accuracy=acc,
                    provider=prov,
                    timestamp=time.time(),
                    is_familiar=is_familiar,
                    zone_name=zone_name
                )
        except Exception:
            pass
        return None

    def _evaluate_geofence(self, lat: float, lon: float) -> Tuple[bool, str]:
        if lat == 0.0 and lon == 0.0:
            return False, '위치 미식별'

        for zone in self.config.familiar_zones:
            dist = haversine_distance_km(lat, lon, zone.lat, zone.lon)
            if dist <= zone.radius_km:
                return True, f'{zone.name} (일상 구역, 거리 {dist:.1f}km)'

        return False, '새로운 미지의 좌표 (비일상 구역)'

    def get_latest_location(self) -> LocationData:
        if self.current_location:
            return self.current_location
        return LocationData(
            latitude=37.2754,
            longitude=127.1158,
            is_familiar=True,
            zone_name='위치 캐시 대기 중 (기본: 용인)'
        )
