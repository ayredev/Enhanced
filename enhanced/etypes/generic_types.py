"""
Enhanced v2 — Generic Types.
Typed lists and maps with element/key/value type tracking.
"""


class GenericTypeInfo:
    """Tracks generic type information for typed collections."""

    def __init__(self, container_type, element_type=None, key_type=None, value_type=None):
        self.container_type = container_type  # 'list' or 'map'
        self.element_type = element_type      # for typed lists
        self.key_type = key_type              # for typed maps
        self.value_type = value_type           # for typed maps

    def check_element(self, actual_type, line, collection_name):
        """Check if an element matches the expected type of a typed list."""
        if self.element_type and actual_type != self.element_type:
            return (f"I found a problem on line {line}: '{collection_name}' is a list of "
                    f"{self.element_type}, not {actual_type}. "
                    f"Use 'create a new {self.element_type}' to add one to {collection_name}.")
        return None

    def check_map_key(self, actual_type, line, map_name):
        """Check if a key matches the expected key type of a typed map."""
        if self.key_type and actual_type != self.key_type:
            return (f"I found a problem on line {line}: '{map_name}' uses {self.key_type} keys, "
                    f"not {actual_type}.")
        return None

    def check_map_value(self, actual_type, line, map_name):
        """Check if a value matches the expected value type of a typed map."""
        if self.value_type and actual_type != self.value_type:
            return (f"I found a problem on line {line}: '{map_name}' stores {self.value_type} values, "
                    f"not {actual_type}.")
        return None
