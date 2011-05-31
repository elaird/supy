import ROOT as r
import os,math,string,collections
import utils,configuration
##############################
def setupStyle() :
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)
    r.gStyle.SetOptStat(1111111)
##############################
def setupTdrStyle() :
    r.gROOT.ProcessLine(".L tdrstyle.C")
    r.setTDRStyle()
    #tweaks
    r.tdrStyle.SetPadRightMargin(0.06)
    r.tdrStyle.SetErrorX(r.TStyle().GetErrorX())
##############################
def combineBinContentAndError(histo, binToContainCombo, binToBeKilled) :
    xflows     = histo.GetBinContent(binToBeKilled)
    xflowError = histo.GetBinError(binToBeKilled)

    if xflows==0.0 : return #ugly

    currentContent = histo.GetBinContent(binToContainCombo)
    currentError   = histo.GetBinError(binToContainCombo)
    
    histo.SetBinContent(binToBeKilled, 0.0)
    histo.SetBinContent(binToContainCombo, currentContent+xflows)
    
    histo.SetBinError(binToBeKilled, 0.0)
    histo.SetBinError(binToContainCombo, math.sqrt(xflowError**2+currentError**2))
##############################
def shiftUnderAndOverflows(dimension, histos, dontShiftList = []) :
    if dimension!=1 : return
    for histo in histos:
        if not histo : continue
        if histo.GetName() in dontShiftList : continue
        bins = histo.GetNbinsX()
        entries = histo.GetEntries()
        combineBinContentAndError(histo, binToContainCombo = 1   , binToBeKilled = 0     )
        combineBinContentAndError(histo, binToContainCombo = bins, binToBeKilled = bins+1)
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
    if not anMode :
        r.gPad.SetRightMargin(0.15)
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
                 pegMinimum = None,
                 anMode = False,
                 drawYx = False,
                 doMetFit = False,
                 doColzFor2D = True,
                 compactOutput = False,
                 noSci = False,
                 showErrorsOnDataYields = False,
                 linYAfter = None,
                 nLinesMax = 17,
                 nColumnsMax = 67,
                 pageNumbers = True,
                 detailedCalculables = False,
                 shiftUnderOverFlows = True,
                 dontShiftList = ["lumiHisto","xsHisto","nJobsHisto"],
                 blackList = [],
                 whiteList = []
                 ) :
        for item in ["someOrganizer","psFileName","samplesForRatios","sampleLabelsForRatios","doLog","linYAfter",
                     "pegMinimum", "anMode","drawYx","doMetFit","doColzFor2D","nLinesMax","nColumnsMax","compactOutput","pageNumbers",
                     "noSci", "showErrorsOnDataYields", "shiftUnderOverFlows","dontShiftList","whiteList","blackList","showStatBox","detailedCalculables"] :
            setattr(self,item,eval(item))

        self.useWhiteList = len(self.whiteList)>0
        self.blackList.append("counts")
        self.plotRatios = self.samplesForRatios!=("","")        
        self.psOptions = "Landscape"
        self.canvas = r.TCanvas("canvas", "canvas", 500, 500) if self.anMode else r.TCanvas()
        self.pageNumber = -1
        
    def plotAll(self) :
        print utils.hyphens
        setupStyle()

        self.printCanvas("[")

        text1 = self.printTimeStamp()
        text2 = self.printNEventsIn()
        self.printCanvas()
        self.canvas.Clear()

        if self.detailedCalculables :
            lines = self.someOrganizer.formattedCalculablesGraph()
            mark = ('','','')
            indices = [0,0]
            for iLine,line in enumerate(lines) :
                if line!=mark : continue
                elif iLine - indices[-2] < 50 : indices[-1] = iLine
                else : indices.append(iLine)
            for start,finish in zip(indices[:-1],indices[1:]):
                self.printCalculablesDetailed(filter(None,utils.splitList(lines[start:finish],mark)))
                self.printCanvas()
                self.canvas.Clear()
        else :
            text3 = self.printCalculables(selectImperfect = False)
            self.printCanvas()
            self.canvas.Clear()
            
            text4 = self.printCalculables(selectImperfect = True)
            self.printCanvas()
            self.canvas.Clear()

        self.selectionsSoFar=[]
        for iSelection,selection in enumerate(self.someOrganizer.selections) :
            if selection.name != "" :
                self.selectionsSoFar.append(selection)
                if (not self.compactOutput and len(selection)>1) or iSelection==len(self.someOrganizer.selections)-1:
                    self.printSelections(self.selectionsSoFar, printAll = self.compactOutput)
            if (selection.name, selection.title)==self.linYAfter : self.doLog = False
            if self.compactOutput and not self.whiteList : continue
            for plotName in sorted(selection.keys()) :
                if self.useWhiteList and plotName not in self.whiteList : continue
                if plotName in self.blackList : continue
                self.onePlotFunction(selection[plotName])

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

    def individualPlots(self, plotSpecs, newSampleNames, preliminary = True) :
        def goods(spec) :
            for item in ["selName", "selDesc", "plotName"] :
                if item not in spec : return
            
            for selection in self.someOrganizer.selections :
                if (selection.name, selection.title) != (spec["selName"], spec["selDesc"]) : continue
                if spec["plotName"] not in selection : continue
                histos = selection[spec["plotName"]]
                break

            if "sampleWhiteList" not in spec :
                return histos,None
            else :
                return histos,[not (sample["name"] in spec["sampleWhiteList"]) for sample in self.someOrganizer.samples]

        def onlyDumpToFile(histos, spec) :
            if "onlyDumpToFile" in spec and spec["onlyDumpToFile"] :
                rootFileName = self.psFileName.replace(".ps","_%s.root"%spec["plotName"])
                f = r.TFile(rootFileName, "RECREATE")
                for h in histos :
                    h.Write()
                f.Close()
                print "The output file \"%s\" has been written."%rootFileName
                return True
            return False

        def rebin(h, spec) :
            if "reBinFactor" in spec :
                for histo in h :
                    if histo!=None : histo.Rebin(spec["reBinFactor"])
                
        def setTitles(h, spec) :
            if "newTitle" in spec :
                for histo in h :
                    histo.SetTitle(spec["newTitle"])

        def stylize(h) :
            for histo in h :
                histo.UseCurrentStyle()

        print utils.hyphens
        setupTdrStyle()

        for spec in plotSpecs :
            histos,ignoreHistos = goods(spec)
            if histos==None : continue
            
            if onlyDumpToFile(histos, spec) : continue
            rebin(histos, spec)
            setTitles(histos, spec)
            stylize(histos)
            
            stuff = self.onePlotFunction(histos, ignoreHistos, newSampleNames, individual = True)
            utils.cmsStamp(lumi = self.someOrganizer.lumi, preliminary = preliminary)
            self.printOnePage(spec["plotName"], tight = self.anMode)
        print utils.hyphens

    def printCalculablesDetailed(self, blocks) :
        text = r.TText()
        text.SetNDC()
        text.SetTextFont(102)
        text.SetTextSize(0.35*text.GetTextSize())
        
        iLine = 0
        for block in blocks :
            iLine += 1
            maxLenName = max([len(line[1]) for line in block])
            for line in block :
                x=0.00
                y=1.0 - 0.35*(iLine+0.5)/self.nLinesMax
                text.DrawTextNDC(x,y, "%s%s  %s"%(line[0],line[1].ljust(maxLenName),line[2]))
                iLine += 1

    def printCalculables(self, selectImperfect) :
        text = r.TText()
        text.SetNDC()
        text.SetTextFont(102)
        text.SetTextSize(0.45*text.GetTextSize())

        allCalcs = sum([s.keys() for s in self.someOrganizer.calculables], [])

        def genuineCalcs() :
            '''the list of genuine calculables which have a moreName'''
            return [(c[0],c[1],"") for c in filter(lambda c: c[1] and c[2]=="calc", set(allCalcs))]

        def imperfectCalcs() :
            def type1(c) : return c[2]=="fake"
            def type2(c) : return c[2]=="calc" and not (bool(counts["leaf"][c[0]])^bool(counts["calc"][c[0]]))
            def statString(counts, name) :
                return (3*"%4d  ")%tuple([counts[item][name] for item in ["leaf","calc","fake"]])
            def histogram(item) :
                itemCalcs = [c[0] for c in filter(lambda c: c[2]==item, allCalcs)]
                return collections.defaultdict(int, [(c,itemCalcs.count(c)) for c in set(itemCalcs)])
            counts = dict([(item,histogram(item)) for item in ["leaf","calc","fake","absent"]])

            return [ ( c[0],
                       c[1].replace(configuration.fakeString(),""),
                       statString(counts,c[0])
                       ) for c in filter(lambda c: type1(c) or type2(c), set(allCalcs))]
                
        calcs = sorted( imperfectCalcs() if selectImperfect else genuineCalcs() )
        calcs.insert(0, ("","",""))
        calcs.insert(0, ("Calculables",)+(("(imperfect)","leaf  calc  fake") if selectImperfect else ("", "") ))
        length0 = max([len(calc[0]) for calc in calcs])
        length1 = max([len(calc[1]) for calc in calcs])
        if len(calcs)==2 : calcs.append( ("","NONE","") )
        for i,calc in enumerate(calcs) :
            x = 0.02
            y = 0.98 - 0.4*(i+0.5)/self.nLinesMax
            text.DrawTextNDC(x, y, "%s   %s   %s"%(calc[0].rjust(length0+2), calc[1].ljust(length1+2), calc[2]) )
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
        text.SetTextSize(0.38*text.GetTextSize())
        defSize = text.GetTextSize()
        
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

            total = sLength + nLength + lLength + 15
            if total>self.nColumnsMax : text.SetTextSize(defSize*self.nColumnsMax/(total+0.0))
                
            nSamples = len(sampleNames)
            if nSamples == 1 : return
            for i in range(nSamples) :
                y = 0.9 - 0.55*(i+0.5)/self.nLinesMax
                out = sampleNames[i].ljust(sLength)+nEventsIn[i].rjust(nLength+3)+lumis[i].rjust(lLength+3)
                text.DrawTextNDC(x, y, out)

        printOneType( 0.02, *loopOneType(False) )
        printOneType( 0.52, *loopOneType(True)  )
        return text
    
    def printCanvas(self, extra = "") :
        self.pageNumber += 1
        if self.pageNumbers and self.pageNumber>1 :
            text = r.TText()
            text.SetNDC()
            text.SetTextFont(102)
            text.SetTextSize(0.45*text.GetTextSize())
            text.SetTextAlign(33)
            text.DrawText(0.95, 0.03, "page %3d"%self.pageNumber)
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
        text.SetTextSize(0.45*text.GetTextSize())

        pageWidth = 111
        colWidth = min(25, pageWidth/len(self.someOrganizer.samples))
        space = 1

        nametitle = "{0}:  {1:<%d}   {2}" % (3+max([len(s.name) for s in self.someOrganizer.selections]))
        for i,selection in enumerate(selections[-self.nLinesMax:]) :
            absI = i + (0 if len(selections) <= self.nLinesMax else len(selections)-self.nLinesMax)
            letter = string.ascii_letters[absI]
            x = 0.01
            y = 0.98 - 0.33*(i+0.5+absI/5)/self.nLinesMax
            text.DrawTextNDC(x, y, nametitle.format(letter, selection.name, selection.title ))

            nums = []
            for iYield,k in enumerate(selection.yields()) :
                special = "lumi" in self.someOrganizer.samples[iYield] and not self.showErrorsOnDataYields
                s = utils.roundString(*k, width=(colWidth-space), noSci = self.noSci or special, noErr = special) if k else "-    "
                nums.append(s.rjust(colWidth))
            text.DrawTextNDC(x, y-0.49, "%s: %s"%(letter, "".join(nums)))

        text.DrawTextNDC(x, 0.5, "   "+"".join([s["name"][:(colWidth-space)].rjust(colWidth) for s in self.someOrganizer.samples]))
        text.SetTextAlign(13)
        text.DrawTextNDC(0.05, 0.03, "events / %.3f pb^{-1}"% self.someOrganizer.lumi )
        self.printCanvas()
        self.canvas.Clear()

    def getExtremes(self, dimension, histos, ignoreHistos) :
        globalMax = -1.0
        globalMin = 1.0e9

        for histo,ignore in zip(histos,ignoreHistos) :
            if ignore or (not histo) : continue
            if dimension==1 :
                for iBinX in range(histo.GetNbinsX()+2) :
                    content = histo.GetBinContent(iBinX)
                    error   = histo.GetBinError(iBinX)
                    valueUp   = content + error
                    if valueUp>0.0 and valueUp>globalMax : globalMax = valueUp
                    if self.doLog and content>0 : globalMin = min(globalMin,content)
                    if not self.doLog : globalMin = min(globalMin,content-error)
            if dimension==2 :
                for iBinX in range(histo.GetNbinsX()+2) :
                    for iBinY in range(histo.GetNbinsY()+2) :
                        value = histo.GetBinContent(iBinX,iBinY)
                        if value>0.0 :
                            if value<globalMin : globalMin = value
                            if value>globalMax : globalMax = value                            
        return globalMin,globalMax

    def setRanges(self, histos, globalMin, globalMax) :
        for histo in histos :
            if not histo or histo.GetName()[-len("_dependence"):] == "_dependence" : continue        
            if self.doLog :
                histo.SetMinimum(0.5*globalMin) if self.pegMinimum==None else histo.SetMinimum(self.pegMinimum)
                histo.SetMaximum(2.0*globalMax)
            else :
                histo.SetMaximum(1.1*globalMax)
                histo.SetMinimum(1.1*globalMin if globalMin<0 else 0)

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
                if self.anMode : self.canvas.UseCurrentStyle()
        else :
            mx=1
            my=1
            while mx*my<len(histos) :
                if mx==my : mx+=1
                else :      my+=1
            self.canvas.Divide(mx,my)

    def plotEachHisto(self, dimension, histos, ignoreHistos, newSampleNames = None) :
        stuffToKeep = []
        legend = r.TLegend(0.86, 0.60, 1.00, 0.10) if not self.anMode else r.TLegend(0.55, 0.55, 0.85, 0.85)
        stuffToKeep.append(legend)
        if self.anMode :
            legend.SetFillStyle(0)
            legend.SetBorderSize(0)

        count = 0
        for sample,histo,ignore in zip(self.someOrganizer.samples, histos, ignoreHistos) :
            if ignore or (not histo) or (not histo.GetEntries()) : continue

            sampleName = sample["name"]
            if "color" in sample :
                histo.SetLineColor(sample["color"])
                histo.SetMarkerColor(sample["color"])
            if "markerStyle" in sample :
                histo.SetMarkerStyle(sample["markerStyle"])
            if "lineStyle" in sample :
                histo.SetLineStyle(sample["lineStyle"])
            if "lineWidth" in sample :
                histo.SetLineWidth(sample["lineWidth"])

            legend.AddEntry(histo, newSampleNames[sampleName] if (newSampleNames!=None and sampleName in newSampleNames) else sampleName, "lp")
            if dimension==1   : self.plot1D(histo, count, sample["goptions"] if ("goptions" in sample) else "", stuffToKeep)
            elif dimension==2 : self.plot2D(histo, count, sampleName, stuffToKeep)
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

    def onePlotFunction(self, histos, ignoreHistos = None, newSampleNames = None, individual = False) :
        dimension = dimensionOfHisto(histos)
        self.prepareCanvas(histos, dimension)

        if ignoreHistos==None : ignoreHistos = [False]*len(histos)
        if self.shiftUnderOverFlows : shiftUnderAndOverflows(dimension, histos, self.dontShiftList)
        self.setRanges(histos, *self.getExtremes(dimension, histos, ignoreHistos))

        if individual : 
            count,stuffToKeep = self.plotEachHisto(dimension, histos, ignoreHistos, newSampleNames = newSampleNames)
        else :
            count,stuffToKeep = self.plotEachHisto(dimension, histos, ignoreHistos)
            
        if self.plotRatios and dimension==1 :
            ratios = self.plotRatio(histos,dimension)
        self.canvas.cd(0)
        if count>0 and not individual :
            self.printCanvas()
        if individual :
            return stuffToKeep

    def plot1D(self, histo, count, goptions, stuffToKeep) :
        adjustPad(r.gPad, self.anMode)
        if count==0 :
            histo.SetStats(self.showStatBox)
            if not self.anMode : histo.GetYaxis().SetTitleOffset(1.25)
            histo.Draw(goptions)
            if self.doLog : r.gPad.SetLogy()
        else :
            histo.SetStats(self.showStatBox)
            histo.Draw(goptions+"same")
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
