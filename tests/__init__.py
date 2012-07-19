import os,supy

class defaultOptions(object) :
    "in normal usage, these are given to supy as options"

    #defaults
    loop = None
    slices = None
    profile = False
    batch = False
    tag = ""
    sample = None
    update = None
    report = None
    jobId = None
    site = None
    tags = None
    samples = None
    omit = ""
    nocheck = False

def run(analysis = None, options = {}) :
    "see supy/bin/supy"

    opts = defaultOptions()
    for key,value in options.iteritems() :
        setattr(opts, key, value)

    assert opts.jobId==None
    assert not opts.batch

    a = analysis(opts)
    a.loop()
    a.mergeAllOutput()
    a.manageSecondaries(opts.update, opts.report)
    if opts.update==None and opts.report==None :
        a.concludeAll()

def runAll(lst = ["integers"]) :
    for item in lst :
        cmd = "cd %s/tests/%s && python __init__.py"%(supy.whereami(), item)
        print cmd
        os.system(cmd)
