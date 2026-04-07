import numpy as np

POPULATION = 1000

INITIAL_SIZE = 10

NUMBER_OF_FRIENDS = 3

P = 0.3 # value 1
Q = 0.6 # value -1
R = 0.1

P_VALUE = 1
Q_VALUE = -1
R_VALUE = 0

class SocialGraph:
    opinions = np.empty(POPULATION, dtype=int) 
    relations = np.zeros((POPULATION, POPULATION), dtype=int)
    size = POPULATION

    def __init__(self, population=POPULATION, complete=False, initial_graph:SocialGraph=None):
        
        self.size = population
        
        self.opinions = np.empty(population, dtype=int)
        
        if complete:
            self.relations = np.ones((population, population), dtype=int)
            return
        
        self.relations = np.zeros((population, population), dtype=int)
        
        if self.initial_graph != None:
            size_of_initial = len(initial_graph.opinions)
            for i in range(size_of_initial):
                self.opinions[i] = initial_graph.opinions[i]
                for j in range(size_of_initial):
                    self.set_relation(i, j, initial_graph.relations[i][j])

    def set_opinion(self, i, value):
        self.opinions[i] = value

    # Sets (i,j); if symm: (j,i)s
    def set_relation(self, i, j, value, symm=False):
        self.relations[i][j] = value
        if symm:
            self.relations[j][i] = value
    
    def roll_opinion(self, i):
        self.opinions[i] = np.random.choice([P_VALUE, Q_VALUE, R_VALUE], p=[P, Q, R])

    def roll_new_relations(self, i, relations):
        new_relations = np.random.choice(range(i), size=relations, replace=False)
        for j in new_relations:
            self.set_relation(i, j, 1, symm=True)
        
    def initial_graph():
        ig = SocialGraph(INITIAL_SIZE, True)
        p = int(np.round(P))
        q = int(np.round(Q))
        for i in range(p):
            ig.opinions[i] = 1
        for j in range(p, p+q):
            ig.opinions[j] = -1

def generate_graph_recursive(step=0, population=POPULATION, sg=None):
    if step==0:
        ig = SocialGraph.initial_graph()
        sg = SocialGraph(population, initial_graph=ig)
        step = ig.size
    
    sg.roll_opinion(step)
    sg.roll_new_relations(step, NUMBER_OF_FRIENDS)
    
    step += 1
    if step < population:
        generate_graph_recursive(step=step, population=population, sg=sg)
    else:
        return sg
    
def generate_graph(population=POPULATION):
    
    ig = SocialGraph.initial_graph()
    sg = SocialGraph(population, initial_graph=ig)

    for i in range(ig.size, population):
        sg.roll_opinion(i)
        sg.roll_new_relations(i, NUMBER_OF_FRIENDS)

    return sg



