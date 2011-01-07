#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class scanLook(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def listOfCalculables(self, params) :
        outList  = calculables.zeroArgs()
        return outList
    
    def listOfSteps(self, params) :
        return [
            steps.Print.progressPrinter(),
            #steps.Gen.susyScanPointPrinter(),
            #steps.Gen.ParticleCountFilter({"squark":2}),
            steps.Other.passFilter("scanPlots"),
            steps.Gen.genParticleCountHistogrammer(tanBeta = 3.0),
            #steps.Gen.genParticlePrinter(minPt = -10.0, minStatus = 3),
            #steps.Other.histogrammer("genpthat", 200, 0, 1000, title = ";#hat{p_{T}} (GeV);events / bin"),
            ]
    
    def listOfSampleDictionaries(self) :
        return [samples.mc]

    def listOfSamples(self,params) :
        from samples import specify
        susy = [                                                    
            specify(name = "scan_tanbeta3_skim100",        nFilesMax = -1, color = r.kRed     ),
            ]

        outList = []
        outList+=susy
        
        ##uncomment for short tests
        #for i in range(len(outList)):
        #    o = outList[i]
        #    outList[i] = specify(name = o.name, color = o.color, markerStyle = o.markerStyle, nFilesMax = 1, nEventsMax = 1000)

        return outList

    def conclude(self) :
        ##for skimming only
        #org = organizer.organizer( self.sampleSpecs() )
        #utils.printSkimResults(org)            
            
        #organize
        org=organizer.organizer( self.sampleSpecs() )
        #org.scale()
            
        ##plot
        #pl = plotter.plotter(org,
        #                     psFileName = self.psFileName(),
        #                     doLog = False,
        #                     #compactOutput = True,
        #                     #noSci = True,
        #                     #pegMinimum = 0.1,
        #                     blackList = ["lumiHisto","xsHisto","nJobsHisto"],
        #                     )
        #pl.plotAll()
        
        self.makeScanPlots(org)

    def makeScanPlots(self, org) :
        def keys(selection, nameReqs) :
            out = []
            for key in selection :
                use = True
                for req in nameReqs :
                    if req not in key : use = False
                if use : out.append(key)
            return out

        def matchingHistosSummed(selection, nameReqs) :
            out = None
            for key in keys(selection, nameReqs) :
                h = selection[key][0]
                if out==None : out = h.Clone("matchingOut")
                else : out.Add(h)
            print "%s: %s"%(nameReqs, str(keys(selection, nameReqs)).replace("genParticleCounter_","") )
            return out
            
        def printRatio(selection, canvas = None, psFileName = None,
                       numNameReqs = None, nameDen = None, xsHisto = None,
                       title = None, zTitle = None, zLimits = None, yLimitsForProjX = None ) :
            h1 = matchingHistosSummed(selection, numNameReqs)
            h2 = selection[nameDen][0] if nameDen in selection else None

            if not h1 or not h2 : return None
            h = h1.Clone("out")
            h.Reset()
            h.SetStats(False)
            h.Divide(h1, h2)
            if xsHisto!=None : h.Multiply(xsHisto)
            if title!=None : h.SetTitle(title)
            if zTitle!=None : h.GetZaxis().SetTitle(zTitle)
            if zLimits!=None : h.GetZaxis().SetRangeUser(*zLimits)

            if yLimitsForProjX!=None :
                g = h.ProjectionX("outProjX", h.GetYaxis().FindBin(yLimitsForProjX[0]), h.GetYaxis().FindBin(yLimitsForProjX[1]) )
                if zLimits!=None : g.GetYaxis().SetRangeUser(*zLimits)
                g.GetYaxis().SetTitle(h.GetZaxis().GetTitle())
                g.SetTitle(g.GetTitle()+"#semicolon   m_{1/2} in [%g,%g] GeV"%yLimitsForProjX)
                g.SetStats(False)
                g.Draw()
            else :
                h.Draw("colz")

            canvas.Print(psFileName)
            if yLimitsForProjX!=None :
                g.Delete()
            return h
            
        def loopHistos(org, canvas, psFileName) :
            for selection in org.selections :
                if selection.name != "passFilter" or selection.title != "scanPlots" : continue

                yLimitsForProjX = None
                #yLimitsForProjX = (100.0, 100.0)
                #yLimitsForProjX = (200.0, 200.0)


                xsHisto = printRatio(selection, canvas = canvas, psFileName = psFileName,
                                     numNameReqs = ["genParticleCounterXS"], nameDen = "genParticleCounternEvents",
                                     title = "XS", zTitle = "#sigma (pb)", yLimitsForProjX = yLimitsForProjX
                                     )

                finalOnly = True
                initialOnly = False

                if finalOnly :
                    #fractions
                    printRatio(selection, canvas = canvas, psFileName = psFileName,
                               numNameReqs = ["squark=2"], nameDen = "genParticleCounternEvents",
                               title = "squark-squark", zTitle = "fraction", zLimits = (0.0, 1.0) )
                    printRatio(selection, canvas = canvas, psFileName = psFileName,
                               numNameReqs = ["gluino=2"], nameDen = "genParticleCounternEvents",
                               title = "gluino-gluino", zTitle = "fraction", zLimits = (0.0, 1.0) )
                    printRatio(selection, canvas = canvas, psFileName = psFileName,
                               numNameReqs = ["gluino=1", "squark=1"], nameDen = "genParticleCounternEvents",
                               title = "squark-gluino", zTitle = "fraction", zLimits = (0.0, 1.0) )
                    printRatio(selection, canvas = canvas, psFileName = psFileName,
                               numNameReqs = ["otherSusy=1", "squark=1"], nameDen = "genParticleCounternEvents",
                               title = "squark-other", zTitle = "fraction", zLimits = (0.0, 1.0) )
                    printRatio(selection, canvas = canvas, psFileName = psFileName,
                               numNameReqs = ["gluino=0", "squark=0"], nameDen = "genParticleCounternEvents",
                               title = "no squark, no qluino", zTitle = "fraction", zLimits = (0.0, 1.0) )
                    #cross sections
                    printRatio(selection, canvas = canvas, psFileName = psFileName,
                               numNameReqs = ["squark=2"], nameDen = "genParticleCounternEvents",
                               title = "squark-squark", zTitle = "#sigma (pb)", xsHisto = xsHisto )
                    printRatio(selection, canvas = canvas, psFileName = psFileName,
                               numNameReqs = ["gluino=2"], nameDen = "genParticleCounternEvents",
                               title = "gluino-gluino", zTitle = "#sigma (pb)", xsHisto = xsHisto )
                    printRatio(selection, canvas = canvas, psFileName = psFileName,
                               numNameReqs = ["gluino=1", "squark=1"], nameDen = "genParticleCounternEvents",
                               title = "squark-gluino", zTitle = "#sigma (pb)", xsHisto = xsHisto )
                    printRatio(selection, canvas = canvas, psFileName = psFileName,
                               numNameReqs = ["otherSusy=1", "squark=1"], nameDen = "genParticleCounternEvents",
                               title = "squark-other", zTitle = "#sigma (pb)", xsHisto = xsHisto )
                    printRatio(selection, canvas = canvas, psFileName = psFileName,
                               numNameReqs = ["gluino=0", "squark=0"], nameDen = "genParticleCounternEvents",
                               title = "no squark, no qluino", zTitle = "#sigma (pb)", xsHisto = xsHisto)

                if initialOnly :
                    #fractions
                    printRatio(selection, canvas = canvas, psFileName = psFileName,
                               numNameReqs = ["_quark=2"], nameDen = "genParticleCounternEvents",
                               title = "initial quark-quark", zTitle = "fraction", zLimits = (0.0, 1.0),
                               yLimitsForProjX = yLimitsForProjX
                               )
                    printRatio(selection, canvas = canvas, psFileName = psFileName,
                               numNameReqs = ["gluon=2"], nameDen = "genParticleCounternEvents",
                               title = "intial gluon-gluon", zTitle = "fraction", zLimits = (0.0, 1.0),
                               yLimitsForProjX = yLimitsForProjX
                               )
                    printRatio(selection, canvas = canvas, psFileName = psFileName,
                               numNameReqs = ["gluon=1", "_quark=1"], nameDen = "genParticleCounternEvents",
                               title = "initial quark-gluon", zTitle = "fraction", zLimits = (0.0, 1.0),
                               yLimitsForProjX = yLimitsForProjX
                               )
                           
        keep = []
        canvas = r.TCanvas()
        canvas.SetRightMargin(0.2)
        canvas.SetTickx()
        canvas.SetTicky()
        psFileName = "scan.ps"
        canvas.Print(psFileName+"[","Lanscape")

        loopHistos(org, canvas, psFileName)

        canvas.Print(psFileName+"]","Lanscape")                
        os.system("ps2pdf "+psFileName)
        os.remove(psFileName)

