#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples

class jsonMaker(analysis.analysis) :
    def outputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def listOfSteps(self) :
        return [ steps.progressPrinter(2,300),
                 steps.jsonMaker("/vols/cms02/%s/tmp/"%os.environ["USER"]),
                 ]

    def listOfCalculables(self) :
        return calculables.zeroArgs()

    def listOfSamples(self) :
        return [samples.specify(name = "JetMET.Run2010A")]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet]

    def mainTree(self) :
        return ("lumiTree","tree")

    def otherTreesToKeepWhenSkimming(self) :
        return []
