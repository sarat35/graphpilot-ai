.PHONY: api-sync api-run api-test api-check web-install web-dev web-build

api-sync:
	cd apps/api && uv sync --all-groups

api-run:
	cd apps/api && uv run buyseconds

api-test:
	cd apps/api && uv run pytest

api-check:
	cd apps/api && uv run ruff check . && uv run black --check . && uv run pytest

web-install:
	cd apps/web && npx --yes pnpm@10.20.0 install --frozen-lockfile

web-dev:
	cd apps/web && npx --yes pnpm@10.20.0 dev

web-build:
	cd apps/web && npx --yes pnpm@10.20.0 build
