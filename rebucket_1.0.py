#! 
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

hatena_flag = 0
analyze_flag = 0
stackLen = []

def getCallStack (files):
	totalCallStack = 0
	totalHatena = 0
	allFunction = []

	allCallStack = []
	allHatena = []
	for file in files:
		if re.search('.*oops$', file):
			f = open(file, 'r')

			file = re.sub('\.oops', '', file)
			allFunc = [file, []]
			
			flag = 0
			ripFlag = 0
			
			for row in f:
				if ripFlag == 1 :
					if row.find('RIP') == -1:
						print 'ERROR: there is not RIP ->' + allFunc[0]
						quit()
					row = re.sub('RIP', '', row)
					row.lstrip()
					row = re.sub('[\s]*\[<[a-f,0-9]*>\][\s]*', '', row)
					row = re.sub('\+.+', '', row).rstrip('\n')
					totalCallStack += 1
					allFunc[1].insert(0, row)
					allFunction.append(row)
					allCallStack.append(allFunc)
					break

				if row.find('Call Trace') != -1 and flag == 0:
					flag = 1
					continue
				if flag == 1:
					if row.find('Call Trace') != -1:
						del allFunc[1][:]
						continue
					if row.find('<IRQ>') != -1 or row.find('<EOI>') != -1:
						continue
					if re.search("\[<[a-f0-9]*>\].*", row):
						row = re.sub('[\s]*\[<[a-f,0-9]*>\][\s]*', '', row)
						#offset on
						#row = re.sub('/.+', '', row).rstrip('\n')
						#offset off
						row = re.sub('\+.+', '', row).rstrip('\n')

						#if there is hatena
						if re.search('[\s]*\?[\s]*', row):
							allHatena.append(row)
							totalHatena += 1
							if hatena_flag == 1:
								continue
							row = re.sub('[\s]*\?[\s]*', '', row)

						totalCallStack += 1
						allFunc[1].append(row)
						allFunction.append(row)
					if row.startswith('Code:'):
						ripFlag = 1
						flag = 0
						#allCallStack.append(allFunc)
						#break
						
			f.close()
	print 'total CallStack: %d'%(totalCallStack)
	print 'average length:  %d'%(totalCallStack / len(allCallStack))
	print 'total hatena:    %d'%(totalHatena)
	print 'average hatena:  %d'%(totalHatena / len(allCallStack))
	createHatena(allHatena)
	createAllFunction(allFunction)
	return allCallStack

def createHatena(allHatena):
	f = open('hatena', 'w')

	allHatena.sort()

	total = 1
	length = len(allHatena)

	for i in range(length):
		if i + 1 == length:
			f.write(str(total) + ' ' + allHatena[i] + '\n')
		else:
			if allHatena[i] == allHatena[i+1]:
				total += 1
				continue
			else:
				f.write(str(total) + ' ' + allHatena[i] + '\n')
				total = 1
	f.close()
	print 'create hatena'

def createAllFunction(allFunction):
	f = open('allFunction', 'w')

	allFunction.sort()

	total = 1
	length = len(allFunction)
	
	for i in range(length):
		if i + 1 == length:
			f.write(str(total) + ' ' + allFunction[i] + '\n')
		else:
			if allFunction[i] == allFunction[i+1]:
				total += 1
				continue
			else:
				f.write(str(total) + ' ' + allFunction[i] + '\n')
				total = 1
	f.close()
	print 'create allFunction'

def getlcs (index1, index2, allCallStack, c, o):
	stack_len1 = len(allCallStack[index1][1])
	stack_len2 = len(allCallStack[index2][1])

	if stack_len1 == 0:
		#print stack_len1
		#print allCallStack[index1][0]
		return 1
	if stack_len2 == 0:
		#print stack_len2
		#print allCallStack[index2][0]
		return 1

	lcs = [[0. for j in range(len(allCallStack[index2][1]) + 1)] for i in range(len(allCallStack[index1][1]) + 1)]

	for i in xrange(1, stack_len1 + 1):
		for j in xrange(1, stack_len2 + 1):
			if (allCallStack[index1][1][i-1] == allCallStack[index2][1][j-1]):
				x = ( math.e ** (-c * min(i-1, j-1)) ) * ( math.e ** (-o * abs(i-j)) )
			else:
				x = 0.
			lcs[i][j] = max(lcs[i-1][j-1] + x, lcs[i-1][j], lcs[i][j-1])

	sig = 0.
	for i in range(min(stack_len1, stack_len2)):
		sig += math.e ** (-c * i)
	
	res = lcs[stack_len1][stack_len2] / sig
	return (1 - res)

