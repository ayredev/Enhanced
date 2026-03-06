"""
Enhanced v2 — Optional Types.
Safe handling of values that may be absent.
"""


class OptionalTypeInfo:
    """Tracks optional value state."""

    def __init__(self, inner_type, has_value=False):
        self.inner_type = inner_type
        self.has_value = has_value
