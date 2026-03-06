"""
Enhanced LSP — Completion Engine.
Context-aware autocomplete for verbs, keywords, variables, and pattern templates.
"""

# Full pattern templates for line-start completions
VERB_TEMPLATES = [
    {"label": "say", "detail": "Print a value", "insertText": 'say ', "kind": 14,
     "documentation": "Prints a value to the output.\nUsage: say \"Hello\" or say my_variable"},
    {"label": "the number", "detail": "Declare a number variable", "insertText": "the number ", "kind": 14,
     "documentation": "Declares a number variable.\nUsage: the number x is 5"},
    {"label": "the text", "detail": "Declare a text variable", "insertText": "the text ", "kind": 14,
     "documentation": "Declares a text variable.\nUsage: the text name is \"Alice\""},
    {"label": "create a list called", "detail": "Create a new list", "insertText": "create a list called ", "kind": 14,
     "documentation": "Creates an empty list.\nUsage: create a list called team"},
    {"label": "create a new", "detail": "Allocate heap object", "insertText": "create a new ", "kind": 14,
     "documentation": "Allocates a new object on the heap.\nUsage: create a new person called alice"},
    {"label": "add", "detail": "Add values or append to list", "insertText": "add ", "kind": 14,
     "documentation": "Adds numbers or appends to list.\nUsage: add x and y  OR  add \"Alice\" to team"},
    {"label": "subtract", "detail": "Subtract two numbers", "insertText": "subtract ", "kind": 14,
     "documentation": "Subtracts the second number from the first.\nUsage: subtract x from y"},
    {"label": "multiply", "detail": "Multiply two numbers", "insertText": "multiply ", "kind": 14,
     "documentation": "Multiplies two numbers.\nUsage: multiply x and y"},
    {"label": "divide", "detail": "Divide two numbers", "insertText": "divide ", "kind": 14,
     "documentation": "Divides the first number by the second.\nUsage: divide x by y"},
    {"label": "for each", "detail": "Loop over a list", "insertText": "for each ", "kind": 14,
     "documentation": "Iterates over every item in a list.\nUsage: for each name in team say name"},
    {"label": "if", "detail": "Conditional statement", "insertText": "if ", "kind": 14,
     "documentation": "Executes body if condition is true.\nUsage: if x greater than 5 say x"},
    {"label": "open the file", "detail": "Open a file handle", "insertText": 'open the file ', "kind": 14,
     "documentation": 'Opens a file as a linear resource.\nUsage: open the file "data.txt" as f'},
    {"label": "read from", "detail": "Read from handle", "insertText": "read from ", "kind": 14,
     "documentation": "Reads data from an open file handle.\nUsage: read from f"},
    {"label": "write", "detail": "Write data", "insertText": "write ", "kind": 14,
     "documentation": 'Writes data to a file or handle.\nUsage: write "hello" to f'},
    {"label": "close", "detail": "Close a resource", "insertText": "close ", "kind": 14,
     "documentation": "Closes an open file handle.\nUsage: close f"},
    {"label": "free", "detail": "Free heap object", "insertText": "free ", "kind": 14,
     "documentation": "Frees a heap-allocated object.\nUsage: free alice"},
    {"label": "check if", "detail": "Check condition", "insertText": "check if ", "kind": 14,
     "documentation": "Checks a condition.\nUsage: check if x is still valid"},
    {"label": "wait", "detail": "Sleep for seconds", "insertText": "wait ", "kind": 14,
     "documentation": "Pauses execution.\nUsage: wait 5 seconds"},
    {"label": "get the url", "detail": "HTTP GET request", "insertText": 'get the url ', "kind": 14,
     "documentation": 'Makes an HTTP GET request.\nUsage: get the url "https://..."'},
    {"label": "load the library", "detail": "Load shared library", "insertText": 'load the library ', "kind": 14,
     "documentation": 'Loads a native library for FFI.\nUsage: load the library "mylib"'},
    {"label": "call", "detail": "Call FFI function", "insertText": "call ", "kind": 14,
     "documentation": 'Calls a foreign function.\nUsage: call "func_name" with arg1 and arg2'},
    {"label": "sort", "detail": "Sort a list", "insertText": "sort ", "kind": 14,
     "documentation": "Sorts a list in place.\nUsage: sort my_list"},
    {"label": "remove", "detail": "Remove from list", "insertText": "remove ", "kind": 14,
     "documentation": "Removes a value from a list.\nUsage: remove \"Alice\" from team"},
]


class CompletionEngine:
    def complete(self, doc, position):
        """Return completion items for the given position."""
        items = []
        line_num = position.get('line', 0)
        char_num = position.get('character', 0)

        # Get current line text up to cursor
        lines = doc.content.split('\n')
        if line_num < len(lines):
            line_text = lines[line_num][:char_num]
        else:
            line_text = ''

        prefix = line_text.strip().lower()

        # At line start or beginning: suggest verb templates
        if not prefix or any(prefix.startswith(t['label'].lower()[:len(prefix)])
                            for t in VERB_TEMPLATES):
            for tmpl in VERB_TEMPLATES:
                if not prefix or tmpl['label'].lower().startswith(prefix):
                    items.append(self._make_item(tmpl, sort_prefix='0'))

        # Suggest variable names from definitions
        if doc.definitions:
            for name, info in doc.definitions.items():
                if not prefix or name.lower().startswith(prefix):
                    items.append({
                        'label': name,
                        'kind': 6,  # Variable
                        'detail': info.get('type', 'unknown'),
                        'documentation': f"Defined on line {info.get('line', '?')}",
                        'insertText': name,
                        'sortText': '1' + name,
                    })

        return items

    def _make_item(self, tmpl, sort_prefix='0'):
        return {
            'label': tmpl['label'],
            'kind': tmpl.get('kind', 14),
            'detail': tmpl.get('detail', ''),
            'documentation': tmpl.get('documentation', ''),
            'insertText': tmpl.get('insertText', tmpl['label']),
            'sortText': sort_prefix + tmpl['label'],
        }
