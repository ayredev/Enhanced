class TypeError(Exception):
    pass

class TypeSystem:
    # Primitive types
    INT = "int"
    STR = "str"
    BOOL = "bool"
    LIST = "list"
    MAP = "map"
    OPTIONAL = "optional"

    @classmethod
    def check_binary_op(cls, op, left_type, right_type, line):
        if op == '+':
            if left_type == cls.INT and right_type == cls.INT:
                return cls.INT
            else:
                raise TypeError(f"I found a problem on line {line}: You can't add {cls.noun_for_type(left_type)} and {cls.noun_for_type(right_type)} together. They need to be the same type.")
        elif op == '-':
            if left_type == cls.INT and right_type == cls.INT:
                return cls.INT
            else:
                raise TypeError(f"I found a problem on line {line}: You can't subtract {cls.noun_for_type(right_type)} from {cls.noun_for_type(left_type)}. Both must be numbers.")
        elif op in ('*', '/', '%', 'pow'):
            if left_type == cls.INT and right_type == cls.INT:
                return cls.INT
            else:
                raise TypeError(f"I found a problem on line {line}: You can't use math on {cls.noun_for_type(left_type)} and {cls.noun_for_type(right_type)}. They both must be numbers.")
        raise TypeError(f"I found a problem on line {line}: Unknown operation '{op}'")

    @classmethod
    def noun_for_type(cls, type_name):
        if type_name == cls.INT:
            return "a number"
        elif type_name == cls.STR:
            return "a text"
        elif type_name == cls.BOOL:
            return "a truth"
        elif type_name == cls.LIST:
            return "a list"
        elif type_name == cls.MAP:
            return "a map"
        elif type_name == cls.OPTIONAL:
            return "an optional"
        return f"a {type_name}"
        
    @classmethod
    def check_condition(cls, cond_type, line):
        if cond_type != cls.BOOL:
            raise TypeError(f"I found a problem on line {line}: The condition needs to be true or false, but you gave {cls.noun_for_type(cond_type)}.")

    @classmethod
    def check_assignment(cls, expected_type, actual_type, line, name):
        if expected_type == "any":
            return  # accept any type
        if expected_type != actual_type:
             raise TypeError(f"I found a problem on line {line}: '{name}' is declared as {cls.noun_for_type(expected_type)}, but you assigned {cls.noun_for_type(actual_type)} to it.")

    @classmethod
    def check_list_append(cls, list_type, element_type, val_type, line, name):
        if list_type != cls.LIST:
            raise TypeError(f"I found a problem on line {line}: '{name}' is {cls.noun_for_type(list_type)}, not a list. You can't add to it.")
        if element_type is not None and val_type != element_type:
            raise TypeError(f"I found a problem on line {line}: '{name}' holds {cls.noun_for_type(element_type)}s, but you're trying to add {cls.noun_for_type(val_type)}.")

