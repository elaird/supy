import ROOT as r
import os,math,string
import utils
##############################
def setupStyle() :
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)
    r.gStyle.SetOptStat(1111111)
##############################
def combineBinContentAndError(histo,binToContainCombo,binToBeKilled) :
    xflows=histo.GetBinContent(binToBeKilled)
    xflowError=histo.GetBinError(binToBeKilled)
    
    currentContent=histo.GetBinContent(binToContainCombo)
    currentError=histo.GetBinError(binToContainCombo)
    
    histo.SetBinContent(binToBeKilled,0.0)
    histo.SetBinContent(binToContainCombo,currentContent+xflows)
    
    histo.SetBinError(binToBeKilled,0.0)
    histo.SetBinError(binToContainCombo,math.sqrt(xflowError**2+currentError**2))
##############################
def shiftUnderAndOverflows(histo) :
    bins=histo.GetNbinsX()
    entries=histo.GetEntries()
    
    combineBinContentAndError(histo,binToContainCombo=1   ,binToBeKilled=0     )
    combineBinContentAndError(histo,binToContainCombo=bins,binToBeKilled=bins+1)

    histo.SetEntries(entries)
##############################
def dimensionOfHisto(histos) :
    dimensions=[]
    for histo in histos :
        if not histo : continue
        className=histo.ClassName()
        if className == "TProfile" :
            dimensions.append("1")
            continue
        if len(className)<3 or className[0:2]!="TH" : continue
        dimensions.append(className[2])
        
    dimensions=set(dimensions)
    assert len(dimensions)==1,"histograms have different dimensions"
    return int(list(dimensions)[0])
##############################        
def metFit(histo) :
    funcName="func"
    func=r.TF1(funcName,"[0]*x*exp( -(x-[1])**2 / (2.0*[2])**2 )/[2]",0.5,30.0)
    func.SetParameters(1.0,5.0,3.0)
    histo.Fit(funcName,"lrq","sames")
    histo.GetFunction(funcName).SetLineWidth(1)
    histo.GetFunction(funcName).SetLineColor(histo.GetLineColor())
    return func
##############################
def makeAlphaTFunc(alphaTValue) :
    alphaTFunc=r.TF1("alphaTCurve"+str(alphaTValue),
                     "1.0-2.0*("+str(alphaTValue)+")*sqrt(1.0-x*x)",
                     0.0,1.0)
    alphaTFunc.SetLineColor(r.kBlack)
    alphaTFunc.SetLineWidth(1)
    alphaTFunc.SetNpx(300)
    return alphaTFunc
##############################
def adjustPad(pad, anMode) :
    if not anMode : r.gPad.SetRightMargin(0.15)
    r.gPad.SetTicky()
    r.gPad.SetTickx()
