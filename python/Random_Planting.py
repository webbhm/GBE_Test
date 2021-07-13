from random import seed, shuffle
from numpy import reshape
from numpy import ndarray
seed()
l = list(range(1, 7))
#print(l)
shuffle(l)
#print(l)
l = reshape(l, (2, 3))
#print(l)
env = {}
env["planting"] = ndarray.tolist(l)
print(env)