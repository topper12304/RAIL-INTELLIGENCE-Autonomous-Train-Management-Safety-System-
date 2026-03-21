# Design Document: RAIL-INTELLIGENCE

## Overview

RAIL-INTELLIGENCE is an autonomous railway management system built on four core modules that work together to optimize train operations, detect faults instantly, schedule platforms efficiently, and enforce safety constraints. The system uses graph algorithms for routing, linked data structures for fault localization, balanced trees for scheduling, and decision trees for safety enforcement.

The architecture emphasizes real-time performance with strict latency requirements: route computation within 2 seconds, fault localization within 500ms, platform assignment in O(log N) time, and brake override initiation within 200ms. All operations are logged persistently to SQLite for auditing and analysis.

## Architecture

The system follows a modular architecture with four independent but coordinated subsystems:

```
┌─────────────────────────────────────────────────────────────┐
│                    RAIL-INTELLIGENCE Core                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │   Network        │  │   ACP & Fault    │                │
│  │   Rescheduler    │  │   Localization   │                │
│  │                  │  │                  │                │
│  │  - Graph (Adj)   │  │  - Digital Twin  │                │
│  │  - Dijkstra      │  │  - DLL + DFS     │                │
│  │  - Priority Q    │  │                  │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │   Platform       │  │   Safety &       │                │
│  │   Scheduler      │  │   Override       │                │
│  │                  │  │   Controller     │                │
│  │  - AVL Tree      │  │  - Decision Tree │                │
│  │  - Greedy Int.   │  │  - Geofencing    │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                    Persistence Layer (SQLite)                 │
├─────────────────────────────────────────────────────────────┤
│                    Real-Time Dashboard                        │
└─────────────────────────────────────────────────────────────┘
```

Each module operates independently with its own data structures and algorithms, communicating through well-defined interfaces. The persistence layer captures all events for auditing, and the dashboard provides real-time visualization.

## Components and Interfaces

### Module 1: Dynamic Network Rescheduler

**Purpose**: Compute optimal alternative routes when track segments become unavailable, with priority handling for premium trains.

**Core Data Structures**:

- **Railway Network Graph**: Adjacency list representation
  - Nodes: Stations and junctions
  - Edges: Track segments with weights (travel time in minutes)
  - Supports directed edges for one-way tracks
  
- **Priority Queue**: Min-heap ordered by train priority
  - Premium trains: priority = 1
  - Standard trains: priority = 2
  - Lower numeric value = higher priority

**Key Algorithms**:

- **Dijkstra's Algorithm**: Shortest path computation
  - Input: Source station, destination station, unavailable segments set
  - Output: Shortest valid route or failure status
  - Time complexity: O(E log V) where E = edges, V = vertices
  
**Interface**:

```python
class NetworkRescheduler:
    def add_track_segment(station_a: str, station_b: str, travel_time: int) -> None
    def mark_segment_unavailable(station_a: str, station_b: str) -> None
    def mark_segment_available(station_a: str, station_b: str) -> None
    def compute_route(train_id: str, origin: str, destination: str, is_premium: bool) -> Route | None
    def get_network_status() -> NetworkStatus
```

**Route Computation Logic**:

1. Receive routing request with train metadata
2. Insert request into priority queue based on train classification
3. Dequeue highest priority request
4. Build modified graph excluding unavailable segments
5. Run Dijkstra's algorithm from origin to destination
6. If path exists, return route; otherwise return failure with isolated stations
7. Log routing decision to database

### Module 2: Smart ACP & Fault Localization

**Purpose**: Maintain digital twins of train compositions and instantly localize faults to specific coaches.

**Core Data Structures**:

- **Doubly Linked List**: Train composition representation
  - Each node represents one coach
  - Node data: coach_id, coach_type, sensor_status
  - Bidirectional pointers for forward/backward traversal
  
**Key Algorithms**:

