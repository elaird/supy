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
             ("char",  "b", "B"),
             ("uchar", "B", "b"),
             ("bool",  "B", "O"),
             ("short", "h", "S"),
             ("ushort","H", "s"),
             ]

    addresses = {}
    tree = r.TTree(name,name)
    for name,ar,ro in types :
        addresses[name] = array.array(ar,[0])
        tree.Branch(name, addresses[name], "%s/%s"%(name,ro))

        vname = "v_"+name
        addresses[vname] = r.std.vector(name if name[0]!='u' else "unsigned %s"%name[1:])()
        tree.Branch(vname, addresses[vname])

    upper = {"char": 2**7-1, "short": 2**15-1, "int": 2**31-1, "long":2**63-1}

    for iEntry in range(10) :
        for var in ["char","short","int","long"] :
            addresses[var][0]     = iEntry if iEntry<5 else -iEntry
            addresses["u"+var][0] = iEntry if iEntry<5 else upper[var] + iEntry

            vvar = "v_"+var
            addresses[vvar].clear()
            for i in range(iEntry) : addresses[vvar].push_back(-i if i<5 else upper[var]-i )

            if var=="long" : continue # c++ crashes on unsigned long above upper in std.vector
            vvar = "v_u"+var
            addresses[vvar].clear()
            for i in range(iEntry) : addresses[vvar].push_back(i if i<5 else upper[var]+i )

        for var in ["float","double"] :
            addresses[var][0] = iEntry + 0.5
            vvar = "v_"+var
            addresses[vvar].clear()
            for i in range(iEntry) : addresses[vvar].push_back(i)

        addresses["bool"][0] = bool(iEntry%2)
        addresses["v_bool"].clear()
        for i in range(iEntry+3) : addresses["v_bool"].push_back(bool(i%2))

        tree.Fill()
    
    tree.Write()
    file.Close()


if __name__ == "__main__" :
    writeTree()
