# Este Makefile foi criado seguindo as definições existentes no subject deste projeto e incluí adaptações para compatibilidade entre sistemas operacionais diferentes
# Autor: gquaresm

# ============================================================
# Sistema Operacional
# ============================================================

# Definição de variáveis para compatibilidade das utilidades em SO POSIX e Windows
ifeq ($(OS),Windows_NT)
    PLATFORM := WINDOWS
    USERNAME := $(USERNAME)

    CLEAR := cls
    MKDIR := if not exist
else
    PLATFORM := UNIX
    USERNAME := $(USER)

    CLEAR := clear
    MKDIR := mkdir -p
endif

# ============================================================
# Ambiente específico da 42 Rio
# ============================================================

# Variáveis para inserir nos processos filhos que iram trocar os caminhos de onde as ferramentas guardam o cache (especificamente para os computadores do laboratório da 42Rio)
ifeq ($(USERNAME),gquaresm)
    export UV_PROJECT_ENVIRONMENT = /home/$(USER)/sgoinfre/.venv
    export UV_CACHE_DIR = /home/$(USER)/sgoinfre/.uv_cache
    export UV_TOOL_DIR = /home/$(USER)/sgoinfre/.uv_tools
    export HF_HOME = /home/$(USER)/sgoinfre/hf_cache
endif

# ============================================================
# Arquivos
# ============================================================

# Variáveis para o comando que roda o projeto
FUNCTIONS_DEFINITION = data/input/functions_definition.json
DATA_INPUT = data/input/function_calling_tests.json
DATA_OUTPUT = data/output/function_calling_results.json
# MODEL = Qwen/Qwen3-0.6B
# MODEL = HuggingFaceTB/SmolLM2-360M-Instruct   # é um SLM então tem a acuracia baixissima
# MODEL = google/gemma-3-1b-it   # acuracia baixa 6/11
# MODEL = microsoft/Phi-3-mini-4k-instruct   # SLM horrivel também
MODEL = NousResearch/Hermes-3-Llama-3.2-3B

.PHONY: all install run run-no-install debug clean lint lint-strict check

# ============================================================
# Targets
# ============================================================

all: run

# Comando para exibir uma mensagem amigável caso o projeto seja executado em um ambiente sem as ferramentas de requisito
check:
ifeq ($(PLATFORM),WINDOWS)
	@$ where uv || ( \
		echo. & \
		echo 'uv' nao encontrado. & \
		echo Consulte as instrucoes no README.md ou instale em: & \
		echo https://astral.sh/uv/#installation & \
		exit /b 1 \
	)
else
	@ command -v uv || ( \
		echo ""; \
		echo "'uv' não encontrado."; \
		echo "Consulte as instruções no README.md"; \
		echo "ou instale em https://astral.sh/uv/#installation"; \
		exit 1; \
	)
endif

install: check
ifeq ($(USERNAME),gquaresm)
ifeq ($(PLATFORM),UNIX)
	@$(MKDIR) $(UV_CACHE_DIR)
	@$(MKDIR) $(UV_TOOL_DIR)
	@$(MKDIR) $(HF_HOME)
endif
endif
	uv sync

run: install
	@$(CLEAR)
	uv run python -m src --functions_definition $(FUNCTIONS_DEFINITION) --input $(DATA_INPUT) --output $(DATA_OUTPUT) --model $(MODEL)

run-no-install: check
	@echo Executando sem sincronizar dependências...
	uv run --no-sync python -m src --functions_definition $(FUNCTIONS_DEFINITION) --input $(DATA_INPUT) --output $(DATA_OUTPUT) --model $(MODEL)

debug: install
	uv run python -m pdb -m src --functions_definition $(FUNCTIONS_DEFINITION) --input $(DATA_INPUT) --output $(DATA_OUTPUT) --model $(MODEL)

clean:
ifeq ($(PLATFORM),WINDOWS)
	if exist __pycache__ for /d /r %%d in (__pycache__) do @rmdir /s /q "%%d"
	for /r %%f in (*.pyc) do @del /q "%%f"
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist .mypy_cache rmdir /s /q .mypy_cache
else
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
endif

lint: install
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	uv run flake8 .

lint-strict: install
	uv run mypy . --strict
	uv run flake8 .
