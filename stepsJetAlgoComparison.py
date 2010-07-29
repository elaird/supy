from analysisStep import analysisStep
import ROOT as r
#####################################
class leadingJetPtHistogrammer(analysisStep) :
    """leadingJetPtHistogrammer"""

    def __init__(self,jetCollection1,jetSuffix1,jetCollection2,jetSuffix2) :
        self.jetCollection1=jetCollection1
        self.jetSuffix1=jetSuffix1
        self.jetCollection2=jetCollection2
        self.jetSuffix2=jetSuffix2
        self.neededBranches=[
            self.jetCollection1+'CorrectedP4'+self.jetSuffix1,
            self.jetCollection2+'CorrectedP4'+self.jetSuffix2,
            ]

    def bookHistos(self) :
        self.leadingJetPtHisto=r.TH2D("ptLeadingComparison",
                                      ";p_{T} (GeV) of leading "+self.jetCollection1+" jet"
                                      +";p_{T} (GeV) of leading "+self.jetCollection2+" jet"
                                      +";events / bin",20,0.0,50.0,20,0.0,50.0)

    def uponAcceptance (self,chain,chainVars,extraVars) :
        pt1=getattr(chainVars,self.jetCollection1+'CorrectedP4'+self.jetSuffix1)[0].pt()
        pt2=getattr(chainVars,self.jetCollection2+'CorrectedP4'+self.jetSuffix2)[0].pt()
        self.leadingJetPtHisto.Fill(pt1,pt2)
