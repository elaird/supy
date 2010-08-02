from analysisStep import analysisStep
import ROOT as r
#####################################
class leadingJetPtHistogrammer(analysisStep) :
    """leadingJetPtHistogrammer"""

    def __init__(self,jetCollection1,jetSuffix1,jetCollection2,jetSuffix2) :
        self.jetCollection1 = jetCollection1
        self.jetCollection2 = jetCollection2
        self.p4jets1 = jetCollection1+'CorrectedP4'+jetSuffix1,
        self.p4jets2 = jetCollection2+'CorrectedP4'+jetSuffix2,

    def bookHistos(self) :
        self.leadingJetPtHisto=r.TH2D("ptLeadingComparison",
                                      ";p_{T} (GeV) of leading "+self.jetCollection1+" jet"
                                      +";p_{T} (GeV) of leading "+self.jetCollection2+" jet"
                                      +";events / bin",20,0.0,50.0,20,0.0,50.0)

    def uponAcceptance (self,evetVars) :
        pt1 = eventVars[self.p4jets1].at(0).pt()
        pt2 = eventVars[self.p4jets1].at(0).pt()
        self.leadingJetPtHisto.Fill(pt1,pt2)
