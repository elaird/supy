from core.analysis import analysis
import os,steps,calculables,samples,samples.JetMET

class benchmark(analysis) :

    def listOfSampleDictionaries(self) :  return [samples.JetMET.jetmet]

    def listOfSamples(self,_) :  return samples.specify(names = "JetMETTau.Run2010A-Nov4ReReco_v1.RECO.Burt", nFilesMax = 10)

    def listOfCalculables(self,_) :  return []
    
    def listOfSteps(self,_) :
        import steps.Other
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
        return [ steps.Other.touchstuff(touch) ]


