import numpy as np
from main import n

scale = 15
sample = np.random.exponential(scale)

times = [0 for _ in range(n)]


for i in range(n):
    times[i] += np.random.exponential(scale)

