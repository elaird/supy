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

    def uponAcceptance (self,eventVars) :
        pt1 = eventVars[self.p4jets1].at(0).pt()
        pt2 = eventVars[self.p4jets1].at(0).pt()
        self.book(eventVars).fill( (pt1,pt2),
                                   "ptLeadingComparison",
                                   (20,20),
                                   (0.0,0.0),
                                   (50.0,50.0),
                                   ";p_{T} (GeV) of leading "+self.jetCollection1+" jet"+ \
                                   ";p_{T} (GeV) of leading "+self.jetCollection2+" jet"+ \
                                   +";events / bin")
