import ROOT as r
import os,math
##############################
doLog1D=True
doLog2D=True
drawYx=False
doMetFit=False
doScaleByXs=True
doColzFor2D=True
lumiToUseInAbsenceOfData=100 #/pb
##############################
colorDict={}
#colorDict["currentColorIndex"]=r.kGreen
colorDict["currentColorIndex"]=2

colorDict["NT7_LM0"]=r.kBlack
colorDict["NT7_LM1"]=r.kBlue

colorDict["NT7_MG_QCD_bin1"]=r.kGreen
colorDict["NT7_MG_QCD_bin2"]=r.kGreen+2
colorDict["NT7_MG_QCD_bin3"]=r.kGreen-3
colorDict["NT7_MG_QCD_bin4"]=r.kGreen+3

colorDict["NT7_MG_TT_jets"]=r.kOrange+7
colorDict["NT7_MG_W_jets"]=r.kOrange
colorDict["NT7_MG_Z_jets"]=r.kRed
colorDict["NT7_MG_Z_inv"]=r.kMagenta
##############################
def getColor(label) :
    if not label in colorDict :
        colorDict[label]=colorDict["currentColorIndex"]
        colorDict["currentColorIndex"]+=1
        if colorDict["currentColorIndex"]==5 : colorDict["currentColorIndex"]+=1
    return colorDict[label]
##############################
def setupStyle() :
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)
    #r.gStyle.SetOptStat(111111)
##############################
def getNamesAndDimensions(plotFileNameDict) :
    dimensionDict={}
    for plotFileName in plotFileNameDict.values() :
        f0=r.TFile(plotFileName)
        keys=f0.GetListOfKeys()
        for key in keys :
            name=key.GetName()
            className=object=f0.Get(name).ClassName()
            if className[0:2]=="TH" :
                dimensionDict[name]=int(className[2])
            else :
                dimensionDict[name]=0
    return dimensionDict
##############################
def get_Xs_Lumi_Event_Job_Numbers(plotFileNameDict) :
    xsDict={}
    lumiDict={}
    nEventsDict={}
    nJobsDict={}
    for sampleName,plotFileName in plotFileNameDict.iteritems() :
        f=r.TFile(plotFileName)
        nJobs=f.Get("nJobsHisto").GetBinContent(1)
        xsDict      [sampleName] = f.Get("xsHisto").GetBinContent(1) / nJobs
        lumiDict    [sampleName] = f.Get("lumiHisto").GetBinContent(1) /  nJobs
        nEventsDict [sampleName] = f.Get("nEventsHisto").GetBinContent(1)
        nJobsDict   [sampleName] = nJobs

    return [xsDict,lumiDict,nEventsDict,nJobsDict]
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
def scaleHistos(histoDict,plotSpec) :
    maximum=0.0
    if len(histoDict)<1 : return maximum

    for sample,histo in histoDict.iteritems() :
        scale=True
        if "xsHisto" in histo.GetName() or "lumiHisto" in histo.GetName() :
            scale=False
            histo.Scale(1.0/plotSpec["nJobsDict"][sample])
        if "nEventsHisto" in histo.GetName() : scale=False
        if "nJobsHisto"   in histo.GetName() : scale=False

        if scale :
            #scale the MC samples to match the data (if present) or the default lumi value
            xs=plotSpec["xsDict"][sample]
            if xs>0.0 and plotSpec["nEventsDict"][sample]>0:
                histo.Scale(plotSpec["lumiValue"]*xs/plotSpec["nEventsDict"][sample])
            if plotSpec["dimension"]==1 :
                newTitle=histo.GetYaxis().GetTitle()+" / "+str(plotSpec["lumiValue"])+" pb^{-1}"
                histo.GetYaxis().SetTitle(newTitle)
            if plotSpec["dimension"]==2 :
                newTitle=histo.GetZaxis().GetTitle()+" / "+str(plotSpec["lumiValue"])+" pb^{-1}"
                histo.GetZaxis().SetTitle(newTitle)

        hMax=histo.GetMaximum()
        if hMax>maximum : maximum=hMax
    return maximum
