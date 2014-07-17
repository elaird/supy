import os
from supy import sites, whereami


__prefix = "%s/sites/%s" % (whereami(), sites.prefix())


def subScript():
    return "%sSub.sh" % __prefix


def jobTemplate():
    return "%sJob.sh" % __prefix


def condorTemplate():
    return  "%sTemplate.condor" % __prefix


def baseDir(fileName=""):
    return fileName[:fileName.rfind('/')]


def condored(script):
    return script.replace(".sh", ".condor") if os.path.exists(condorTemplate()) else script


def jobScriptFull(base="", tag="", sample="", iSlice=None, **_):
    return "/".join([base, tag, sample, "job%d.sh" % iSlice])


def prepareJob(jobCmd, indexDict):
    jobScriptFileName = jobScriptFull(**indexDict)
    jobScriptDir = baseDir(jobScriptFileName)
    if not os.path.isdir(jobScriptDir): os.system("mkdir -p %s"%jobScriptDir)
    with open(jobTemplate()) as template:
        with open(jobScriptFileName, 'w') as script:
            for line in template.readlines():
                if "INSERT_BATCH_SETUP" in line:
                    for item in ["PYTHONPATH", "LD_LIBRARY_PATH"] :
                        print >>script, "export %s=%s"%(item, os.environ[item])
                    print >>script, sites.info(key="extractCommand")
                    print >>script, "cd " + sites.info(key="workingDir")
                else: print >>script, line,
            print >>script, jobCmd.replace(os.environ["PWD"],sites.info(key="workingDir"))
    os.system("chmod +x "+jobScriptFileName)

    condorFileName = condored(jobScriptFileName)
    if condorFileName != jobScriptFileName:
        condorInputSpec = ",".join([os.environ["PWD"]+".tar",])
        condorOutputSpec = "/".join([".",
                                     indexDict["analysis"],
                                     indexDict["tag"],
                                     "%s_%d_%d" % (indexDict["sample"],
                                                   indexDict["nSlices"],
                                                   indexDict["iSlice"],
                                                   ),
                                     "",
                                    ])
        pipes = " | ".join(["cat %s" % condorTemplate(),
                            "sed s@JOBFLAG@%s@g" % jobScriptFileName,
                            "sed s@INFLAG@%s@g" % condorInputSpec,
                            "sed s@OUTFLAG@%s@g" % condorOutputSpec,
                            ])
        os.system(" > ".join([pipes, condorFileName]))

def submitJob(jobScript=""):
    subCmd = "; ".join(["cd %s" % baseDir(jobScript),
                        "%s %s" % (subScript(), condored(jobScript)),
                        ])
    os.system(subCmd)
