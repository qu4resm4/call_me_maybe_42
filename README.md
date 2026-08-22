_This project has been created as part of the 42 curriculum by gquaresm._

TO-DO
- começar a implementação da restrição de geração e etc (buscando desacoplamento com strategies)

- entender como  Templates for Chat Models vão ajudar nos modelos.

ChatML templat

DFA = Deterministic Finite Automaton (Autômato Finito Determinístico).


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

`generation_state`

Representa algo como:
```
Estou dentro de um objeto JSON.
A próxima coisa esperada é uma propriedade.
A propriedade atual é "arguments".
O nome da função já foi escolhido.
A função é fn_add_numbers.
Agora estou dentro dos argumentos.
O próximo campo esperado é "a".
O tipo de "a" é integer.
```

Isso não precisa conter os tokens inteiros do contexto.
*Ele pode manter informações derivadas do contexto.*


<|im_start|> e <|im_end|>, que estruturam as mensagens combinados com três papéis principais: system, user e assistant

<think>...</think> blocks


tool (ou function): Usado em algumas variações modernas para chamadas e retornos de ferramentas externas

Constrained Decoding

--- MODELO DE INFERENCIA

LLM inference is the process of running a pre-trained large language model to generate output tokens for new input prompts, without updating the models learned parameters. During inference, the model processes the input through its transformer layers to predict the probability of possible next tokens. Then, the model generates the response one token at a time while using previously generated tokens as context.

https://www.ibm.com/think/topics/llm-inference

# switch to inference-only mode
for p in self._model.parameters():
    p.requires_grad = False


O que são modelos autorregressivos?
Os modelos autorregressivos são uma classe de modelos de aprendizado de máquina (ML) que predizem automaticamente o próximo componente em uma sequência fazendo medições de entradas anteriores na sequência. A autorregressão é uma técnica estatística usada na análise de séries temporais que pressupõe que o valor atual de uma série temporal é uma função de seus valores passados. Modelos autorregressivos usam técnicas matemáticas semelhantes para determinar a correlação probabilística entre elementos em uma sequência. Eles então usam o conhecimento derivado para adivinhar o próximo elemento em uma sequência desconhecida. Por exemplo, durante o treinamento, um modelo autorregressivo processa várias frases em inglês e identifica que a palavra “is” sempre segue a palavra “there”. Em seguida, ele gera uma nova sequência que tem “there is” junto.

https://aws.amazon.com/pt/what-is/autoregressive-models/


---

float('-inf'): A forma mais comum, que não exige nenhuma importação.-math.inf: Usando o módulo nativo math (necessita de import math).-np.inf: Usando a biblioteca NumPy, caso trabalhe com análise de 



Um pad token (token de preenchimento) é um marcador especial usado para igualar o tamanho de diferentes sequências de texto em um lote (batch). As redes neurais processam matrizes e precisam que todas as frases tenham exatamente a mesma quantidade de números/tokens

igualar tamanho 


calculo de atenção

O cálculo de atenção é uma ferramenta matemática usada em inteligência artificial para ajudar modelos de linguagem a entenderem o contexto de palavras em uma frase. Ele usa três vetores principais chamados de Consulta (Query), Chave (Key) e Valor (Value).


                    Function Schemas
                           │
                           ▼
                 Constraint Compiler
             (Schema → DFA/Grammar)
                           │
                           ▼
                  GenerationState
                           │
                           ▼
                  TokenRestrictor
                           │
                 logits mascarados
                           │
                           ▼
                  TokenSelector
                           │
                           ▼
                     next_token_id


                     ---

contexto atual:  user
Se meu nome é Gabriel Quaresma, qual seria meu nome primeiro nome?
assistant
<think>
Okay, the user is asking for Gabriel Quaresma's first name. Let me start by recalling that Gabriel is the last name. The first name would be the initial part of the surname. So, Gabriel is the last name, and the first part is G. Therefore, the first name should be Gabriel. I should confirm that there's no confusion with other names or that the user might have a different intended name. Also, make sure to present the answer clearly and concisely.
</think>

Seu primeiro nome é **Gabriel**.





https://huggingface.co/docs/transformers/chat_response_parsing


