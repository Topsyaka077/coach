Coach — personal AI life coach.

## Development

Start DB + backend:

```
docker compose up
```

Run frontend locally (separate terminal):

```
cd frontend && npm run dev
```

Frontend at http://localhost:3000, backend at http://localhost:8000.

## Production

Run everything in Docker:

```
docker compose -f docker-compose.prod.yml up --build
```
