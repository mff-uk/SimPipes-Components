import math
from typing import Set, Dict, List, Union, Any
import numpy as np
from numba import jit, prange

from . import tlsh
from . import similarities

def _levenshtein(str1: str, str2: str) -> float:
  if str1 == str2:
    return 0

  ld = np.full((len(str1) + 1, len(str2) + 1), 0)

  for i in range(1, len(str1) + 1):
    ld[i, 0] = i
  for j in range(1, len(str2) + 1):
    ld[0, j] = j

  for j in range(1, len(str2) + 1):
    for i in range(1, len(str1) + 1):
      sub_cost = 1
      if str1[i - 1] == str2[j - 1]:
        sub_cost = 0
      ld[i, j] = min(ld[i - 1, j] + 1,
                     ld[i, j - 1] + 1,
                     ld[i - 1, j - 1] + sub_cost)

  return ld[len(str1), len(str2)]


def _jaccard(set1: Set[str], set2: Set[str]) -> float:
  if set1 == set2:
    return 0
  if len(set1) == 0 and len(set2) == 0:
    return 0
  
  and_ = set1.intersection(set2)
  or_ = set1.union(set2)
  return (len(or_) - len(and_)) / len(or_)


def _cosine(words1: Dict[str, float], words2: Dict[str, float]) -> float:
  if len(words1) == 0 and len(words2) == 0:
    return 0
  if len(words1) == 0 or len(words2) == 0:
    return math.inf
  return 1 - similarities._e_cosine(words1, words2)

@jit(nopython=True)
def _cosine_v(vec1, vec2) -> float:
  if vec1.shape != vec2.shape:
    return math.inf
  W1 = np.sum(vec1**2)
  W2 = np.sum(vec2**2)
  if W1 == 0 or W2 == 0:
    return math.inf
  WW = np.sum(vec1*vec2)
  return 1 - WW/math.sqrt(W1*W2)

def _angle(words1: Dict[str, float], words2: Dict[str, float]) -> float:
  if len(words1) == 0 and len(words2) == 0:
    return 0
  if len(words1) == 0 or len(words2) == 0:
    return math.inf
  return math.acos(similarities._e_cosine(words1, words2))

@jit(nopython=True)
def _angle_v(vec1, vec2) -> float:
  if vec1.shape != vec2.shape:
    return math.inf
  W1 = np.sum(vec1**2)
  W2 = np.sum(vec2**2)
  if W1 == 0 or W2 == 0:
    return math.inf
  WW = np.sum(vec1*vec2)
  return math.acos(WW/math.sqrt(W1*W2))


_FS = tlsh.FingerprintSimilarity()
def _tlsh(hash1: List[int], hash2: List[int]) -> float:
  return _FS.similarity(hash1, hash2)

@jit(nopython=True)
def _hausdorff_uni_f(cont1, cont2, dist) -> float:
  return max([ min([ dist(i1, i2) for i2 in cont2 ]) for i1 in cont2 ])

@jit(nopython=True)
def _hausdorff_uni(cont1, cont2, dist) -> float:
  dmax = 0
  for i1 in cont1:
    dmin = math.inf
    for i2 in cont2:
      d = dist(i1, i2)
      if d < dmin:
        dmin = d
        if dmin == 0:
          break
    if dmin > dmax:
      dmax = dmin
      if dmax == math.inf:
        break
  return dmax

@jit(nopython=True)
def _hausdorff_sym(cont1, cont2, dist) -> float:
  lhs = _hausdorff_uni(cont1, cont2, dist)
  rhs = _hausdorff_uni(cont2, cont1, dist)
  return lhs if lhs < rhs else rhs

@jit(nopython=True)
def _hausdorff(cont1, cont2, dist) -> float:
  return _hausdorff_sym(cont1, cont2, dist)

_DISTANCES = {
  "levenshtein": _levenshtein,
  "jaccard": _jaccard,
  "angle": _angle,
  "cosine": _cosine,
  "cosine_v": _cosine_v,
  "tlsh": _tlsh
}


def distance_factory(name: str):
  assert name in _DISTANCES, "Unknown distance measure."
  return _DISTANCES[name]

class HausdorffDistance(object):
  def __init__(self, distance):
    self.distance = distance
  
  def __call__(self, d1, d2):
    return _hausdorff(d1, d2, self.distance)

def hausdorff_factory(name: str):
  assert name in _DISTANCES, "Unknown distance measure."
  return HausdorffDistance(_DISTANCES[name])