##############################
def scale1DHistosByArea(histoDict) :
    max=0.0
    if (len(histoDict)<1) : return max
    
    integral0=histoList[0].Integral(0,histoList[0].GetNbinsX()+1)
    for iHisto in range(len(histoList)) :
        histo=histoList[iHisto]
        if (histo.GetName()=="xsHisto" or histo.GetName()=="nEventsHisto") :
            continue
        integralThis=histo.Integral(0,histo.GetNbinsX()+1)
        histo.Scale(integral0/integralThis)
        hMax=histo.GetMaximum()
        if (hMax>max) : max=hMax
    return max
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
def getLogMin(plotSpec) :
    if not doScaleByXs :
        return 0.5
    else :
        factorList=[]
        for sample in plotSpec["plotFileNameDict"].keys() :
            xs=plotSpec["xsDict"][sample]
            if plotSpec["nEventsDict"][sample]>0 and plotSpec["nJobsDict"][sample]>0 :
                if xs>0.0 : factorList.append(plotSpec["lumiValue"]*xs/plotSpec["nEventsDict"][sample])
                else :      factorList.append(1.0)
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
def histoLoop(plotSpec,histoDict) :
    stuffToKeep=[]

    #x1=0.40
    #x2=0.75
    #y1=0.75
    #y2=1.00

    #x1=0.86
    #x2=1.00
    #y1=0.50
    #y2=0.75

    x1=0.86
    x2=1.00
    y1=0.60
    y2=0.10

    legend=r.TLegend(x1,y1,x2,y2)
    count=0
    for sampleName,histo in histoDict.iteritems() :
        #merge requested histos
        targetName=sampleName
        if sampleName in plotSpec["mergeRequest"] :
            targetName=plotSpec["mergeRequest"][sampleName]
        if plotSpec["mergeAllMc"] :
            if plotSpec["xsDict"][sampleName]!=0.0 : #exclude data
                if  "lm" not in sampleName : #exclude SUSY
                    targetName="all MC"
        
        if sampleName!=targetName :
            someName=histo.GetName().replace("_"+str(count),"")+targetName
            isPresent=r.gDirectory.Get(someName)
            if not isPresent :
                mergedHisto=histo.Clone(someName)
                legend.AddEntry(mergedHisto,targetName,"l")
            else :
                mergedHisto.Add(histo)
            stuffToKeep.append(mergedHisto)
            histo=mergedHisto
        else :
            legend.AddEntry(histo,sampleName,"l")

        yx=r.TF1("yx","x",histo.GetXaxis().GetXmin(),histo.GetXaxis().GetXmax())
        yx.SetLineColor(r.kBlue)
        yx.SetLineWidth(1)
        yx.SetNpx(300)

        #1D here
        if plotSpec["dimension"]==1 :
            r.gPad.SetRightMargin(0.15)
            r.gPad.SetTicky()            
            if count==0 :
                histo.Draw()
                if doLog1D :
                    histo.SetMaximum(2.0*plotSpec["maximum"])
                    histo.SetMinimum(getLogMin(plotSpec))
                    r.gPad.SetLogy()
                else :
                    histo.SetMaximum(1.1*plotSpec["maximum"])
                    histo.SetMinimum(0.0)

            else :
                histo.Draw("same")

            r.gStyle.SetOptFit(0)
            if doMetFit and "met" in histo.GetName() :
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

            if "countsHisto" in histo.GetName() :
                outString=histo.GetName().ljust(20)
                outString+=sampleName.ljust(12)
                outString+=": "
                outString+="%#8.2f"%histo.GetBinContent(1)
                outString+=" +/-"
                outString+="%#8.2f"%histo.GetBinError(1)
                if doScaleByXs : print outString
                else : print "for counts, set doScaleByXs=True"
            
        #2D here
        else :
            plotSpec["canvas"].cd(count+1)
            histo.GetYaxis().SetTitleOffset(1.2)
            oldTitle=histo.GetTitle()
            histo.SetTitle(oldTitle+sampleName)
            histo.SetStats(False)
            histo.GetZaxis().SetTitleOffset(1.3)
            r.gPad.SetRightMargin(0.15)
            r.gPad.SetTicky()
            if doColzFor2D : histo.Draw("colz")
            else :           histo.Draw()

            if doLog2D :
                if doScaleByXs : histo.SetMaximum(2.0*plotSpec["maximum"])
                histo.SetMinimum(getLogMin(plotSpec))
                r.gPad.SetLogz()
            else :
                #histo.SetMaximum(1.1*plotSpec.maximum)
                histo.SetMinimum(0.0)

            if "deltaHtOverHt vs mHtOverHt" in histo.GetName() :
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
                if drawYx :
                    yx.Draw("same")
                    stuffToKeep.append(yx)
        count+=1
    if plotSpec["dimension"]==1 : legend.Draw()
    plotSpec["canvas"].Print(plotSpec["psFile"],plotSpec["psOptions"])
