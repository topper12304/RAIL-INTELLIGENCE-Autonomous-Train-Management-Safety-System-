# Implementation Plan: RAIL-INTELLIGENCE

## Overview

This implementation plan breaks down the RAIL-INTELLIGENCE system into discrete coding tasks. The system will be implemented in Python using graph algorithms, linked data structures, balanced trees, and decision trees. Each task builds incrementally, with property-based tests using the `hypothesis` library to validate correctness properties from the design document.

## Tasks

- [ ] 1. Set up project structure and dependencies
  - Create directory structure: `src/`, `tests/`, `data/`
  - Set up `requirements.txt` with dependencies: `hypothesis`, `sqlite3` (built-in), `typing`
  - Create `__init__.py` files for package structure
  - Initialize SQLite database schema for event logging
  - _Requirements: 9.5_

- [ ] 2. Implement core data models and types
  - [ ] 2.1 Create data model classes for all modules
    - Define `TrackSegment`, `NetworkGraph`, `Route` classes
    - Define `CoachNode`, `TrainComposition`, `FaultLocation` classes
    - Define `PlatformNode`, `PlatformTree`, `PlatformStatus` classes
    - Define `Geofence`, `SafetyDecisionNode`, `SafetyAction` classes
    - Add type hints for all attributes and methods
    - _Requirements: 1.5, 3.3, 5.5, 7.4, 8.3_

- [ ] 3. Implement Module 1: Dynamic Network Rescheduler
  - [ ] 3.1 Implement railway network graph with adjacency list
    - Create `NetworkGraph` class with adjacency list storage
    - Implement `add_track_segment()` method
    - Implement `mark_segment_unavailable()` and `mark_segment_available()` methods
    - Implement `get_network_status()` method
    - _Requirements: 1.5_
  
  - [ ] 3.2 Implement Dijkstra's shortest path algorithm
    - Create `compute_route()` method using Dijkstra's algorithm
    - Use min-heap (heapq) for priority queue in Dijkstra
    - Filter out unavailable segments during path computation
    - Return route as list of station IDs or None if no path exists
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [ ]* 3.3 Write property test for optimal route selection
    - **Property 1: Optimal Route Selection**
    - **Validates: Requirements 1.2**
  
  - [ ]* 3.4 Write property test for unavailable segment exclusion
    - **Property 2: Unavailable Segment Exclusion**
    - **Validates: Requirements 1.3**
  
  - [ ]* 3.5 Write unit tests for network rescheduler edge cases
    - Test disconnected graph (no path exists)
    - Test single-node graph
    - Test invalid station IDs
    - _Requirements: 1.4_
  
  - [ ] 3.6 Implement priority queue for train routing requests
    - Create `RoutingRequest` class with train metadata and priority
    - Implement priority queue using heapq with custom comparison
    - Premium trains get priority=1, standard trains get priority=2
    - Implement `enqueue_request()` and `dequeue_request()` methods
    - _Requirements: 2.1, 2.3, 2.4_
  
  - [ ]* 3.7 Write property test for priority queue ordering
    - **Property 3: Priority Queue Ordering**
    - **Validates: Requirements 2.1**
  
  - [ ]* 3.8 Write unit test for premium vs standard train conflict
    - Test specific scenario where premium and standard trains compete
    - _Requirements: 2.2_
  
  - [ ] 3.9 Implement route event logging
    - Create `log_route_event()` method
    - Insert into `route_events` table with all required fields
    - _Requirements: 9.1_

