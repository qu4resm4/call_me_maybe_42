FUNCTIONS_DEFINITION = data/input/functions_definition.json
DATA_INPUT = data/input/function_calling_tests.json
DATA_OUTPUT = data/output/function_calls.json

.PHONY: all install run run-no-install debug clean lint lint-strict check

all: run

check:
	@command -v uv >/dev/null || \
		(echo "'uv' não encontrado.\n Consulte as instruções no README.md ou instale em https://astral.sh/uv/#installation"; exit 1)

install: check
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