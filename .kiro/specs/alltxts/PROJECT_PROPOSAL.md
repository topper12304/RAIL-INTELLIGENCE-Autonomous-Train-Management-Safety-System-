# Railway Smart Network Simulator - Project Proposal

## Motivation (1 pt)
Railway networks frequently experience cascading delays due to track blockages, inefficient platform allocation, slow fault identification, and unsafe emergency stops. Real-world systems rely on manual operators or proprietary centralized controls, rarely demonstrated academically using core DSA.

**This project solves** by implementing **4 DSA modules** for railway intelligence:
1. **Graph + Dijkstra**: Automatic rerouting around blocked tracks
2. **Greedy Intervals**: Optimal platform allocation 
3. **Doubly Linked List**: O(n) coach fault localization
4. **State Machine**: Intelligent emergency stops (avoid bridges/tunnels)

Bridges DSA theory to transportation engineering, teaching algorithm application to infrastructure challenges.

## State of the Art / Current Solutions (1 pt)
**Industry**: Centralized Traffic Control (CTC) systems + human dispatchers for rerouting/platforms. Mechanical emergency brakes without geo-awareness. Manual coach inspections.

**Academia**: Ticket booking apps dominate; few DSA-driven railway sims. **Our gap**: Pure algorithmic simulation of **Network, Platform, Coach, Safety** modules as REST API + interactive UI.

## Project Goals & Milestones (2 pts)
**General Goals**:
- Simulate railway ops using DSA: Graphs, Greedy, DLL, FSM
- Build FastAPI backend + interactive frontend
- Demonstrate real-time rerouting, allocation, fault-finding, safety

**Milestones** (completed):
1. **Graph Module**: Adjacency list + Dijkstra with edge removal (rerouting)
2. **Platform Module**: Greedy sweep line for min platforms
3. **Coach Module**: DLL for fault index detection
4. **Safety Module**: FSM preventing unsafe stops

## Project Approach (3 pts)
**Modular DSA Architecture** (Python/FastAPI):

1. **Network Layer**: 
   - Stations = nodes, tracks = weighted edges
   - `Graph.add_edge()`, `remove_edge()` for blockages
   - `dijkstra()` priority queue → shortest alternate path

2. **Platform Layer**: 
   - Intervals → events sort → sweep line max overlap

3. **Coach Layer**: 
   - DLL tail-append coaches → single pass fault traversal

4. **Safety Layer**: 
   - Enum states + unsafe zones → nearest safe position

**Tech Stack**:
- Backend: FastAPI (API) + Pydantic (validation) + Uvicorn
- Frontend: Vanilla HTML/JS/CSS + Fetch API
- Testing: pytest unit tests per module

**Interfaces**: REST POST /network/shortest-path, etc. → Interactive forms UI

## System Architecture Diagram
```
[Frontend UI] --> REST API (FastAPI + CORS)
                    |
                    v
[Main App] --> [Routers] --> [Core DSA Modules]
  |                |            |
Swagger /docs   Models      Graph | Platform | Coach DLL | Safety FSM
```

## Project Outcome / Deliverables (1 pt)
1. ✅ **Working API**: 4 endpoints with Swagger docs
2. ✅ **Interactive UI**: Form inputs → DSA results (no JSON typing)
3. ✅ **Core DSA**: 4 algorithms with unit tests
4. ✅ **Full Guide**: RAIL_INTELLIGENCE_GUIDE.txt (file-wise code breakdown)
5. ✅ **Responsive Design**: Mobile-ready simulator

**Demo**: `uvicorn app.main:app --reload` → `frontend/index.html`

## Assumptions
1. Simulation (manual inputs, no real hardware)
2. Minutes/km as comparable units
3. Predefined unsafe zones
4. Undirected railway graph

## References
1. Cormen et al. *Introduction to Algorithms* (Dijkstra, Greedy)
2. FastAPI docs: https://fastapi.tiangolo.com/
3. Pydantic v2 models
4. Railway signaling: ETCS/ETMS standards (safety inspiration)

**Total Implementation**: Clean, modular, educational - ready for production extension (DB, WebSocket real-time).
