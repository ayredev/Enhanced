import pytest
import os
import subprocess
from enhanced.pipeline import Pipeline, PipelineError

def test_wasm_hello_compilation():
    pipeline = Pipeline(keep_ll=True, target="web")
    source = "enhanced/examples/hello_web.en"
    html_path, stats = pipeline.run(source)
    assert os.path.exists(html_path)
    assert html_path.endswith(".html")
    assert os.path.exists(html_path.replace(".html", ".wasm"))
    with open(html_path, 'r') as f:
        content = f.read()
        assert "Enhanced - hello_web" in content
        assert "hello_web.wasm" in content

def test_wasm_ir_target_triple():
    pipeline = Pipeline(keep_ll=True, target="web")
    source = "enhanced/examples/hello_web.en"
    html_path, stats = pipeline.run(source)
    ll_path = stats['ll_path']
    with open(ll_path, 'r') as f:
        content = f.read()
        assert 'target triple = "wasm32-unknown-unknown"' in content
        assert 'declare void @enhanced_print_str(i8*)' in content

def test_wasm_compat_file_read():
    pipeline = Pipeline(target="web")
    with open("test_fail.en", "w") as f:
        f.write('read the file "test.txt"')
    with pytest.raises(PipelineError) as excinfo:
        pipeline.run("test_fail.en")
    assert "File I/O operations (read) are not supported" in str(excinfo.value)
    os.remove("test_fail.en")

def test_wasm_compat_file_write():
    pipeline = Pipeline(target="web")
    with open("test_fail.en", "w") as f:
        f.write('write "hello" to the file "test.txt"')
    with pytest.raises(PipelineError) as excinfo:
        pipeline.run("test_fail.en")
    assert "File I/O operations (write) are not supported" in str(excinfo.value)
    os.remove("test_fail.en")

def test_wasm_compat_http():
    pipeline = Pipeline(target="web")
    with open("test_fail.en", "w") as f:
        f.write('get the url "http://example.com"')
    with pytest.raises(PipelineError) as excinfo:
        pipeline.run("test_fail.en")
    assert "HTTP operations are not supported" in str(excinfo.value)
    os.remove("test_fail.en")

def test_wasm_compat_db():
    pipeline = Pipeline(target="web")
    with open("test_fail.en", "w") as f:
        f.write('open database "test.db" as mydb')
    with pytest.raises(PipelineError) as excinfo:
        pipeline.run("test_fail.en")
    assert "Database operations are not supported" in str(excinfo.value)
    os.remove("test_fail.en")

def test_wasm_compat_server():
    pipeline = Pipeline(target="web")
    with open("test_fail.en", "w") as f:
        f.write('start a server on port 8080')
    with pytest.raises(PipelineError) as excinfo:
        pipeline.run("test_fail.en")
    assert "Server operations are not supported" in str(excinfo.value)
    os.remove("test_fail.en")

def test_wasm_print_int_codegen():
    pipeline = Pipeline(keep_ll=True, target="web")
    with open("test_print_int.en", "w") as f:
        f.write("say 42")
    _, stats = pipeline.run("test_print_int.en")
    with open(stats['ll_path'], 'r') as f:
        content = f.read()
        assert "call void @enhanced_print_int(i32 42)" in content
    os.remove("test_print_int.en")

def test_wasm_print_bool_codegen():
    pipeline = Pipeline(keep_ll=True, target="web")
    with open("test_print_bool.en", "w") as f:
        f.write("say true")
    _, stats = pipeline.run("test_print_bool.en")
    with open(stats['ll_path'], 'r') as f:
        content = f.read()
        assert "call void @enhanced_print_bool(i32 1)" in content
    os.remove("test_print_bool.en")

def test_wasm_counter_compilation():
    pipeline = Pipeline(target="web")
    html_path, _ = pipeline.run("enhanced/examples/counter_web.en")
    assert os.path.exists(html_path)

def test_wasm_structs_compilation():
    pipeline = Pipeline(target="web")
    html_path, _ = pipeline.run("enhanced/examples/structs_web.en")
    assert os.path.exists(html_path)

def test_wasm_native_remains_unchanged():
    # Verify that default target is still native and generates printf/puts
    pipeline = Pipeline(keep_ll=True, target="native")
    with open("test_native.en", "w") as f:
        f.write('say "hello"')
    _, stats = pipeline.run("test_native.en")
    with open(stats['ll_path'], 'r') as f:
        content = f.read()
        assert 'declare i32 @puts(i8*)' in content
        assert 'target triple =' in content # Should have native triple
        assert 'wasm32' not in content
    os.remove("test_native.en")

def test_wasm_print_variable_str():
    pipeline = Pipeline(keep_ll=True, target="web")
    with open("test_var.en", "w") as f:
        f.write('the name is "Bob"\nsay name')
    _, stats = pipeline.run("test_var.en")
    with open(stats['ll_path'], 'r') as f:
        content = f.read()
        assert "call void @enhanced_print_str(i8* %v" in content or "call void @enhanced_print_str(i8* %name" in content
    os.remove("test_var.en")

def test_wasm_print_variable_int():
    pipeline = Pipeline(keep_ll=True, target="web")
    with open("test_var_int.en", "w") as f:
        f.write('the age is 25\nsay age')
    _, stats = pipeline.run("test_var_int.en")
    with open(stats['ll_path'], 'r') as f:
        content = f.read()
        assert "call void @enhanced_print_int(i32 %v" in content or "call void @enhanced_print_int(i32 %age" in content
    os.remove("test_var_int.en")

def test_wasm_binary_op_compilation():
    pipeline = Pipeline(target="web")
    with open("test_binop.en", "w") as f:
        f.write("say add 10 and 20")
    html_path, _ = pipeline.run("test_binop.en")
    assert os.path.exists(html_path)
    os.remove("test_binop.en")

def test_wasm_for_loop_compilation():
    pipeline = Pipeline(target="web")
    with open("test_for.en", "w") as f:
        f.write("for each number i from 1 to 3:\n    say i")
    html_path, _ = pipeline.run("test_for.en")
    assert os.path.exists(html_path)
    os.remove("test_for.en")

def test_wasm_nested_compat_check():
    # Test that compat checker works inside blocks
    pipeline = Pipeline(target="web")
    with open("test_nested_fail.en", "w") as f:
        f.write("if true:\n    read the file \"test.txt\"")
    with pytest.raises(PipelineError) as excinfo:
        pipeline.run("test_nested_fail.en")
    assert "File I/O operations (read) are not supported" in str(excinfo.value)
    os.remove("test_nested_fail.en")

def test_wasm_browser_runtime_exists():
    assert os.path.exists("enhanced/browser/enhanced_browser.js")
    with open("enhanced/browser/enhanced_browser.js", "r") as f:
        content = f.read()
        assert "enhanced_print_str" in content
        assert "enhanced_print_int" in content