def clustering(allCallStack, c, o, dist, filename):
	sim = []
	for i in range(len(allCallStack) - 1):
		for j in range(i + 1, len(allCallStack)):
			res = getlcs(i, j, allCallStack, c, o)
			sim.append(res)

	link = linkage(sim, method = 'complete')
	result = fcluster(link, dist, criterion='distance', depth = 2, R=None, monocrit = None)

	maximum = max(result)
	bucket = [[] for i in range(maximum)]
	for i in range(len(result)):
		bucket[result[i]) - 1].append(str(allCallStack[i][0]))
	bucket.sort()

	if hatena_flag == 1:
		f = open(filename + '_result_hatena', 'w')
	else:
		f = open(filename + '_result', 'w')

	for i in range(len(bucket)):
		f.write(str(bucket[i]) + '\n')
	f.close()

	return bucket

def read_set_file():
	crash_entry =[]

	if os.path.exists('crash_entry') != True:
		return None, None
	if os.path.exists('func_line') != True:
		return None, None

	f = open('crash_entry', 'r')
	for row in f:
		tmp = row.split()
		crash_entry.append([tmp[0], tmp[1]])
	f.close()
	
	f = open('func_line', 'r')
	fault_func = []
	for row in f:
		tmp = row.split()
		fault_func.append([tmp[0], tmp[1]])
	f.close

	return crash_entry, fault_func

def set_bucket(bucket):
	for i in range(len(bucket)):
		for j in range(len(bucket[i])):
			if re.search("ub.?_", bucket[i][j]):
			#if bucket[i][j].find('ub_') != -1:
				bucket[i][j] = re.sub('ub.?_', '', bucket[i][j])
			if re.search("fb.?_", bucket[i][j]):
			#if bucket[i][j].find('fb_') != -1:
				bucket[i][j] = re.sub('fb.?_', '', bucket[i][j])
			if re.search("db.?_", bucket[i][j]):
			#if bucket[i][j].find('db_') != -1:
				bucket[i][j] = re.sub('db.?_', '', bucket[i][j])
			if re.search("iz.?_", bucket[i][j]):
			#if bucket[i][j].find('iz_') != -1:
				bucket[i][j] = re.sub('iz.?_', '', bucket[i][j])
			if re.search("ltp.?_", bucket[i][j]):
			#if bucket[i][j].find('ltp_') != -1:
				bucket[i][j] = re.sub('ltp.?_', '', bucket[i][j])	

def create_type_bucket(bucket, tmp_count, filename):
	if hatena_flag == 1:
		f = open(filename + '_typeBucket_hatena', 'w')
	else:
		f = open(filename + '_typeBucket', 'w')
	
	for i in range(len(bucket)):
		before_num = str(len(bucket[i]))
		bucket[i] = list(set(bucket[i]))
		bucket[i].sort()
		tmp_count.extend(bucket[i])
		after_num = str(len(bucket[i]))

		f.write(before_num + ' -> ' + after_num + ' ' + str(bucket[i]) + '\n')
	f.close()

def create_func_bucket(bucket, filename, fault_func):
	func_bucket = []
	for i in range(len(bucket)):
		tmp_bucket = []
		for j in range(len(bucket[i])):
			for k in range(len(fault_func)):
				if bucket[i][j] == fault_func[k][0]:
					tmp_bucket.append(fault_func[k][1])
					break
		func_bucket.append(tmp_bucket)

	if hatena_flag == 1:
		f = open(filename + '_funcBucket_hatena', 'w')
	else:
		f = open(filename + '_funcBucket', 'w')
	for i in range(len(func_bucket)):
		before_num = str(len(func_bucket[i]))
		func_bucket[i] = list(set(func_bucket[i]))
		func_bucket[i].sort()
		after_num = str(len(func_bucket[i]))
	
		f.write(before_num + ' -> ' + after_num + str(func_bucket[i]) + '\n')
	f.close()

	return func_bucket	

