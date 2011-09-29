import ROOT as r

class cutSorter(object) :

    @classmethod
    def fromOrganizer(cls, organizer, iStep, iSample) :
        ConfigCounts,Names,MoreNames = tuple([organizer.steps[iStep][key][iSample]
                                              for key in ["cutSorterConfigurationCounts","cutSorterNames","cutSorterMoreNames"]])
        return cls.fromHistograms(ConfigCounts,Names,MoreNames)

    @classmethod
    def fromHistograms(cls, ConfigCounts, Names, MoreNames) :
        nCuts = Names.GetNbinsX()
        counts = [ ConfigCounts.GetBinContent(i+1) for i in range(1<<nCuts)]
        cutSpecs = [ ( Names.GetXaxis().GetBinLabel(i+1),
                       MoreNames.GetXaxis().GetBinLabel(i+1)  )  for i in reversed(range(nCuts)) ]
        return cls(cutSpecs, counts)

    def __init__(self,cutSpecs,counts) :
        self.cutSpecs = cutSpecs
        self.counts = counts
        self.updated = False
        self.inversions = 0
        for restriction in ["groups","blocks","runs","relatives","absolutes"] :
            setattr(self, restriction, [])

    def printCutIndices(self) :
        for i in range(len(self.cutSpecs)) :
            print "{0:<5}{1:<30}{2:<50}".format(*((i,)+self.cutSpecs[i]))

    def count(self, bit, previous, veto=False) :
        return sum([ count * ((((bits^self.inversions)>>bit)&1)^veto) * ((bits&previous==previous))
                     for bits,count in enumerate(self.counts)])

    def appendBlock(self,bitset) :
        self.blocks.append( reduce(lambda i,j: i|(1<<j), bitset,0) )
        return

    def update(self) :
        if self.updated : return
        self.indices = []
        self.orderedCounts = [None] * len(self.cutSpecs)
        self.orderedVetos = [None] * len(self.cutSpecs)
        prev = 0
        for unused in range(len(self.cutSpecs)) :
            block = reduce(lambda b1,b2: b1|(b2&~prev) if b2&(b1|prev) else b1, self.blocks, 0)
            searchbits = block if block else ~prev
            iSearch = filter(lambda i: (1<<i)&searchbits, range(len(self.cutSpecs)))
            
            surviveIndex = [(self.count(i, prev),i) for i in iSearch]
            survive,index = min(surviveIndex)
            
            
            self.orderedCounts[index] = survive
            self.orderedVetos[index] = ( (self.orderedCounts[self.indices[-1]] if prev else sum(self.counts))
                                         - survive )
            self.indices.append(index)
            
            prev|=(1<<index)
        self.updated = True
        self.orderedConfigCountIndices = self.bitSort(self.indices, range(len(self.counts)))
        return

    def bitSort(self, bitorder, aList) :
        if not bitorder :
            return aList
        else :
            bit = bitorder[0]
            on = []
            off = []
            for n in aList :
                if (n>>bit)&1 : on.append(n)
                else : off.append(n)
            return self.bitSort(bitorder[1:],on) + self.bitSort(bitorder[1:],off)

    def histogram(self) :
        import array

        binHeights = [self.counts[i] for i in self.orderedConfigCountIndices]
        yBoundaries = array.array('d',[sum(binHeights[:i]) for i in range(len(binHeights)+1)])
        yBoundaries[0] = 0.5
        histo = r.TH2D("histo",";step;events",len(self.indices),array.array('d',range(len(self.indices)+1)), len(binHeights), yBoundaries)
        bits = len(self.indices)
        for i in range(len(binHeights)) :
            for j in range(bits):
                histo.SetBinContent(j+1,i+1,(i>>(bits-j-1))&1)
        return histo
