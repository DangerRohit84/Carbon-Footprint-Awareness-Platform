from datetime import datetime
from typing import Dict, Any, List

MAX_RECORDS: int = 100


class FootprintRecord:
    _records: List['FootprintRecord'] = []

    def __init__(self, data: Dict[str, Any], result: Dict[str, Any], transport_distance: float) -> None:
        self.transport_type: str = data.get('transport_type')
        self.transport_distance: float = transport_distance
        self.diet: str = data.get('diet')
        self.energy: str = data.get('energy')
        self.consumption: str = data.get('consumption')
        self.total: float = result['total']
        self.breakdown: Dict[str, float] = result['breakdown']
        self.category: str = result['category']
        self.timestamp: datetime = datetime.utcnow()

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
            'timestamp': self.timestamp.isoformat(),
        }

    @classmethod
    def save(cls, record: 'FootprintRecord') -> None:
        cls._records.append(record)
        if len(cls._records) > MAX_RECORDS:
            cls._records = cls._records[-MAX_RECORDS:]

    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in cls._records]

    @classmethod
    def get_recent(cls, limit: int = 10) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in cls._records[-limit:]]
