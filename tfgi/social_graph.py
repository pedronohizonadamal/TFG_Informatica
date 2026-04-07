import numpy as np

POPULATION = 10

INITIAL_SIZE = 5

NUMBER_OF_FRIENDS = 3

P = 0.3 # value 1
Q = 0.4 # value -1
R = 1-P-Q

P_VALUE = 1
Q_VALUE = -1
R_VALUE = 0

class SocialGraph:
    pass

class SocialGraph:
    opinions = np.empty(POPULATION, dtype=int) 
    adjacency = np.zeros((POPULATION, POPULATION), dtype=int)
    size = POPULATION
    edges = set() # Symmetric (tuple set)

    def __init__(self, population=POPULATION, complete=False, initial_graph:SocialGraph=None):
        
        self.size = population
        self.opinions = np.empty(population, dtype=int)
        
        if complete:
            self.adjacency = np.ones((population, population), dtype=int)
            for i in range(population):
                for j in range(i, population): # (i,i) ?
                    self.edges.add((i,j))
        else:
            self.adjacency = np.zeros((population, population), dtype=int)
        
        if initial_graph != None:
            size_of_initial = len(initial_graph.opinions)
            self.edges = initial_graph.edges
            for i in range(size_of_initial):
                self.opinions[i] = initial_graph.opinions[i]
                for j in range(size_of_initial):
                    self.set_adjacency(i, j, initial_graph.adjacency[i][j], addEdge=False)


    def __str__(self):
        return f'SocialGraph(opinions:{self.opinions}, edges:{self.edges})'

    def set_opinion(self, i, value):
        self.opinions[i] = value

    # Sets (i,j); if symm: (j,i)s
    def set_adjacency(self, i, j, value, symm=False, addEdge=True):
        self.adjacency[i][j] = value
        if addEdge:
            self.edges.add((j, i))
                
        if symm:
            self.adjacency[j][i] = value
    
    def roll_opinion(self, i):
        self.opinions[i] = np.random.choice([P_VALUE, Q_VALUE, R_VALUE], p=[P, Q, R])

    def roll_new_adjacency(self, i, adjacency):
        new_adjacency = np.random.choice(range(i), size=adjacency, replace=False)
        for j in new_adjacency:
            self.set_adjacency(i, int(j), 1, symm=True)
        
    def initial_graph():
        ig = SocialGraph(INITIAL_SIZE, complete=True)
        p = int(np.round(P*INITIAL_SIZE))
        q = int(np.round(Q*INITIAL_SIZE))
        threshold = min(p+q, INITIAL_SIZE)
        for i in range(p):
            ig.opinions[i] = 1
        for j in range(p, threshold):
            ig.opinions[j] = -1
        for k in range (threshold, INITIAL_SIZE):
            ig.opinions[k] = 0
        return ig

def generate_graph_recursive(step=0, population=POPULATION, sg=None):
    if step==0:
        ig = SocialGraph.initial_graph()
        sg = SocialGraph(population, initial_graph=ig)
        step = ig.size
    
    sg.roll_opinion(step)
    sg.roll_new_adjacency(step, NUMBER_OF_FRIENDS)
    
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
        sg.roll_new_adjacency(i, NUMBER_OF_FRIENDS)

    return sg

print(generate_graph())



