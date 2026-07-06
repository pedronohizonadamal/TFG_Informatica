import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from visualize import visualize_graph, get_colours
from scipy.special import expit 
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
from scipy.integrate import solve_ivp

# N
POPULATION = 100

# Number of simulations to average
SAMPLE_SIZE = 10

COLOURS_PLT = ["firebrick", "olivedrab", "coral", "mediumseagreen", "rebeccapurple", "peru", "hotpink", "deepskyblue", "mediumorchid"]

SAMPLE_VALUES = np.linspace(0.1, 0.9, num=9)

# J
J = 1

# Preferably don't change (10)
# alpha
INITIAL_SIZE = 10

# alpha - 1
NUMBER_OF_NEIGHBORS = INITIAL_SIZE-1

DEFAULT_STEPS = 50
MAX_STEPS = 10000

# Initial Proportion (Keep at 1 decimal, Sum=1)
P_INIT = 0.5 # value 1
Q_INIT = 1-P_INIT # value -1

P_VALUE = 1
Q_VALUE = -1

CORRECTING_FACTOR = 0.2

def generate_initial_graph():
    return nx.complete_graph(INITIAL_SIZE)

# Probabilidad para la generación BA
def probability_function_BA(G):
    number_of_edges = G.number_of_edges()
    prob = [float(G.degree(node))/(2*number_of_edges) for node in G.nodes()]
    # Por si redondeando el float se generase una distribución inválida
    s = sum(prob)
    if s != 1:
        prob[-1] = 1 - s + prob[-1]
    return prob

def generate_graph():
    G = generate_initial_graph()

    for i in range(INITIAL_SIZE, POPULATION):
        connections = np.random.choice(G.nodes(), size=NUMBER_OF_NEIGHBORS, replace=False, p=probability_function_BA(G)).tolist()
        G.add_node(i)
        G.add_edges_from([(j,i) for j in connections])
    
    return G

def set_initial_opinions(G):
    ordering = list(range(POPULATION))
    np.random.shuffle(ordering)
    initial_P_population = int(P_INIT * POPULATION)
    for node in range(initial_P_population):
        G.nodes[ordering[node]]["opinion"] = P_VALUE
    for node in range(initial_P_population, POPULATION):
        G.nodes[ordering[node]]["opinion"] = Q_VALUE
        
def set_initial_opinions(G, initial_p):
    ordering = list(range(POPULATION))
    np.random.shuffle(ordering)
    initial_P_population = int(initial_p * POPULATION)
    for node in range(initial_P_population):
        G.nodes[ordering[node]]["opinion"] = P_VALUE
    for node in range(initial_P_population, POPULATION):
        G.nodes[ordering[node]]["opinion"] = Q_VALUE
        
def get_neighbors(G, node):
    return G.neighbors(node)

def get_neighborhood_overall_opinion(G, node):
    return sum(G.nodes[neighbor]["opinion"] for neighbor in G.neighbors(node))

def get_local_field(G, node, h):
    return J*get_neighborhood_overall_opinion(G, node) + h

def get_signed_fields(G, h):
    return np.array([G.nodes[node]["opinion"]*get_local_field(G, node, h) for node in G.nodes], dtype=float)

def get_flip_likelyhoods(G, beta, h):
    return expit(-2*beta*get_signed_fields(G, h))

def update_opinions(G, beta, h):
    flip_likelyhoods = get_flip_likelyhoods(G, beta, h)
    for node in G.nodes:
        if np.random.rand() <= flip_likelyhoods[node]:
            G.nodes[node]["opinion"] *= -1
            
def get_number_nodes(G):
    return G.number_of_nodes()
            
def count_opinions(G):
    opinions = {
        P_VALUE:0,
        Q_VALUE:0,
    }
    for node in G.nodes():
        opinions[G.nodes[node]["opinion"]] += 1
    return opinions            

def print_opinions(G):
    print(count_opinions(G)) 

def print_opinions_and_step(G, step):
    print(step, count_opinions(G))     
    
def get_k():
    return (INITIAL_SIZE-1)*(2*POPULATION-INITIAL_SIZE)/POPULATION

