"""
Enhanced LSP — Hover Documentation.
Returns structured hover content for verbs, variables, type keywords, and resources.
"""

VERB_DOCS = {
    "say": "**say**\nPrints a value to the output.\n\nUsage: `say \"Hello\"` or `say my_variable`\n\nEquivalent to: `print()` in Python",
    "create": "**create**\nCreates a new list or heap object.\n\nUsage: `create a list called team`\nor: `create a new person called alice`",
    "add": "**add**\nAdds two numbers or appends to a list.\n\nUsage: `add x and y` or `add \"Alice\" to team`",
    "subtract": "**subtract**\nSubtracts the second number from the first.\n\nUsage: `subtract x from y`\n\nStores result in `result`.",
    "multiply": "**multiply**\nMultiplies two numbers.\n\nUsage: `multiply x and y`",
    "divide": "**divide**\nDivides the first number by the second.\n\nUsage: `divide x by y`",
    "set": "**set**\nAssigns a value to a variable.\n\nUsage: `set the presence state to \"Active\"`",
    "read": "**read**\nReads a file or handle.\n\nUsage: `read the file \"data.txt\"` or `read from f`",
    "write": "**write**\nWrites data to a file or handle.\n\nUsage: `write \"hello\" to the file \"out.txt\"` or `write \"data\" to f`",
    "append": "**append**\nAppends data to a file.\n\nUsage: `append \"more\" to the file \"log.txt\"`",
    "open": "**open**\nOpens a file handle (linear resource).\n\nUsage: `open the file \"data.txt\" as f`\n\n*Must be closed before end of program.*",
    "close": "**close**\nCloses an open file handle.\n\nUsage: `close f`",
    "free": "**free**\nFrees a heap-allocated object.\n\nUsage: `free alice`\n\nAfter freeing, the object is invalid.",
    "check": "**check**\nChecks a condition.\n\nUsage: `check if x is still valid`\nor: `check if the file \"f\" exists`",
    "sort": "**sort**\nSorts a list in place.\n\nUsage: `sort my_list`",
    "remove": "**remove**\nRemoves a value from a list.\n\nUsage: `remove \"Alice\" from team`",
    "wait": "**wait**\nPauses execution.\n\nUsage: `wait 5 seconds`",
    "get": "**get**\nMakes an HTTP GET request.\n\nUsage: `get the url \"https://api.example.com\"`",
    "load": "**load**\nLoads a native shared library for FFI.\n\nUsage: `load the library \"discord_rpc\"`",
    "call": "**call**\nCalls a foreign function.\n\nUsage: `call \"func\" with arg1 and arg2`",
    "send": "**send**\nSends data through a handle.\n\nUsage: `send \"data\" through conn`",
    "exists": "**exists**\nChecks if a file exists.\n\nUsage: `check if the file \"x\" exists`",
}

TYPE_DOCS = {
    "number": "**number**\nA whole integer value (32-bit).\n\nOperations: add, subtract, multiply, divide\n\nExample: `the number x is 5`",
    "text": "**text**\nA string of characters.\n\nOperations: say, write, concatenation\n\nExample: `the text name is \"Alice\"`",
    "list": "**list**\nAn ordered collection of items.\n\nOperations: add to, remove from, sort, for each\n\nExample: `create a list called team`",
    "file": "**file**\nA file path or file handle.\n\nOperations: read, write, append, open, close\n\nExample: `open the file \"data.txt\" as f`",
    "person": "**person**\nA heap-allocated object type.\n\nManaged by generational references.\n\nExample: `create a new person called alice`",
    "user": "**user**\nA heap-allocated object type.\n\nManaged by generational references.\n\nExample: `create a new user called bob`",
    "connection": "**connection**\nA network connection (linear resource).\n\nMust be opened and closed.\n\nExample: `open the connection to \"...\" as conn`",
}

KEYWORD_DOCS = {
    "the": "**the** — Article\nUsed before type names in declarations.\n\nExample: `the number x is 5`",
    "a": "**a** — Article\nUsed before `list` or `new` in creation.\n\nExample: `create a list called team`",
    "an": "**an** — Article\nAlternative article before vowels.\n\nExample: `create an item`",
    "is": "**is** — Assignment operator\nAssigns a value to a variable.\n\nExample: `the number x is 5`",
    "for": "**for** — Loop keyword\nUsed with `each` to iterate.\n\nExample: `for each name in team say name`",
    "each": "**each** — Iteration keyword\nIterates over every item.\n\nExample: `for each item in list`",
    "in": "**in** — Membership/iteration\nUsed in loops and membership checks.\n\nExample: `for each x in list` or `check if x is in list`",
    "if": "**if** — Conditional\nExecutes code if condition is true.\n\nExample: `if x greater than 5 say x`",
}


class HoverEngine:
    def hover(self, doc, position):
        """Return hover content for the word at position."""
        line_num = position.get('line', 0)
        char_num = position.get('character', 0)

        lines = doc.content.split('\n')
        if line_num >= len(lines):
            return None

        line = lines[line_num]
        word = self._word_at(line, char_num)
        if not word:
            return None

        wl = word.lower()

        # Check verbs
        if wl in VERB_DOCS:
            return {'contents': {'kind': 'markdown', 'value': VERB_DOCS[wl]}}

        # Check type keywords
        if wl in TYPE_DOCS:
            return {'contents': {'kind': 'markdown', 'value': TYPE_DOCS[wl]}}

        # Check structural keywords
        if wl in KEYWORD_DOCS:
            return {'contents': {'kind': 'markdown', 'value': KEYWORD_DOCS[wl]}}

        # Check user-defined variables
        if doc.definitions and word in doc.definitions:
            info = doc.definitions[word]
            var_type = info.get('type', 'unknown')
            def_line = info.get('line', '?')
            is_handle = var_type in ('handle', 'handle_closed')
            status = ''
            if is_handle:
                status = '\n\n*Linear resource — must be closed before end of program.*'
            content = (f"**{word}** — {var_type}\n\n"
                       f"Defined on line {def_line}"
                       f"{status}")
            return {'contents': {'kind': 'markdown', 'value': content}}

        return None

    def _word_at(self, line, col):
        """Extract the word at column position."""
        if col >= len(line):
            col = max(0, len(line) - 1)
        if not line or not line[col].isalnum() and line[col] != '_':
            return None

        start = col
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
            start -= 1
        end = col
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        return line[start:end] if start < end else None
