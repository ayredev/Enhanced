.PHONY: build install test clean hello

build:
	clang -c runtime/enhanced_runtime.c -o runtime/enhanced_runtime.o
	clang -c runtime/enhanced_stdlib.c -o runtime/enhanced_stdlib.o
	clang -c runtime/enhanced_memory.c -o runtime/enhanced_memory.o

install: build
	cp enhc.py /usr/local/bin/enhc
	chmod +x /usr/local/bin/enhc
	@echo "Enhanced 0.1.0 installed successfully."

test:
	python -m unittest discover tests

clean:
	rm -f *.o *.ll *.exe enhanced_runtime*.o
	rm -f runtime/*.o
	rm -f examples/*.o examples/*.ll examples/*.exe

hello: build
	python enhc.py examples/hello.en --run
