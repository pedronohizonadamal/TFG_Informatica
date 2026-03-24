import networkx as nx
import numpy as np

POPULATION = 1000

INITIAL_SIZE = 10

NUMBER_OF_FRIENDS = 3

STEPS = 50

P = 0.6 # value 1
Q = 0.3 # value -1
R = 1-P-Q

P_VALUE = 1
Q_VALUE = -1
R_VALUE = 0

# From R
DELTA_R_P = 0.2
DELTA_R_Q = 0.2

# To R
DELTA_P_R = 0.1
DELTA_Q_R = 0.1

# From P or Q
DELTA_P_Q = 0.1
DELTA_Q_P = 0.1

GAMMA_P = DELTA_R_P/DELTA_P_R
GAMMA_Q = DELTA_R_Q/DELTA_Q_R

K = 0.5 # Positive means towards P, negative, Q

def roll_opinion():
    return int(np.random.choice([P_VALUE, Q_VALUE, R_VALUE], p=[P, Q, R]))

def generate_initial_graph():
    initial_graph = nx.complete_graph(INITIAL_SIZE)
    for node in initial_graph.nodes():
        initial_graph.nodes[node]["opinion"] = roll_opinion()
    return initial_graph

def probability_function(G):
    number_of_edges = G.number_of_edges()
    prob = [float(G.degree(node))/(2*number_of_edges) for node in G.nodes()]
    # Por si redondeando el float se generase una función inválida
    s = sum(prob)
    if s != 1:
        prob[-1] = 1 - s + prob[-1]
    return prob

def generate_graph():
    G = nx.Graph(generate_initial_graph())

    for i in range(INITIAL_SIZE, POPULATION):
        connections = np.random.choice(G.nodes(), size=NUMBER_OF_FRIENDS, replace=False, p=probability_function(G)).tolist()
        G.add_node(i, opinion=roll_opinion())
        G.add_edges_from([(j,i) for j in connections])
    
    return G

def count_opinions(G):
    opinions = {
        P_VALUE:0,
        Q_VALUE:0,
        R_VALUE:0
    }
    
    for node in G.nodes():
        opinions[G.nodes[node]["opinion"]] += 1
    
    return opinions

def update_opinion_probability(opinion, p_neighbors, q_neighbors, r_neighbors):
    
    neighbors = p_neighbors + q_neighbors + r_neighbors
    
    if opinion == P_VALUE:    
        change_q = DELTA_P_Q * q_neighbors
        change_r = DELTA_P_R * q_neighbors
        if K > 0:
            probability = [(neighbors-change_q-change_r+K)/(neighbors+K), change_q/(neighbors+K), change_r/(neighbors+K)]
        else:
            k = abs(K)
            probability = [(neighbors-change_q-change_r)/(neighbors+k), (change_q+k)/(neighbors+k), change_r/(neighbors+k)]
            
    elif opinion == Q_VALUE:
        change_p = DELTA_Q_P * p_neighbors
        change_r = DELTA_Q_R * p_neighbors
        if K > 0:
            probability = [(change_p+K)/(neighbors+K), (neighbors-change_p-change_r)/(neighbors+K), change_r/(neighbors+K)]
        else:
            k = abs(K)
            probability = [change_p/(neighbors+k), (neighbors-change_p-change_r+k)/(neighbors+k), change_r/(neighbors+k)]
    
    else:
        change_p = DELTA_R_P * p_neighbors
        change_q = DELTA_R_Q * q_neighbors
        if K > 0:
            probability = [(change_p+K)/(neighbors+K), change_q/(neighbors+K), (neighbors-change_p-change_q)/(neighbors+K)]        
        else:
            k = abs(K)
            probability = [change_p/(neighbors+k), (change_q+k)/(neighbors+k), (neighbors-change_p-change_q)/(neighbors+k)]
        
    # float shenanigans
    s = sum(probability)
    if s != 1:
        probability[0] = 1 - s + probability[0]
        
    return probability

def new_opinions(G):
    for node in G.nodes():
        tally = {
            P_VALUE:0,
            Q_VALUE:0,
            R_VALUE:0
        }
        neighbors = nx.all_neighbors(G, node)
        for neighbor in neighbors:
            tally[G.nodes[neighbor]["opinion"]] += 1
        opinion = G.nodes[node]["opinion"]
        G.nodes[node]["new_opinion"] = int(np.random.choice([P_VALUE, Q_VALUE, R_VALUE], \
            p=update_opinion_probability(opinion, tally[P_VALUE], tally[Q_VALUE], tally[R_VALUE])))     
    for node in G.nodes():
        G.nodes[node]["opinion"] = G.nodes[node]["new_opinion"]
        
    return G
        
def simulate_s_steps (G, s=STEPS):
    for _ in range(s): 
        G = new_opinions(G)
    return G

G = generate_graph()

print(count_opinions(G))

print(count_opinions(simulate_s_steps(G, 5)))
