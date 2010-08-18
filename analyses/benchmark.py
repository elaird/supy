#!/usr/bin/env python

import os,analysis,utils,steps,calculables,samples

class triggerSpeedTest(analysis.analysis) :
    def outputDirectory(self) :
        return "./"

    def listOfCalculables(self) :
        return []

    
    def listOfSteps(self) :
        touch = [
            #"triggered",
            #"prescaled",
            #"L1triggered",
            #"L1prescaled"
            "ak5JetCorrectedP4Pat",
            "ak5JetJPTCorrectedP4Pat",
            "ak5JetPFCorrectedP4Pat",
            "muonP4Pat",
            "electronP4Pat",
            ]
        return [ steps.touchstuff(touch) ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet]

    def listOfSamples(self) :
        return [samples.specify(name = "JetMET.Run2010A")]
