import re

# Indexing

def process_dataset(title, description, fl=32):
  stitle, sdescription = sanitize(title), sanitize(description)
  combined = stitle + "    " + sdescription
  #combined = stitle + "\t" + sdescription
  fingerprint = tlsh_fingerprint(combined, 2*fl)
  return [ 4*fingerprint[i] + fingerprint[i+1] for i in range(0, len(fingerprint), 2) ]

def sanitize(text):
  text = re.sub('[^\w\s\"]', "", text)
  text = re.sub('\"', "'", text)
  #text = re.sub("  ", " ", text)
  text = text.lower()
  #text = ' '.join([ word for word in text.split(" ") if re.sub("'", "", word) not in ENGLISH_STOP_WORDS ])
  return text

def tlsh_fingerprint(text, buckets=64):
  bucketCount = [0 for _ in range(buckets)]  
  
  c0, c1, c2, c3, c4 = ord(text[0]), ord(text[1]), ord(text[2]), ord(text[3]), ord(text[4])
  nexti = 5

  while True:
    bucketCount[pearson_three_bytes(c0, c1, c2, buckets)] += 1
    bucketCount[pearson_three_bytes(c0, c3, c1, buckets)] += 1
    bucketCount[pearson_three_bytes(c1, c0, c4, buckets)] += 1
    bucketCount[pearson_three_bytes(c3, c2, c0, buckets)] += 1
    bucketCount[pearson_three_bytes(c4, c0, c2, buckets)] += 1
    bucketCount[pearson_three_bytes(c3, c4, c0, buckets)] += 1

    if nexti >= len(text):
      break
    
    c0, c1, c2, c3, c4 = c1, c2, c3, c4, ord(text[nexti])
    nexti += 1

  bucketCount[pearson_three_bytes(c1, c2, c3, buckets)] += 1
  bucketCount[pearson_three_bytes(c1, c4, c2, buckets)] += 1
  bucketCount[pearson_three_bytes(c4, c3, c1, buckets)] += 1
  bucketCount[pearson_three_bytes(c2, c3, c4, buckets)] += 1

  tmpaux = bucketCount.copy()
  tmpaux.sort()

  qutil1, qutil2, qutil3 = tmpaux[int(len(tmpaux)/4)], tmpaux[int(len(tmpaux)/2)], tmpaux[int(3*len(tmpaux)/4)]

  return [
    ( 0 if bucketCount[i] <= qutil1 else 
    ( 1 if bucketCount[i] <= qutil2 else 
    ( 2 if bucketCount[i] <= qutil3 else 
      3 ) ) ) for i in range(buckets)
  ]

def pearson_three_bytes(pc0, pc1, pc2, buckets=64):
  return (PEARSON_TABLE[PEARSON_TABLE[pc0 & 255] ^ (pc1 & 255)] ^ (pc2 & 255)) % buckets

PEARSON_TABLE = [
  98, 6, 85, 150, 36, 23, 112, 164, 135, 207, 169, 5, 26, 64, 165, 219,
  61, 20, 68, 89, 130, 63, 52, 102, 24, 229, 132, 245, 80, 216, 195, 115,
  90, 168, 156, 203, 177, 120, 2, 190, 188, 7, 100, 185, 174, 243, 162, 10,
  237, 18, 253, 225, 8, 208, 172, 244, 255, 126, 101, 79, 145, 235, 228, 121,
  123, 251, 67, 250, 161, 0, 107, 97, 241, 111, 181, 82, 249, 33, 69, 55,
  59, 153, 29, 9, 213, 167, 84, 93, 30, 46, 94, 75, 151, 114, 73, 222,
  197, 96, 210, 45, 16, 227, 248, 202, 51, 152, 252, 125, 81, 206, 215, 186,
  39, 158, 178, 187, 131, 136, 1, 49, 50, 17, 141, 91, 47, 129, 60, 99,
  154, 35, 86, 171, 105, 34, 38, 200, 147, 58, 77, 118, 173, 246, 76, 254,
  133, 232, 196, 144, 198, 124, 53, 4, 108, 74, 223, 234, 134, 230, 157, 139,
  189, 205, 199, 128, 176, 19, 211, 236, 127, 192, 231, 70, 233, 88, 146, 44,
  183, 201, 22, 83, 13, 214, 116, 109, 159, 32, 95, 226, 140, 220, 57, 12,
  221, 31, 209, 182, 143, 92, 149, 184, 148, 62, 113, 65, 37, 27, 106, 166,
  3, 14, 204, 72, 21, 41, 56, 66, 28, 193, 40, 217, 25, 54, 179, 117,
  238, 87, 240, 155, 180, 170, 242, 212, 191, 163, 78, 218, 137, 194, 175, 110,
  43, 119, 224, 71, 122, 142, 42, 160, 104, 48, 247, 103, 15, 11, 138, 239
]

ENGLISH_STOP_WORDS = [
  "it", "there", "if", "of",
  "and", "so", "yet", "or", "moreover", "also", "too", "thus", "hence", "therefore", "furthermore", "likewise",
  "a", "an", "the", "other", "another", "some", "any", "its", "their", "such",
  "all", "every", "each",
  "is", "are", "be", "was", "were", "been", "do", "does", "did", "will", "would",
  "la", "der", "y", "de"
]

# Similarity

class FingerprintSimilarity:
  def __init__(self):
    self.unit_dist = 8
    self.diff_count = [ 0 for _ in range(256) ]

    l = 1
    while l < 256:
      for i in range(l):
        self.diff_count[i + l] = self.diff_count[i + 3*l] = self.diff_count[i] + self.unit_dist
        self.diff_count[i + 2*l] = self.diff_count[i] + self.unit_dist + 2
      l *= 4
  
  def similarity(self, left, right):
    dist = 0;
    for i in range(16):
      dist += self.diff_count[(left[i] ^ right[i]) & 255]
    dist /= self.unit_dist

    x = abs(len(left) - len(right)) / max(len(left), len(right))
    dist += int(48.0 * x**2 * (-2.0 * x + 3.0))

    return dist
