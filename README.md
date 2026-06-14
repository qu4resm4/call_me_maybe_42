TO-DO

- terminar leitura do subject

- criar o makefile

- incluir o SDK
- rodar e testar o modelo no meu notebook (conferir viabilidade do projeto ser feito em casa)

- estudar os usos do SDK
- planejar o fluxo das interações
- arquitetar para cumprir os requisitos do bônus e disponibilizar a biblioteca (testar com outros modelos além do qwen? como?)


uv run python -m src [--functions_definition <function_definition_file>] [--input <input_file>] [--
output <output_file>]


uv run python -m src
--functions_definition data/input/functions_definition.json
--input data/input/function_calling_tests.json
--output data/output/function_calls.json



README:

Pré-requisitos

- uv
- ram

Instalação do uv:

curl -LsSf https://astral.sh/uv/install.sh | sh