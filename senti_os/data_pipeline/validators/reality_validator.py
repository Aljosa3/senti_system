from senti_os.security.data_integrity_engine import DataIntegrityEngine

class RealityValidator:
    def __init__(self):
        self.integrity = DataIntegrityEngine()

    def validate(self, data):
        self.integrity.check_source(data)
