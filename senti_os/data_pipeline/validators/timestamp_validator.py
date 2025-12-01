import time

class TimestampValidator:
    MAX_SKEW_SECONDS = 60 * 10  # 10 minutes

    def validate(self, data):
        now = time.time()
        if abs(now - data["timestamp"]) > self.MAX_SKEW_SECONDS:
            raise ValueError("Timestamp skew outside allowed range.")
