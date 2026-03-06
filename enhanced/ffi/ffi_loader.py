# FFI Loader maps Python-side resolution checking.

import ctypes
import os
import sys

def resolve_library_path(name):
    # Depending on OS, append extension
    if sys.platform == 'win32':
        ext = '.dll'
    elif sys.platform == 'darwin':
        ext = '.dylib'
    else:
        ext = '.so'
    
    if not name.endswith(ext):
        name += ext
        
    return name

def validate_function(lib_path, func_name):
    # In a full compiler, this verifies at compile time.
    # For now, it just ensures the file exists.
    if not os.path.exists(lib_path):
        raise Exception(f"I couldn't find the library '{lib_path}'. Make sure it's in the same folder as your .en file.")
    return True
