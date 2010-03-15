import ROOT as r
##############################
doLog1D=True
doLog2D=True
doMetFit=False
doScaleByXs=True
doColzFor2D=True
xsNorm=100 #pb^-1
##############################
def setupStyle() :
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)
    #r.gStyle.SetOptStat(111111)
##############################
def getNamesAndDimensions(outputDir,sample) :
    f0=r.TFile(outputDir+"/"+sample.outputPlotFileName)
    keys=f0.GetListOfKeys()
    names=[]
    dims=[]
    for key in keys :
        name=key.GetName()
        names.append(name)
        className=object=f0.Get(name).ClassName()
        if (className[0:2]=="TH") :
            dims.append(int(className[2]))
        else :
            dims.append(0)
    return [names,dims]
##############################
def shiftOverflows(histo) :
    bins=histo.GetNbinsX()
    entries=histo.GetEntries()
    overflows=histo.GetBinContent(bins+1)
    lastBinContent=histo.GetBinContent(bins)
    histo.SetBinContent(bins+1,0.0)
    histo.SetBinContent(bins,lastBinContent+overflows)
    histo.SetEntries(entries)
##############################
def scaleHistos(dimension,histoList,xsList,nEventsList) :
    max=0.0
    if (len(histoList)<1) : return max
    
    for iHisto in range(len(histoList)) :
        histo=histoList[iHisto]
        histo.Scale(xsNorm*xsList[iHisto]/nEventsList[iHisto])

        if (dimension==1) :
            newTitle=histo.GetYaxis().GetTitle()+" / "+str(xsNorm)+" pb^{-1}"
            histo.GetYaxis().SetTitle(newTitle)
        if (dimension==2) :
            newTitle=histo.GetZaxis().GetTitle()+" / "+str(xsNorm)+" pb^{-1}"
            histo.GetZaxis().SetTitle(newTitle)

        hMax=histo.GetMaximum()
        if (hMax>max) : max=hMax
    return max
##############################
def scale1DHistosByArea(histoList,xsList,nEventsList) :
    max=0.0
    if (len(histoList)<1) : return max
    
    integral0=histoList[0].Integral(0,histoList[0].GetNbinsX()+1)
    for iHisto in range(len(histoList)) :
        histo=histoList[iHisto]
        integralThis=histo.Integral(0,histo.GetNbinsX()+1)
        histo.Scale(integral0/integralThis)
        hMax=histo.GetMaximum()
        if (hMax>max) : max=hMax
    return max
##############################
def metFit(histo) :
    funcName="func"
    func=r.TF1(funcName,"[0]*x*exp( -(x-[1])**2 / (2.0*[2])**2 )/[2]",0.5,10.0)
    func.SetParameters(1.0,5.0,3.0)
    histo.Fit(funcName,"lrq","sames")
    histo.GetFunction(funcName).SetLineWidth(1)
    histo.GetFunction(funcName).SetLineColor(histo.GetLineColor())
    return func
##############################
def xsFunc(var) :
    return var.xs
##############################
def nEventsFunc(var) :
    return var.nEvents
