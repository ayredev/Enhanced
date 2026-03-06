"""
Enhanced v2 — Struct Types.
Manages struct definitions and instance tracking.
"""


class StructRegistry:
    """Global registry of struct type definitions."""

    def __init__(self):
        self.structs = {}  # name -> {'fields': {field_name: field_type}}

    def define(self, name, fields):
        """Register a struct type definition.
        fields: list of (field_name, field_type) tuples
        """
        if name in self.structs:
            return f"The type '{name}' has already been defined."
        field_map = {}
        for fname, ftype in fields:
            if fname in field_map:
                return f"The field '{fname}' is defined twice in '{name}'."
            field_map[fname] = ftype
        self.structs[name] = {'fields': field_map}
        return None

    def lookup(self, name):
        """Get a struct definition by name."""
        return self.structs.get(name)

    def has_field(self, struct_name, field_name):
        """Check if a struct type has a given field."""
        defn = self.structs.get(struct_name)
        if not defn:
            return False
        return field_name in defn['fields']

    def field_type(self, struct_name, field_name):
        """Get the type of a field on a struct."""
        defn = self.structs.get(struct_name)
        if not defn:
            return None
        return defn['fields'].get(field_name)

    def all_fields(self, struct_name):
        """Get all fields for a struct type."""
        defn = self.structs.get(struct_name)
        if not defn:
            return {}
        return dict(defn['fields'])

    def resolve_field_path(self, base_type, field_path):
        """Resolve a nested field path and return the final type.
        Returns (resolved_type, error_message).
        """
        current_type = base_type
        for field_name in field_path:
            defn = self.structs.get(current_type)
            if not defn:
                return None, f"'{current_type}' is not a struct type, so it doesn't have fields."
            if field_name not in defn['fields']:
                return None, f"'{current_type}' doesn't have a field called '{field_name}'."
            current_type = defn['fields'][field_name]
        return current_type, None