ChatML (Chat Markup Language) is a structured text format that organizes conversations for AI models using special tokens and roles like system, user, and assistant.Key Parts of ChatMLSpecial Tokens: Uses tags like <|im_start|> and <|im_end|> to mark where a message begins and ends.Roles: Identifies who is speaking using labels like system, user, assistant, and tool.Why People Use ItClear Boundaries: Stops the AI from getting confused about who gave an instruction.Better Safety: Helps block prompt injection attacks by separating developer rules from user text.Standard Control: Works well across many different open-source and commercial language models.Would you like to see a code example of how a ChatML prompt is written, or do you want to learn how to use it in an API request?


    # Special tokens support (moved from SpecialTokensMixin)
    # V5: Clean separation of named special tokens from extra special tokens
    SPECIAL_TOKENS_ATTRIBUTES = [
        "bos_token",
        "eos_token",
        "unk_token",
        "sep_token",
        "pad_token",
        "cls_token",
        "mask_token",
    ]


Esses atributos vêm da biblioteca Hugging Face Transformers e representam os principais tokens especiais usados na história do Processamento de Linguagem Natural (PLN). Modelos diferentes (como Qwen, BERT, GPT, Llama) usam esses tokens para propósitos específicos.
Aqui está a explicação direta do papel de cada um:
## 1. bos_token (Beginning of Sequence)

* O que faz: Indica o início absoluto de um texto ou documento.
* Para que serve: Avisa o modelo que uma nova sequência está começando do zero. Ao gerar texto livre, o modelo usa esse token como o primeiro "input" para começar a prever a primeira palavra.
* Exemplos comuns: <s>, <|startoftext|>.

## 2. eos_token (End of Sequence)

* O que faz: Indica o fim absoluto de um texto ou documento.
* Para que serve: Como vimos no Qwen, ele avisa o modelo (e o script de inferência) que a geração de texto chegou ao fim e o processo deve ser interrompido.
* Exemplos comuns: </s>, <|endoftext|>, <|im_end|>.

## 3. unk_token (Unknown Token)

* O que faz: Representa uma palavra ou caractere desconhecido pelo vocabulário do modelo.
* Para que serve: Se o usuário digitar algo que o tokenizador não consegue processar (como um caractere japonês raro em um modelo puramente inglês), esse caractere é substituído pelo unk_token para o modelo não quebrar.
* Nota moderna: LLMs modernos (como o Qwen e o Llama) usam tokenizadores do tipo Byte-Pair Encoding (BPE) baseados em bytes. Eles quase nunca usam o unk_token, pois conseguem quebrar qualquer palavra desconhecida em bytes brutos.
* Exemplos comuns: <unk>, [UNK].

## 4. sep_token (Separator Token)

* O que faz: Separa duas partes distintas de um mesmo texto na mesma entrada.
* Para que serve: Era muito usado em modelos de arquitetura Encoder (como o BERT) para tarefas que envolviam dois blocos de texto. Por exemplo: separar a Pergunta do Contexto em tarefas de responder perguntas, ou separar a Frase A da Frase B.
* Exemplos comuns: [SEP], </s>.

## 5. pad_token (Padding Token)

* O que faz: Serve para preenchimento de espaço vazio.
* Para que serve: As GPUs processam dados em lotes (batches), e todas as sequências de um lote precisam ter exatamente o mesmo tamanho (comprimento de matriz). Se você processa uma frase de 5 tokens e uma de 10 tokens juntas, o modelo adiciona o pad_token 5 vezes no final da frase menor para equilibrar os comprimentos.
* Exemplos comuns: <pad>, [PAD], <|endoftext|>.

## 6. cls_token (Classification Token)

* O que faz: Token de classificação posicionado no início do texto.
* Para que serve: Muito específico da arquitetura BERT. O modelo é treinado para consolidar a representação semântica de toda a frase dentro do vetor desse único token. Se você quer classificar se uma frase é positiva ou negativa, você passa o vetor gerado na posição do cls_token para uma camada linear de classificação.
* Exemplos comuns: [CLS].

## 7. mask_token (Masked Token)

