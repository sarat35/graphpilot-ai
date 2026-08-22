# buyseconds

BuySeconds is a monorepo for the web experience and the API service. Each application can be developed and deployed independently.

## Applications

- `apps/web` — Next.js frontend.
- `apps/api` — Python API service, managed with uv.
- `packages/api-client` — shared/generated frontend API client.

## Local development

Run the frontend:

```sh
make web-install
make web-dev
```

The frontend is pinned to pnpm 10.20.0, which matches its downloaded lockfile.

Run the API:

```sh
make api-sync
make api-run
```

See [docs/architecture.md](docs/architecture.md) and [docs/api-contract.md](docs/api-contract.md) for the intended application boundaries.

## Prerequisites

- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- Node.js 20 or later, with npm
- Docker and Docker Compose (optional)

## Frontend: build and run

The Next.js frontend is in `apps/web`. It uses pnpm 10.20.0, which is pinned to match its lockfile.

### Development

```sh
make web-install
make web-dev
```

Open http://localhost:3000.

### Production build

```sh
make web-build
cd apps/web
npx --yes pnpm@10.20.0 start
```

The production server listens on port 3000 by default.

## Backend: build and run

The FastAPI service is in `apps/api`.

### Development

```sh
make api-sync
make api-run
```

The API listens on http://localhost:8000. Its interactive OpenAPI documentation is at http://localhost:8000/docs.

### Production build and run

```sh
cd apps/api
uv sync --frozen --no-dev
APP_ENV=production uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Tests and checks

```sh
make api-test
make api-check
```

To build distributable backend packages:

```sh
cd apps/api
uv build
```

## Mock API endpoints

The local backend provides demonstration responses at:

- `GET /health`
- `GET /api/v1/cars`
- `GET /api/v1/searches`
- `GET /api/v1/saved-cars`
- `GET /api/v1/chatbot/status`

## Configuration

The mock flow works without credentials. To configure external services, copy the example environment file and set only the values you need:

```sh
cp .env.example .env
```

Docker Compose reads the root `.env` file. For local API development, export configuration values in your shell or place an `.env` file in `apps/api`.

## Docker

Build and run the API service directly:

```sh
docker build -t buyseconds-api apps/api
docker run --rm --env-file .env -p 8000:8000 buyseconds-api
```

Or use Docker Compose:

```sh
docker compose -f infra/docker-compose.yml up --build
```
