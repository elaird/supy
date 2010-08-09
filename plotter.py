import ROOT as r
import os,math
##############################
def setupStyle() :
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)
    #r.gStyle.SetOptStat(111111)
##############################
def getColor(label,colorDict) :
    if "currentColorIndex" not in colorDict :
        colorDict["currentColorIndex"]=2

    if not label in colorDict :
        colorDict[label]=colorDict["currentColorIndex"]
        colorDict["currentColorIndex"]+=1
        if colorDict["currentColorIndex"]==5 : colorDict["currentColorIndex"]+=1
    return colorDict[label]
##############################
def getMarkerStyle(label,markerStyleDict) :
    if not label in markerStyleDict :
        markerStyleDict[label]=1
    return markerStyleDict[label]
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
def setColorsAndStyles(plotContainer,colorDict,markerStyleDict) :
    for sampleName,histo in plotContainer["histoDict"].iteritems() :
        color=getColor(sampleName,colorDict)
        markerStyle=getMarkerStyle(sampleName,markerStyleDict)
        histo.SetLineColor(color)
        histo.SetMarkerColor(color)
        histo.SetMarkerStyle(markerStyle)
##############################
def setRanges(plotContainer,logAxes) :
    globalMax = -1.0
    globalMin = 1.0e9
    
    for histo in plotContainer["histoDict"].values() :
        max=histo.GetMaximum()
        if max>globalMax : globalMax=max

        if plotContainer["dimension"]==1 :
            for iBinX in range(histo.GetNbinsX()+2) :
                value=histo.GetBinContent(iBinX)
                if value>0.0 :
                    if value<globalMin : globalMin=value
                    
        if plotContainer["dimension"]==2 :
            for iBinX in range(histo.GetNbinsX()+2) :
                for iBinY in range(histo.GetNbinsY()+2) :
                    value=histo.GetBinContent(iBinX,iBinY)
                    if value>0.0 :
                        if value<globalMin : globalMin=value
                    
    for histo in plotContainer["histoDict"].values() :
        if logAxes :
            histo.SetMaximum(2.0*globalMax)
            histo.SetMinimum(0.5*globalMin)
        else :
            histo.SetMaximum(1.1*globalMax)
            histo.SetMinimum(0.0)
##############################
def plot1D(canvasDict,histo,count,stuffToKeep) :
    r.gPad.SetRightMargin(0.15)
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    if count==0 :
        histo.Draw()
        if canvasDict["doLog"] : r.gPad.SetLogy()
    else :
        histo.Draw("same")
        r.gStyle.SetOptFit(0)
        if canvasDict["doMetFit"] and "met" in histo.GetName() :
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

    if "countsHisto" in histo.GetName() :
        outString=histo.GetName().ljust(20)
        outString+=sampleName.ljust(12)
        outString+=": "
        outString+="%#8.2f"%histo.GetBinContent(1)
        outString+=" +/-"
        outString+="%#8.2f"%histo.GetBinError(1)
        #if not plotSpec["scaleByAreaRatherThanByXs"] : print outString
        #else : print "for counts, set scaleByAreaRatherThanByXs=False"
##############################
def plot2D(canvasDict,histo,count,sampleName,stuffToKeep) :
    yx=r.TF1("yx","x",histo.GetXaxis().GetXmin(),histo.GetXaxis().GetXmax())
    yx.SetLineColor(r.kBlue)
    yx.SetLineWidth(1)
    yx.SetNpx(300)
    
    canvasDict["canvas"].cd(count+1)
    histo.GetYaxis().SetTitleOffset(1.2)
    histo.SetTitle(histo.GetTitle()+sampleName)
    histo.SetStats(False)
    histo.GetZaxis().SetTitleOffset(1.3)
    r.gPad.SetRightMargin(0.15)
    r.gPad.SetTicky()
    if canvasDict["doLog"] : r.gPad.SetLogz()

    if canvasDict["doColzFor2D"] : histo.Draw("colz")
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
    else :
        if canvasDict["drawYx"] :
            yx.Draw("same")
            stuffToKeep.append(yx)
