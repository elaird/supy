import collections

class SampleHolder(dict) :
    sample = collections.namedtuple("sample", "filesCommand xs lumi ptHatMin")

    def __init__(self) : self.overlappingSamples = []

    def add(self, name, filesCommand = None, xs = None, lumi = None, ptHatMin = None) :

        if lumi and (xs or ptHatMin) : raise Exception("Overspecified sample: %s"%name)
        if not (lumi or xs) :          raise Exception("Underspecified sample: %s"%name)

        self[name] = self.sample(filesCommand, xs, lumi, ptHatMin)

    def adjustOverlappingSamples( self, listOfSamples, useRejectionMethod = True ) :
        if len(listOfSamples) is not len(set(listOfSamples)) :
            raise Exception("Non unique overlapping samples",listOfSamples)

        for s in listOfSamples :
            if s not in self :
                raise Exception("unknown sample",s)

        for s in listOfSamples :
            for otherOverlappingSamples in self.overlappingSamples :
                if s in otherOverlappingSamples[0] :
                    raise Exception("sample already grouped with others",s)

        self.overlappingSamples.append( (listOfSamples, useRejectionMethod ) )

from samplesMC import *
