class WrapperError(Exception):
    pass


class WrapperSchemaError(WrapperError):
    pass


class WrapperNormalizationError(WrapperError):
    pass


class WrapperValidationError(WrapperError):
    pass


class WrapperAnomalyError(WrapperError):
    pass


class WrapperProviderError(WrapperError):
    pass
