from typing import List, Tuple, Optional, Dict


# ---------------------------------------------------------------------------
# Original sweep-line function (kept for backward-compat with existing tests)
# ---------------------------------------------------------------------------

def min_platforms(intervals: List[Tuple[int, int]]) -> int:
    """
    Compute minimum number of platforms needed using sweep-line / greedy.
    intervals: list of (arrival, departure) in minutes.
    """
    events = []
    for arr, dep in intervals:
        events.append((arr, 1))
        events.append((dep, -1))
    events.sort()
    current = 0
    max_platforms = 0
    for _, delta in events:
        current += delta
        max_platforms = max(max_platforms, current)
    return max_platforms


# ---------------------------------------------------------------------------
# Task 6.1 — AVL Tree for platform availability tracking
# ---------------------------------------------------------------------------

class PlatformStatus:
    """Availability window for a single platform."""
    def __init__(self, platform_id: int, available_from: int = 0) -> None:
        self.platform_id = platform_id
        self.available_from = available_from   # earliest time platform is free


class PlatformNode:
    """AVL tree node keyed by platform_id."""
    def __init__(self, status: PlatformStatus) -> None:
        self.status = status
        self.key: int = status.platform_id
        self.height: int = 1
        self.balance_factor: int = 0
        self.left: Optional["PlatformNode"] = None
        self.right: Optional["PlatformNode"] = None


class PlatformTree:
    """
    AVL tree storing PlatformNode objects keyed by platform_id.
    Supports O(log n) insert, delete, and search.
    """

    def __init__(self) -> None:
        self.root: Optional[PlatformNode] = None

    # ------------------------------------------------------------------ #
    #  Height / balance helpers                                            #
    # ------------------------------------------------------------------ #

    def _height(self, node: Optional[PlatformNode]) -> int:
        return node.height if node else 0

    def update_height(self, node: PlatformNode) -> None:
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    def update_balance_factor(self, node: PlatformNode) -> None:
        node.balance_factor = self._height(node.left) - self._height(node.right)

    def _update(self, node: PlatformNode) -> None:
        self.update_height(node)
        self.update_balance_factor(node)

    # ------------------------------------------------------------------ #
    #  Rotations                                                           #
    # ------------------------------------------------------------------ #

    def rotate_right(self, y: PlatformNode) -> PlatformNode:
        x = y.left  # type: ignore[assignment]
        t2 = x.right
        x.right = y
        y.left = t2
        self._update(y)
        self._update(x)
        return x

    def rotate_left(self, x: PlatformNode) -> PlatformNode:
        y = x.right  # type: ignore[assignment]
        t2 = y.left
        y.left = x
        x.right = t2
        self._update(x)
        self._update(y)
        return y

    def rotate_left_right(self, node: PlatformNode) -> PlatformNode:
        node.left = self.rotate_left(node.left)  # type: ignore[arg-type]
        return self.rotate_right(node)

    def rotate_right_left(self, node: PlatformNode) -> PlatformNode:
        node.right = self.rotate_right(node.right)  # type: ignore[arg-type]
        return self.rotate_left(node)

    # ------------------------------------------------------------------ #
    #  Rebalance                                                           #
    # ------------------------------------------------------------------ #

    def _rebalance(self, node: PlatformNode) -> PlatformNode:
        self._update(node)
        bf = node.balance_factor

        if bf > 1:  # Left heavy
            if self._height(node.left.left) >= self._height(node.left.right):  # type: ignore
                return self.rotate_right(node)
            else:
                return self.rotate_left_right(node)

        if bf < -1:  # Right heavy
            if self._height(node.right.right) >= self._height(node.right.left):  # type: ignore
                return self.rotate_left(node)
            else:
                return self.rotate_right_left(node)

        return node

    # ------------------------------------------------------------------ #
    #  Insert                                                              #
    # ------------------------------------------------------------------ #

    def insert(self, status: PlatformStatus) -> None:
        self.root = self._insert(self.root, status)

    def _insert(self, node: Optional[PlatformNode], status: PlatformStatus) -> PlatformNode:
        if node is None:
            return PlatformNode(status)
        if status.platform_id < node.key:
            node.left = self._insert(node.left, status)
        elif status.platform_id > node.key:
            node.right = self._insert(node.right, status)
        else:
            # Update existing
            node.status = status
            return node
        return self._rebalance(node)

    # ------------------------------------------------------------------ #
    #  Delete                                                              #
    # ------------------------------------------------------------------ #

    def delete(self, platform_id: int) -> None:
        self.root = self._delete(self.root, platform_id)

    def _delete(self, node: Optional[PlatformNode], key: int) -> Optional[PlatformNode]:
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # Replace with in-order successor
            successor = self._min_node(node.right)
            node.status = successor.status
            node.key = successor.key
            node.right = self._delete(node.right, successor.key)
        return self._rebalance(node)

    def _min_node(self, node: PlatformNode) -> PlatformNode:
        while node.left:
            node = node.left
        return node

    # ------------------------------------------------------------------ #
    #  Search                                                              #
    # ------------------------------------------------------------------ #

    def search(self, platform_id: int) -> Optional[PlatformNode]:
        cur = self.root
        while cur:
            if platform_id == cur.key:
                return cur
            cur = cur.left if platform_id < cur.key else cur.right
        return None

    def inorder(self) -> List[PlatformStatus]:
        """Return all platforms sorted by platform_id."""
        result: List[PlatformStatus] = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node: Optional[PlatformNode], result: List[PlatformStatus]) -> None:
        if node:
            self._inorder(node.left, result)
            result.append(node.status)
            self._inorder(node.right, result)

    # ------------------------------------------------------------------ #
    #  Task 6.3 — Greedy platform assignment                              #
    # ------------------------------------------------------------------ #

    def assign_platform(self, arrival_time: int, departure_time: int) -> Optional[int]:
        """
        Find the platform with earliest availability_from <= arrival_time.
        Assign it and update its available_from to departure_time.
        Returns platform_id or None if no platform is free.
        """
        best: Optional[PlatformNode] = None
        self._find_best(self.root, arrival_time, best_holder := [None])
        best = best_holder[0]

        if best is None:
            return None

        best.status.available_from = departure_time
        return best.status.platform_id

    def _find_best(
        self,
        node: Optional[PlatformNode],
        arrival_time: int,
        best_holder: list,
    ) -> None:
        """Traverse tree to find platform with earliest available_from <= arrival_time."""
        if node is None:
            return
        if node.status.available_from <= arrival_time:
            current_best: Optional[PlatformNode] = best_holder[0]
            if current_best is None or node.status.available_from < current_best.status.available_from:
                best_holder[0] = node
        self._find_best(node.left, arrival_time, best_holder)
        self._find_best(node.right, arrival_time, best_holder)
