from collections import deque
from utils import add, in_bounds
from settings import DIR_LIST

def flood_fill_free_space(start, occupied):
    if start in occupied or not in_bounds(start):
        return 0
    q = deque([start])
    seen = {start}
    while q:
        cur = q.popleft()
        for d in DIR_LIST:
            nxt = add(cur, d)
            if nxt in seen or nxt in occupied or not in_bounds(nxt):
                continue
            seen.add(nxt)
            q.append(nxt)
    return len(seen)


def count_safe_neighbors(cell, occupied):
    n = 0
    for d in DIR_LIST:
        nxt = add(cell, d)
        if in_bounds(nxt) and nxt not in occupied:
            n += 1
    return n
