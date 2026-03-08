/**
 * Enhanced Browser Runtime
 * Loads and runs Enhanced .wasm files.
 */

const EnhancedRuntime = {
    async loadAndRun(wasmUrl) {
        const outputElement = document.getElementById('enhanced-output');
        const screenElement = document.getElementById('enhanced-screen') || document.body;
        
        const uiElements = new Map(); // id -> element
        let nextElementId = 1;

        const appendOutput = (text) => {
            if (outputElement) {
                outputElement.textContent += text + '\n';
            } else {
                console.log(text);
            }
        };

        const memory = new WebAssembly.Memory({ initial: 256, maximum: 256 });
        let instance;
        
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
                // UI Functions
                enhanced_ui_create_element: (typePtr) => {
                    const type = readString(typePtr);
                    let el;
                    if (type === 'text') {
                        el = document.createElement('div');
                        el.className = 'enhanced-text';
                    } else if (type === 'button') {
                        el = document.createElement('button');
                        el.className = 'enhanced-button';
                    } else if (type === 'input') {
                        el = document.createElement('input');
                        el.className = 'enhanced-input';
                    } else if (type === 'box') {
                        el = document.createElement('div');
                        el.className = 'enhanced-box';
                    } else {
                        el = document.createElement('div');
                    }
                    const id = nextElementId++;
                    uiElements.set(id, el);
                    return id;
                },
                enhanced_ui_set_property: (id, propPtr, valPtr) => {
                    const el = uiElements.get(id);
                    if (!el) return;
                    const prop = readString(propPtr);
                    const val = readString(valPtr);
                    if (prop === 'text') {
                        if (el.tagName === 'INPUT') el.value = val;
                        else el.textContent = val;
                    } else if (prop === 'color') {
                        el.style.color = val;
                    }
                },
                enhanced_ui_add_to_screen: (id) => {
                    const el = uiElements.get(id);
                    if (el) screenElement.appendChild(el);
                },
                enhanced_ui_set_event_handler: (id, eventPtr, funcIndex) => {
                    const el = uiElements.get(id);
                    if (!el) return;
                    const event = readString(eventPtr);
                    const jsEvent = event === 'clicked' ? 'click' : 
                                    event === 'hovered' ? 'mouseover' :
                                    event === 'changed' ? 'input' : event;
                    
                    el.addEventListener(jsEvent, () => {
                        // Call WASM function by index if possible, or just mock it
                        // In real WASM Table, we'd use instance.exports.table.get(funcIndex)()
                        if (instance.exports.__indirect_function_table) {
                            instance.exports.__indirect_function_table.get(funcIndex)();
                        }
                    });
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
            const result = await WebAssembly.instantiate(bytes, importObject);
            instance = result.instance;
            
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