##############################
def onePlotFunction(plotContainer,canvasDict,colorDict,markerStyleDict) :
    #prepare canvas
    canvasDict["canvas"].cd(0)
    canvasDict["canvas"].Clear()
    if plotContainer["dimension"]==1 :
        canvasDict["canvas"].Divide(1,1)
    else :
        canvasDict["canvas"].Divide(len(plotContainer["histoDict"]),1)

    #set ranges
    setRanges(plotContainer,canvasDict["doLog"])

    #set colors and styles
    setColorsAndStyles(plotContainer,colorDict,markerStyleDict)
    
    #loop over available histos and plot them
    stuffToKeep=[]
    x1=0.86
    x2=1.00
    y1=0.60
    y2=0.10
    legend=r.TLegend(x1,y1,x2,y2)
    count=0

    sampleNames=plotContainer["histoDict"].keys()
    sampleNames.sort()
    
    for sampleName in sampleNames :
        histo=plotContainer["histoDict"][sampleName]
        if not histo.GetEntries() : continue
        legend.AddEntry(histo,sampleName,"l")

        if plotContainer["dimension"]==1   : plot1D(canvasDict,histo,count,stuffToKeep)
        elif plotContainer["dimension"]==2 : plot2D(canvasDict,histo,count,sampleName,stuffToKeep)
        else :
            print "Skipping histo",histo.GetName(),"with dimension",plotContainer["dimension"]
            continue
        count+=1
    if plotContainer["dimension"]==1 : legend.Draw()
    canvasDict["canvas"].Print(canvasDict["psFile"],canvasDict["psOptions"])
##############################
def printTimeStamp(canvasDict) :
    text=r.TText()
    text.SetNDC()
    dateString="file created at ";
    tdt=r.TDatime()
    text.DrawText(0.1,0.3,dateString+tdt.AsString())
    canvasDict["canvas"].Print(canvasDict["psFile"],canvasDict["psOptions"])
    canvasDict["canvas"].Clear()
##############################
def plotAll(someAnalysis,
            colorDict={},
            markerStyleDict={},
            doLog=True,
            drawYx=False,
            doMetFit=False,
            doColzFor2D=True,
            ) :

    if not someAnalysis.hasLooped : print someAnalysis.hyphens
    listOfPlotContainers=someAnalysis.organizeHistograms()

    if len(listOfPlotContainers)<1 : return
    setupStyle()

    canvasDict={}
    canvasDict["doLog"]=True,
    canvasDict["drawYx"]=False,
    canvasDict["doMetFit"]=False,
    canvasDict["doColzFor2D"]=True,
    
    canvasDict["psFile"]=someAnalysis.outputDir+"/"+someAnalysis.name+".ps"
    canvasDict["psOptions"]="Landscape"
    
    canvasDict["canvas"]=r.TCanvas()
    canvasDict["canvas"].Print(canvasDict["psFile"]+"[",canvasDict["psOptions"])
    #canvasDict["canvas"].SetRightMargin(0.4)
    printTimeStamp(canvasDict)

    for plotContainer in listOfPlotContainers :
        onePlotFunction(plotContainer,canvasDict,colorDict,markerStyleDict)

    canvasDict["canvas"].Print(canvasDict["psFile"]+"]",canvasDict["psOptions"])
    pdfFile=canvasDict["psFile"].replace(".ps",".pdf")
    os.system("ps2pdf "+canvasDict["psFile"]+" "+pdfFile)
    os.system("gzip -f "+canvasDict["psFile"])
    print "The output file \""+pdfFile+"\" has been written."
    print "colors used:"
    print colorDict
    print "marker styles used:"
    print markerStyleDict
    print someAnalysis.hyphens
    #print "The output file \""+canvasDict["psFile"]+".gz\" has been written."
##############################
