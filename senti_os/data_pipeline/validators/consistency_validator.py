class ConsistencyValidator:
    """
    Preverja, ali podatki niso 'self-contradictory'.
    """

    def validate(self, data):
        payload = data.get("payload", {})
        if payload is None:
            raise ValueError("Payload cannot be None.")
