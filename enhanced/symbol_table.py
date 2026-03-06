class SymbolTableError(Exception):
    pass

class SymbolTable:
    def __init__(self):
        # List of dictionaries, each dict represents a scope level
        # Index 0 is global scope
        self.scopes = [{}]
    
    def enter_scope(self):
        self.scopes.append({})
        
    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
            
    def define(self, name, type_name, line):
        scope = self.scopes[-1]
        if name in scope and name != "result":
            raise SymbolTableError(f"I found a problem on line {line}: '{name}' is already defined in this scope.")
        
        scope[name] = {
            'name': name,
            'type': type_name,
            'line': line,
            'initialized': True # assume defined means initialized for now
        }
        
    def lookup(self, name, current_line):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
                
        raise SymbolTableError(f"I found a problem on line {current_line}: '{name}' hasn't been defined yet. Define it first with 'the ... {name} is ...'")
