#!/usr/bin/env python

import os
import analysis,utils,calculables,calculablesJet,steps,plotter
import ROOT as r

def makeSteps() :
    jets=("ak5JetPF","Pat")
    minJetPt=10.0
    
    outSteps=[
        steps.progressPrinter(),
        steps.techBitFilter([0],True),
        steps.physicsDeclared(),
        steps.vertexRequirementFilter(),
        steps.monsterEventFilter(),

        steps.jetPtSelector(jets,minJetPt,0),#leading corrected jet
        steps.jetPtSelector(jets,minJetPt,1),#next corrected jet
        #steps.jetPtVetoer( jets,minJetPt,2),#next corrected jet
        steps.minNCleanJetEventFilter(jets,2),
        steps.maxNOtherJetEventFilter(jets,0),
        
        steps.cleanJetPtHistogrammer(jets),
        steps.cleanJetHtMhtHistogrammer(jets),
        #steps.variableGreaterFilter(25.0,jets[0]+"SumPt"+jets[1]),
        
        steps.alphaHistogrammer(jets),
        #steps.skimmer("/tmp/%s/"%os.environ["USER"]),
        ]
    return outSteps

def makeCalculables() :
    jetTypes = [("ak5Jet","Pat"),("ak5JetJPT","Pat"),("ak5JetPF","Pat")]
    listOfCalculables = calculables.zeroArgs()
    listOfCalculables += [ calculablesJet.indices( collection = jetType, ptMin = 20.0, etaMax = 3.0, flagName = "JetIDloose") for jetType in jetTypes]
    listOfCalculables += [ calculablesJet.PFJetIDloose( collection = jetTypes[2],
                                                        fNeutralEmMax = 1.0, fChargedEmMax = 1.0, fNeutralHadMax = 1.0, fChargedHadMin = 0.0, nChargedMin = 0) ]
    listOfCalculables += [ calculablesJet.sumPt(          collection = jetType) for jetType in jetTypes ]
    listOfCalculables += [ calculablesJet.sumP4(          collection = jetType) for jetType in jetTypes ]
    listOfCalculables += [ calculablesJet.deltaPseudoJet( collection = jetType) for jetType in jetTypes ]
    listOfCalculables += [ calculablesJet.alphaT(         collection = jetType) for jetType in jetTypes ]
    listOfCalculables += [ calculablesJet.diJetAlpha(     collection = jetType) for jetType in jetTypes ]
    return listOfCalculables

a=analysis.analysis(name="example",
                    outputDir = "/tmp/%s/"%os.environ["USER"],
                    listOfSteps=makeSteps(),
                    listOfCalculables=makeCalculables(),
                    )

a.addSample(sampleName="Example_Skimmed_900_GeV_Data", nEvents = -1, lumi = 1.0e-5, #/pb
            listOfFileNames=["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_Data.root"] )

a.addSample(sampleName="Example_Skimmed_900_GeV_MC", nEvents = -1, xs = 1.0e8, #pb
            listOfFileNames=["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_MC.root"] )


#loop over events and make root files containing histograms
a.loop(profile=False,   #profile the code
       nCores=1,        #use multiple cores to process input files in parallel
       )

#make a pdf file with plots from the histograms created above
colorDict={}
colorDict["Example_Skimmed_900_GeV_Data"]=r.kBlack
colorDict["Example_Skimmed_900_GeV_MC"]=r.kRed

markerStyleDict={}
markerStyleDict["Example_Skimmed_900_GeV_Data"]=20

plotter.plotAll(a,colorDict,markerStyleDict)