def get_h(p):
    return get_k()*(2*p*(1-p)*np.log(p/(1-p))/CORRECTING_FACTOR-2*p+1)

def get_h_beta(p, beta):
    return 1/(2*beta)*np.log(p/(1-p))-get_k()*(2*p-1)

def get_beta(p):
    return 1/(4*get_k()*p*(1-p))*CORRECTING_FACTOR

def get_degree(G):
    return G.degree()

def get_degree(G, node):
    return get_degree(G)[node]

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

# solve_ivp trabaja con vectores. 
# p[0] es la primera coordenada de nuestro vector
# aunque en realidad sea un escalar.
def F(t,p):
    u = 2*FBETA*(FH + FK*(2*p[0]-1))
    return 1 - p[0] - 1/(1+np.exp(u))

def update_graph_data(G, data, t_step=1):
    tally = count_opinions(G)
    data[P_VALUE].append((tally[P_VALUE])/POPULATION)
    # data[Q_VALUE].append(1)
    data["t"].append(data["t"][-1] + t_step)

def init_graph_data(G):
    tally = count_opinions(G)
    data = {
        P_VALUE:[tally[P_VALUE]/POPULATION],
        # Q_VALUE:[1],
        "t":[0]
    }
    return data

def plot_frequency(data):
    
    #plt.ylim(0,1)
    
    plt.plot(data["degree"], data["count"], color='rebeccapurple', label='average absolute frequency')

    plt.xlabel("Degree")
    plt.ylabel("Number of Nodes")
    plt.title("Average Number of Nodes against Degree.")
    plt.legend()
    plt.show()
    
def plot_frequency_loglog(data):
    
    #plt.ylim(0,1)
    
    plt.loglog(data["degree"], data["count"], color='rebeccapurple', label='average absolute frequency')

    plt.xlabel("Degree")
    plt.ylabel("Number of Nodes")
    plt.title("Average Number of Nodes against Degree (loglog).")
    plt.legend()
    plt.show()

# I hate having to define globals here but...
def plot_population_distribution(data, beta, h, initial_p):
    
    #plt.ylim(0,1)
    
    plt.plot(data["t"], data["mean_pstd"], color='rebeccapurple', label='mean+std')
    plt.plot(data["t"], data["mean"], color='black', label='mean')
    plt.plot(data["t"], data["mean_mstd"], color='rebeccapurple', label='mean-std')
    
    plt.fill_between(data["t"], data["mean_mstd"], data["mean"], color='mediumorchid',
                 alpha=0.5)
    plt.fill_between(data["t"], data["mean"], data["mean_pstd"], color='mediumorchid',
                 alpha=0.5)
    global FBETA,FH,FK
    FBETA=beta
    FH=h
    FK=get_k()
    sol = solve_ivp(F, (0,DEFAULT_STEPS), [initial_p])
    
    plt.plot(sol.t, sol.y[0], color="mediumseagreen", label='numerical solution')

    plt.xlabel("Steps")
    plt.ylabel("Proportion of the Population")
    plt.title("Value of p Over Time [(beta,h)=({:.3f},{:.3f})]".format(beta, h))
    plt.legend()
    plt.show()
    
def plot_absolute_error(data, beta, h, initial_p, p):
    
    #plt.ylim(0,1)
    
    plt.plot(data["t"], np.absolute(np.subtract(np.array(data["mean"], dtype='float32'), p)), color='rebeccapurple', label='simulation error')
    
    global FBETA,FH,FK
    FBETA=beta
    FH=h
    FK=get_k()
    sol = solve_ivp(F, (0,DEFAULT_STEPS), [initial_p])
    
    plt.plot(sol.t, np.absolute(np.subtract(np.array(sol.y[0], dtype='float32'), p)), color="mediumseagreen", label='numerical solution error')

    plt.xlabel("Steps")
    plt.ylabel("Absolute error")
    plt.title("Value of p Over Time [(beta,h)=({:.3f},{:.3f}), (p,c)=({:.1f},{})]".format(beta, h, p, CORRECTING_FACTOR))
    plt.legend()
    plt.show()
    
