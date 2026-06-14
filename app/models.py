"""In-memory data store with JSON file persistence.

Records survive server restarts by writing to a JSON file.
Capped at MAX_RECORDS to control memory usage.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

MAX_RECORDS: int = 100
DATA_FILE: str = os.path.join(os.path.dirname(__file__), '..', 'data', 'records.json')


class FootprintRecord:
    """Stores a single carbon footprint calculation result."""

    _records: List[Dict[str, Any]] = []
    _loaded: bool = False

    def __init__(self, data: Dict[str, Any], result: Dict[str, Any], transport_distance: float) -> None:
        self.transport_type: Optional[str] = data.get('transport_type')
        self.transport_distance: float = transport_distance
        self.diet: Optional[str] = data.get('diet')
        self.energy: Optional[str] = data.get('energy')
        self.consumption: Optional[str] = data.get('consumption')
        self.total: float = result['total']
        self.breakdown: Dict[str, float] = result['breakdown']
        self.category: str = result['category']
        self.timestamp: str = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'transport_type': self.transport_type,
            'transport_distance': self.transport_distance,
            'diet': self.diet,
            'energy': self.energy,
            'consumption': self.consumption,
            'total': self.total,
            'breakdown': self.breakdown,
            'category': self.category,
            'timestamp': self.timestamp,
        }

    @classmethod
    def _ensure_loaded(cls) -> None:
        if not cls._loaded:
            cls._load_from_disk()

    @classmethod
    def _load_from_disk(cls) -> None:
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    cls._records = json.load(f)
            except (json.JSONDecodeError, IOError):
                cls._records = []
        cls._loaded = True

    @classmethod
    def _save_to_disk(cls) -> None:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(cls._records, f, indent=2)
        except IOError:
            pass

    @classmethod
    def save(cls, record: 'FootprintRecord') -> None:
        cls._ensure_loaded()
        record_dict = record.to_dict()
        cls._records.append(record_dict)
        if len(cls._records) > MAX_RECORDS:
            cls._records = cls._records[-MAX_RECORDS:]
        cls._save_to_disk()

    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        cls._ensure_loaded()
        return list(cls._records)

    @classmethod
    def get_recent(cls, limit: int = 10) -> List[Dict[str, Any]]:
        cls._ensure_loaded()
        return list(cls._records[-limit:])