##############################
def onePlotFunction(plotSpec) :
    plotSpec["canvas"].cd(0)
    plotSpec["canvas"].Clear()

    histoDict=makeHistoDict(plotSpec)
    if plotSpec["dimension"]==1 :
        plotSpec["canvas"].Divide(1,1)
        if not doScaleByXs :
            plotSpec["maximum"]=scale1DHistosByArea(histoDict)
    else :
        plotSpec["canvas"].Divide(len(histoDict),1)

    if doScaleByXs :
        plotSpec["maximum"]=scaleHistos(histoDict,plotSpec)
    histoLoop(plotSpec,histoDict)
##############################
def makeHistoDict(plotSpec) :
    histoDict={}

    count=0
    for sampleName,plotFileName in plotSpec["plotFileNameDict"].iteritems() :
        f=r.TFile(plotFileName)

        extraName=""
        if count>0 : extraName+="_"+str(count)
        h1=f.Get(plotSpec["plotName"])
        if not h1 : continue
        h=h1.Clone(plotSpec["plotName"]+extraName)
        h.SetDirectory(0)
        histoDict[sampleName]=h

        color=r.kBlack
        if plotSpec["lumiDict"][sampleName]==0.0 : 
            color=getColor(sampleName)
        h.SetLineColor(color)
        h.SetMarkerColor(color)
        if plotSpec["dimension"]==1 : shiftUnderAndOverflows(h)
        count+=1

    return histoDict
##############################
def printTimeStamp(canvas,psFile,psOptions) :
    text=r.TText()
    text.SetNDC()
    dateString="file created at ";
    tdt=r.TDatime()
    text.DrawText(0.1,0.3,dateString+tdt.AsString())
    canvas.Print(psFile,psOptions)
    canvas.Clear()
##############################
def plotAll(analysisName,plotFileNameDict,mergeAllMc,mergeRequest,outputDir,hyphens) :
    if len(plotFileNameDict)<1 : return
    setupStyle()

    psFile=outputDir+"/"+analysisName+".ps"
    psOptions="Landscape"
    
    canvas=r.TCanvas()
    canvas.Print(psFile+"[",psOptions)
    #canvas.SetRightMargin(0.4)
    
    printTimeStamp(canvas,psFile,psOptions)
    
    dimensionDict=getNamesAndDimensions(plotFileNameDict)
    
    xsDict,lumiDict,nEventsDict,nJobsDict=get_Xs_Lumi_Event_Job_Numbers(plotFileNameDict)

    nDataSamples=len(lumiDict.values())-lumiDict.values().count(0.0)
    lumiValue=lumiToUseInAbsenceOfData
    if nDataSamples==1 :
        lumiValue=max(lumiDict.values())
    elif nDataSamples>1 :
        raise Exception("at the moment, plotting multiple data samples is not supported")

    for plotName in dimensionDict :
        plotSpec={}

        plotSpec["lumiValue"]        = lumiValue
        plotSpec["plotName"]         = plotName
        plotSpec["dimension"]        = dimensionDict[plotName]
        plotSpec["canvas"]           = canvas
        plotSpec["plotFileNameDict"] = plotFileNameDict
        plotSpec["mergeAllMc"]       = mergeAllMc
        plotSpec["mergeRequest"]     = mergeRequest
        plotSpec["outputDir"]        = outputDir
        plotSpec["xsDict"]           = xsDict
        plotSpec["lumiDict"]         = lumiDict
        plotSpec["nEventsDict"]      = nEventsDict
        plotSpec["nJobsDict"]        = nJobsDict
        plotSpec["psFile"]           = psFile
        plotSpec["psOptions"]        = psOptions

        onePlotFunction(plotSpec)

    canvas.Print(psFile+"]",psOptions)
    pdfFile=psFile.replace(".ps",".pdf")
    os.system("ps2pdf "+psFile+" "+pdfFile)
    os.system("gzip -f "+psFile)
    print "The output file \""+pdfFile+"\" has been written."
    print hyphens
    #print "The output file \""+psFile+".gz\" has been written."
##############################
