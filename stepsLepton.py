from analysisStep import analysisStep

class leptonFilter(analysisStep) :
        """leptonFilter"""

        def __init__(self,nMinLeptons, minPt=0) :
            self.nMinLeptons=nMinLeptons
            self.minPt=minPt
            self.moreName="(nLeptons >= %d, pt > %f)" % (self.nMinLeptons, self.minPt)

        def select(self,eventVars) :
            # muons
            nMuonsPF = len(eventVars["muonP4PF"])
            nMuonsPAT = len(eventVars["muonP4Pat"])

            nGoodMuonsPF = 0
            for i in range(nMuonsPF):
                #print "mu pf pt: %f" % eventVars["muonP4PF"][i].pt()
                if (eventVars["muonP4PF"][i].pt() > self.minPt):
                    nGoodMuonsPF += 1
                    
            nGoodMuonsPAT = 0
            for i in range(nMuonsPAT):
                #print "mu pat pt: %f" % eventVars["muonP4Pat"][i].pt()
                if (eventVars["muonP4Pat"][i].pt() > self.minPt):
                    nGoodMuonsPAT += 1


            # electrons
            nElectronsPF = len(eventVars["electronP4PF"])
            nElectronsPAT = len(eventVars["electronP4Pat"])
            
            nGoodElectronsPF = 0
            for i in range(nElectronsPF):
                #print "e pf pt: %f" % eventVars["electronP4PF"][i].pt()
                if (eventVars["electronP4PF"][i].pt() > self.minPt):
                    nGoodElectronsPF += 1
                    

            nGoodElectronsPAT = 0
            for i in range(nElectronsPAT):
                #print "e pat pt: %f" % eventVars["electronP4Pat"][i].pt()
                if (eventVars["electronP4Pat"][i].pt() > self.minPt):
                    nGoodElectronsPAT += 1


            # taus
            nTausPF = len(eventVars["tauP4PF"])
            nTausPAT = len(eventVars["tauP4Pat"])

            nGoodTausPF = 0
            for i in range(nTausPF):
                #print "tau pf pt: %f" % eventVars["tauP4PF"][i].pt()
                if (eventVars["tauP4PF"][i].pt() > self.minPt):
                    nGoodTausPF += 1
                    
            nGoodTausPAT = 0
            for i in range(nTausPAT):
                #print "tau pat pt: %f" % eventVars["tauP4Pat"][i].pt()
                if (eventVars["tauP4Pat"][i].pt() > self.minPt):
                    nGoodTausPAT += 1


            #print "mu: %d / %d, e: %d / %d, tau: %d / %d" % (nGoodMuonsPF, nGoodMuonsPAT, nGoodElectronsPF, nGoodElectronsPAT, nGoodTausPF, nGoodTausPAT)
            if (self.nMinLeptons == 1):
                # select events with at least one lepton candidate (pat as well as pf)
                return (nGoodMuonsPF != 0 or nGoodMuonsPAT != 0 or nGoodElectronsPF != 0 or nGoodElectronsPAT != 0 or nGoodTausPF != 0 or nGoodTausPAT != 0)
            else:
                # number != 1 has been specified, count only PF candidates
                return (nGlobalMuonsPF + nGoodElectronsPF + nGoodTausPF) >= self.nMinLeptons



