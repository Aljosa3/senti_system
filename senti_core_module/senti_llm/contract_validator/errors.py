class ContractValidationError(Exception):
    pass


class ContractSanitizationError(Exception):
    pass


class ContractSchemaError(Exception):
    pass


class StrictModeViolation(Exception):
    pass
