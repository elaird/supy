import ROOT as r

def setupStyle() :
    r.gROOT.SetStyle("Plain")
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

def scale1DHistos(histoList) :
    max=0.0
    if (len(histoList)<1) : return max
    
    num=histoList[0].Integral(0,histoList[0].GetNbinsX()+1)
    for iHisto in range(len(histoList)) :
        histo=histoList[iHisto]
        denom=histo.Integral(0,histo.GetNbinsX()+1)
        
        histo.Scale(num/denom)
        hMax=histo.GetMaximum()
        if (hMax>max) : max=hMax
    return max

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
            max=scale1DHistos(histoList)
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
                    histo.SetMaximum(1.1*max)
                else :
                    histo.Draw("same")
            #2D here
            else :
                canvas.cd(iHisto+1)
                histo.GetYaxis().SetTitleOffset(1.3)
                histo.Draw()
                yx.Draw("same")

        if (is1D) : legend.Draw()
        canvas.Print(psFile,psOptions)
    
    canvas.Print(psFile+"]",psOptions)
