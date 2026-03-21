# Requirements Document: RAIL-INTELLIGENCE

## Introduction

RAIL-INTELLIGENCE is an autonomous railway management system designed to optimize train operations, enhance safety, and provide real-time fault detection and resolution. The system comprises four integrated modules: Dynamic Network Rescheduler for intelligent routing, Smart ACP & Fault Localization for rapid failure detection, Junction Platform Scheduler for optimal platform assignment, and Centralized Safety & Override Controller for contextual safety management.

## Glossary

- **Network_Rescheduler**: The module responsible for computing alternative routes when track segments become unavailable
- **Track_Segment**: A directed edge in the railway network graph connecting two stations or junctions
- **Premium_Train**: A train with higher priority classification requiring preferential routing
- **ACP_System**: Alarm Chain Pull system that allows passengers to signal emergencies
- **Digital_Twin**: A virtual representation of the physical train composition maintained in memory
- **Coach**: A single railway carriage unit within a train composition
- **Platform_Scheduler**: The module responsible for assigning arriving trains to available platforms
- **Idle_Time**: The duration a platform remains unoccupied between train departures and arrivals
- **Safety_Controller**: The centralized module that evaluates and enforces safety constraints
- **Geofence**: A virtual geographic boundary defining a safety-critical zone
- **Brake_Override**: A system-initiated emergency braking action that supersedes driver control
- **Junction**: A railway node where multiple track segments converge
- **Route**: A sequence of track segments connecting an origin station to a destination station

## Requirements

### Requirement 1: Real-Time Route Computation

**User Story:** As a railway operations manager, I want the system to compute alternative routes when track blockages occur, so that train services continue with minimal disruption.

#### Acceptance Criteria

1. WHEN a track segment becomes unavailable, THE Network_Rescheduler SHALL compute an alternative route within 2 seconds
2. WHEN multiple alternative routes exist, THE Network_Rescheduler SHALL select the route with minimum total travel time
3. WHEN computing routes, THE Network_Rescheduler SHALL exclude all unavailable track segments from consideration
4. WHEN no alternative route exists, THE Network_Rescheduler SHALL return a failure status with the isolated stations list
5. THE Network_Rescheduler SHALL maintain the railway network as a directed graph using adjacency list representation

### Requirement 2: Priority-Based Train Scheduling

**User Story:** As a railway operations manager, I want premium trains to receive routing priority during network congestion, so that high-value services maintain their schedules.

#### Acceptance Criteria

1. WHEN multiple trains require rerouting simultaneously, THE Network_Rescheduler SHALL process premium trains before standard trains
2. WHEN a premium train and standard train compete for the same track segment, THE Network_Rescheduler SHALL allocate the segment to the premium train
3. THE Network_Rescheduler SHALL maintain train routing requests in a priority queue ordered by train classification
4. WHEN processing routing requests, THE Network_Rescheduler SHALL dequeue trains in priority order

### Requirement 3: Instant Fault Localization

**User Story:** As a train maintenance operator, I want to instantly identify which coach has a failure, so that I can dispatch repair crews to the exact location.

#### Acceptance Criteria

1. WHEN an ACP alarm is triggered, THE ACP_System SHALL identify the specific coach ID within 500 milliseconds
2. WHEN a coach reports a fault, THE ACP_System SHALL return both the coach ID and its position in the train composition
3. THE ACP_System SHALL maintain the train composition as a doubly linked list of coach nodes
4. WHEN traversing the train composition, THE ACP_System SHALL support bidirectional navigation between coaches

### Requirement 4: Digital Twin Synchronization

**User Story:** As a railway operations manager, I want the system to maintain an accurate digital representation of each train's composition, so that fault localization remains reliable.

#### Acceptance Criteria

1. WHEN a train composition changes, THE ACP_System SHALL update the digital twin within 1 second
2. WHEN a coach is added to a train, THE ACP_System SHALL insert the coach node at the specified position in the linked list
3. WHEN a coach is removed from a train, THE ACP_System SHALL delete the coach node and maintain list integrity
4. THE ACP_System SHALL persist all digital twin updates to the logging database

### Requirement 5: Optimal Platform Assignment

