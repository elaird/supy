import os

def whereami() :
    return max('/'.join(__file__.split('/')[:-1]), '.')

def runAll(modules = ["integers"]) :
    for item in modules :
        cmd = "python %s/%s/__init__.py"%(whereami(), item)
        print cmd
        os.system(cmd)

if __name__ == "__main__" :
    runAll()
