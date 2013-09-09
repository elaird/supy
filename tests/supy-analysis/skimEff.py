import configuration
import supy


def params():
    return [(0, 100), (20, 100), (50, 100), (90, 100)]


def var():
    return "run"


def stem(min, max):
    return "%d_%d" % (min, max)


def fileName(min, max):
    dir = "%s/%s" % (supy.whereami(), configuration.localpath())
    return '%s/skim_%s.root' % (dir, stem(min, max))


class skimEff(supy.analysis):
    def listOfSteps(self, _):
        return [supy.steps.filters.value(var(), min=91, max=100)]


    def listOfCalculables(self, _):
        return []


    def listOfSampleDictionaries(self):
        h = supy.samples.SampleHolder()
        for min, max in params():
            xs = 1.0*(max-min)  # as in docs/skimEfficiency.txt
            h.add(stem(min, max), '["%s"]' % fileName(min, max), xs=xs)
        return [h]


    def listOfSamples(self, _):
        w = supy.calculables.other.value("run")
        out = []
        for min, max in params():
            out += supy.samples.specify(names=stem(min, max), weights=w)
        return out
