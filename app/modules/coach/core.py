from typing import Optional, List


class CoachNode:
    def __init__(self, coach_id: str, faulty: bool = False) -> None:
        self.coach_id = coach_id
        self.faulty = faulty
        self.prev: Optional["CoachNode"] = None
        self.next: Optional["CoachNode"] = None


class CoachDLL:
    def __init__(self) -> None:
        self.head: Optional[CoachNode] = None
        self.tail: Optional[CoachNode] = None

    def append(self, coach_id: str, faulty: bool = False) -> None:
        node = CoachNode(coach_id, faulty)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node

    def to_list(self) -> List[str]:
        res = []
        cur = self.head
        while cur:
            res.append(cur.coach_id)
            cur = cur.next
        return res

    def find_faulty_index(self) -> int:
        """
        Returns 0-based index of first faulty coach, -1 if none.
        """
        idx = 0
        cur = self.head
        while cur:
            if cur.faulty:
                return idx
            cur = cur.next
            idx += 1
        return -1