**User Story:** As a station manager, I want trains assigned to platforms that minimize idle time, so that platform utilization is maximized.

#### Acceptance Criteria

1. WHEN a train arrival is scheduled, THE Platform_Scheduler SHALL assign a platform that minimizes total idle time across all platforms
2. WHEN multiple platforms are available, THE Platform_Scheduler SHALL select the platform with the earliest availability time
3. THE Platform_Scheduler SHALL complete platform assignment in O(log N) time complexity where N is the number of platforms
4. WHEN platform assignments conflict, THE Platform_Scheduler SHALL resolve conflicts using greedy interval partitioning
5. THE Platform_Scheduler SHALL maintain platform availability using a balanced AVL tree structure

### Requirement 6: Junction Bottleneck Resolution

**User Story:** As a railway operations manager, I want the system to resolve platform conflicts at busy junctions efficiently, so that train throughput is maximized.

#### Acceptance Criteria

1. WHEN multiple trains arrive at a junction simultaneously, THE Platform_Scheduler SHALL assign platforms without conflicts
2. WHEN a platform becomes available, THE Platform_Scheduler SHALL update the availability tree in O(log N) time
3. THE Platform_Scheduler SHALL maintain tree balance after every insertion and deletion operation
4. WHEN querying platform availability, THE Platform_Scheduler SHALL return results in O(log N) time

### Requirement 7: Contextual Safety Enforcement

**User Story:** As a railway safety officer, I want the system to automatically apply brakes when trains enter unsafe zones at excessive speeds, so that accidents are prevented.

#### Acceptance Criteria

1. WHEN a train enters a geofenced safety zone, THE Safety_Controller SHALL evaluate the train's current speed against the zone's speed limit
2. IF a train exceeds the speed limit in a safety zone, THEN THE Safety_Controller SHALL initiate a brake override within 200 milliseconds
3. WHEN evaluating safety conditions, THE Safety_Controller SHALL traverse a decision tree based on zone type, speed, and weather conditions
4. THE Safety_Controller SHALL classify safety zones into bridge, tunnel, curve, and station categories
5. WHEN a brake override is initiated, THE Safety_Controller SHALL log the event with timestamp, location, and reason

### Requirement 8: Geofence Management

**User Story:** As a railway safety officer, I want to define and manage safety-critical zones with specific speed limits, so that contextual safety rules are enforced.

#### Acceptance Criteria

1. WHEN a geofence is created, THE Safety_Controller SHALL store the zone boundaries, type, and speed limit
2. WHEN a train's GPS coordinates are updated, THE Safety_Controller SHALL determine if the train is within any active geofence
3. THE Safety_Controller SHALL support geofence types for bridges, tunnels, sharp curves, and station approaches
4. WHEN multiple geofences overlap, THE Safety_Controller SHALL apply the most restrictive speed limit

### Requirement 9: Persistent Event Logging

**User Story:** As a railway operations analyst, I want all system events logged to a persistent database, so that I can perform post-incident analysis and auditing.

#### Acceptance Criteria

1. WHEN a route is computed, THE Network_Rescheduler SHALL log the train ID, origin, destination, computed route, and timestamp
2. WHEN a fault is detected, THE ACP_System SHALL log the train ID, coach ID, fault type, and timestamp
3. WHEN a platform is assigned, THE Platform_Scheduler SHALL log the train ID, platform ID, arrival time, and departure time
4. WHEN a brake override occurs, THE Safety_Controller SHALL log the train ID, location, speed, zone type, and timestamp
5. THE System SHALL use SQLite for all persistent logging operations

### Requirement 10: Real-Time Dashboard Visualization

**User Story:** As a railway operations manager, I want to view real-time system status on a dashboard, so that I can monitor operations and respond to incidents.

#### Acceptance Criteria

1. WHEN the dashboard is loaded, THE System SHALL display the current network topology with track segment status
2. WHEN a train is rerouted, THE System SHALL update the dashboard to show the new route within 1 second
3. WHEN a fault is detected, THE System SHALL display an alert on the dashboard with coach location details
4. WHEN a brake override occurs, THE System SHALL display a safety alert on the dashboard with incident details
5. THE System SHALL refresh dashboard data at minimum 1 Hz frequency
