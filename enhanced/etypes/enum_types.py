"""
Enhanced v2 — Enum Types.
Named variant tracking and validation.
"""


class EnumRegistry:
    """Registry for enum type definitions."""

    def __init__(self):
        self.enums = {}  # name -> list of variant strings

    def define(self, name, variants):
        """Register an enum type."""
        if name in self.enums:
            return f"The type '{name}' has already been defined."
        self.enums[name] = list(variants)
        return None

    def lookup(self, name):
        return self.enums.get(name)

    def has_variant(self, enum_name, variant):
        variants = self.enums.get(enum_name)
        if not variants:
            return False
        return variant in variants

    def variant_index(self, enum_name, variant):
        variants = self.enums.get(enum_name)
        if not variants or variant not in variants:
            return -1
        return variants.index(variant)