##############################
class plotter(object) :
    def __init__(self,
                 someOrganizer,
                 psFileName = "out.ps",
                 samplesForRatios = ("",""),
                 sampleLabelsForRatios = ("",""),
                 showStatBox = True,
                 doLog = True,
                 anMode = False,
                 drawYx = False,
                 doMetFit = False,
                 doColzFor2D = True,
                 compactOutput = False,
                 noSci = False,
                 nLinesMax = 17,
                 shiftUnderOverFlows = True,
                 dontShiftList = ["lumiHisto","xsHisto","nJobsHisto"],
                 blackList = [],
                 whiteList = []
                 ) :
        for item in ["someOrganizer","psFileName","samplesForRatios","sampleLabelsForRatios","doLog",
                     "anMode","drawYx","doMetFit","doColzFor2D","nLinesMax","compactOutput", "noSci",
                     "shiftUnderOverFlows","dontShiftList","whiteList","blackList","showStatBox" ] :
            setattr(self,item,eval(item))

        self.useWhiteList = len(self.whiteList)>0
        self.blackList.append("counts")
        self.plotRatios = self.samplesForRatios!=("","")        
        self.psOptions = "Landscape"
        self.canvas = r.TCanvas("canvas", "canvas", 500, 500) if self.anMode else r.TCanvas()

    def plotAll(self) :
        print utils.hyphens
        setupStyle()

        self.printCanvas("[")

        text2 = self.printTimeStamp()
        text3 = self.printNEventsIn()
        self.printCanvas()
        self.canvas.Clear()

        text1 = self.printCalculables()
        self.printCanvas()
        self.canvas.Clear()
    
        self.selectionsSoFar=[]
        for iSelection,selection in enumerate(self.someOrganizer.selections) :
            if selection.name != "" :
                self.selectionsSoFar.append(selection)
                if (not self.compactOutput and len(selection)>1) or iSelection==len(self.someOrganizer.selections)-1:
                    self.printSelections(self.selectionsSoFar, printAll = self.compactOutput)
            if self.compactOutput : continue
            for plotName in sorted(selection.keys()) :
                if self.useWhiteList and plotName not in self.whiteList : continue
                if plotName in self.blackList : continue
                self.onePlotFunction(selection[plotName],plotName)

        self.printCanvas("]")
        self.makePdf()
        print utils.hyphens


    def printOnePage(self, name, tight = False) :
        fileName = "%s_%s.eps"%(self.psFileName.replace(".ps",""),name)
        self.canvas.Print(fileName)

        if not tight : #make pdf
            os.system("epstopdf "+fileName)
            os.system("rm       "+fileName)
        else : #make pdf with tight bounding box
            epsiFile = fileName.replace(".eps",".epsi")
            os.system("ps2epsi "+fileName+" "+epsiFile)
            os.system("epstopdf "+epsiFile)
            os.system("rm       "+epsiFile)

        print "The output file \"%s\" has been written."%fileName.replace(".eps",".pdf")

    def individualPlots(self, plotSpecs, newSampleNames) :
        print utils.hyphens
        setupStyle()

        def histos(p) :
            for item in ["selName", "selDesc", "plotName"] :
                if item not in p : return
            
            for selection in self.someOrganizer.selections :
                if (selection.name, selection.title) != (p["selName"], p["selDesc"]) : continue
                if p["plotName"] not in selection : continue
                return selection[p["plotName"]]

        for spec in plotSpecs :
            h = histos(spec)
            if "reBinFactor" in spec :
                for histo in h :
                    if histo!=None : histo.Rebin(spec["reBinFactor"])
            if h==None : continue
            stuff = self.onePlotFunction(h, spec["newTitle"] if "newTitle" in spec else None, newSampleNames, individual = True)
            utils.cmsStamp(self.someOrganizer.lumi)
            self.printOnePage(spec["plotName"], tight = self.anMode)

        print utils.hyphens

    def printCalculables(self) :
        text = r.TText()
        text.SetNDC()
        text.SetTextFont(102)
        text.SetTextSize(0.55*text.GetTextSize())

        calcs = filter(lambda x:x[1]!="",list(self.someOrganizer.calculables) )
        if not len(calcs) : return text
        length = max([len(calc[0]) for calc in calcs])
        calcs.sort()
        calcs.insert(0,("",""))
        calcs.insert(0,("Calculables",""))
        nCalcs = len(calcs)
        for i in  range(nCalcs):
            x = 0.02
            y = 0.98 - 0.6*(i+0.5)/self.nLinesMax
            name,title = calcs[i]
            name = name.rjust(length+2)
            text.DrawTextNDC(x, y, "%s   %s"%(name,title) )
        return text
        
    def printTimeStamp(self) :
        text=r.TText()
        text.SetNDC()
        dateString="file created at ";
        tdt=r.TDatime()
        text.DrawText(0.1,0.1,dateString+tdt.AsString())
        return text

    def printNEventsIn(self) :
        text = r.TText()
        text.SetNDC()
        text.SetTextFont(102)
        text.SetTextSize(0.55*text.GetTextSize())

        def getLumi(sample = None, iSource = None) :
            value = 0.0
            if sample!=None :
                if "lumi" in sample :
                    if iSource!=None :
                        value = sample["lumiOfSources"][iSource]
                    else :
                        value = sample["lumi"]                        
                elif "xs" in sample :
                    if iSource!=None :
                        value = sample["nEvents"][iSource]/sample["xsOfSources"][iSource]
                    else :
                        value = sample["nEvents"]/sample["xs"]
            return "%.1f"%value
            
        def loopOneType(mergedSamples = False) :
            sampleNames  = ["sample",""]
            nEventsIn    = ["nEventsIn",""]
            lumis        = ["  lumi (/pb)",""]
            for sample in self.someOrganizer.samples :
                if "sources" not in sample :
                    if mergedSamples : continue
                    sampleNames.append(sample["name"])
                    nEventsIn.append(str(int(sample["nEvents"])))
                    lumis.append(getLumi(sample = sample))
                else :
                    if not mergedSamples : continue
                    localSampleNames = []
                    localNEventsIn = []
                    localLumis = []
                    useThese = True

                    for iSource in range(len(sample["sources"])) :
                        name = sample["sources"][iSource]
                        N    = sample["nEvents"][iSource]
                        if type(N) is list :
                            useThese = False
                            break
                        localSampleNames.append(name)
                        localNEventsIn.append(str(int(N)))
                        localLumis.append(getLumi(sample,iSource))
                    if useThese :
                        sampleNames.extend(localSampleNames)
                        nEventsIn.extend(localNEventsIn)
                        lumis.extend(localLumis)
            return sampleNames,nEventsIn,lumis

        def printOneType(x, sampleNames, nEventsIn, lumis) :
            sLength = max([len(item) for item in sampleNames])
            nLength = max([len(item) for item in nEventsIn]  )
            lLength = max([len(item) for item in lumis]      )
            nSamples = len(sampleNames)
            if nSamples == 1 : return
            for i in range(nSamples) :
                y = 0.9 - 0.55*(i+0.5)/self.nLinesMax
                out = sampleNames[i].ljust(sLength)+nEventsIn[i].rjust(nLength+3)+lumis[i].rjust(lLength+3)
                text.DrawTextNDC(x, y, out)

        printOneType( 0.02, *loopOneType(False) )
        printOneType( 0.52, *loopOneType(True)  )
        return text
    
    def printCanvas(self,extra="") :
        self.canvas.Print(self.psFileName+extra,self.psOptions)

    def makePdf(self) :
        pdfFile=self.psFileName.replace(".ps",".pdf")
        os.system("ps2pdf "+self.psFileName+" "+pdfFile)
        os.system("gzip -f "+self.psFileName)
        print "The output file \""+pdfFile+"\" has been written."

    def printSelections(self,selections, printAll=False) :
        if printAll and len(selections)>self.nLinesMax : self.printSelections(selections[:1-self.nLinesMax],printAll)
        self.canvas.cd(0)
        self.canvas.Clear()
        
        text = r.TText()
        text.SetNDC()
        text.SetTextFont(102)
        text.SetTextSize(0.5*text.GetTextSize())

        nametitle = "{0}:  {1:<%d}   {2}" % (3+max([len(s.name) for s in self.someOrganizer.selections]))
        for i,selection in enumerate(selections[-self.nLinesMax:]) :
            absI = i + (0 if len(selections) <= self.nLinesMax else len(selections)-self.nLinesMax)
            letter = string.ascii_letters[absI]
            x = 0.01
            y = 0.98 - 0.35*(i+0.5+absI/5)/self.nLinesMax
            text.DrawTextNDC(x, y, nametitle.format(letter, selection.name, selection.title ))
            text.DrawTextNDC(x, y-0.5, "%s: %s"%(letter,
                                                  "".join([(utils.roundString(*k, width=8, noSci = self.noSci) if k else "-    ").rjust(11) for k in selection.yields()])))
        text.DrawTextNDC(x, 0.5, "   "+"".join([s["name"][:8].rjust(11) for s in self.someOrganizer.samples]))
        text.DrawTextNDC( 0.8,0.01,"events / %.3f pb^{-1}"% self.someOrganizer.lumi )
        self.printCanvas()
        self.canvas.Clear()

    def getExtremes(self,histos,dimension) :
        globalMax = -1.0
        globalMin = 1.0e9
        for histo in histos :
            if not histo : continue
            if dimension==1 :
                for iBinX in range(histo.GetNbinsX()+2) :
                    content = histo.GetBinContent(iBinX)
                    error   = histo.GetBinError(iBinX)
                    valueUp   = content + error
                    if valueUp>0.0 and valueUp>globalMax : globalMax = valueUp
                    if content>0.0 and content<globalMin : globalMin = content
            if dimension==2 :
                for iBinX in range(histo.GetNbinsX()+2) :
                    for iBinY in range(histo.GetNbinsY()+2) :
                        value = histo.GetBinContent(iBinX,iBinY)
                        if value>0.0 :
                            if value<globalMin : globalMin = value
                            if value>globalMax : globalMax = value                            
        return globalMax,globalMin

    def setRanges(self,histos,dimension) :
        globalMax,globalMin = self.getExtremes(histos,dimension)
                    
        for histo in histos :
            if not histo or histo.GetName()[-len("_dependence"):] == "_dependence" : continue        
            if self.doLog :
                histo.SetMinimum(0.5*globalMin)
                histo.SetMaximum(2.0*globalMax)
            else :
                histo.SetMaximum(1.1*globalMax)
                histo.SetMinimum(0.0)

    def prepareCanvas(self,histos,dimension) :
        self.canvas.cd(0)
        self.canvas.Clear()
        if dimension==1 :
            if self.plotRatios :
                split = 0.2
                self.canvas.Divide(1,2)
                self.canvas.cd(1).SetPad(0.01,split+0.01,0.99,0.99)
                self.canvas.cd(2).SetPad(0.01,0.01,0.99,split)
                #self.canvas.cd(2).SetTopMargin(0.07)#default=0.05
                #self.canvas.cd(2).SetBottomMargin(0.45)
                self.canvas.cd(1)
            else :
                self.canvas.Divide(1,1)
        else :
            mx=1
            my=1
            while mx*my<len(histos) :
                if mx==my : mx+=1
                else :      my+=1
            self.canvas.Divide(mx,my)

    def plotEachHisto(self, histos, dimension, newTitle = None, newSampleNames = {}) :
        stuffToKeep=[]
        legend = r.TLegend(0.86, 0.60, 1.00, 0.10) if not self.anMode else r.TLegend(0.55, 0.55, 0.85, 0.85)
        if self.anMode :
            legend.SetFillStyle(0)
            legend.SetBorderSize(0)
        stuffToKeep.append(legend)

        count = 0
        for sample,histo in zip(self.someOrganizer.samples,histos) :
            if not histo : continue
            if not histo.GetEntries() : continue

            if newTitle!=None : histo.SetTitle(newTitle)
            sampleName = sample["name"]
            if "color" in sample :
                histo.SetLineColor(sample["color"])
                histo.SetMarkerColor(sample["color"])
            if "markerStyle" in sample :
                histo.SetMarkerStyle(sample["markerStyle"])
            
            legend.AddEntry(histo, newSampleNames[sampleName] if sampleName in newSampleNames else sampleName, "l")

            if dimension==1   : self.plot1D(histo,count,stuffToKeep)
            elif dimension==2 : self.plot2D(histo,count,sampleName,stuffToKeep)
            else :
                print "Skipping histo",histo.GetName(),"with dimension",dimension
                continue
            count+=1
        if dimension==1 : legend.Draw()
        return count,stuffToKeep


    def plotRatio(self,histos,dimension) :
        numLabel,denomLabel = self.sampleLabelsForRatios
        numSampleName,denomSampleNames = self.samplesForRatios
        if type(denomSampleNames)!=list: denomSampleNames = [denomSampleNames]
        
        numHisto = histos[self.someOrganizer.indexOfSampleWithName(numSampleName)]
        denomHistos = map(lambda name: histos[self.someOrganizer.indexOfSampleWithName(name)], denomSampleNames)

        ratios = []
        same = ""
        for denomHisto in denomHistos :
            ratio = None
            if numHisto and denomHisto and numHisto.GetEntries() and denomHisto.GetEntries() :
                try:
                    ratio = utils.ratioHistogram(numHisto,denomHisto)
                    ratio.SetMinimum(0.0)
                    ratio.SetMaximum(2.0)
                    ratio.GetYaxis().SetTitle(numLabel+"/"+denomLabel)
                    self.canvas.cd(2)
                    adjustPad(r.gPad, self.anMode)
                    r.gPad.SetGridy()
                    ratio.SetStats(False)
                    ratio.GetXaxis().SetLabelSize(0.0)
                    ratio.GetXaxis().SetTickLength(3.5*ratio.GetXaxis().GetTickLength())
                    ratio.GetYaxis().SetLabelSize(0.2)
                    ratio.GetYaxis().SetNdivisions(502,True)
                    ratio.GetXaxis().SetTitleOffset(0.2)
                    ratio.GetYaxis().SetTitleSize(0.2)
                    ratio.GetYaxis().SetTitleOffset(0.2)
                    if len(denomHistos)==1: ratio.SetMarkerStyle(numHisto.GetMarkerStyle())
                    color = numHisto.GetLineColor() if len(denomHistos)==1 else denomHisto.GetLineColor()
                    ratio.SetLineColor(color)
                    ratio.SetMarkerColor(color)
                    ratio.Draw(same)
                    same = "same"
                except:
                    print "failed to make ratio for plot",numHisto.GetName()
            else :
                self.canvas.cd(2)
            ratios.append(ratio)
        return ratios

    def onePlotFunction(self, histos, newTitle = None, newSampleNames = {}, individual = False) :
        dimension = dimensionOfHisto(histos)
        self.prepareCanvas(histos,dimension)
        self.setRanges(histos,dimension)

        if individual : 
            count,stuffToKeep = self.plotEachHisto(histos, dimension, newTitle = newTitle, newSampleNames = newSampleNames)
        else :
            count,stuffToKeep = self.plotEachHisto(histos, dimension)
            
        if self.plotRatios and dimension==1 :
            ratios = self.plotRatio(histos,dimension)
        self.canvas.cd(0)
        if count>0 and not individual :
            self.printCanvas()
        if individual :
            return stuffToKeep

    def plot1D(self,histo,count,stuffToKeep) :
        if self.shiftUnderOverFlows and histo.GetName() not in self.dontShiftList :
            shiftUnderAndOverflows(histo)

        adjustPad(r.gPad, self.anMode)
        if count==0 :
            histo.SetStats(self.showStatBox)
            histo.GetYaxis().SetTitleOffset(1.25)
            histo.Draw()
            if self.doLog : r.gPad.SetLogy()
        else :
            histo.SetStats(self.showStatBox)
            histo.Draw("same")
            r.gStyle.SetOptFit(0)
            if self.doMetFit and "met" in histo.GetName() :
                r.gStyle.SetOptFit(1111)
                func=metFit(histo)
                stuffToKeep.append(func)
                    
                r.gPad.Update()
                tps=histo.FindObject("stats")
                stuffToKeep.append(tps)
                tps.SetLineColor(histo.GetLineColor())
                tps.SetTextColor(histo.GetLineColor())
                if iHisto==0 :
                    tps.SetX1NDC(0.75)
                    tps.SetX2NDC(0.95)
                    tps.SetY1NDC(0.75)
                    tps.SetY2NDC(0.95)
                else :
                    tps.SetX1NDC(0.75)
                    tps.SetX2NDC(0.95)
                    tps.SetY1NDC(0.50)
                    tps.SetY2NDC(0.70)

        #move stat box
        r.gPad.Update()
        tps=histo.FindObject("stats")
        stuffToKeep.append(tps)
        if tps :
            tps.SetTextColor(histo.GetLineColor())
            tps.SetX1NDC(0.86)
            tps.SetX2NDC(1.00)
            tps.SetY1NDC(0.70)
            tps.SetY2NDC(1.00)

    def lineDraw(self, name, offset, slope, histo, color = r.kBlack, suffix = "") :
        if name not in histo.GetName() : return None
        axis = histo.GetXaxis()
        func = r.TF1(name+suffix,"(%g)+(%g)*x"%(offset,slope),axis.GetXmin(),axis.GetXmax())
        func.SetLineWidth(1)
        func.SetLineColor(color)
        func.Draw("same")
        return func
        
    def plot2D(self,histo,count,sampleName,stuffToKeep) :
    	yx=r.TF1("yx","x",histo.GetXaxis().GetXmin(),histo.GetXaxis().GetXmax())
    	yx.SetLineColor(r.kBlack)
    	yx.SetLineWidth(1)
    	yx.SetNpx(300)
    	
    	self.canvas.cd(count+1)
    	histo.GetYaxis().SetTitleOffset(1.2)
    	oldTitle=histo.GetTitle()
    	newTitle=sampleName if oldTitle=="" else sampleName+"_"+oldTitle
    	histo.SetTitle(newTitle)
    	histo.SetStats(False)
    	histo.GetZaxis().SetTitleOffset(1.3)
    	r.gPad.SetRightMargin(0.15)
    	r.gPad.SetTicky()
        if self.doLog : r.gPad.SetLogz()

        if self.doColzFor2D : histo.Draw("colz")
        else :           histo.Draw()

        #plot-specific stuff
        if "deltaHtOverHt_vs_mHtOverHt" in histo.GetName() \
               or "deltaHtOverHt_vs_metOverHt" in histo.GetName() :
            histo.GetYaxis().SetRangeUser(0.0,0.7)
            funcs=[
                makeAlphaTFunc(0.55),
                makeAlphaTFunc(0.50),
                makeAlphaTFunc(0.45)
                ]
            for func in funcs : func.Draw("same")
            stuffToKeep.extend(funcs)
        elif self.drawYx :
            yx.Draw("same")
            stuffToKeep.append(yx)

        stuffToKeep.append( self.lineDraw(name = "alphaTMet_vs_alphaT",      offset = 0.0,   slope = 1.0,   histo = histo) )
        stuffToKeep.append( self.lineDraw(name = "alphaTMet_zoomvs_alphaT",  offset = 0.0,   slope = 1.0,   histo = histo) )
        stuffToKeep.append( self.lineDraw(name = "mhtVsPhotonPt",            offset = 0.0,   slope = 1.0,   histo = histo) )

        #loose
        stuffToKeep.append( self.lineDraw(name = "jurassicEcalIsolation",    suffix = "loose", offset = 4.2,   slope = 0.006,  histo = histo) )
        stuffToKeep.append( self.lineDraw(name = "towerBasedHcalIsolation",  suffix = "loose", offset = 2.2,   slope = 0.0025, histo = histo) )
        stuffToKeep.append( self.lineDraw(name = "hadronicOverEm",           suffix = "loose", offset = 0.05,  slope = 0.0,    histo = histo) )
        stuffToKeep.append( self.lineDraw(name = "hollowConeTrackIsolation", suffix = "loose", offset = 3.5,   slope = 0.001,  histo = histo) )

        #tight
        stuffToKeep.append( self.lineDraw(name = "jurassicEcalIsolation",    suffix = "tight", offset = 4.2,   slope = 0.006,  histo = histo, color = r.kBlue) )
        stuffToKeep.append( self.lineDraw(name = "towerBasedHcalIsolation",  suffix = "tight", offset = 2.2,   slope = 0.0025, histo = histo, color = r.kBlue) )
        stuffToKeep.append( self.lineDraw(name = "hadronicOverEm",           suffix = "tight", offset = 0.05,  slope = 0.0,    histo = histo, color = r.kBlue) )
        stuffToKeep.append( self.lineDraw(name = "hollowConeTrackIsolation", suffix = "tight", offset = 2.0,   slope = 0.001,  histo = histo, color = r.kBlue) )
        stuffToKeep.append( self.lineDraw(name = "sigmaIetaIetaBarrel",      suffix = "tight", offset = 0.013, slope = 0.0,    histo = histo, color = r.kBlue) )
        stuffToKeep.append( self.lineDraw(name = "sigmaIetaIetaEndcap",      suffix = "tight", offset = 0.030, slope = 0.0,    histo = histo, color = r.kBlue) )
##############################