def plot_population_distribution_ics(data_ics, beta, h):
    
    plt.ylim(0,1)
    
    for i in range(len(SAMPLE_VALUES)):
        plt.plot(data_ics[i]["t"], data_ics[i][P_VALUE], \
            color=COLOURS_PLT[i], label="{:.1f}".format(SAMPLE_VALUES[i]))

    plt.xlabel("Steps")
    plt.ylabel("Proportion of the Population")
    plt.title("Population Distribution Over Time [(beta,h)=({:.3f},{:.3f})]".format(beta, h))
    plt.legend()
    plt.show()
    
def init_graph():
    G = generate_graph()
    set_initial_opinions(G)
    return G

def init_graph(initial_p):
    G = generate_graph()
    set_initial_opinions(G, initial_p)
    return G
 
def simulate (G, beta, h):
    graph_data = init_graph_data(G)
    for i in range(DEFAULT_STEPS): 
        update_opinions(G, beta, h)
        update_graph_data(G, graph_data)
    return graph_data

def simulate_no_data (G, beta, h):
    for i in range(DEFAULT_STEPS): 
        update_opinions(G, beta, h)
    
def simulate_graph (G, beta, h):
    plot_population_distribution(simulate(G,beta,h), beta, h)

def init_simulate_graph(beta, h):
    simulate_graph(init_graph(), beta, h)
    
def init_simulate(beta, h):
    return simulate(init_graph(), beta, h)

def init_simulate(beta, h, initial_p):
    return simulate(init_graph(initial_p), beta, h)
    
def get_mean(samples):
    return np.mean(samples)

# N-ddof
def get_std(samples):
    return np.std(samples, ddof=1)

def convergence_test_1(averages):
    size_of_sample = 10
    tolerance = 0.05
    if len(averages) < size_of_sample:
        return None
    ret = np.array(averages[-size_of_sample-1:])
    if np.max(np.absolute(np.subtract( \
        ret, ret[0]))) < tolerance:
        return ret[0]
    return None

def convergence_test_1_numerical(sol):
    size_of_sample = 10
    tolerance = 0.05
    size_of_domain = len(sol)
    for i in range(size_of_domain-size_of_sample):    
        ret = np.array(sol[i:i+size_of_sample+1])
        if np.max(np.absolute(np.subtract( \
            ret, ret[0]))) < tolerance:
            return (ret[0], i)
    return None
    
def convergence_test_2(averages):
    size_of_sample = 100
    tolerance = 0.1
    if len(averages) < size_of_sample-1:
        return None
    ret = np.array(averages[-size_of_sample:])
    if np.max(np.absolute(np.subtract( \
        ret, ret[0]))) < tolerance:
        return ret[0]
    return None
    
def convergence_test_2_numerical(sol):
    size_of_sample = 100
    tolerance = 0.1
    size_of_domain = len(sol)
    for i in range(size_of_domain-size_of_sample):    
        ret = np.array(sol[i:i+size_of_sample])
        if np.max(np.absolute(np.subtract( \
            ret, ret[0]))) < tolerance:
            return (ret[0], i)
    return None    
    
def get_average_simulation (simulations):
    average_simulation = {}
    average_simulation["t"] = simulations[0]["t"]
    # Since the first step is the zeroth one.
    number_of_steps = simulations[0]["t"][-1]+1
    # minus std, plus std.
    average_simulation["mean_mstd"] = list()
    average_simulation["mean"] = list()
    average_simulation["mean_pstd"] = list()
    for i in range(number_of_steps):
        samples = [simulations[simulation_index][P_VALUE][i] \
                        for simulation_index in range(SAMPLE_SIZE)]
        mean = get_mean(samples)
        std = get_std(samples)
        average_simulation["mean_mstd"].append(mean-std)
        average_simulation["mean"].append(mean)
        average_simulation["mean_pstd"].append(mean+std)
    return average_simulation

def get_average_graph (graphs):
    average_graph = {}
    samples = [count_opinions(graph)[P_VALUE]/POPULATION \
            for graph in graphs]
    mean = get_mean(samples)
    std = get_std(samples)
    average_graph["mean_mstd"] = mean-std
    average_graph["mean"] = mean
    average_graph["mean_pstd"] = mean+std
    return average_graph

def generate_simulations(beta, h):
    return  [init_simulate(beta, h) for _ in range(SAMPLE_SIZE)]

