#!/usr/bin/env python

import subprocess,collections,os
from core import configuration,utils

def lines(cmd) :
    return utils.getCommandOutput(cmd)["stdout"].split("\n")

def stats(l) :
    run  = collections.defaultdict(int)
    wait = collections.defaultdict(int)

    for line in l[2:] :
        d = dict(zip(configuration.siteInfo(key = "queueHeaders"), line.split()))
        if vars["state"] not in d : continue
        if "queueName" in vars and not vars["queueName"] in d[vars["queue"]] : continue
        
        if d[vars["state"]]==vars["run"] :
            run[d[vars["user"]]]+=1
        else :
            wait[d[vars["user"]]]+=1
    return run,wait

def summary(run, wait) :
    def printLine(user, r, w) :
        on,off = ('\033[91m','\033[0m') if user==os.environ["USER"] else ('','')
        print "|%s%17s %6d %6d %6d%s|"%(on, user, r, w, r+w, off)
        
    print "+--------------------------------------+"
    print "|      user             r  other  total|"
    print "|--------------------------------------|"
    runTotal  = 0
    waitTotal = 0
    for user in sorted(list(set(run.keys()+wait.keys()))) :
        runTotal += run[user]
        waitTotal+=wait[user]
        printLine(user, run[user], wait[user])
    print "|--------------------------------------|"
    printLine("all", runTotal, waitTotal)
    print "+--------------------------------------+"

def sample(l) :
    print "\n".join(l)[:-1]

vars = configuration.siteInfo(key = "queueVars")
summary(*stats(lines(vars["summary"])))
sample(lines(vars["sample"]))