- **Depth-First Search (DFS)**: Fault localization
  - Traverse from head coach
  - Check each coach's sensor status
  - Return first coach with fault condition
  - Time complexity: O(N) where N = number of coaches
  
**Interface**:

```python
class ACPSystem:
    def create_train(train_id: str) -> None
    def add_coach(train_id: str, coach_id: str, coach_type: str, position: int) -> None
    def remove_coach(train_id: str, coach_id: str) -> None
    def locate_fault(train_id: str) -> FaultLocation | None
    def handle_acp_alarm(train_id: str, alarm_signal: AlarmSignal) -> FaultLocation
    def get_train_composition(train_id: str) -> List[Coach]
```

**Fault Localization Logic**:

1. Receive ACP alarm signal with train ID
2. Retrieve digital twin (DLL) for the train
3. Perform DFS traversal starting from head coach
4. For each coach, check sensor status and alarm indicators
5. When fault detected, record coach ID and position (1-indexed from head)
6. Return fault location within 500ms requirement
7. Log fault event to database

### Module 3: Junction Platform Scheduler

**Purpose**: Assign arriving trains to platforms optimally to minimize idle time and resolve conflicts efficiently.

**Core Data Structures**:

- **AVL Tree**: Balanced binary search tree for platform availability
  - Key: Platform availability timestamp
  - Value: Platform ID and metadata
  - Maintains balance factor ∈ {-1, 0, 1} at all nodes
  - Height: O(log N) for N platforms
  
**Key Algorithms**:

- **Greedy Interval Partitioning**: Platform assignment strategy
  - Sort trains by arrival time
  - Assign each train to earliest available platform
  - Update platform availability to train's departure time
  
- **AVL Rebalancing**: Maintain tree balance
  - Left rotation, right rotation, left-right, right-left
  - Triggered after insertions and deletions
  - Ensures O(log N) operations
  
**Interface**:

```python
class PlatformScheduler:
    def add_platform(platform_id: str, initial_availability: datetime) -> None
    def remove_platform(platform_id: str) -> None
    def assign_platform(train_id: str, arrival_time: datetime, departure_time: datetime) -> str | None
    def release_platform(platform_id: str) -> None
    def get_platform_status() -> Dict[str, PlatformStatus]
```

**Platform Assignment Logic**:

1. Receive train arrival request with arrival and departure times
2. Query AVL tree for platform with earliest availability ≤ arrival time
3. If no platform available, return failure
4. Assign platform to train
5. Update platform availability to departure time
6. Perform AVL rebalancing if needed (rotations)
7. Log assignment to database
8. Return assigned platform ID

### Module 4: Centralized Safety & Override Controller

**Purpose**: Enforce contextual safety rules using geofencing and decision trees to prevent accidents.

**Core Data Structures**:

- **Decision Tree**: Safety rule evaluation
  - Root: Zone type classification (bridge, tunnel, curve, station)
  - Internal nodes: Speed threshold checks, weather conditions
  - Leaf nodes: Actions (allow, brake_override, alert)
  
- **Geofence Registry**: Map of safety zones
  - Key: Zone ID
  - Value: Boundaries (lat/lon polygon), zone type, speed limit
  
**Key Algorithms**:

- **Point-in-Polygon**: Geofence containment check
  - Ray casting algorithm
  - Determines if train coordinates are within zone boundaries
  - Time complexity: O(M) where M = polygon vertices
  
- **Decision Tree Traversal**: Safety evaluation
  - Start at root with current context (zone, speed, weather)
  - Traverse tree based on condition evaluations
  - Reach leaf node with action decision
  - Time complexity: O(log D) where D = tree depth
  
**Interface**:

```python
class SafetyController:
    def create_geofence(zone_id: str, boundaries: Polygon, zone_type: str, speed_limit: int) -> None
    def update_train_position(train_id: str, latitude: float, longitude: float, speed: int) -> None
    def evaluate_safety(train_id: str) -> SafetyAction
    def initiate_brake_override(train_id: str, reason: str) -> None
    def get_active_geofences() -> List[Geofence]
```

