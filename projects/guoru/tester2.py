import sut
import sys
import os
import time
import random

class FBDR_Tester():
	def __init__(self):
		self.errorSeqs = []
		self.nonErrorSeqs = []
		self.sut = sut.sut()
		
	def CheckArguments(self):
		if len(sys.argv) == 8:
			self.timeout 	= int(sys.argv[1])
			self.seed 		= int(sys.argv[2])
			self.depth 		= int(sys.argv[3])
			self.width 		= int(sys.argv[4])
			self.faults 	= int(sys.argv[5])
			self.coverage 	= int(sys.argv[6])
			self.running  	= int(sys.argv[7])
			return True
		else:
			print "ERROR! Need 7 arguments:"
			print "[timeout] [seed] [depth] [width] [faults] [coverage] [running]"
			return False

	def DiscardDuplicates(self, newSequence):
		for nes in self.nonErrorSeqs:
			if set(newSequence) < set(nes):
				return True
		for es in self.errorSeqs:
			if set(newSequence) < set(es):
				return True
		return False # no duplicate

	def RandomSeqsAndVals(self, nonErrorSeqs, n=1):
		if self.nonErrorSeqs == [] or n > len(self.nonErrorSeqs):
			return []
		return [random.choice(self.nonErrorSeqs) for i in xrange(n)]

	def SetExtensibleFlags(self, newSequence):
		pass

	def ProduceRunningInfo(self, act, elapsed):
		if self.sut.newBranches() != set([]):
			print "ACTION:",act[0]
			for b in self.sut.newBranches():
				print elapsed,len(self.sut.allBranches()),"New branch",b
	
	def RecordFailure(self):
		count = 0
		while os.path.exists('failure' +str(count) + '.test') == True:
			count += 1
		#recoder = open('failure' +str(count) + '.test', 'w')
		#recoder.write(str(self.sut.failure())) 
		#recoder.close
		filename = 'failure' +str(count) + '.test'
		self.sut.saveTest(self.sut.test(),filename) 
		

	def Generation(self):
		# random seed
		rgen = random.Random(self.seed)

		# Testing loop
		startTime = time.time()
		while (time.time()-startTime) < self.timeout:
			#print (time.time()-startTime)

			# Generate a sequence of n actions
			newSequence = self.sut.randomEnableds(rgen, self.depth * self.width) 
			seqs = self.RandomSeqsAndVals(self.nonErrorSeqs,n=1)
			newSequence.extend(seqs)

			# Discard duplicates
			if self.DiscardDuplicates(newSequence):
				continue

			# Excute (newSeq, contracts)
			violated = False
			for act in newSequence:
				if self.running == True:
					self.ProduceRunningInfo(act, elapsed=(time.time() - startTime))
				# Check if violated
				stepOK = self.sut.safely(act)
				

				# Failure check and record
				if self.faults == True:
				 	if stepOK != True:#or violated == True:
						self.RecordFailure()
						print (time.time()-startTime), 'Failure found. Program is terminated'
						#return self.nonErrorSeqs, self.errorSeqs
						continue
						
				if self.sut.check() != True:
					violated = True

			if violated == True:
				self.errorSeqs += newSequence
			else:
				self.nonErrorSeqs += newSequence
				self.SetExtensibleFlags(newSequence)

		return self.nonErrorSeqs, self.errorSeqs

	def Report(self):
		if self.coverage == True:
			self.sut.internalReport()
		


if __name__ == '__main__':

	tester = FBDR_Tester()

	if not tester.CheckArguments():
		sys.exit()

	tester.Generation()
	tester.Report()