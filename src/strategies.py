
from abc import ABC, abstractmethod

# ESCOLHA DE TOKEN:
# Greedy
# Sampling

# VERIFICAÇÃO DE TOKEN VALIDO:
# DFA
# Trie
# Grammar

class TokenSelector(ABC):

    @abstractmethod
    def select(self, logits: np.ndarray) -> int:
        pass

class GreedySelector(TokenSelector):
    def select(self, logits):
        return int(np.argmax(logits))

# GreedySelector
# TopKSelector
# TopPSelector
# TemperatureSelector

# A estratégia de escolha (Greedy, Top-K, Top-P, Temperature) é uma coisa.
# A restrição estrutural (DFA, Trie, Grammar) é outra.
# Eu separaria isso em dois contratos independentes.

# TokenRestrictor
# ConstrainedDecoder
# TokenConstraint


# assinatura errada, o modelo nao deerica entrar aqui
# a lista de ids de tokens viriam no parametro, saidno de um método usado da classe LLM
# isso não deveria ser para desscobrir qual é o token aprovado (id token)
# deveria ser a estrategia de como identificar se o token é ou não um dos tokens permitidos recebidos por parametros
# class TokenRestrictor(ABC):

#     @abstractmethod
#     def allowed_tokens(
#         self,
#         generated_text: str,
#         backend: LLMBackend # ?
#     ) -> set[int]:
#         pass

    # class TokenConstraint(ABC):

    # @abstractmethod
    # def allowed_tokens(
    #     self,
    #     generated_ids: list[int]
    # ) -> set[int]:
    #     pass

    # class TokenConstraint(ABC):

    # @abstractmethod
    # def mask_logits(
    #     self,
    #     logits: list[float],
    #     generated_ids: list[int]
    # ) -> list[float]:
    #     pass

#     mplementações:

# JSONDFARestrictor

# TrieRestrictor

# GrammarRestrictor

# NoRestriction


# Ou trocar:

# JsonSchemaDfaEngine()

# por

# JsonGrammarEngine()

# sem tocar na LLM.