##############################
def getLogMin(sampleSpecs) :
    if (not doScaleByXs) :
        return 0.5
    else :
        xsList=map(xsFunc,sampleSpecs)
        nEventsList=map(nEventsFunc,sampleSpecs)
        factorList=[]
        for i in range(len(sampleSpecs)) :
            factorList.append(xsList[i]/nEventsList[i])
        return 0.5*min(factorList)
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
def histoLoop(plotSpec,histoList) :
    stuffToKeep=[]
    
    legend=r.TLegend(0.4,0.75,0.75,1.0)
    for iHisto in range(len(histoList)) :
        histo=histoList[iHisto]

        legend.AddEntry(histo,plotSpec.sampleSpecs[iHisto].name,"l")

        yx=r.TF1("yx","x",histo.GetXaxis().GetXmin(),histo.GetXaxis().GetXmax())
        yx.SetLineColor(r.kBlue)
        yx.SetLineWidth(1)
        yx.SetNpx(300)

        #1D here
        if (plotSpec.dimension==1) :
            if (iHisto==0) :
                histo.Draw()
                if (doLog1D) :
                    histo.SetMaximum(2.0*plotSpec.maximum)
                    histo.SetMinimum(getLogMin(plotSpec.sampleSpecs))
                    r.gPad.SetLogy()
                else :
                    histo.SetMaximum(1.1*plotSpec.maximum)
                    histo.SetMinimum(0.0)

            else :
                histo.Draw("same")

            r.gStyle.SetOptFit(0)
            if (doMetFit) :
                r.gStyle.SetOptFit(1111)
                func=metFit(histo)
                stuffToKeep.append(func)
                    
                r.gPad.Update()
                tps=histo.FindObject("stats")
                stuffToKeep.append(tps)
                tps.SetLineColor(histo.GetLineColor())
                tps.SetTextColor(histo.GetLineColor())
                if (iHisto==0) :
                    tps.SetX1NDC(0.75)
                    tps.SetX2NDC(0.95)
                    tps.SetY1NDC(0.75)
                    tps.SetY2NDC(0.95)
                else :
                    tps.SetX1NDC(0.75)
                    tps.SetX2NDC(0.95)
                    tps.SetY1NDC(0.50)
                    tps.SetY2NDC(0.70)

        #2D here
        else :
            plotSpec.canvas.cd(iHisto+1)
            histo.GetYaxis().SetTitleOffset(1.3)
            oldTitle=histo.GetTitle()
            histo.SetTitle(oldTitle+plotSpec.sampleSpecs[iHisto].name)
            histo.SetStats(False)
            histo.GetZaxis().SetTitleOffset(1.2)
            r.gPad.SetRightMargin(0.15)
            if (doColzFor2D) : histo.Draw("colz")
            else :             histo.Draw()

            if (doLog2D) :
                histo.SetMaximum(2.0*plotSpec.maximum)
                histo.SetMinimum(getLogMin(plotSpec.sampleSpecs))
                r.gPad.SetLogz()
            else :
                histo.SetMaximum(1.1*plotSpec.maximum)
                histo.SetMinimum(0.0)

            if ("deltaHtOverHt vs mHtOverHt" in histo.GetName()) :
                histo.GetYaxis().SetRangeUser(0.0,0.7)
                funcs=[
                    makeAlphaTFunc(0.55),
                    makeAlphaTFunc(0.50),
                    makeAlphaTFunc(0.45)
                    ]
                for func in funcs :
                    func.Draw("same")
                stuffToKeep.extend(funcs)
            else :
                yx.Draw("same")
                stuffToKeep.append(yx)

    if (plotSpec.dimension==1) : legend.Draw()
    plotSpec.canvas.Print(plotSpec.psFile,plotSpec.psOptions)
##############################
def onePlotFunction(plotSpec) :
    plotSpec.canvas.cd(0)
    plotSpec.canvas.Clear()

    histoList=makeHistoList(plotSpec)
    if (plotSpec.dimension==1) :
        plotSpec.canvas.Divide(1,1)
        if (not doScaleByXs) :
            plotSpec.maximum=scale1DHistos(histoList,map(xsFunc,plotSpec.sampleSpecs),map(nEventsFunc,plotSpec.sampleSpecs))
    else :
        plotSpec.canvas.Divide(len(histoList),1)

    plotSpec.maximum=scaleHistos(plotSpec.dimension,histoList,map(xsFunc,plotSpec.sampleSpecs),map(nEventsFunc,plotSpec.sampleSpecs))
    histoLoop(plotSpec,histoList)
##############################
def makeHistoList(plotSpec) :
    histoList=[]
    for iSample in range(len(plotSpec.sampleSpecs)) :
        sample=plotSpec.sampleSpecs[iSample]
        f=r.TFile(plotSpec.outputDir+"/"+sample.outputPlotFileName)

        extraName=""
        if (iSample>0) : extraName+="_"+str(iSample)
        h=f.Get(plotSpec.plotName).Clone(plotSpec.plotName+extraName)
        h.SetDirectory(0)
        histoList.append(h)

        color=iSample+1
        h.SetLineColor(color)
        h.SetMarkerColor(color)
        if (plotSpec.dimension==1) : shiftOverflows(h)

    return histoList
##############################
def plotAll(analysisName,sampleSpecs,outputDir) :
    if (len(sampleSpecs)<1) : return
    setupStyle()

    psFile=outputDir+"/"+analysisName+".ps"
    psOptions="Landscape"
    
    canvas=r.TCanvas()
    canvas.Print(psFile+"[",psOptions)

    outList=getNamesAndDimensions(outputDir,sampleSpecs[0])
    plotNames=outList[0]
    dimensions=outList[1]
    for iPlotName in range(len(plotNames)) :
        plotSpec=onePlotSpec()

        plotSpec.plotName=plotNames[iPlotName]
        plotSpec.dimension=dimensions[iPlotName]
        plotSpec.canvas=canvas
        plotSpec.sampleSpecs=sampleSpecs
        plotSpec.outputDir=outputDir
        plotSpec.psFile=psFile
        plotSpec.psOptions=psOptions

        onePlotFunction(plotSpec)

    canvas.Print(psFile+"]",psOptions)
##############################
class onePlotSpec :
    """onePlotSpec"""
##############################
