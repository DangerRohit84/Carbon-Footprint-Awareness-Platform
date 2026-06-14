from datetime import datetime

MAX_RECORDS = 100


class FootprintRecord:
    _records = []

    def __init__(self, data, result, transport_distance):
        self.transport_type = data.get('transport_type')
        self.transport_distance = transport_distance
        self.diet = data.get('diet')
        self.energy = data.get('energy')
        self.consumption = data.get('consumption')
        self.total = result['total']
        self.breakdown = result['breakdown']
        self.category = result['category']
        self.timestamp = datetime.utcnow()

    def to_dict(self):
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
    def save(cls, record):
        cls._records.append(record)
        if len(cls._records) > MAX_RECORDS:
            cls._records = cls._records[-MAX_RECORDS:]

    @classmethod
    def get_all(cls):
        return [r.to_dict() for r in cls._records]

    @classmethod
    def get_recent(cls, limit=10):
        return [r.to_dict() for r in cls._records[-limit:]]