- [ ] 4. Implement Module 2: Smart ACP & Fault Localization
  - [ ] 4.1 Implement doubly linked list for train composition
    - Create `CoachNode` class with prev/next pointers
    - Create `TrainComposition` class with head/tail pointers
    - Implement `add_coach()` method with position parameter
    - Implement `remove_coach()` method
    - Implement `get_train_composition()` method returning list of coaches
    - _Requirements: 3.3, 4.2, 4.3_
  
  - [ ]* 4.2 Write property test for coach insertion correctness
    - **Property 6: Coach Insertion Correctness**
    - **Validates: Requirements 4.2**
  
  - [ ]* 4.3 Write property test for coach deletion integrity
    - **Property 7: Coach Deletion Integrity**
    - **Validates: Requirements 4.3**
  
  - [ ]* 4.4 Write property test for bidirectional traversal
    - **Property 5: Bidirectional Traversal Completeness**
    - **Validates: Requirements 3.4**
  
  - [ ] 4.5 Implement DFS-based fault localization
    - Create `locate_fault()` method using DFS traversal
    - Traverse from head coach checking sensor_status and has_fault flag
    - Return `FaultLocation` with coach_id and position (1-indexed)
    - Return None if no fault found
    - _Requirements: 3.1, 3.2_
  
  - [ ]* 4.6 Write property test for fault localization accuracy
    - **Property 4: Fault Localization Accuracy**
    - **Validates: Requirements 3.2**
  
  - [ ]* 4.7 Write unit tests for ACP system edge cases
    - Test empty train composition
    - Test single-coach train
    - Test train not found error
    - _Requirements: 3.2_
  
  - [ ] 4.8 Implement fault event logging
    - Create `log_fault_event()` method
    - Insert into `fault_events` table with all required fields
    - _Requirements: 9.2, 4.4_

- [ ] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement Module 3: Junction Platform Scheduler
  - [ ] 6.1 Implement AVL tree for platform availability
    - Create `PlatformNode` class with height and balance_factor
    - Create `PlatformTree` class with root pointer
    - Implement `insert()` method with AVL rebalancing
    - Implement `delete()` method with AVL rebalancing
    - Implement rotation methods: `rotate_left()`, `rotate_right()`, `rotate_left_right()`, `rotate_right_left()`
    - Implement `update_height()` and `update_balance_factor()` helper methods
    - _Requirements: 5.5, 6.2, 6.3_
  
  - [ ]* 6.2 Write property test for AVL tree balance invariant
    - **Property 10: AVL Tree Balance Invariant**
    - **Validates: Requirements 6.3**
  
  - [ ] 6.3 Implement greedy platform assignment algorithm
    - Create `assign_platform()` method
    - Query AVL tree for platform with earliest availability ≤ arrival_time
    - Update platform availability to departure_time
    - Return assigned platform_id or None if no platform available
    - _Requirements: 5.1, 5.2, 5.4_
  
  - [ ]* 6.4 Write property test for platform selection optimality
    - **Property 8: Platform Selection Optimality**
    - **Validates: Requirements 5.2**
  
  - [ ]* 6.5 Write property test for conflict-free assignment
    - **Property 9: Conflict-Free Platform Assignment**
    - **Validates: Requirements 6.1**
  
  - [ ]* 6.6 Write unit tests for platform scheduler edge cases
    - Test no available platforms
    - Test invalid time range (departure before arrival)
    - Test platform not found error
    - _Requirements: 5.1, 6.1_
  
  - [ ] 6.7 Implement platform event logging
    - Create `log_platform_event()` method
    - Insert into `platform_events` table with all required fields
    - _Requirements: 9.3_

- [ ] 7. Implement Module 4: Centralized Safety & Override Controller
  - [ ] 7.1 Implement geofence data structure and management
    - Create `Geofence` class with boundaries (polygon vertices), zone_type, speed_limit
    - Create `GeofenceRegistry` class to store active geofences
    - Implement `create_geofence()` method with validation (min 3 vertices)
    - Implement `get_active_geofences()` method
    - _Requirements: 8.1, 8.3_
  
  - [ ] 7.2 Implement point-in-polygon algorithm for geofence containment
    - Create `point_in_polygon()` function using ray casting algorithm
    - Input: point (lat, lon), polygon vertices
    - Output: boolean indicating containment
    - _Requirements: 8.2_
  
  - [ ]* 7.3 Write property test for geofence containment detection
    - **Property 12: Geofence Containment Detection**
    - **Validates: Requirements 8.2**
  
  - [ ] 7.4 Implement decision tree for safety evaluation
    - Create `SafetyDecisionNode` class with condition, threshold, action, children
    - Build decision tree structure for zone types (bridge, tunnel, curve, station)
    - Implement `traverse_decision_tree()` method
    - Return `SafetyAction` enum: ALLOW, BRAKE_OVERRIDE, ALERT
    - _Requirements: 7.3, 7.4_
  
  - [ ] 7.5 Implement safety evaluation logic
    - Create `evaluate_safety()` method
    - Check if train position is within any geofence using point-in-polygon
    - If in multiple zones, select most restrictive speed limit
    - Traverse decision tree with current context (zone_type, speed, speed_limit)
    - Return safety action
    - _Requirements: 7.1, 7.2, 8.2, 8.4_
  
  - [ ]* 7.6 Write property test for speed limit enforcement
    - **Property 11: Speed Limit Enforcement**
    - **Validates: Requirements 7.2**
  
  - [ ]* 7.7 Write property test for most restrictive speed limit
    - **Property 13: Most Restrictive Speed Limit**
    - **Validates: Requirements 8.4**
  
  - [ ]* 7.8 Write unit tests for safety controller edge cases
    - Test invalid geofence (< 3 vertices)
    - Test GPS signal loss handling
    - Test brake override retry logic
    - _Requirements: 7.2, 8.1_
  
  - [ ] 7.9 Implement brake override mechanism
    - Create `initiate_brake_override()` method
    - Implement retry logic (3 attempts, 50ms intervals)
    - Log brake override event
    - Raise critical alert if all retries fail
    - _Requirements: 7.2, 7.5_
  
  - [ ] 7.10 Implement safety event logging
    - Create `log_safety_event()` method
    - Insert into `safety_events` table with all required fields
    - _Requirements: 9.4, 7.5_

