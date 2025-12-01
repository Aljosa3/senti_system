from senti_os.security.security_policy import SecurityPolicy

class PermissionsValidator:
    def __init__(self):
        self.policy = SecurityPolicy()

    def validate(self, data):
        if not self.policy.is_allowed_data_source(data):
            raise PermissionError("This data source is not allowed by policy.")
