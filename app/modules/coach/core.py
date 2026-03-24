from typing import List, Optional, Dict, Any


class CoachNode:
    """Node in the doubly-linked train composition list."""
    def __init__(self, coach_id: str, faulty: bool = False) -> None:
        self.coach_id = coach_id
        self.faulty = faulty
        self.next: Optional["CoachNode"] = None
        self.prev: Optional["CoachNode"] = None


class FaultLocation:
    """Result of a fault localization scan."""
    def __init__(self, coach_id: str, position: int) -> None:
        self.coach_id = coach_id
        self.position = position  # 1-indexed

    def to_dict(self) -> Dict[str, Any]:
        return {"coach_id": self.coach_id, "position": self.position}


class TrainComposition:
    """Doubly-linked list representing a train's coach composition."""

    def __init__(self) -> None:
        self.head: Optional[CoachNode] = None
        self.tail: Optional[CoachNode] = None
        self._size: int = 0

    # ------------------------------------------------------------------ #
    #  Insertion                                                           #
    # ------------------------------------------------------------------ #

    def add_coach(self, coach_id: str, faulty: bool = False, position: Optional[int] = None) -> None:
        """
        Insert a coach.
        position=None or position >= size  → append to tail
        position=0                         → prepend to head
        position=k                         → insert before the k-th node (0-indexed)
        """
        new_node = CoachNode(coach_id, faulty)

        if self.head is None:
            self.head = self.tail = new_node
            self._size += 1
            return

        if position is None or position >= self._size:
            # Append to tail
            new_node.prev = self.tail
            self.tail.next = new_node  # type: ignore[union-attr]
            self.tail = new_node
        elif position <= 0:
            # Prepend to head
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        else:
            # Insert before node at `position`
            cur = self.head
            for _ in range(position):
                cur = cur.next  # type: ignore[assignment]
            prev_node = cur.prev  # type: ignore[union-attr]
            new_node.next = cur
            new_node.prev = prev_node
            if prev_node:
                prev_node.next = new_node
            cur.prev = new_node  # type: ignore[union-attr]

        self._size += 1

    # Convenience alias used by existing code
    def append(self, coach_id: str, faulty: bool = False) -> None:
        self.add_coach(coach_id, faulty)

    # ------------------------------------------------------------------ #
    #  Deletion                                                            #
    # ------------------------------------------------------------------ #

    def remove_coach(self, coach_id: str) -> bool:
        """Remove coach by ID. Returns True if found and removed."""
        cur = self.head
        while cur:
            if cur.coach_id == coach_id:
                if cur.prev:
                    cur.prev.next = cur.next
                else:
                    self.head = cur.next
                if cur.next:
                    cur.next.prev = cur.prev
                else:
                    self.tail = cur.prev
                self._size -= 1
                return True
            cur = cur.next
        return False

    # ------------------------------------------------------------------ #
    #  Traversal                                                           #
    # ------------------------------------------------------------------ #

    def get_train_composition(self) -> List[str]:
        """Return ordered list of coach IDs (head → tail)."""
        result: List[str] = []
        cur = self.head
        while cur:
            result.append(cur.coach_id)
            cur = cur.next
        return result

    def get_train_composition_reverse(self) -> List[str]:
        """Return ordered list of coach IDs (tail → head)."""
        result: List[str] = []
        cur = self.tail
        while cur:
            result.append(cur.coach_id)
            cur = cur.prev
        return result

    # ------------------------------------------------------------------ #
    #  Fault localization (DFS / linear scan)                             #
    # ------------------------------------------------------------------ #

    def locate_fault_dfs(
        self,
        current_node: Optional[CoachNode] = None,
        index: int = 0,
    ) -> Optional[Dict[str, Any]]:
        """
        Recursive DFS traversal from head to locate first faulty coach.
        Returns dict {coach_id, position} or None.
        """
        if current_node is None and index == 0:
            current_node = self.head

        if current_node is None:
            return None

        if current_node.faulty:
            return FaultLocation(current_node.coach_id, index + 1).to_dict()

        return self.locate_fault_dfs(current_node.next, index + 1)

    # Legacy alias used by old test
    def find_faulty_index(self) -> int:
        """Return 0-based index of first faulty coach, or -1 if none."""
        cur = self.head
        idx = 0
        while cur:
            if cur.faulty:
                return idx
            cur = cur.next
            idx += 1
        return -1

    def __len__(self) -> int:
        return self._size


# ---------------------------------------------------------------------------
# Backward-compat alias — old router imports CoachDLL
# ---------------------------------------------------------------------------
CoachDLL = TrainComposition
