## Why

O LLM, em sua natureza probabilística, muitas vezes gera JSONs sintaticamente inválidos ou desalinhados com o esquema esperado (function calling). Para garantir que as chamadas de função sejam sempre executáveis e semanticamente corretas, é necessária a implementação de um sistema de Decodificação Restrita (Constrained Decoding) via FSM (Máquina de Estados Finitos) baseada em fases de cobertura e mascaramento de logits.

## What Changes

- **Implementação do `TokenRestrictor`**: Nova classe responsável pelo mascaramento de logits com base no estado atual da geração, prevenindo a seleção de tokens que violam a estrutura JSON esperada ou o esquema definido.
- **Criação do `GenerationState`**: Gerenciador da máquina de estados baseada em fases de cobertura (FSM) que rastreia a evolução da geração (ex: esperando `<tool_call>`, esperando chave, esperando valor, etc.).
- **Integração com Moulinette**: Inclusão de um fluxo de teste final utilizando a ferramenta `moulinette` para garantir a conformidade do output com os requisitos do projeto.

## Capabilities

### New Capabilities
- `constrained-decoding`: Capacidade de restringir a geração do LLM a um JSON válido e conforme ao esquema de funções via FSM de fases.

### Modified Capabilities
<!-- Nenhuma alteração em requisitos de capacidades existentes -->

## Impact

- **Código**: Refatoração substancial de `src/llm_sdk_calling_function.py` para injetar a lógica de restrição.
- **Novos Módulos**: `src/token_restrictors.py`, `src/constraints.py`.
- **Validação**: Inclusão da `moulinette` no pipeline de testes.
