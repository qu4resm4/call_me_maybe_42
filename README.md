_This project has been created as part of the 42 curriculum by gquaresm._

TO-DO
- começar a implementação da restrição de geração e etc (buscando desacoplamento com strategies)

- entender como  Templates for Chat Models vão ajudar nos modelos.

ChatML templat


DONE
- terminar leitura do subject
- criar o makefile
- incluir o SDK
- rodar e testar o modelo no meu notebook (conferir viabilidade do projeto ser feito em casa)
- estudar os usos do SDK
- planejar o fluxo das interações
- arquitetar para cumprir os requisitos do bônus e disponibilizar a biblioteca (testar com outros modelos além do qwen? como?)
- extender classe com calling functions

- leitura e validação dos arquivos jsons
- definir esquema para o output (terminar main)



métodos como
-> invoke e etc
-> invoke calling function?
Tipar resposta normal e tipar resposta calling function

invoke  ->  uma chamada simples e bloqueante
stream  ->  um gerador é uma transmissão de dados das apis (bonus eu acho)
batch   ->  processamento em paralelo (bonus eu acho)

chain -> avançado do langchain para manipulação de correntes de prompts, conversas etc não vou fazer


// Cache de Prompt, Cache de Chave-Valor (KV) e Cache Semântico


não quero fazer um tokenizador proproi vai daR MUITO TRABALHO

ENTÃO O FLUXO SERÁ O SUGERIDO:
(prompts) -> tokenizador -> (tokens) -> conversor de input ids -> (input_ids) -> LLM processing -> (logits) -> geração token por token aplicando o restritor de JSON (constrained decoding) -> JSON vádilo 100% dos casos


prompt -> Tokenization -> Input IDs -> LLM -> Logits -> Next Token Selection

1. O modelo gera *logits* para todos os *tokens* possíveis.
2. Você identifica quais *tokens* manteriam tanto uma estrutura JSON válida quanto a conformidade com o esquema esperado.
3. Você define os *logits* dos *tokens* inválidos (aqueles que violam o esquema ou a estrutura) como menos infinito.
4. Você realiza a amostragem apenas a partir dos *tokens* válidos restantes.

Neste projeto, a decodificação com restrições deve não apenas garantir um JSON sintaticamente válido, mas também assegurar a conformidade com um esquema específico. Por exemplo, se um campo estiver restrito a um número no arquivo `functions_definition.json`, o decodificador limita a seleção de tokens a valores que correspondam a um número inteiro ou de ponto flutuante, preservando tanto a validade do JSON quanto a conformidade com o esquema. Isso garante que cada token gerado mantenha validade estrutural e semântica, respeitando o esquema exigido. Como resultado, o JSON produzido é totalmente recuperável e pode ser sempre analisado (parsed) sem erros.


Pense em como você pode usar o arquivo JSON de vocabulário para mapear a relação entre
tokens e suas representações em string. Isso é fundamental para
determinar quais tokens são válidos em cada etapa da geração.


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

Instalação do uv:

curl -LsSf https://astral.sh/uv/install.sh | sh



tecnicas de tags para LLMs



 https://huggingface.co/docs/transformers/v4.43.2/en/chat_templating?utm_source=chatgpt.com


 ---

TESTE DE FILHO DA PUTA

<|system|>
You are a friendly chatbot who always responds in the style of a pirate</s> 
<|user|>
How many helicopters can a human eat in one sitting?</s> 
<|assistant|>



---

<|im_start|> e <|im_end|>, que estruturam as mensagens combinados com três papéis principais: system, user e assistant

<think>...</think> blocks


tool (ou function): Usado em algumas variações modernas para chamadas e retornos de ferramentas externas