def generate_simulations(beta, h, initial_p):
    return  [init_simulate(beta, h, initial_p) for _ in range(SAMPLE_SIZE)]
    
def init_simulate_graph_samples(beta, h):
    plot_population_distribution(get_average_simulation(generate_simulations(beta, h)), beta, h)
    
def init_simulate_graph_samples(beta, h, initial_p):
    plot_population_distribution(get_average_simulation(generate_simulations(beta, h, initial_p)), beta, h, initial_p)
        
# ics == initial conditions        
def init_simulate_graph_samples_ics (beta, h):
    average_simulations = list() 
    for i in range(len(SAMPLE_VALUES)):
        P_INIT = SAMPLE_VALUES[i]
        average_simulations.append(get_average_simulation(generate_simulations(beta, h, SAMPLE_VALUES[i])))
    plot_population_distribution_ics(average_simulations, beta, h)
    
def get_absolute_frequency(G):
    tally = {
        "degree": [INITIAL_SIZE-1],
        "count": [0]
    }
    for node in G.nodes:
        current_degree = G.degree[node]
        if current_degree > tally["degree"][-1]:
            for i in range( tally["degree"][-1]+1, current_degree+1):
                tally["degree"].append(i)
                tally["count"].append(0)
        tally["count"][current_degree-INITIAL_SIZE+1]+=1
    return tally

def get_absolute_average_frequency(graphs):
    tally = {
        "degree": [INITIAL_SIZE-1],
        "count": [0]
    }
    for node in range(POPULATION):
        for graph in range(SAMPLE_SIZE):
            current_degree = graphs[graph].degree[node]
            if current_degree > tally["degree"][-1]:
                for i in range(tally["degree"][-1]+1, current_degree+1):
                    tally["degree"].append(i)
                    tally["count"].append(0)
            tally["count"][current_degree-INITIAL_SIZE+1]+=1/SAMPLE_SIZE
    return tally
    
def get_initial_graphs(initial_condition):
    return [init_graph(initial_condition) for _ in range(SAMPLE_SIZE)]   
   
def simulate_until_convergence_beta(beta):
    initial_condition = 0.7
    p_star = 0.7
    h = get_h_beta(p_star, beta)
    average_graph = list()
    graphs = get_initial_graphs(initial_condition)
    average_graph.append(get_average_graph(graphs)["mean"])
    for i in range(1, MAX_STEPS+1):
        for graph in graphs:
            update_opinions (graph, beta, h) 
        average_graph.append(get_average_graph(graphs)["mean"])
        if i < 500:
            p_star = convergence_test_1(average_graph)
            if p_star != None:
                return (p_star, i-10)
        else:
            p_star = convergence_test_2(average_graph)
            if p_star != None:
                return (p_star, i-99)     
    return (-0.1,-1)

def test_solution_convergence(solution_image):
    for i in range(MAX_STEPS):
        ret = convergence_test_1_numerical(solution_image) if i<500 \
            else convergence_test_2_numerical(solution_image)
        if ret != None:
            return ret
    return (-0.1, -1)

def simulate_until_convergence():
    simulation = {}
    B = [1, 2, 5]
    M = [0.001, 0.01, 0.1, 1, 10, 100]
    global FBETA, FH, FK
    FK = get_k()
    beta_space = sorted([b*m for b in B for m in M])
    simulation["betas"] = beta_space
    for beta in beta_space:
        simulation[beta] = {}
        simulation[beta]["BA"] = simulate_until_convergence_beta(beta)
        y = [0.7]
        FBETA = beta
        FH = get_h_beta(0.7, beta)
        sol = solve_ivp(F,(0, MAX_STEPS),y)
        simulation[beta]["H"] = test_solution_convergence(sol.y[0])
    return simulation

def plot_convergence(data):
    betas = data["betas"]

    ba_vals = [data["BA"][b][0] for b in betas]
    h_vals  = [data["H"][b][0] for b in betas]

    x = np.arange(len(betas))

    plt.figure(figsize=(14,5))

    plt.bar(x - 0.2, ba_vals, width=0.4, color='rebeccapurple', label='simulation convergence')
    plt.bar(x + 0.2, h_vals,  width=0.4, color='mediumseagreen', label='numerical convergence')

    plt.xticks(x, [str(b) for b in betas], rotation=45)
    plt.xlabel("Beta")
    plt.ylabel("Convergence value")
    plt.title("P* Convergence per Beta")
    plt.legend()

    plt.tight_layout()
    plt.show()

