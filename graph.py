import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from visualize import visualize_graph, get_colours

POPULATION = 500

# Preferably don't change
INITIAL_SIZE = 10

# m
NUMBER_OF_NEIGHBORS = INITIAL_SIZE-1

STEPS = 50

# Initial Proportion (Keep at 1 decimal, Sum=1)
P_PROB = 0.6 # value 1
Q_PROB = 0 # value -1
R_PROB = 1-P_PROB-Q_PROB

P_VALUE = 1
Q_VALUE = -1
R_VALUE = 0

K = 0 # Positive means towards P, negative, Q

# K > 0
KRAFT_BROADCASTER = 0.9
BROADCASTER_OPINION = P_VALUE

def roll_opinion():
    return int(np.random.choice([P_VALUE, Q_VALUE, R_VALUE], p=[P_PROB, Q_PROB, R_PROB]))

def generate_initial_graph():
    initial_graph = nx.complete_graph(INITIAL_SIZE)
    for node in initial_graph.nodes():
        initial_graph.nodes[node]["opinion"] = roll_opinion()
    return initial_graph

def probability_function(G):
    number_of_edges = G.number_of_edges()
    prob = [float(G.degree(node))/(2*number_of_edges) for node in G.nodes()]
    # Por si redondeando el float se generase una distribución inválida
    s = sum(prob)
    if s != 1:
        prob[-1] = 1 - s + prob[-1]
    return prob

def generate_graph():
    G = nx.Graph(generate_initial_graph())

    for i in range(INITIAL_SIZE, POPULATION):
        connections = np.random.choice(G.nodes(), size=NUMBER_OF_NEIGHBORS, replace=False, p=probability_function(G)).tolist()
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
        change_q = (q_neighbors + KRAFT_BROADCASTER) / (neighbors + KRAFT_BROADCASTER)
        change_p = 1 - change_q
        change_r = 0
                  
    elif opinion == Q_VALUE:
        change_p = p_neighbors / (neighbors + KRAFT_BROADCASTER)
        change_q = 1 - change_p
        change_r = 0
           
    else:
        change_p = p_neighbors / (neighbors + KRAFT_BROADCASTER)
        change_q = (q_neighbors + KRAFT_BROADCASTER) / (neighbors + KRAFT_BROADCASTER)
        change_r = 1 - change_p - change_q
        
    probability = [change_p, change_q, change_r]        
           
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

def count_neighbors_per_opinion(G):
    
    tally = {
        P_VALUE: 0,
        Q_VALUE: 0,
        R_VALUE: 0
    }
    s = 0
    previous_node = -1
    for node in G.nodes():
        number_of_neighbors = len(list(nx.all_neighbors(G, node)))
        s += number_of_neighbors
        tally[G.nodes[node]["opinion"]] += number_of_neighbors
    
    return tally

def sort_nodes_by_number_of_neighbors(G):
    # https://realpython.com/sort-python-dictionary/
    neighbors_per_node = {}
    colour_list = get_colours(G)
    for node in G.nodes():
        neighbors_per_node[node] = (len(list(nx.all_neighbors(G, node))), colour_list[node])
    return dict(sorted(neighbors_per_node.items(), key=lambda item: -item[1][0]))

# Ordena según el número (decreciente) de vecinos
def graph_nodes_against_number_of_neighbors(G):
    # https://pythonguides.com/matplotlib-bar-chart-different-colors-python/
    sorted_nodes = sort_nodes_by_number_of_neighbors(G)
    
    node_info = list(sorted_nodes.values())
    
    x_axis = range(len(sorted_nodes))
    counts = [count[0] for count in node_info]
    colors = [colour[1] for colour in node_info]
    
    plt.bar(x_axis, counts, color=colors)
    plt.title("Nodes Against Number of Neighbors")
    plt.xlabel("Node Index")
    plt.ylabel("Number of Friends")
    plt.show()
    
# Ordena según el orden de creación    
def graph_nodes_against_number_of_neighbors_with_ids(G):
    # https://pythonguides.com/matplotlib-bar-chart-different-colors-python/
    sorted_nodes = sort_nodes_by_number_of_neighbors(G)
    
    node_info = list(sorted_nodes.values())
    
    x_axis = list(sorted_nodes.keys())
    counts = [count[0] for count in node_info]
    colors = [colour[1] for colour in node_info]
    
    plt.bar(x_axis, counts, color=colors)
    plt.title("Nodes Against Number of Neighbors")
    plt.xlabel("Node Index")
    plt.ylabel("Number of Friends")
    plt.show()
    
        
def simulate_s_steps (G, s=STEPS, frequency=STEPS/10):
    for i in range(s): 
        G = new_opinions(G)
        if (i+1)%frequency == 0:
            print(f"After {i+1} steps:", count_opinions(G))
    return G



if __name__ == "__main__":

    G = generate_graph()
    
    
    #print("Counting neighbors:", count_neighbors_per_opinion(G))
    
    print("Counting opinions:", count_opinions(G))
    
    simulate_s_steps(G)
    
    #graph_nodes_against_number_of_neighbors(G)
    
    #graph_nodes_against_number_of_neighbors_with_ids(G)
    
    #visualize_graph(G)

    # print(count_opinions(G))

    # print(count_opinions(simulate_s_steps(G, 5)))

    #simulate_s_steps(G)
    
    #print("Counting neighbors:", count_neighbors_per_opinion(G))