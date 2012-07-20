import supy,configuration,array,ROOT as r

def filePath() :
    return "%s/%s/typetree.root"%(supy.whereami(),configuration.localpath())

def writeTree() :
    file = r.TFile.Open(filePath(), "RECREATE")
    dir,name = configuration.mainTree()
    file.mkdir(dir)
    file.cd(dir)

    tree = r.TTree(name,name)

    # Note : ROOT and array.array use opposite conventions for upper/lowercase (un)signed
    addresses = {}
    addresses["int"] = array.array('i',[0])
    addresses["uint"] = array.array('I',[0])
    addresses["long"] = array.array('l',[0])
    addresses["ulong"] = array.array('L',[0])

    tree.Branch("int", addresses["int"], 'int/I')
    tree.Branch("uint", addresses["uint"], 'uint/i')
    tree.Branch("long", addresses["long"], 'long/L')
    tree.Branch("ulong", addresses["ulong"], 'ulong/l')

    for iEntry in range(10) :
        addresses["int"][0] = iEntry if iEntry<5 else -iEntry
        addresses["long"][0] = iEntry if iEntry<5 else -iEntry
        addresses["uint"][0] = iEntry
        addresses["ulong"][0] = iEntry
        tree.Fill()
    
    tree.Write()
    file.Close()


if __name__ == "__main__" :
    writeTree()