**Safety Evaluation Logic**:

1. Receive train position update (GPS coordinates, speed)
2. Check all geofences to determine if train is within any zone
3. If in multiple zones, select most restrictive speed limit
4. If in a zone, traverse decision tree:
   - Check zone type (bridge/tunnel/curve/station)
   - Compare current speed vs. zone speed limit
   - Consider weather conditions if available
5. If decision tree returns brake_override action:
   - Initiate brake override within 200ms
   - Log event with full context
6. Return safety action to caller

## Data Models

### Network Graph

```python
class TrackSegment:
    origin: str              # Station/junction ID
    destination: str         # Station/junction ID
    travel_time: int         # Minutes
    is_available: bool       # Track status
    segment_type: str        # "single" | "double" | "junction"

class NetworkGraph:
    adjacency_list: Dict[str, List[TrackSegment]]
    stations: Set[str]
    unavailable_segments: Set[Tuple[str, str]]
```

### Train Composition (Digital Twin)

```python
class CoachNode:
    coach_id: str
    coach_type: str          # "engine" | "passenger" | "cargo" | "dining"
    sensor_status: Dict[str, Any]
    has_fault: bool
    prev: CoachNode | None
    next: CoachNode | None

class TrainComposition:
    train_id: str
    head: CoachNode | None
    tail: CoachNode | None
    length: int              # Number of coaches
```

### Platform Availability

```python
class PlatformNode:
    platform_id: str
    available_at: datetime
    current_train: str | None
    height: int              # AVL tree height
    balance_factor: int      # {-1, 0, 1}
    left: PlatformNode | None
    right: PlatformNode | None

class PlatformTree:
    root: PlatformNode | None
    platform_count: int
```

### Safety Geofence

```python
class Geofence:
    zone_id: str
    boundaries: List[Tuple[float, float]]  # Polygon vertices (lat, lon)
    zone_type: str           # "bridge" | "tunnel" | "curve" | "station"
    speed_limit: int         # km/h
    is_active: bool

class SafetyDecisionNode:
    condition: str           # Evaluation condition
    threshold: float | None
    action: str | None       # Leaf node action
    left_child: SafetyDecisionNode | None   # Condition false
    right_child: SafetyDecisionNode | None  # Condition true
```

### Event Logging Schema

