from typing import Any, Dict

class SchemaToDFACompiler:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        
    def compile(self) -> Dict[str, Any]:
        """
        Converte JSON Schema simplificado em estados navegáveis.
        Retorna um dicionário representando as transições permitidas.
        """
        # Implementação simplificada para o MVP
        # Exemplo: mapear tipos para restrições de token
        dfa = {}
        properties = self.schema.get("properties", {})
        
        for prop, details in properties.items():
            dfa[prop] = details.get("type")
            
        return dfa