def plot_time(data):
    betas = data["betas"]

    ba_steps = [data["BA"][b][1] for b in betas]
    h_steps  = [data["H"][b][1] for b in betas]

    x = np.arange(len(betas))

    plt.figure(figsize=(14,5))

    plt.bar(x - 0.2, ba_steps, width=0.4, color='rebeccapurple', label='simulation steps')
    plt.bar(x + 0.2, h_steps,  width=0.4, color='mediumseagreen', label='numerical steps')

    plt.xticks(x, [str(b) for b in betas], rotation=45)
    plt.xlabel("Beta")
    plt.ylabel("Steps to Convergence")
    plt.title("Number of Steps to Convergence")
    plt.legend()

    plt.tight_layout()
    plt.show()  
            
def manage_data(data):
    
    #plt.ylim(0,1)
    
    betas = data["betas"]
    
    relevant_data = [(data[beta]["BA"][0], \
        data[beta]["BA"][1], \
        data[beta]["H"][0], \
        data[beta]["H"][1]) for beta in betas]
    
    number_of_betas = len(betas)
    
    plot_convergence([relevant_data[i][0] for i in range(number_of_betas)], 
                     [relevant_data[i][2] for i in range(number_of_betas)], 
                     betas)   
    
    plot_time([relevant_data[i][1] for i in range(number_of_betas)], 
            [relevant_data[i][3] for i in range(number_of_betas)], 
            betas) 
    
def simulate_until_convergence_test():
    simulation = {}
    B = [1, 2, 5]
    M = [0.001, 0.01, 0.1, 1, 10, 100]
    global FBETA, FH, FK
    FK = get_k()
    beta_space = sorted([b*m for b in B for m in M])
    simulation["betas"] = beta_space
    for beta in beta_space[:6]:
        simulation[beta] = {}
        simulation[beta]["BA"] = simulate_until_convergence_beta(beta)
        y = [0.2]
        FBETA = beta
        FH = get_h_beta(0.7, beta)
        sol = solve_ivp(F,(0, MAX_STEPS),y)
        simulation[beta]["H"] = test_solution_convergence(sol.y[0])
    return simulation
        
def manage_data_test(data):
    
    print(data)
    return
    #plt.ylim(0,1)
    
    betas = data["betas"]
    
    relevant_data = [(data[beta]["BA"][0], \
        data[beta]["BA"][1], \
        data[beta]["H"]["p_star"], \
        data[beta]["H"]["i"]) for beta in betas]
    
    number_of_betas = len(betas)
    
    plot_convergence([relevant_data[i][0] for i in range(number_of_betas)], \
                     [relevant_data[i][2] for i in range(number_of_betas)], \
                     betas)   
    
    plot_time([relevant_data[i][1] for i in range(number_of_betas)], \
            [relevant_data[i][3] for i in range(number_of_betas)], \
            betas)     
    
    
    
    

