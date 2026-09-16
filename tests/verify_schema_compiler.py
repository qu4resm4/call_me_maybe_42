from src.schema_compiler import SchemaToDFACompiler

def test_compiler():
    schema = {
        "type": "object",
        "properties": {
            "a": {"type": "integer"},
            "b": {"type": "string"}
        }
    }
    
    compiler = SchemaToDFACompiler(schema)
    dfa = compiler.compile()
    
    assert dfa["a"] == "integer"
    assert dfa["b"] == "string"
    print("Compiler verified: types mapped correctly!")

if __name__ == "__main__":
    test_compiler()