```sql
-- Route computation events
CREATE TABLE route_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    train_id TEXT NOT NULL,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    computed_route TEXT,  -- JSON array of stations
    is_premium BOOLEAN,
    success BOOLEAN
);

-- Fault detection events
CREATE TABLE fault_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    train_id TEXT NOT NULL,
    coach_id TEXT NOT NULL,
    coach_position INTEGER,
    fault_type TEXT,
    sensor_data TEXT  -- JSON
);

-- Platform assignment events
CREATE TABLE platform_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    train_id TEXT NOT NULL,
    platform_id TEXT NOT NULL,
    arrival_time DATETIME NOT NULL,
    departure_time DATETIME NOT NULL
);

-- Safety override events
CREATE TABLE safety_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    train_id TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    speed INTEGER NOT NULL,
    zone_type TEXT NOT NULL,
    action TEXT NOT NULL,
    reason TEXT
);
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Optimal Route Selection

*For any* railway network graph with multiple valid paths between an origin and destination, the computed route should have the minimum total travel time among all valid paths.

**Validates: Requirements 1.2**

### Property 2: Unavailable Segment Exclusion

*For any* route computation with a set of unavailable track segments, the returned route should not contain any segment from the unavailable set.

**Validates: Requirements 1.3**

### Property 3: Priority Queue Ordering

*For any* set of routing requests containing both premium and standard trains, all premium train requests should be processed before any standard train requests.

**Validates: Requirements 2.1**

### Property 4: Fault Localization Accuracy

*For any* train composition with a fault in any coach, the fault localization function should return the correct coach ID and the correct position (1-indexed from head) of that coach.

**Validates: Requirements 3.2**

### Property 5: Bidirectional Traversal Completeness

*For any* train composition represented as a doubly linked list, traversing forward from head to tail and backward from tail to head should visit all coaches exactly once in reverse order.

**Validates: Requirements 3.4**

### Property 6: Coach Insertion Correctness

*For any* train composition and any valid position (1 to length+1), inserting a coach at that position should result in the coach appearing at the specified position when the composition is traversed.

**Validates: Requirements 4.2**

### Property 7: Coach Deletion Integrity

*For any* train composition and any coach in that composition, removing the coach should result in a valid doubly linked list that contains all other coaches in their original order and does not contain the removed coach.

**Validates: Requirements 4.3**

### Property 8: Platform Selection Optimality

*For any* set of available platforms with different availability times, the platform assignment should select the platform with the earliest availability time that is less than or equal to the train's arrival time.

**Validates: Requirements 5.2**

### Property 9: Conflict-Free Platform Assignment

*For any* set of train arrivals at a junction, no two trains should be assigned to the same platform with overlapping time intervals (where overlap means one train's [arrival, departure] intersects another's).

**Validates: Requirements 6.1**

### Property 10: AVL Tree Balance Invariant

*For any* sequence of platform insertions and deletions, every node in the AVL tree should maintain a balance factor in the set {-1, 0, 1} after each operation completes.

**Validates: Requirements 6.3**

### Property 11: Speed Limit Enforcement

*For any* train position within a geofenced safety zone, if the train's current speed exceeds the zone's speed limit, the system should initiate a brake override action.

**Validates: Requirements 7.2**

### Property 12: Geofence Containment Detection

*For any* train GPS coordinates and any set of active geofences, the system should correctly determine whether the coordinates fall within any geofence boundary using point-in-polygon testing.

**Validates: Requirements 8.2**

### Property 13: Most Restrictive Speed Limit

*For any* train position that falls within multiple overlapping geofences, the system should apply the minimum speed limit among all overlapping zones.

**Validates: Requirements 8.4**

## Error Handling

### Network Rescheduler Error Handling

**No Path Available**:
- When Dijkstra's algorithm cannot find a path to the destination
- Return `None` or failure status with list of isolated stations
- Log the failed routing attempt with reason "NO_PATH_AVAILABLE"

**Invalid Station IDs**:
- When origin or destination station does not exist in network
- Raise `InvalidStationError` with the invalid station ID
- Do not attempt route computation

**Empty Network**:
- When network graph has no track segments
- Raise `EmptyNetworkError`
- Prevent routing operations until network is initialized

### ACP System Error Handling

**Train Not Found**:
- When fault localization requested for non-existent train ID
- Raise `TrainNotFoundError` with the train ID
- Log the error attempt

**Empty Train Composition**:
- When train has no coaches in its digital twin
- Return `None` for fault localization
- Log warning about empty composition

**Corrupted Linked List**:
- When traversal encounters null pointer unexpectedly
- Raise `CorruptedCompositionError`
- Trigger digital twin rebuild from persistent state

### Platform Scheduler Error Handling

**No Available Platform**:
- When all platforms are occupied during requested time window
- Return `None` for platform assignment
- Log the failed assignment with train ID and time window

**Invalid Time Range**:
- When departure time is before arrival time
- Raise `InvalidTimeRangeError`
- Reject the assignment request

**Platform Not Found**:
- When attempting to release or query non-existent platform
- Raise `PlatformNotFoundError` with platform ID

### Safety Controller Error Handling

**Invalid Geofence**:
- When geofence polygon has fewer than 3 vertices
- Raise `InvalidGeofenceError`
- Reject geofence creation

**GPS Signal Loss**:
- When train position update fails or coordinates are invalid
- Use last known valid position
- Log warning and set train status to "GPS_DEGRADED"
- Do not evaluate safety rules with stale position data

**Brake Override Failure**:
- When brake override command cannot be sent to train
- Retry up to 3 times with 50ms intervals
- If all retries fail, raise critical alert
- Log as `CRITICAL_SAFETY_FAILURE`

## Testing Strategy

### Dual Testing Approach

The RAIL-INTELLIGENCE system requires both unit testing and property-based testing for comprehensive correctness validation:

**Unit Tests**: Focus on specific examples, edge cases, and error conditions
- Test specific network topologies (linear, circular, disconnected)
- Test boundary conditions (empty trains, single-coach trains, full platforms)
- Test error handling paths (invalid inputs, missing data, system failures)
- Test integration points between modules
- Verify logging outputs contain required fields

**Property-Based Tests**: Verify universal properties across all inputs
- Generate random railway networks with varying sizes and topologies
- Generate random train compositions with varying lengths and coach types
- Generate random platform schedules with varying arrival/departure patterns
- Generate random geofences with varying shapes and positions
- Each property test validates one correctness property from this design document

### Property-Based Testing Configuration

**Framework Selection**:
- Python: Use `hypothesis` library for property-based testing
- C++: Use `RapidCheck` library for property-based testing

**Test Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each test must reference its design document property in a comment
- Tag format: `# Feature: rail-intelligence, Property N: [property text]`

