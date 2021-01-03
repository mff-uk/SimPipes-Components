import math
from typing import Dict, List, Union
from functools import reduce
import numpy as np
from numba import jit

def _cosine(words1: Dict[str, float], words2: Dict[str, float]) -> float:
  W1 = 0
  for w in words1:
    W1 += words1[w]*words1[w]
  W2 = 0
  for w in words2:
    W2 += words2[w]*words2[w]
  WW = 0
  for w in set(words1.keys()) & set(words2.keys()):
    WW += words1[w]*words2[w]
  return WW/math.sqrt(W1 * W2)


def _e_cosine(words1: Dict[str, float], words2: Dict[str, float]) -> float:
  W1 = reduce(lambda x, y: x+y, map(lambda a: a*a, words1.values()), 0)
  W2 = reduce(lambda x, y: x+y, map(lambda a: a*a, words2.values()), 0)
  WW = reduce(lambda x, y: x+y, map(lambda a: words1[a]*words2[a], words1.keys() & words2.keys()), 0)
  return WW/math.sqrt(W1 * W2)


@jit(nopython=True)
def _e_cosine_v(vec1, vec2) -> float:
  W1 = np.sum(vec1**2)
  W2 = np.sum(vec2**2)
  WW = np.sum(vec1*vec2)
  return WW/math.sqrt(W1 * W2)