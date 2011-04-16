import utils, ROOT as r

fileName = "Spring10_PtResolution_AK5Calo.txt"

c = r.TCanvas()
c.SetLogx()
r.gStyle.SetOptStat(0)
h = r.TH1D("h",fileName+";p_{T};#sigma(p_{T})/p_{T}",1,20,2000)
h.SetBinContent(1,0.3)
h.SetMinimum(0)
h.Draw()

rainbow = [r.kBlack,r.kBlue,r.kCyan,r.kGreen,r.kSpring,r.kYellow,r.kRed,r.kPink,r.kMagenta,r.kGray]

legend = r.TLegend(0.6,0.4,0.9,0.9)
legend.SetHeader("#eta bin")

funcs = utils.cmsswFuncData(fileName,"sigma")
for i,f in enumerate(funcs[:len(funcs)/2]) :
    print f
    legend.AddEntry(f[2],"%.1f : %.1f"%tuple(f[:2]))
    f[2].SetLineWidth(1 if i>4 else 2)
    f[2].SetLineColor(rainbow[i])
    f[2].Draw('same')
legend.Draw()
c.Update()
raw_input()
