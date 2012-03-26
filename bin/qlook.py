#!/usr/bin/env python

import subprocess,collections,os
from supy import sites,utils

def lines(cmd) :
    return utils.getCommandOutput(cmd)["stdout"].split("\n")

def stats(l) :
    run  = collections.defaultdict(lambda : collections.defaultdict(int))
    wait = collections.defaultdict(int)

    blackList = vars["userBlackList"] if "userBlackList" in vars else []
    for line in l :
        d = dict(zip(sites.info(key = "queueHeaders"), line.split()))
        if vars["user"] in d and d[vars["user"]] in blackList : continue
        if vars["state"] not in d : continue
        if "queueName" in vars and not vars["queueName"] in d[vars["queue"]] : continue
        
        if d[vars["state"]]==vars["run"] :
            queue = d[vars['queue']] if 'queue' in vars else ""
            run[d[vars["user"]]][queue[:7]]+=1
        else :
            wait[d[vars["user"]]]+=1
    return run,wait

def summary(run, wait) :
    def printLine(user, rsd, w) :
        on,off = ('\033[91m','\033[0m') if user==os.environ["USER"] else ('','')
        rs = [ rsd[queue] for queue in queues ]
        formRs = '(%s)'%','.join(str(r).rjust(3) for r in rs)
        print "|%s%17s %s %6d %6d%s|"%(on, user, formRs, w, sum(rs)+w, off)

    queues = sorted(set(sum([user.keys() for user in run.values()],[])))

    if any(queues) : print '(%s)'%', '.join(queues)
    print "+------------------%s---------------+"%(len(queues)*"----")
    print "|      user        %sr  other  total|"%(len(queues)*"    ")
    print "|------------------%s---------------|"%(len(queues)*"----")
    runTotals  = collections.defaultdict(int)
    waitTotal = 0
    for user in sorted(list(set(run.keys()+wait.keys()))) :
        for q in queues : runTotals[q] += run[user][q]
        waitTotal+=wait[user]
        printLine(user, run[user], wait[user])
    print "|------------------%s---------------|"%(len(queues)*"----")
    printLine("all", runTotals, waitTotal)
    print "+------------------%s---------------+"%(len(queues)*"----")

def sample(l) :
    print "\n".join(l)[:-1]

vars = sites.info(key = "queueVars")
summary(*stats(lines(vars["summary"])))
sample(lines(vars["sample"]))