**Example Property Test Structure** (Python with hypothesis):

```python
from hypothesis import given, strategies as st
import hypothesis

@given(
    network=st.railway_networks(min_stations=3, max_stations=20),
    unavailable=st.sets(st.track_segments(), max_size=5)
)
@hypothesis.settings(max_examples=100)
def test_unavailable_segment_exclusion(network, unavailable):
    """
    Feature: rail-intelligence, Property 2: Unavailable Segment Exclusion
    For any route computation with unavailable segments, 
    the route should not contain any unavailable segment.
    """
    rescheduler = NetworkRescheduler(network)
    for segment in unavailable:
        rescheduler.mark_segment_unavailable(segment.origin, segment.destination)
    
    route = rescheduler.compute_route("T1", "A", "Z", is_premium=False)
    
    if route is not None:
        route_segments = set(zip(route[:-1], route[1:]))
        unavailable_segments = {(s.origin, s.destination) for s in unavailable}
        assert route_segments.isdisjoint(unavailable_segments)
```

### Test Coverage Requirements

Each correctness property MUST be implemented by exactly ONE property-based test. The following properties require property-based tests:

1. Property 1: Optimal Route Selection
2. Property 2: Unavailable Segment Exclusion
3. Property 3: Priority Queue Ordering
4. Property 4: Fault Localization Accuracy
5. Property 5: Bidirectional Traversal Completeness
6. Property 6: Coach Insertion Correctness
7. Property 7: Coach Deletion Integrity
8. Property 8: Platform Selection Optimality
9. Property 9: Conflict-Free Platform Assignment
10. Property 10: AVL Tree Balance Invariant
11. Property 11: Speed Limit Enforcement
12. Property 12: Geofence Containment Detection
13. Property 13: Most Restrictive Speed Limit

### Unit Test Focus Areas

Unit tests should complement property tests by covering:

- **Specific Examples**: Test known scenarios (e.g., specific network topology from requirements)
- **Edge Cases**: Empty inputs, single-element collections, boundary values
- **Error Conditions**: Invalid inputs, missing data, system failures
- **Logging Verification**: Ensure all events are logged with required fields (Requirements 9.1-9.4)
- **Integration Points**: Module interactions and data flow

### Performance Testing

While property-based tests focus on correctness, performance requirements should be validated separately:

- Route computation: < 2 seconds (Requirement 1.1)
- Fault localization: < 500 milliseconds (Requirement 3.1)
- Platform assignment: O(log N) complexity (Requirement 5.3)
- Brake override: < 200 milliseconds (Requirement 7.2)

Performance tests should use realistic data volumes and measure actual execution times under load.
