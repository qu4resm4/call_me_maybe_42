## Context

Esta mudança altera o pipeline de geração de tokens para injetar uma camada de restrição (constrained decoding) antes da seleção de tokens do modelo. Ver `proposal.md` para motivação.

## Goals / Non-Goals

**Goals:**
- Implementar mecanismo de mascaramento de logits (`TokenRestrictor`) para forçar conformidade com o JSON Schema.
- Implementar máquina de estados (`GenerationState`) para rastrear o progresso da gramática JSON.
- Garantir que o output seja sempre um JSON recuperável.

**Non-Goals:**
- Implementar um novo tokenizador.
- Suportar chamadas de função complexas com recursividade profunda (neste momento).

# Design: Constrained Decoding (FSM-based)

O objetivo é garantir a geração de chamadas de função (`tool_call`) estritamente formatadas e válidas, restringindo os tokens da LLM de forma dinâmica baseada em uma Máquina de Estados Finitos (FSM) que opera em nível de string decodificada.

## Estrutura da FSM de Cobertura (JSON)

A FSM valida a sequência de tokens decodificados, garantindo a sintaxe JSON e a inclusão das tags XML `<tool_call>`.

```text
START
  │
  ▼
OPEN_TOOL_TAG ("<tool_call>")
  │
  ▼
OPEN_JSON_BRACE ("{")
  │
  ▼
KEY_NAME_START ("\"") ──> KEY_NAME_CONTENT ("name") ──> KEY_NAME_END ("\"")
  │
  ▼
COLON_1 (":")
  │
  ▼
VALUE_NAME_START ("\"") ──> VALUE_NAME_CONTENT (func_name) ──> VALUE_NAME_END ("\"")
  │
  ▼
COMMA (",")
  │
  ▼
KEY_ARGS_START ("\"") ──> KEY_ARGS_CONTENT ("arguments") ──> KEY_ARGS_END ("\"")
  │
  ▼
COLON_2 (":")
  │
  ▼
ARGS_VALUE_CONTENT (JSON Object/Schema Validated)
  │
  ▼
CLOSE_JSON_BRACE ("}")
  │
  ▼
CLOSE_TOOL_TAG ("</tool_call>")
  │
  ▼
FINISHED
```

## Princípios de Implementação

1.  **Decodificação de Tokens:** O `GenerationState` decodifica cada token gerado e o adiciona a um buffer.
2.  **Validação de Fase (`update_phase_by_buffer`):** A FSM transita de estado validando a conformidade com a estrutura JSON e as tags XML.
3.  **Restrição Dinâmica:**
    *   Fases estáticas (tags e sintaxe JSON) são verificadas contra tokens candidatos.
    *   A fase `VALUE_NAME_CONTENT` restringe tokens aos nomes de funções válidas (`bind_functions`).
    *   A fase `ARGS_VALUE_CONTENT` utiliza o Schema da função selecionada para restringir dinamicamente a geração dos argumentos.
4.  **Robustez:** O validador será tolerante a whitespace irrelevante, mas estrito quanto à sintaxe JSON.
5.  **Recuperação:** Erros de sintaxe ou violação da estrutura forçarão o fechamento da sequência (`-inf` em logits de tokens inesperados).

## Histórico de Decisões

- **Mudança da abordagem original (DFA de Schema complexo) para FSM de Cobertura (nível string/buffer)**: Decidimos simplificar para evitar bibliotecas externas e complexidade excessiva, tratando a estrutura como fases sequenciais obrigatórias.

