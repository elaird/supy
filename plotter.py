import ROOT as r
import os,math,string
import utils
##############################
def setupStyle() :
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)
    #r.gStyle.SetOptStat(111111)
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
def adjustPad(pad) :
    r.gPad.SetRightMargin(0.15)
    r.gPad.SetTicky()
    r.gPad.SetTickx()
##############################
class plotter(object) :
    def __init__(self,
                 someOrganizer,
                 psFileName="out.ps",
                 samplesForRatios=("",""),
                 sampleLabelsForRatios=("",""),
                 doLog=True,
                 drawYx=False,
                 doMetFit=False,
                 doColzFor2D=True,
                 blackList=["counts","lumiWarn","nEventsOriginalHisto"]
                 ) :
        for item in ["someOrganizer","psFileName","samplesForRatios","sampleLabelsForRatios",
                     "doLog","drawYx","doMetFit","doColzFor2D","blackList" ] :
            setattr(self,item,eval(item))
        self.plotRatios = self.samplesForRatios!=("","")        
        self.psOptions="Landscape"
        self.canvas=r.TCanvas()

    def plotAll(self) :
        print utils.hyphens
        setupStyle()

        self.printCanvas("[")
        self.printTimeStamp()
    
        self.selectionsSoFar=[]
        for selection in self.someOrganizer.selections :
            self.selectionsSoFar.append(selection.name+" "+selection.title)
            printTable = True if len(self.selectionsSoFar)>0 else False
            for plotName in selection :
                if plotName in self.blackList : continue
                if printTable : self.printSelections()
                self.onePlotFunction(selection[plotName],plotName)
                printTable = False
            #if printTable : printSelections(selectionsSoFar,canvasDict)

        self.printCanvas("]")
        self.makePdf()
        print utils.hyphens

    def printTimeStamp(self) :
        text=r.TText()
        text.SetNDC()
        dateString="file created at ";
        tdt=r.TDatime()
        text.DrawText(0.1,0.3,dateString+tdt.AsString())
        self.printCanvas()
        self.canvas.Clear()

    def printCanvas(self,extra="") :
        self.canvas.Print(self.psFileName+extra,self.psOptions)

    def makePdf(self) :
        pdfFile=self.psFileName.replace(".ps",".pdf")
        os.system("ps2pdf "+self.psFileName+" "+pdfFile)
        os.system("gzip -f "+self.psFileName)
        print "The output file \""+pdfFile+"\" has been written."

    def printSelections(self) :
        if set(self.selectionsSoFar)==set([' ']) :
            return
        self.canvas.cd(0)
        self.canvas.Clear()    

        text = r.TText()
        text.SetNDC()
        text.SetTextFont(102)
        text.SetTextSize(0.5*text.GetTextSize())

        nSelections = len(self.selectionsSoFar)
        for i in  range(nSelections):
            x=0.02
            y=0.98 - 0.3*(i+0.5)/nSelections
            text.DrawTextNDC(x, y, string.ascii_letters[i]+": "+self.selectionsSoFar[i])

        #nPass={}
        #nPassErr={}
        #for iSelection,selection in enumerate(self.someOrganizer.selections) :
        #    for sample,countHisto in zip(self.someOrganizer.samples,selection["counts"]) :
        #        if not countHisto : continue
        #        nPass   [ (sample["name"],iSelection) ]=countHisto.GetBinContent(1)
        #        nPassErr[ (sample["name"],iSelection) ]=countHisto.GetBinError(1)
        #
        #for iSelection in  range(nSelections):
        #    x=0.02            
        #    y=0.5 - 0.3*(iSelection+0.5)/nSelections
        #    nSamples = len(self.someOrganizer.samples)
        #
        #    toPrint=string.ascii_letters[i]+": "
        #    for iSample in range(nSamples) :
        #        sample = self.someOrganizer.samples[iSample]
        #        key = (sample["name"],iSelection)
        #        if key in nPass :
        #            toPrint+=str( nPass[key] )
        #        else :
        #            toPrint+="-"
        #
        #    text.DrawTextNDC(x, y, toPrint)
        
        self.printCanvas()
        self.canvas.Clear()

    def getExtremes(self,histos,dimension) :
        globalMax = -1.0
        globalMin = 1.0e9
        for histo in histos :
            if not histo : continue
            max=histo.GetMaximum()
            if max>globalMax : globalMax=max

            if dimension==1 :
                for iBinX in range(histo.GetNbinsX()+2) :
                    value=histo.GetBinContent(iBinX)
                    if value>0.0 :
                        if value<globalMin : globalMin=value
            if dimension==2 :
                for iBinX in range(histo.GetNbinsX()+2) :
                    for iBinY in range(histo.GetNbinsY()+2) :
                        value=histo.GetBinContent(iBinX,iBinY)
                        if value>0.0 :
                            if value<globalMin : globalMin=value
        return globalMax,globalMin

    def setRanges(self,histos,dimension) :
        globalMax,globalMin = self.getExtremes(histos,dimension)
                    
        for histo in histos :
            if not histo : continue        
            if self.doLog :
                histo.SetMaximum(2.0*globalMax)
                histo.SetMinimum(0.5*globalMin)
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

    def plotEachHisto(self,histos,dimension) :
        stuffToKeep=[]
        x1=0.86
        x2=1.00
        y1=0.60
        y2=0.10
        legend=r.TLegend(x1,y1,x2,y2)

        count = 0
        for sample,histo in zip(self.someOrganizer.samples,histos) :
            if not histo : continue
            if not histo.GetEntries() : continue

            sampleName=sample["name"]
            if "color" in sample :
                histo.SetLineColor(sample["color"])
                histo.SetMarkerColor(sample["color"])
            if "markerStyle" in sample :
                histo.SetMarkerStyle(sample["markerStyle"])
            
            legend.AddEntry(histo,sampleName,"l")

            if dimension==1   : self.plot1D(histo,count,stuffToKeep)
            elif dimension==2 : self.plot2D(histo,count,sampleName,stuffToKeep)
            else :
                print "Skipping histo",histo.GetName(),"with dimension",dimension
                continue
            count+=1
        if dimension==1 : legend.Draw()
        return count,stuffToKeep


    def plotRatio(self,histos,dimension) :
        numSampleName,denomSampleName=self.samplesForRatios
        numLabel,denomLabel=self.sampleLabelsForRatios
    
        numHisto = None
        denomHisto = None
        for sample,histo in zip(self.someOrganizer.samples,histos) :
            if sample["name"]==numSampleName :
                numHisto = histo
            if sample["name"]==denomSampleName :
                denomHisto = histo

        ratio = None
        if numHisto and denomHisto and numHisto.GetEntries() and denomHisto.GetEntries() :
            try:
                ratio=utils.ratioHistogram(numHisto,denomHisto)
                ratio.SetMinimum(0.0)
                ratio.SetMaximum(2.0)
                ratio.GetYaxis().SetTitle(numLabel+"/"+denomLabel)
                self.canvas.cd(2)
                adjustPad(r.gPad)
                r.gPad.SetGridy()
                ratio.SetStats(False)
                ratio.GetXaxis().SetLabelSize(0.0)
                ratio.GetXaxis().SetTickLength(3.5*ratio.GetXaxis().GetTickLength())
                ratio.GetYaxis().SetLabelSize(0.2)
                ratio.GetYaxis().SetNdivisions(502,True)
                ratio.GetXaxis().SetTitleOffset(0.2)
                ratio.GetYaxis().SetTitleSize(0.2)
                ratio.GetYaxis().SetTitleOffset(0.2)
                ratio.SetMarkerStyle(numHisto.GetMarkerStyle())
                ratio.Draw()
            except:
                print "failed to make ratio for plot",plotName
        else :
            self.canvas.cd(2)
        return ratio

    def onePlotFunction(self,histos,plotName) :
        dimension = dimensionOfHisto(histos)
        self.prepareCanvas(histos,dimension)
        self.setRanges(histos,dimension)

        count,stufftoKeep = self.plotEachHisto(histos,dimension)
        if self.plotRatios and dimension==1 :
            ratio = self.plotRatio(histos,dimension)
        self.canvas.cd(0)
        if count>0 :
            self.printCanvas()

    def plot1D(self,histo,count,stuffToKeep) :
        adjustPad(r.gPad)
        if count==0 :
            histo.Draw()
            if self.doLog : r.gPad.SetLogy()
        else :
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

    def plot2D(self,histo,count,sampleName,stuffToKeep) :
    	yx=r.TF1("yx","x",histo.GetXaxis().GetXmin(),histo.GetXaxis().GetXmax())
    	yx.SetLineColor(r.kBlue)
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

        if "deltaHtOverHt_vs_mHtOverHt" in histo.GetName() :
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
##############################
