#!/usr/bin/env python

import subprocess,collections,os

def lines(cmd) :
    stdout,stderr = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE).communicate()
    out = stdout.split("\n")
    return out,["ID","OWNER","SUBMITTED1", "SUBMITTED2", "RUN_TIME","ST","PRI","SIZE","CMD"]

def stats(l, h) :
    run  = collections.defaultdict(int)
    wait = collections.defaultdict(int)

    for line in l[2:] :
        d = dict(zip(h, line.split()))
        if "ST" not in d : continue
        if d["ST"]=="R" :
            run[d["OWNER"]]+=1
        else :
            wait[d["OWNER"]]+=1
    return run,wait

def summary(run, wait) :
    def printLine(user, r, w) :
        on,off = ('\033[91m','\033[0m') if user==os.environ["USER"] else ('','')
        print "|%s%10s %6d %6d %6d%s|"%(on, user, r, w, r+w, off)
        
    print "+-------------------------------+"
    print "|      user      r  other  total|"
    print "|-------------------------------|"
    runTotal  = 0
    waitTotal = 0
    for user in sorted(list(set(run.keys()+wait.keys()))) :
        runTotal += run[user]
        waitTotal+=wait[user]
        printLine(user, run[user], wait[user])
    print "|-------------------------------|"
    printLine("all", runTotal, waitTotal)
    print "+-------------------------------+"

def sample(l, h) :
    print "\n".join(l)[:-1]

summary(*stats(*lines("condor_q -global")))
sample(*lines("condor_q -global -submitter elaird | head"))
