class ProvenanceValidator:
    def validate(self, data):
        if "origin" not in data or not data["origin"]:
            raise ValueError("Invalid data origin.")
