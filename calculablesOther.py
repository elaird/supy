from wrappedChain import *

class localEntry(wrappedChain.calculable) :
    def update(self,localEntry) :
        self.value = localEntry

class entry(wrappedChain.calculable) :
    def update(self,localEntry) :
        self.value = self.source.entry

class chain_access(wrappedChain.calculable) :
    def name(self) : return "chain"
    def update(self,ignored) : self.value = self.source.__wrappedChain_chain

