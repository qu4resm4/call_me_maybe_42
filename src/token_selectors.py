# Token Selection Strategies

# The `TokenSelector` is responsible for selecting the next token from the modified
# logits distribution (after `TokenRestrictor` has applied masking). Separating this
# from restriction allows for flexible sampling strategies.

# ## Implemented Strategies (Planned)
# 1. **Greedy (Argmax):** Always selects the token with the highest probability.
# 2. **Top-K:** Keeps only the `K` most likely tokens and samples from them.
# 3. **Top-P (Nucleus Sampling):** Samples from the smallest set of tokens whose 
# cumulative probability exceeds `P`.
# 4. **Temperature Sampling:** Adjusts the distribution sharpness before sampling
# (`logits / temperature`).

# The `TokenRestrictor` modifies logits (e.g., setting invalid token logits to `-inf`)
# BEFORE the `TokenSelector` processes them.
