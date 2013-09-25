import os


def submitBatchJob(jobCmd, indexDict, subScript, jobScript, condorTemplate) :
    jobScriptFileName = "%(base)s/%(tag)s/%(sample)s/job%(iSlice)d.sh"%indexDict
    jobScriptDir = jobScriptFileName[:jobScriptFileName.rfind('/')]
    if not os.path.isdir(jobScriptDir): os.system("mkdir -p %s"%jobScriptDir)
    os.system("cp -p "+jobScript+" "+jobScriptFileName)
    os.system("chmod +x "+jobScriptFileName)
    with open(jobScriptFileName,"a") as file :
        print >>file
        for item in ["PYTHONPATH", "LD_LIBRARY_PATH"] :
            print >>file, "export %s=%s"%(item, os.environ[item])
        print >>file, "cd "+os.environ["PWD"]
        print >>file, jobCmd

    if os.path.exists(condorTemplate):
        condorFileName = jobScriptFileName.replace(".sh", ".condor")
        condorOutputSpec = "/".join([".",
                                     indexDict["analysis"],
                                     indexDict["tag"],
                                     "%s_%d_%d" % (indexDict["sample"],
                                                   indexDict["nSlices"],
                                                   indexDict["iSlice"],
                                                   ),
                                     "",
                                    ])
        pipes = " | ".join(["cat %s" % condorTemplate,
                            "sed s@JOBFLAG@%s@g" % jobScriptFileName,
                            "sed s@OUTFLAG@%s@g" % condorOutputSpec,
                            ])
        os.system(" > ".join([pipes, condorFileName]))
        arg = condorFileName
    else :
        arg = jobScriptFileName
    subCmd = "cd %s; %s %s" % (jobScriptDir, subScript, arg)
    os.system(subCmd)
