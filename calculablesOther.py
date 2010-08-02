from wrappedChain import *

class localEntry(wrappedChain.calculable) :
    def update(self,localEntry) :
        self.value = localEntry

class entry(wrappedChain.calculable) :
    def update(self,localEntry) :
        self.value = self.source.entry

class chain_access(wrappedChain.calculable) :
    def name(self) : return "chain"
    def update(self,ignored) : self.value = self.source._wrappedChain__chain

class crock(wrappedChain.calculable) :
    def __init__(self,name="crock") : self.__name=name
    def name(self) : return self.__name
    def update(self,localEntry) : self.value = {}
