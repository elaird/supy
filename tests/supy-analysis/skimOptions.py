import configuration
import supy


def var():
    return "run"


def fileName():
    return "%s/%s/skim.root" % (supy.whereami(), configuration.localpath())


class run2(supy.wrappedChain.calculable):
    def update(self, _):
        self.value = self.source["run"]**2


class skimOptions(supy.analysis):
    def parameters(self):
        d = {"mqq": {"mainChain": True,  "otherChains": False, "extraVars": []},
             "moq": {"mainChain": True,  "otherChains": True,  "extraVars": []},
             "moe": {"mainChain": True,  "otherChains": True,  "extraVars": ["run2"]},
             "mqe": {"mainChain": True,  "otherChains": False, "extraVars": ["run2"]},
             #"qqq": {"mainChain": False, "otherChains": False, "extraVars": []},
             #"qoq": {"mainChain": False, "otherChains": True,  "extraVars": []},
             "qoe": {"mainChain": False, "otherChains": True,  "extraVars": ["run2"]},
             "qqe": {"mainChain": False, "otherChains": False, "extraVars": ["run2"]},
             }

        return {"skimmerArgs": self.vary(d),
                "nEventsMax": self.vary({"zero": 0, "all": None}),
                }

    def listOfSteps(self, p):
        return [supy.steps.filters.value(var(), min=91, max=100),
                supy.steps.other.skimmer(**p["skimmerArgs"]),
                ]

    def listOfCalculables(self, _):
        return supy.calculables.zeroArgs(supy.calculables) + [run2()]

    def listOfSampleDictionaries(self):
        h = supy.samples.SampleHolder()
        h.add("sample", '["%s"]' % fileName(), xs=1.0)
        return [h]

    def listOfSamples(self, p):
        return supy.samples.specify(names="sample", nEventsMax=p["nEventsMax"])

