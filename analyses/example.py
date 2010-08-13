#!/usr/bin/env python

import os
import analysis,utils,calculables,steps,samples,plotter
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
    listOfCalculables += calculables.fromJetCollections(jetTypes)
    listOfCalculables += [ calculables.jetIndices( collection = jetType, ptMin = 20.0, etaMax = 3.0, flagName = "JetIDloose") for jetType in jetTypes]
    listOfCalculables += [ calculables.jetIndicesOther( collection = jetType, ptMin = 20.0 ) for jetType in jetTypes]
    listOfCalculables += [ calculables.PFJetIDloose( collection = jetTypes[2],
                                                     fNeutralEmMax = 1.0, fChargedEmMax = 1.0, fNeutralHadMax = 1.0, fChargedHadMin = 0.0, nChargedMin = 0) ]
    return listOfCalculables

def makeSampleDict() :
    exampleDict = samples.SampleHolder()
    exampleDict.add("Example_Skimmed_900_GeV_Data", '["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_Data.root"]', lumi = 1.0e-5 ) #/pb
    exampleDict.add("Example_Skimmed_900_GeV_MC", '["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_MC.root"]', xs = 1.0e8 ) #pb
    return exampleDict

def makeSamples() :    
    return [samples.specify(name = "Example_Skimmed_900_GeV_Data", color = r.kBlack, markerStyle = 20),
            samples.specify(name = "Example_Skimmed_900_GeV_MC", color = r.kRed)
            ]

a=analysis.analysis(name="example",
                    outputDir = "/tmp/%s/"%os.environ["USER"],
                    listOfSteps = makeSteps(),
                    listOfCalculables = makeCalculables(),
                    listOfSamples = makeSamples(),
                    listOfSampleDictionaries = [makeSampleDict()]
                    )

#loop over events and make root files containing histograms
a.loop( nCores = 1 ) #use multiple cores to process input files in parallel

#make a pdf file with plots from the histograms created above
plotter.plotAll(listOfPlotContainers = a.organizeHistograms(),
                psFileName = a.outputDir+"/"+a.name+".ps",
                samplesForRatios = ("Example_Skimmed_900_GeV_Data","Example_Skimmed_900_GeV_MC"),
                sampleLabelsForRatios = ("data","sim"),
                )