- [ ] 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement database persistence layer
  - [ ] 9.1 Create SQLite database initialization
    - Create `database.py` module
    - Implement `init_database()` function to create all tables
    - Create tables: `route_events`, `fault_events`, `platform_events`, `safety_events`
    - Use schema from design document
    - _Requirements: 9.5_
  
  - [ ] 9.2 Implement database connection management
    - Create `DatabaseManager` class with connection pooling
    - Implement context manager for transactions
    - Implement error handling for database operations
    - _Requirements: 9.5_
  
  - [ ]* 9.3 Write unit tests for logging operations
    - Test that route events are logged with all required fields
    - Test that fault events are logged with all required fields
    - Test that platform events are logged with all required fields
    - Test that safety events are logged with all required fields
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [ ] 10. Implement system integration and coordination
  - [ ] 10.1 Create main system controller
    - Create `RAILIntelligence` class that coordinates all modules
    - Initialize all four modules (NetworkRescheduler, ACPSystem, PlatformScheduler, SafetyController)
    - Implement `get_system_status()` method returning status of all modules
    - _Requirements: 1.1, 3.1, 5.1, 7.1_
  
  - [ ] 10.2 Wire modules together with shared database
    - Pass DatabaseManager instance to all modules
    - Ensure all modules log to the same database
    - Implement error propagation between modules
    - _Requirements: 9.5_
  
  - [ ]* 10.3 Write integration tests for module interactions
    - Test end-to-end scenario: route computation → logging
    - Test end-to-end scenario: fault detection → logging
    - Test end-to-end scenario: platform assignment → logging
    - Test end-to-end scenario: safety evaluation → brake override → logging
    - _Requirements: 1.1, 3.1, 5.1, 7.1_

- [ ] 11. Implement real-time dashboard data API
  - [ ] 11.1 Create dashboard data provider
    - Create `DashboardAPI` class
    - Implement `get_network_topology()` method returning current track status
    - Implement `get_active_trains()` method returning train positions and routes
    - Implement `get_recent_alerts()` method returning faults and safety events
    - Implement `get_platform_status()` method returning platform assignments
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [ ] 11.2 Implement dashboard data refresh mechanism
    - Create background thread or async task for data updates
    - Poll system state at 1 Hz minimum frequency
    - Cache dashboard data for efficient retrieval
    - _Requirements: 10.5_
  
  - [ ]* 11.3 Write unit tests for dashboard API
    - Test that network topology includes all track segments
    - Test that alerts include required details
    - Test data refresh timing
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 12. Final checkpoint - Ensure all tests pass
  - Run full test suite including all property-based tests (100 iterations each)
  - Verify all 13 correctness properties pass
  - Ensure all unit tests pass
  - Ensure all integration tests pass
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property-based tests use `hypothesis` library with minimum 100 iterations
- Each property test validates exactly one correctness property from the design document
- Checkpoints ensure incremental validation at logical breakpoints
- All modules share a common SQLite database for event logging
- Python type hints should be used throughout for better code quality
