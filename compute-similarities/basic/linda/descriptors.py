import re
from typing import List, Set, Dict
import numpy as np
from numba import jit

from . import tlsh


def _string(columns: List[str]) -> str:
  text = ""
  for content in columns:
    text += str(content)
  return text


def _vector(columns: List[str]):
  return np.array([ float(x) for x in columns ])


def _set(columns: List[str]) -> Set[str]:
  tokens = set()
  for token in columns:
    if len(token) == 0:
      continue
    tokens.add(token)
  return tokens


def _words_set(columns: List[str]) -> Set[str]:
  words = set()
  for content in columns:
    for word in re.split('[^\w]+', content):
      if len(word) == 0:
        continue
      words.add(word)
  return words


def _words_count(columns: List[str]) -> Dict[str, float]:
  words = {}
  for content in columns:
    for word in re.split('[^\w]+', content):
      if len(word) == 0:
        continue
      if not word in words:
        words[word] = 0
      words[word] += 1
  return words


def _tlsh(columns: List[str]) -> List[int]:
  return tlsh.process_dataset(columns[0], columns[1])


_DESCRIPTORS = {
  "string": _string,
  "vector": _vector,
  "words_count": _words_count,
  "words_set": _words_set,
  "set": _set,
  "tlsh": _tlsh,
}


def descriptor_factory(name: str):
  assert name in _DESCRIPTORS, "Unknown descriptor type."
  return _DESCRIPTORS[name]
