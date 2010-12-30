#!/usr/bin/env python

import os
import analysis,utils,calculables,steps,samples,organizer,plotter
import ROOT as r

class example(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/tmp/%s/"%os.environ["USER"]

    def parameters(self) :
        return {"etRatherThanPt" : [False],
                "jets" : ("ak5JetPF","Pat"),
                "minJetPt" : 10.0,
                }

    def listOfSteps(self,config) :
        jets = config["jets"]
        minJetPt = config["minJetPt"]
        
        outList=[
            steps.Print.progressPrinter(),
            steps.Trigger.techBitFilter([0],True),
            steps.Trigger.physicsDeclared(),
            steps.Other.vertexRequirementFilter(),
            steps.Other.monsterEventFilter(),
            
            steps.Jet.jetPtSelector(jets,minJetPt,0),#leading corrected jet
            steps.Jet.jetPtSelector(jets,minJetPt,1),#next corrected jet
            #steps.Jet.jetPtVetoer( jets,minJetPt,2),#next corrected jet
            steps.Other.multiplicityFilter("%sIndicesOther%s"%jets, nMax = 0),
            steps.Other.multiplicityFilter("%sIndices%s"%jets, nMin = 2),
            
            steps.Jet.singleJetHistogrammer(jets,1), 
            steps.Jet.cleanJetHtMhtHistogrammer(jets, config["etRatherThanPt"]),
            #steps.Other.variableGreaterFilter(25.0,jets[0]+"SumPt"+jets[1]),
            
            steps.Jet.alphaHistogrammer(jets, etRatherThanPt = config["etRatherThanPt"]),
            #steps.Other.skimmer(),
            ]
        return outList
    
    def listOfCalculables(self,config) :
        jets = config["jets"]
        minJetPt = config["minJetPt"]
        listOfCalculables = calculables.zeroArgs()
        listOfCalculables += calculables.fromCollections(calculables.jet,[jets])
        listOfCalculables += [
            calculables.jet.Indices( jets, ptMin = minJetPt, etaMax = 3.0, flagName = "JetIDloose"),
            calculables.jet.SumP4( jets),
            calculables.jet.DeltaPhiStar( jets ),
            calculables.jet.AlphaT        ( jets, config["etRatherThanPt"]),
            calculables.jet.DeltaPseudoJet( jets, config["etRatherThanPt"]),
            ]
        return listOfCalculables

    def listOfSampleDictionaries(self) :
        exampleDict = samples.SampleHolder()
        exampleDict.add("Example_Skimmed_900_GeV_Data", '["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_Data.root"]', lumi = 1.0e-5 ) #/pb
        exampleDict.add("Example_Skimmed_900_GeV_MC", '["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_MC.root"]',       xs = 1.0e3 ) #pb
        return [exampleDict]

    def listOfSamples(self,config) :
        return [samples.specify(name = "Example_Skimmed_900_GeV_Data", color = r.kBlack, markerStyle = 20),
                samples.specify(name = "Example_Skimmed_900_GeV_MC", color = r.kRed)
                ]

    def conclude(self) :
        #make a pdf file with plots from the histograms created above
        org = organizer.organizer( self.sampleSpecs() )
        org.scale()
        plotter.plotter( org,
                         psFileName = self.psFileName(),
                         samplesForRatios = ("Example_Skimmed_900_GeV_Data","Example_Skimmed_900_GeV_MC"),
                         sampleLabelsForRatios = ("data","sim"),
                         ).plotAll()
