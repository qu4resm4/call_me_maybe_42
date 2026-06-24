_This project has been created as part of the 42 curriculum by gquaresm._

TO-DO

- terminar leitura do subject

- criar o makefile

- incluir o SDK
- rodar e testar o modelo no meu notebook (conferir viabilidade do projeto ser feito em casa)

- estudar os usos do SDK
- planejar o fluxo das interações
- arquitetar para cumprir os requisitos do bônus e disponibilizar a biblioteca (testar com outros modelos além do qwen? como?)




extender classe com calling functions

métodos como
-> invoke e etc
-> invoke calling function?
Tipar resposta normal e tipar resposta calling function








[10:09, 6/21/2026] quaresma: extender classe com calling functions

métodos como

-> invoke e etc
-> invoke calling function?
[10:10, 6/21/2026] quaresma: Tipar resposta normal e tipar resposta calling function








Check for bonus features (optional, not required for passing):
• Support for multiple LLM models beyond Qwen/Qwen3-0.6B
• Recoding the tokenizer: avoiding direct use of encode and decode in the main code,
instead using get_logits_from_input_ids and get_path_to_vocabulary_json
• Advanced error recovery mechanisms
• Performance optimizations (caching, batching)
• Comprehensive test suite
• Visualization of the generation process
• Support for complex nested function arguments
• Public implementation of tokenizer encode and optional decode methods
• Demonstration of how encoding and decoding integrate with constrained decoding


---

Verifique os recursos adicionais (opcional, não obrigatório para aprovação):
• Suporte para múltiplos modelos LLM além do Qwen/Qwen3-0.6B
• Recodificação do tokenizador: evitando o uso direto de encode e decode no código principal,
em vez disso, usando get_logits_from_input_ids e get_path_to_vocabulary_json
• Mecanismos avançados de recuperação de erros
• Otimizações de desempenho (cache, processamento em lote)
• Conjunto de testes abrangente
• Visualização do processo de geração
• Suporte para argumentos de função aninhados complexos
• Implementação pública dos métodos encode e decode (opcional) do tokenizador
• Demonstração de como a codificação e a decodificação se integram com a decodificação restrita


---

README:

uv run python -m src [--functions_definition <function_definition_file>] [--input <input_file>] [--output <output_file>]

uv run python -m src
--functions_definition data/input/functions_definition.json
--input data/input/function_calling_tests.json
--output data/output/function_calls.json

Pré-requisitos

- uv
- ram

Instalação do uv:

curl -LsSf https://astral.sh/uv/install.sh | sh