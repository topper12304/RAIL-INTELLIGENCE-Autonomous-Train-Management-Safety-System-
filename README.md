#  RAIL-INTELLIGENCE
### Autonomous Train Management & Safety System

A Python-based intelligent railway management system built with graph algorithms, linked data structures, balanced trees, and decision trees.

---

##  Project Structure

```
code_files/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # SQLite persistence layer
│   ├── modules/
│   │   ├── network/             # Module 1: Dynamic Network Rescheduler
│   │   │   ├── core.py          # Dijkstra + Priority Queue
│   │   │   ├── models.py        # Pydantic models
│   │   │   └── router.py        # API endpoints
│   │   ├── coach/               # Module 2: Smart ACP & Fault Localization
│   │   │   ├── core.py          # Doubly Linked List + DFS
│   │   │   ├── models.py
│   │   │   └── router.py
│   │   ├── platform/            # Module 3: Junction Platform Scheduler
│   │   │   ├── core.py          # AVL Tree + Greedy Assignment
│   │   │   ├── models.py
│   │   │   └── router.py
│   │   └── safety/              # Module 4: Safety Controller
│   │       ├── core.py          # Zone detection + Emergency stop
│   │       ├── models.py
│   │       └── router.py
│   └── utils/
│       └── helpers.py
├── tests/
│   └── modules/
│       ├── network_test.py      # 12 tests (unit + property)
│       ├── coach_test.py        # 14 tests (unit + property)
│       ├── platform_test.py     # 12 tests (unit + property)
│       └── safety_test.py      # 11 tests (unit + property)
├── frontend/
│   ├── index.html               # UI Dashboard
│   ├── script.js
│   └── styles.css
├── data/                        # SQLite DB (auto-created)
└── requirements.txt
```

---

## ⚙️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.13** | Core language |
| **FastAPI** | REST API framework |
| **Uvicorn** | ASGI server |
| **Pydantic** | Request/response validation |
| **SQLite3** | Event logging database |
| **heapq** | Min-heap for Dijkstra & priority queue |
| **hypothesis** | Property-based testing |
| **pytest** | Test runner |

---

## 🚀 How to Run

### 1. Install dependencies
```bash
python3 -m pip install -r requirements.txt
```

### 2. Start the server
```bash
python3 -m uvicorn app.main:app --reload --port 8001
```

### 3. Open in browser
- **API:** http://127.0.0.1:8001
- **Swagger Docs:** http://127.0.0.1:8001/docs
- **Frontend UI:** Open `frontend/index.html` in browser

---

## 🧪 Run Tests

```bash
# All tests
python3 -m pytest tests/ -v

# Single module
python3 -m pytest tests/modules/network_test.py -v
python3 -m pytest tests/modules/coach_test.py -v
python3 -m pytest tests/modules/platform_test.py -v
python3 -m pytest tests/modules/safety_test.py -v
```

**49 tests — all passing ✅**

---

## 📦 Modules & Algorithms

### Module 1 — Dynamic Network Rescheduler

**Algorithm: Dijkstra's Shortest Path**
- Finds minimum-cost route between two stations
- Uses `heapq` min-heap → O((V+E) log V)
- Blocked segments are skipped during traversal

**Algorithm: Priority Queue (Routing Requests)**
- Premium trains (priority=1) served before standard (priority=2)
- Implemented using `heapq` with custom `__lt__`

**API:** `POST /network/shortest-path`
```json
{
  "nodes": ["A", "B", "C"],
  "edges": [{"u":"A","v":"B","w":1}, {"u":"B","v":"C","w":2}],
  "blocked_edges": [],
  "source": "A",
  "target": "C"
}
```

---

### Module 2 — Smart ACP & Fault Localization

**Data Structure: Doubly Linked List**
- Each coach is a node with `prev` and `next` pointers
- Supports position-based insertion, deletion, bidirectional traversal

**Algorithm: DFS Fault Localization**
- Recursive DFS from head coach
- Returns first faulty coach with 1-indexed position
- Time Complexity: O(n)

**API:** `POST /coach/fault-location`
```json
{
  "coaches": [
    {"id": "C1", "is_faulty": false},
    {"id": "C2", "is_faulty": true}
  ]
}
```

---

### Module 3 — Junction Platform Scheduler

**Data Structure: AVL Tree (Self-Balancing BST)**
- Platforms stored as AVL tree nodes keyed by platform_id
- Balance factor = height(left) - height(right), must stay in {-1, 0, 1}
- 4 rotations: Left, Right, Left-Right, Right-Left
- Guaranteed O(log n) insert, delete, search

**Algorithm: Greedy Platform Assignment**
- Finds platform with earliest `available_from <= arrival_time`
- Updates platform availability to `departure_time`

**Algorithm: Sweep-line (min platforms count)**
- Event-based: +1 on arrival, -1 on departure
- Tracks maximum simultaneous trains

**API:** `POST /platform/min-platforms`
```json
{
  "intervals": [
    {"arrival": 900, "departure": 910},
    {"arrival": 940, "departure": 1200}
  ]
}
```

---

### Module 4 — Centralized Safety Controller

**Algorithm: Zone Detection + Nearest Safe Position**
- Checks if train position falls within any unsafe zone
- Calculates nearest boundary (start-1 or end+1)
- Chooses closer boundary to minimize movement

**State Machine:** `MOVING → EMERGENCY_REQUESTED → STOPPED`

**API:** `POST /safety/emergency-stop`
```json
{
  "position": 15,
  "unsafe_zones": [{"start": 10, "end": 20}]
}
```

---

### Database Layer

SQLite with 4 event tables:
- `route_events` — every route computation
- `fault_events` — every fault detection
- `platform_events` — every platform assignment
- `safety_events` — every emergency stop

`DatabaseManager` uses Python context manager for automatic commit/rollback.

---

## 🧪 Property-Based Tests (hypothesis)

| Property | Module | Validates |
|---|---|---|
| P1: Optimal Route Selection | Network | Dijkstra always returns minimum cost path |
| P2: Unavailable Segment Exclusion | Network | Blocked edges never appear in path |
| P3: Priority Queue Ordering | Network | Dequeue always in non-decreasing priority order |
| P4: Fault Localization Accuracy | Coach | DFS finds fault at exact position |
| P5: Bidirectional Traversal | Coach | Forward and reverse are mirrors |
| P6: Coach Insertion Correctness | Coach | Insert increases length, correct position |
| P7: Coach Deletion Integrity | Coach | Delete removes element, decreases length |
| P8: Platform Selection Optimality | Platform | Earliest available platform assigned |
| P9: Conflict-Free Assignment | Platform | No two trains overlap on same platform |
| P10: AVL Balance Invariant | Platform | Every node has \|balance_factor\| ≤ 1 |
| P11: Speed Limit Enforcement | Safety | Train always moves outside unsafe zone |
| P13: Most Restrictive Zone | Safety | Most restrictive zone applied |
