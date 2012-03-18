class configuration(object) :
    def mainTree(self) :
        return ("/","tree")

    def otherTreesToKeepWhenSkimming(self) :
        return []

    def leavesToBlackList(self) :
        return []

    def ttreecacheMB(self) :
        return 20

    def trace(self) :
        return False

    def nCoresDefault(self) :
        return 4

    def useCachedFileLists(self) :
        return False

    def maxArrayLength(self) :
        return 256

    def computeEntriesForReport(self) :
        return False

    def printNodesUsed(self) :
        return False

    def fakeString(self) :
        return ";FAKE"

    def cppFiles(self) :
        return []
    
    def hadd(self) :
        return "hadd"

    def dictionariesToGenerate(self) :
        return []
