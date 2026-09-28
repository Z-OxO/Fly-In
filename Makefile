UV_RUN = uv run
MAP ?= data/maps/easy/01_linear_path.txt

.PHONY: all install run debug clean fclean re lint lint-strict

all: run

install:
	@uv sync

run: install
	@$(UV_RUN) python -m src $(MAP) $(ARGS)
debug: install
	@$(UV_RUN) python -m pdb -m src $(MAP) $(ARGS)
clean:
	@rm -rf .mypy_cache .pytest_cache dist
	@find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	rm -rf .venv

re: fclean all

lint: install
	@$(UV_RUN) flake8 . --exclude='./.venv'
	@$(UV_RUN) mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude './.venv'

lint-strict: install
	@$(UV_RUN) flake8 . --exclude='./.venv'
	@$(UV_RUN) mypy . --strict
