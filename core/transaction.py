from dataclasses import dataclass
from typing import Dict
from time import time

@dataclass
class MedicalTransaction:
    patient_id: str
    doctor_id: str
    record_type: str
    data: Dict
    timestamp: float = None
    signature: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time()

    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'record_type': self.record_type,
            'data': self.data,
            'timestamp': self.timestamp,
            'signature': self.signature
        }