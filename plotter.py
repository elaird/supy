import ROOT as r

doLog1D=True
doMetFit=False
doScaleByAreaRatherThanXs=False
doColzFor2D=True
xsNorm=100 #pb^-1

def setupStyle() :
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)
    #r.gStyle.SetOptStat(111111)

def getNames(outputDir,sample) :
    f0=r.TFile(outputDir+"/"+sample.outputPlotFileName)
    keys=f0.GetListOfKeys()
    names=[]
    for key in keys :
        names.append(key.GetName())
    return names

def shiftOverflows(histo) :
    bins=histo.GetNbinsX()
    entries=histo.GetEntries()
    overflows=histo.GetBinContent(bins+1)
    lastBinContent=histo.GetBinContent(bins)
    histo.SetBinContent(bins+1,0.0)
    histo.SetBinContent(bins,lastBinContent+overflows)
    histo.SetEntries(entries)

def scale1DHistos(histoList,xsList,nEventsList) :
    max=0.0
    if (len(histoList)<1) : return max
    
    integral0=histoList[0].Integral(0,histoList[0].GetNbinsX()+1)
    for iHisto in range(len(histoList)) :
        histo=histoList[iHisto]
        
        if (doScaleByAreaRatherThanXs) :
            integralThis=histo.Integral(0,histo.GetNbinsX()+1)
            histo.Scale(integral0/integralThis)
        else :
            histo.Scale(xsNorm*xsList[iHisto]/nEventsList[iHisto])
            newYTitle=histo.GetYaxis().GetTitle()+" / "+str(xsNorm)+" pb^{-1}"
            histo.GetYaxis().SetTitle(newYTitle)
            #print histo.Integral()

        hMax=histo.GetMaximum()
        if (hMax>max) : max=hMax
    return max

def metFit(histo) :
    funcName="func"
    func=r.TF1(funcName,"[0]*x*exp( -(x-[1])**2 / (2.0*[2])**2 )/[2]",0.5,10.0)
    func.SetParameters(1.0,5.0,3.0)
    histo.Fit(funcName,"lrq","sames")
    histo.GetFunction(funcName).SetLineWidth(1)
    histo.GetFunction(funcName).SetLineColor(histo.GetLineColor())
    return func

def xsFunc(var) :
    return var.xs

def nEventsFunc(var) :
    return var.nEvents

def getLogMin(sampleSpecs) :
    if (doScaleByAreaRatherThanXs) :
        return 0.5
    else :
        xsList=map(xsFunc,sampleSpecs)
        nEventsList=map(nEventsFunc,sampleSpecs)
        factorList=[]
        for i in range(len(sampleSpecs)) :
            factorList.append(xsList[i]/nEventsList[i])
        return 0.5*min(factorList)

def plotAll(analysisName,sampleSpecs,outputDir) :
    if (len(sampleSpecs)<1) : return
    setupStyle()

    psFile=outputDir+"/"+analysisName+".ps"
    psOptions="Landscape"
    
    canvas=r.TCanvas()
    canvas.Print(psFile+"[",psOptions)

    plotNames=getNames(outputDir,sampleSpecs[0])
    for plotName in plotNames :
        histoList=[]
        stuffToKeep=[]
        
        is1D=False
        for iSample in range(len(sampleSpecs)) :
            sample=sampleSpecs[iSample]
            f=r.TFile(outputDir+"/"+sample.outputPlotFileName)

            extraName=""
            if (iSample>0) : extraName+="_"+str(iSample)
            h=f.Get(plotName).Clone(plotName+extraName)
            h.SetDirectory(0)
            histoList.append(h) #keep a reference around for pyROOT

            is1D=(h.ClassName()[0:3]=="TH1")
            color=iSample+1
            h.SetLineColor(color)
            h.SetMarkerColor(color)
            if (is1D) : shiftOverflows(h)

        canvas.cd(0)
        canvas.Clear()
        yx=r.TF1("yx","x",h.GetXaxis().GetXmin(),h.GetXaxis().GetXmax())
        yx.SetLineColor(r.kBlue)
        yx.SetLineWidth(1)
        yx.SetNpx(300)
        
        if (is1D) :
            max=scale1DHistos(histoList,map(xsFunc,sampleSpecs),map(nEventsFunc,sampleSpecs))
            canvas.Divide(1,1)
        else :
            canvas.Divide(len(histoList),1)
            
        legend=r.TLegend(0.4,0.75,0.75,1.0)
        for iHisto in range(len(histoList)) :
            histo=histoList[iHisto]

            legend.AddEntry(histo,sampleSpecs[iHisto].name,"l")

            #1D here
            if (is1D) :
                if (iHisto==0) :
                    histo.Draw()
                    if (doLog1D) :
                        histo.SetMaximum(2.0*max)
                        histo.SetMinimum(getLogMin(sampleSpecs))
                        r.gPad.SetLogy()
                    else :
                        histo.SetMaximum(1.1*max)
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
                canvas.cd(iHisto+1)
                histo.GetYaxis().SetTitleOffset(1.3)
                if (doColzFor2D) :
                    histo.Draw("colz")
                else :
                    histo.Draw()
                yx.Draw("same")

        if (is1D) : legend.Draw()

        canvas.Print(psFile,psOptions)
    
    canvas.Print(psFile+"]",psOptions)