if __name__ == "__main__":
    #count_total_degree(G)
    
    # p=0.2 0.4
    # BETA = 25/(8*get_k())*0.4
    # h=get_k()*(0.32*np.log(1/4)+0.6)
    
    # p=0.5 2/get_k()*0.3??
    
    p=0.7

    P_INIT = 0.2
    
    initial_p = P_INIT
    
    manage_data_test(simulate_until_convergence())
    
    results = {
        "betas": [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500],

        "BA": {
            0.001: (0.716, 11),
            0.002: (0.694, 1),
            0.005: (0.695, 3),
            0.01:  (0.689, 1),
            0.02:  (0.703, 1),
            0.05:  (0.725, 4),
            0.1:   (0.752, 5),
            0.2:   (0.102, 5),
            0.5:   (0.0, 3),
            1:     (0.004, 3),
            2:     (0.0, 3),
            5:     (0.049, 2),
            10:    (0.04, 2),
            20:    (0.0, 3),
            50:    (0.034, 2),
            100:   (0.0, 3),
            200:   (0.001, 3),
            500:   (0.032, 2),
        },

        "H": {
            0.001: (0.6717961347524566, 4),
            0.002: (0.6717641189232013, 4),
            0.005: (0.6709264169013353, 4),
            0.01:  (0.6690204813465995, 4),
            0.02:  (0.6651478637063919, 4),
            0.05:  (0.6866429232976784, 5),
            0.1:   (0.04940520459370717, 3),
            0.2:   (0.029125470688802016, 3),
            0.5:   (0.029675871024286392, 3),
            1:     (0.029675908775380212, 3),
            2:     (0.02967590877829729, 3),
            5:     (0.02967590877829729, 3),
            10:    (0.02967590877829729, 3),
            20:    (0.02967590877829729, 3),
            50:    (0.02967590877829729, 3),
            100:   (0.02967590877829729, 3),
            200:   (0.02967590877829729, 3),
            500:   (0.02967590877829729, 3),
        }
    }
    
    #plot_convergence(results)
    #plot_time(results)
    
    # 
    
    '''
    G = init_graph(initial_p)
    graph_nodes_against_number_of_neighbors_with_ids(G)
    for _ in range(DEFAULT_STEPS):
        update_opinions(G, get_beta(p), get_h(p))
    print_opinions(G)
    graph_nodes_against_number_of_neighbors_with_ids(G)
    '''
    #beta = get_beta(p)
    #h = get_h(p)
    
    # Result from a previous simulation.
    data = {
        "betas": [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5,
                1, 2, 5, 10, 20, 50, 100, 200, 500],

        "BA": {
            0.001: (0.6976, 1),
            0.002: (0.6813, 1),
            0.005: (0.6617, 1),
            0.01:  (0.6762, 2),
            0.02:  (0.6695, 3),
            0.05:  (0.3495, 3),
            0.1:   (0.0589, 2),
            0.2:   (0.0109, 1),
            0.5:   (0.0002, 1),
            1:     (0.0, 1),
            2:     (0.0, 1),
            5:     (0.0, 1),
            10:    (0.0, 1),
            20:    (0.0, 1),
            50:    (0.0, 1),
            100:   (0.0, 1),
            200:   (0.0, 1),
            500:   (0.0, 1),
        },

        "H": {
            0.001: (0.671794371156176, 4),
            0.002: (0.6717616569120524, 4),
            0.005: (0.6708371246881168, 4),
            0.01:  (0.6688381066166701, 4),
            0.02:  (0.664780462325078, 4),
            0.05:  (0.6740946368725336, 5),
            0.1:   (0.044851461594734056, 3),
            0.2:   (0.029243405293949525, 3),
            0.5:   (0.029675892562779103, 3),
            1:     (0.029675908777236783, 3),
            2:     (0.02967590877829729, 3),
            5:     (0.02967590877829729, 3),
            10:    (0.02967590877829729, 3),
            20:    (0.02967590877829729, 3),
            50:    (0.02967590877829729, 3),
            100:   (0.02967590877829729, 3),
            200:   (0.02967590877829729, 3),
            500:   (0.02967590877829729, 3),
        }
    }
    
    #plot_convergence(data)
    #plot_time(data)
    
    # plot_absolute_error(get_average_simulation(generate_simulations(beta, h, initial_p)), beta, h, initial_p, p)
    
    # -> init_simulate_graph_samples(get_beta(p), get_h(p), P_INIT)
    
    
    #print("Counting neighbors:", count_neighbors_per_opinion(G))
    
    # print("Counting opinions:", count_opinions(G))
    
    #      steps_to_takeover(G)
    
    #simulate_s_steps(G)
    
    #graph_nodes_against_number_of_neighbors(G)
    
    #graph_nodes_against_number_of_neighbors_with_ids(G)
    
    # visualize_graph(G)
    
    # graph_nodes_against_number_of_neighbors_with_ids(G)

    # print(count_opinions(G))

    # print(count_opinions(simulate_s_steps(G, 5)))

    #simulate_s_steps(G)
    
    #print("Counting neighbors:", count_neighbors_per_opinion(G))
