import heapq


class Event:
    def __init__(self, object, function, params, time):
        self.object = object
        self.function = function
        self.params = params
        self.time = time

    def __lt__(self, other):
        return self.time < other.time

    def __eq__(self, other):
        return self.time == other.time

    def __gt__(self, other):
        return self.time > other.time

    def __le__(self, other):
        return self.time <= other.time

    def __ge__(self, other):
        return self.time >= other.times

    def __str__(self) -> str:
        return f"Object: {self.object}, Function: {self.function}, Params: {self.params}, Time: {self.time}"


class EventPriorityQueue:
    def __init__(self):
        self._queue = []

    def push(self, event):
        heapq.heappush(self._queue, event)

    def pop(self):
        return heapq.heappop(self._queue)

    def is_empty(self):
        return len(self._queue) == 0