def create_count(tmp_count, count):
	
	total = 1
	length = len(tmp_count)
	tmp_count.sort()
	count = []

	for i in range(length):
		if i + 1 == length:
			count.append([total, tmp_count[i]])
		else:
			if tmp_count[i] == tmp_count[i + 1]:
				total += 1
				continue
			else:
				count.append([total, tmp_count[i]])
				total = 1

	if len(crash_entry) != len(count):
		print 'ERROR: len(crash_entry) != len(count)'
		return None
	
	if hatena_flag == 1:
		f = open(filename + '_count_hatena', 'w')
	else:
		f = open(filename + '_count', 'w')
	for i in range(len(count)):
		if crash_entry[i][1] != count[i][1]:
			print 'ERROR: %s != %s'%(crash_entry[i][1], count[i][1])
			f.close()
			return None
		f.write(str(crash_entry[i][0]) + ' -> ' + str(count[i][0]) + ' ' + count[i][1] + '\n')
	f.close()
	return count

def create_func_count(func_bucket, filename):
	all_func = []
	for i in range(len(func_bucket)):
		all_func.extend(func_bucket[i])
	all_func.sort()

	if hatena_flag == 1:
		f = open(filename + '_funcCount_hatena', 'w')
	else:
		f = open(filename + '_funcCount', 'w')

	total = 1
	length = len(all_func)
	
	for i in range(length):
		if i + 1 == length:
			f.write(str(total) + ' ' + all_func[i])
		else:
			if all_func[i] == all_func[i + 1]:
				total += 1
				continue
			else:
				f.write(str(total) + ' ' + all_func[i] + '\n')
				total = 1
	f.close()

def read_result(filename):
	if os.path.exists(filename) != True:
		print '%s is not found'%filename
		return None
	f = open(filename, 'r')
	trans = string.maketrans('[,\']', '    ')

	bucket = []
	for row in f:
		row = row.translate(trans)
		tmp = row.split()
		bucket.append(tmp)

	return bucket	

def create_offset(bucket, filename):
	all_offset = []

	for i in range(len(bucket)):
		tmp = []
		for j in range(len(bucket[i])):
			rip_flag = 0
			f = open(bucket[i][j] + '.oops', 'r')
			for row in f:
				if re.search('RIP ', row):
					rip_flag = 1
					row = re.sub('RIP', '', row)
					row = re.sub('\[<[a-f0-9]*>\]', '', row)
					row = re.sub('\+.+', '', row).rstrip('\n')
					row = row.strip()
					tmp.append(row)
					break
			if rip_flag == 0:
				tmp.append('None')
			f.close()
		tmp.sort()
		all_offset.append(tmp)

	f = open(filename + '_offset', 'w')
	for i in range(len(all_offset)):
		before_num = str(len(all_offset[i]))
		all_offset[i] = list(set(all_offset[i]))
		all_offset[i].sort()
		after_num = str(len(all_offset[i]))
		f.write(before_num + ' -> ' + after_num + ' ' + str(all_offset[i]) + '\n')
	f.close()			
					

if __name__ == "__main__":

	argvs = sys.argv
	argc = len(argvs)

	if argc == 1:
		c = 0.; o = 0.; dist = 0.1
	else:
		if argvs[1] == 'h':
			#ignore hatena
			hatena_flag = 1
			c = float(argvs[2])
			o = float(argvs[3])
			dist = float(argvs[4])
		elif argvs[1] == 'a':
			#analyze
			analyze_flag = 1
			filename = argvs[2]
		else:
			c = float(argvs[1])
			o = float(argvs[2])
			dist = float(argvs[3])

	if analyze_flag == 0:
		filename = str(c) + '_' + str(o) + '_' + str(dist)
		filename = re.sub('\.', '', filename)
		if os.path.exists(filename) != True:
			os.mkdir(filename)
		filename = filename + '/' + filename

		files = os.listdir(os.getcwd())
		files.sort()

		#read oops file and get Call Stack
		allCallStack = getCallStack(files)

		#clustering oops file
		bucket = clustering(allCallStack, c, o, dist, filename)
	else:
		bucket = read_result(filename)
		if bucket is None:
			print 'ERROR: can not read %s'%filename
		filename = re.sub('_result', '', filename)
		
	#analyze start
	create_offset(bucket, filename)
	crash_entry, fault_func = read_set_file()
	if crash_entry is None:
		print 'ERROR: crash_entry of func_line is not found'
		quit()
	
	tmp_count = []
	set_bucket(bucket)
	create_type_bucket(bucket, tmp_count, filename)
	func_bucket = create_func_bucket(bucket, filename, fault_func)
	count = create_count(tmp_count, filename)
	create_func_count(func_bucket, filename)