* O que faz: Serve para mascarar (esconder) uma palavra.
* Para que serve: Usado no pré-treinamento de modelos de linguagem mascarados (como o BERT novamente). O script substitui palavras aleatórias do texto por esse token (Ex: "O gato subiu no [MASK]") e força o modelo a adivinhar qual era a palavra original ("telhado") para aprender o idioma.
* Exemplos comuns: [MASK], <mask>.

------------------------------
## Resumo prático para o seu Qwen:
Como o Qwen é um modelo do tipo Causal LM (Decoder-only) focado em chat, os únicos tokens dessa lista que realmente importam ativamente no seu dia a dia de código são o eos_token (para parar o chat no momento certo) e o pad_token (para você conseguir treinar ou rodar inferência em lote/batch). Atributos como cls_token, sep_token e mask_token geralmente ficam vazios (None) no Qwen.
Se você quiser, posso te mostrar como aplicar o pad_token e o eos_token na prática em um script do Hugging Face usando o DataCollatorForSeq2Seq para preparar dados de treino, ou como configurar o attention mask para ignorar os tokens de pad. O que prefere ver agora?



---

2. What your added_tokens list in tokenizer.json actually is
The tokenizer.json file is the serialized fast tokenizer from the tokenizers library. It contains: vocabulary, merges, pre/post-processing, plus a list called added_tokens. (Hugging Face)

Your added_tokens snippet:

151643 <|endoftext|> true
151644 <|im_start|> true
151645 <|im_end|> true
151646 <|object_ref_start|> true
151647 <|object_ref_end|> true
151648 <|box_start|> true
151649 <|box_end|> true
151650 <|quad_start|> true
151651 <|quad_end|> true
151652 <|vision_start|> true
151653 <|vision_end|> true
151654 <|vision_pad|> true
151655 <|image_pad|> true
151656 <|video_pad|> true
151657 <tool_call> false
151658 </tool_call> false
151659 <|fim_prefix|> false
151660 <|fim_middle|> false
151661 <|fim_suffix|> false
151662 <|fim_pad|> false
151663 <|repo_name|> false
151664 <|file_sep|> false
151665 <tool_response> false
151666 </tool_response> false
151667 <think> false
151668 </think> false
Here:

The first column is the token ID.
The middle column is the string form of the token.
The last true/false is the Rust-tokenizer-level special flag. (paddlenlp.readthedocs.io)
What that flag does in the fast tokenizer:

special = true

The token is treated as an indivisible “added token”.
The pre-tokenizer will not split it into smaller pieces.
When you decode with skip_special_tokens=True, these tokens will be removed. (Hugging Face)
special = false

The token is just an extra vocab token. It may still be one piece, but it does not get special handling in the tokenizer’s decode / skip logic.


https://discuss.huggingface.co/t/how-to-understand-the-special-tokens/170916/2


---

mensagens (dict)
        │
        ▼
apply_chat_template
        │
        ▼
tokens
        │
        ▼
LLM
        │
        ▼
tokens gerados
        │
        ▼
separar mensagens pelos delimitadores
        │
        ▼
decode de cada mensagem
        │
        ▼
parser XML/JSON
        │
        ▼
dict Python


---

# DIFERENÇA DE Chat Mark Language PARA CADA FAMILIA

O termo ChatML refere-se originalmente a um padrão criado pela OpenAI para estruturar conversas usando tags explícitas de início e fim (<|im_start|> e <|im_end|>). No entanto, a comunidade de IA passou a usar o termo "Chat Template" (ou formatos estilo ChatML) para descrever a forma exata como diferentes Large Language Models (LLMs) convertem um histórico de mensagens em um bloco único de texto bruto. [1, 2] 
Cada modelo usa tokens especiais (control tokens) e sintaxes diferentes para separar o que é comando do sistema, fala do usuário e resposta da IA. Veja abaixo como o mesmo diálogo é formatado em diferentes modelos do mercado: [3, 4] 
------------------------------
## O Diálogo de Exemplo (Input)
Para todas as comparações abaixo, imagine que passamos a seguinte lista estruturada de mensagens: [5] 

* 
* System: "Você é um assistente conciso."
* User: "Qual a cor do céu?"
* Assistant: "O céu é azul."
* User: "E à noite?"
* 

