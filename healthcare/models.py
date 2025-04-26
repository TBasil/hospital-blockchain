from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Patient:
    id: str
    public_key: str
    demographic_data: Dict
    access_list: List[str]

@dataclass
class Doctor:
    id: str
    public_key: str
    specialization: str

@dataclass
class Prescription:
    medication: str
    dosage: str
    frequency: str
    duration: str