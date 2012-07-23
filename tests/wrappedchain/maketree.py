import supy,configuration,array,ROOT as r

def filePath() :
    return "%s/%s/typetree.root"%(supy.whereami(),configuration.localpath())

def writeTree() :
    file = r.TFile.Open(filePath(), "RECREATE")
    dir,name = configuration.mainTree()
    file.mkdir(dir)
    file.cd(dir)


    # Note : ROOT and array.array use opposite conventions for upper/lowercase (un)signed
    #         name  array  ROOT
    types = [("int",   "i", "I"),
             ("uint",  "I", "i"),
             ("long",  "l", "L"),
             ("ulong", "L", "l"),
             ("float", "f", "F"),
             ("double","d", "D"),
             ("byte",  "b", "B"),
             ("ubyte", "B", "b"),
             ("bool",  "B", "O"),
             ("short", "h", "S"),
             ("ushort","H", "s"),
             ]

    addresses = {}
    tree = r.TTree(name,name)
    for name,ar,ro in types :
        addresses[name] = array.array(ar,[0])
        tree.Branch(name, addresses[name], "%s/%s"%(name,ro))

    upper = {"byte": 127, "short": 32767, "int": 2147483647, "long":9223372036854775807}

    for iEntry in range(10) :
        for var in ["byte","short","int","long"] :
            addresses[var][0]     = iEntry if iEntry<5 else -iEntry
            addresses["u"+var][0] = iEntry if iEntry<5 else upper[var] + iEntry

        for var in ["float","double"] : addresses[var][0] = iEntry + 0.5
        addresses["bool"][0] = bool(iEntry%2)
        tree.Fill()
    
    tree.Write()
    file.Close()


if __name__ == "__main__" :
    writeTree()
