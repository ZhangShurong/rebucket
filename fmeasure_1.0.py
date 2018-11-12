import re
import os
import sys
import string
import math
import scipy
import numpy
import scipy.spatial.distance as distance
from matplotlib.pyplot import show
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster, fclusterdata

def read_result(filename, func_line):
  if os.path.exists(filename) != True:
    print '%s is not found'%filename
    return None
  f = open(filename, 'r')
  trans = string.maketrans('[,\']', '    ')

  bucket = []
  funcBucket = []

  for row in f:
    row = row.translate(trans)
    tmp = row.split()
    cluster = []
    funcCluster = []

    for patchname in tmp:
      patchname = cut_workload(patchname)
      funcName = replaceFunc(patchname, func_line)

      cluster.append(patchname)
      funcCluster.append(funcName)
    cluster.sort()
    funcCluster.sort()
    
    bucket.append(cluster)
    funcBucket.append(funcCluster)

  return bucket, funcBucket

def replaceFunc(patchname, func_line):
  for row in func_line:
    if row[0] == patchname:
      return row[1]

def read_entry():
  crash_entry = []
  func_entry = []

  if os.path.exists('crash_entry') != True:
    print 'crash_entry is not found'
    quit()
  f = open('crash_entry', 'r')
  for row in f:
    tmp = row.split()
    crash_entry.append([float(tmp[0]), tmp[1]])
  f.close()

  if os.path.exists('func_entry') != True:
    print 'func_entry is not found'
    quit()
  f = open('func_entry', 'r')
  for row in f:
    tmp = row.split()
    func_entry.append([float(tmp[0]), tmp[1]])
  f.close()

  return crash_entry, func_entry

def read_func_line():
  func_line = []

  if os.path.exists('func_line') != True:
    print 'func_line is not found'
    quit()
  f = open('func_line', 'r')
  for row in f:
    tmp = row.split()
    func_line.append(tmp)
  f.close()

  return func_line

def calculateFmeasure(bucket, entry):
  #num = len(bucket)
  num = 0
  fmeasure = 0

  for row in entry:
    num += row[0]
  print str(num)
  
  for i in range(0, len(entry)):
    f = []
    for j in range(0, len(bucket)):
      precision = float(calculatePrecision(bucket[j], entry[i][1]))
      recall = float(calculateRecall(bucket[j], entry[i][1], entry[i][0]))

      if precision == 0 or recall == 0:
        f.append(0)
      else:
        f.append( float((2 * precision * recall) / (precision + recall)) )
    
    fmeasure += float(entry[i][0]) * float(max(f)) / float(num)
  
  return fmeasure

def calculatePrecision(cluster, bugName):
  return float(cluster.count(bugName)) / float(len(cluster))
  
def calculateRecall(cluster, bugName, bugNum):
  return float(cluster.count(bugName)) / float(bugNum)

def cut_workload(patchname):
  if re.search('ub.?_', patchname):
    patchname = re.sub('ub.?_', '', patchname)
  elif re.search("fb.?_", patchname):
    patchname = re.sub('fb.?_', '', patchname)
  elif re.search('db.?_', patchname):
    patchname = re.sub('db.?_', '', patchname)
  elif re.search('iz.?_', patchname):
    patchname = re.sub('iz.?_', '', patchname)
  elif re.search('ltp.?_', patchname):
    patchname = re.sub('ltp.?_', '', patchname)
  
  return patchname

def create_func_entry(func_entry, funcBucket):
  for i in range(len(func_entry)):
    entryNum = 0
    for j in range(len(funcBucket)):
      entryNum += funcBucket[j].count(func_entry[i][1])
    func_entry[i][0] = entryNum
  return func_entry

if __name__ == "__main__":
  argvs = sys.argv
  argc = len(argvs)

  if argc == 1:
    print 'Please type target file name'
    quit()
  else:
    filename = argvs[1]

  crash_entry, func_entry = read_entry()
  func_line = read_func_line()
  bucket, funcBucket = read_result(filename, func_line)
  func_entry = create_func_entry(func_entry, funcBucket)

  print crash_entry
  print func_entry
  print 'f-measure = ' +  str(calculateFmeasure(bucket, crash_entry))
  print 'f-measure(func) = ' + str(calculateFmeasure(funcBucket, func_entry))
