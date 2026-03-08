/**
 * Enhanced Browser Runtime
 * Loads and runs Enhanced .wasm files.
 */

const EnhancedRuntime = {
    async loadAndRun(wasmUrl) {
        const outputElement = document.getElementById('enhanced-output');
        
        const appendOutput = (text) => {
            if (outputElement) {
                outputElement.textContent += text + '\n';
            } else {
                console.log(text);
            }
        };

        const memory = new WebAssembly.Memory({ initial: 256, maximum: 256 });
        
        const readString = (ptr) => {
            const bytes = new Uint8Array(instance.exports.memory.buffer, ptr);
            let end = 0;
            while (bytes[end] !== 0) end++;
            return new TextDecoder().decode(bytes.slice(0, end));
        };

        const importObject = {
            env: {
                memory: memory,
                enhanced_print_str: (ptr) => {
                    appendOutput(readString(ptr));
                },
                enhanced_print_int: (val) => {
                    appendOutput(val.toString());
                },
                enhanced_print_bool: (val) => {
                    appendOutput(val !== 0 ? "true" : "false");
                },
                // Mock memory safety functions for now
                enhanced_alloc: (size) => {
                    // In a real implementation, we'd have a proper allocator
                    // For now, return a dummy generational reference
                    return { low: 0n, high: 0n }; 
                },
                enhanced_free: (ref) => {},
                enhanced_deref: (ref) => 0,
                enhanced_is_valid: (ref) => 1
            }
        };

        try {
            const response = await fetch(wasmUrl);
            const bytes = await response.arrayBuffer();
            const { instance } = await WebAssembly.instantiate(bytes, importObject);
            
            if (instance.exports.main) {
                instance.exports.main();
            } else if (instance.exports._start) {
                instance.exports._start();
            } else {
                console.error("No main or _start function found in WASM");
            }
        } catch (err) {
            console.error("Failed to load/run WASM:", err);
            appendOutput("Error: " + err.message);
        }
    }
};

window.EnhancedRuntime = EnhancedRuntime;
