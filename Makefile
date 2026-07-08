# Variáveis para inserir nos processos filhos que iram trocar os caminhos de onde as ferramentas guardam o cache
#export UV_PROJECT_ENVIRONMENT = /home/$(USER)/goinfre/.venv
#export UV_CACHE_DIR = /home/$(USER)/goinfre/.uv_cache
#export UV_TOOL_DIR = /home/$(USER)/goinfre/.uv_tools
#export HF_HOME = /home/$(USER)/goinfre/hf_cache

export UV_PROJECT_ENVIRONMENT = /home/$(USER)/sgoinfre/.venv
export UV_CACHE_DIR = /home/$(USER)/sgoinfre/.uv_cache
export UV_TOOL_DIR = /home/$(USER)/sgoinfre/.uv_tools
export HF_HOME = /home/$(USER)/sgoinfre/hf_cache

# Variáveis para definição nos comandos

FUNCTIONS_DEFINITION = data/input/functions_definition.json
DATA_INPUT = data/input/function_calling_tests.json
DATA_OUTPUT = data/output/function_calls.json

.PHONY: all install run run-no-install debug clean lint lint-strict check

all: run

check:
	@command -v uv >/dev/null || \
		(echo "'uv' não encontrado.\n Consulte as instruções no README.md ou instale em https://astral.sh/uv/#installation"; exit 1)

install: check
	mkdir -p $(UV_CACHE_DIR)
	mkdir -p $(UV_TOOL_DIR)
	mkdir -p $(HF_HOME)
	uv sync

run: install
	@clear
	uv run python -m src --functions_definition $(FUNCTIONS_DEFINITION) --input $(DATA_INPUT) --output $(DATA_OUTPUT)

run-no-install: check
	@echo "Executando sem sincronizar dependências..."
	uv run --no-sync python -m src --functions_definition $(FUNCTIONS_DEFINITION) --input $(DATA_INPUT) --output $(DATA_OUTPUT)

debug: install
	uv run python -m pdb -m src --functions_definition $(FUNCTIONS_DEFINITION) --input $(DATA_INPUT) --output $(DATA_OUTPUT)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint: install
	-uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	-uv run flake8 .

lint-strict: install
	-uv run mypy . --strict
	-uv run flake8 .