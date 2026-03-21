# RAIL-INTELLIGENCE

Simulation of railway network intelligence using core DSA:

- Graph + Dijkstra for rerouting
- Greedy interval partitioning for platform allocation
- Doubly linked list for coach fault localization
- State machine for safety controller

## Run

```bash
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` for Swagger UI.

