## 1. Setup e Foundations

- [x] 1.1 Implementar a classe `GenerationState` baseada em FSM de fases de cobertura.
- [x] 1.2 Definir a interface `TokenRestrictor` e integrar com a nova FSM.

## 2. Lógica de Restrição

- [x] 2.1 Implementar mascaramento de logits no `TokenRestrictor` baseado no estado da FSM.
- [x] 2.2 Implementar `update_phase_by_buffer` no `GenerationState` para validar sintaxe JSON e transitar entre estados estruturais.

## 3. Integração e Validação Final

- [ ] 3.1 Integrar o fluxo restrito ao `llm_sdk_calling_function.py` e verificar que o teste `test_pipeline.py` passa (foco em integração).
- [ ] 3.2 Executar a `moulinette` no projeto finalizado e garantir que o score de conformidade seja atingido.
