from core.analysis import analysis
import os,steps,samples,calculables

class jsonMaker(analysis) :
    def parameters(self) :
        jwPrompt = calculables.Other.jsonWeight("cert/Cert_160404-178677_7TeV_PromptReco_Collisions11_JSON.sub.txt")
        jwMay = calculables.Other.jsonWeight("cert/Cert_160404-163869_7TeV_May10ReReco_Collisions11_JSON_v3.txt")
        jwAug = calculables.Other.jsonWeight("cert/Cert_170249-172619_7TeV_ReReco5Aug_Collisions11_JSON_v3.txt")

        group = self.vary()

        group['SingleMu'] = [(['SingleMu.2011A-May.1',
                               'SingleMu.2011A-PR4.1',
                               'SingleMu.2011A-Aug.1',
                               'SingleMu.2011A-Oct.1',
                               'SingleMu.2011B-PR1.1a',
                               'SingleMu.2011B-PR1.1b',
                               ], [])] # no json filtering necessary, golden json used

        group['Photon1'] = [(['Photon.Run2011A-May10ReReco-v1.AOD.job536',
                             'Photon.Run2011A-05Aug2011-v1.AOD.job528',
                             'Photon.Run2011A-PromptReco-v4.AOD.job535',
                             'Photon.Run2011A-PromptReco-v6.AOD.job527',
                             'Photon.Run2011B-PromptReco-v1.AOD.job515',
                             'Photon.Run2011B-PromptReco-v1.AOD.job519',
                             'Photon.Run2011B-PromptReco-v1.AOD.job531',
                             'Photon.Run2011B-PromptReco-v1.AOD.job570',
                             'Photon.Run2011B-PromptReco-v1.AOD.job598',
                             ], [])]

        group['Photon2'] = [(["Photon.Run2011A-05Aug2011-v1.AOD.job663",
                              "Photon.Run2011A-May10ReReco-v1.AOD.job662",
                              "Photon.Run2011A-PromptReco-v4.AOD.job664",
                              "Photon.Run2011A-PromptReco-v6.AOD.job667",
                              "Photon.Run2011B-PromptReco-v1.AOD.job668",
                              ], [])]

        group['Mumu'] = [(["DoubleMu.Run2011A-05Aug2011-v1.AOD.job663",
                           "DoubleMu.Run2011A-May10ReReco-v1.AOD.job662",
                           "DoubleMu.Run2011A-PromptReco-v4.AOD.job664",
                           "DoubleMu.Run2011A-PromptReco-v6.AOD.job665",
                           "DoubleMu.Run2011B-PromptReco-v1.AOD.job666",
                           ], [])]
        
        group['HT1'] = [('HT.Run2011A-May10ReReco-v1.AOD.job536',jwMay),
                        ('HT.Run2011A-05Aug2011-v1.AOD.job528',jwAug),
                        (['HT.Run2011A-PromptReco-v4.AOD.job535',
                          'HT.Run2011A-PromptReco-v6.AOD.job527',
                          'HT.Run2011B-PromptReco-v1.AOD.job515',
                          'HT.Run2011B-PromptReco-v1.AOD.job519',
                          'HT.Run2011B-PromptReco-v1.AOD.job531',
                          'HT.Run2011B-PromptReco-v1.AOD.job533',
                          'HT.Run2011B-PromptReco-v1.AOD.job564',
                          'HT.Run2011B-PromptReco-v1.AOD.job592',
                          ], jwPrompt)]
        
        group['HT2'] = [('HT.Run2011A-May10ReReco-v1.AOD.Darren1',jwMay),
                        ('HT.Run2011A-05Aug2011-v1.AOD.Bryn1',jwAug),
                        (['HT.Run2011A-PromptReco-v4.AOD.Bryn1',
                          'HT.Run2011A-PromptReco-v6.AOD.Bryn1',
                          'HT.Run2011B-PromptReco-v1.AOD.Bryn1',
                          'HT.Run2011B-PromptReco-v1.AOD.Bryn2',
                          'HT.Run2011B-PromptReco-v1.AOD.Bryn3',
                          ], jwPrompt)]

        return {'group':group}

    def listOfSteps(self,pars) :
        return [ steps.Print.progressPrinter(2,300),
                 steps.Other.jsonMaker(),
                 ]

    def listOfCalculables(self,pars) :
        return calculables.zeroArgs()

    def listOfSamples(self,pars) :
        return sum([samples.specify(names = samps, weights = jw) for samps,jw in pars['group']],[])

    def listOfSampleDictionaries(self) :
        return [samples.HT.ht, samples.Muon.muon, samples.Photon.photon, samples.Electron.electron, samples.DoubleMu.mumu]

    def mainTree(self) :
        return ("lumiTree","tree")

    def otherTreesToKeepWhenSkimming(self) :
        return []