------------------------------
## 1. ChatML Puro (Qwen, DeepSeek, Hermes, Dolphin)
O formato ChatML clássico usa tags explícitas que parecem XML para delimitar o início e o fim de cada turno. Modelos modernos que usam raciocínio avançado costumam embutir uma tag <think> dentro da resposta do assistente. [1, 6] 

<|im_start|>system
Você é um assistente conciso.<|im_end|>
<|im_start|>user
Qual a cor do céu?<|im_end|>
<|im_start|>assistant
<think>O usuário perguntou a cor do céu. Devo responder brevemente.</think>O céu é azul.<|im_end|>
<|im_start|>user
E à noite?<|im_end|>
<|im_start|>assistant

## 2. Llama 3 & Llama 3.1 (Meta)
A Meta abandonou os formatos antigos e criou uma estrutura baseada em tokens especiais reservados (<|begin_of_text|>, <|start_header_id|>, <|end_header_id|>, <|eot_id|>). Eles evitam que o usuário simule comandos do sistema injetando texto comum. [1] 

<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Você é um assistente conciso.<|eot_id|><|start_header_id|>user<|end_header_id|>

Qual a cor do céu?<|eot_id|><|start_header_id|>assistant<|end_header_id|>

O céu é azul.<|eot_id|><|start_header_id|>user<|end_header_id|>

E à noite?<|eot_id|><|start_header_id|>assistant<|end_header_id|>

## 3. Mistral & Mixtral (Formatos Instruct)
Os modelos da Mistral AI historicamente usam marcadores rígidos baseados em colchetes [INST] e [/INST]. Um detalhe crítico: os modelos antigos da Mistral não suportavam nativamente uma mensagem de sistema separada, exigindo que ela fosse concatenada junto ao primeiro comando do usuário.

<s>[INST] Você é um assistente conciso.

Qual a cor do céu? [/INST] O céu é azul. </s><s>[INST] E à noite? [/INST]

## 4. Gemma & Gemma 2 (Google)
Os modelos abertos do Google utilizam tags de controle textuais diretas envoltas em sinais de menor e maior (<start_of_turn> e <end_of_turn>), seguidas pelo nome do papel (role).

<start_of_turn>system
Você é um assistente conciso.<end_of_turn>
<start_of_turn>user
Qual a cor do céu?<end_of_turn>
<start_of_turn>assistant
O céu é azul.<end_of_turn>
<start_of_turn>user
E à noite?<end_of_turn>
<start_of_turn>assistant

## 5. Llama 2 (Formato Antigo da Meta)
O Llama 2 possuía um dos templates de chat mais complexos e fáceis de errar manualmente, injetando marcadores <<SYS>> dentro das tags de instrução [INST].

<s>[INST] <<SYS>>
Você é um assistente conciso.
<<SYS>>

Qual a cor do céu? [/INST] O céu é azul. </s><s>[INST] E à noite? [/INST]

------------------------------
## Resumo das Diferenças

| Modelo | Token de Início de Turno | Token de Fim de Turno | Tag de Mensagem de Sistema |
|---|---|---|---|
| ChatML / Qwen | `< | im_start | >[role]\n` |
| Llama 3 / 3.1 | `< | start_header_id | >[role]< |
| Gemma | <start_of_turn>[role]\n | <end_of_turn>\n | Nativa (system) |
| Mistral | [INST] | [/INST] | Embutida no primeiro [INST] |

💡 Nota Importante: Para evitar quebrar a IA, nunca monte essas strings manualmente no seu código. Use sempre a função tokenizer.apply_chat_template(messages) da biblioteca Hugging Face Transformers. Ela lê o arquivo tokenizer_config.json do modelo específico e injeta as tags perfeitamente. [2, 5] 

Se você estiver desenvolvendo uma aplicação, me diga:

* 
* Qual modelo específico você pretende usar?
* Você está montando um arquivo para treinamento (Fine-Tuning) ou para inferência (API/Prompt)?
* 

Posso gerar o código Python exato com o template Jinja2 correto para o seu caso.


https://qwen.readthedocs.io/en/v2.0/inference/chat.html