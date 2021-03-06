# !pip install scipy==1.7.1

# !pip install apimoex yfinance ffn PyPortfolioOpt
import pandas as pd # для хранения и анализа
from tqdm import tqdm # для отслеживания прогресса 
import yfinance as yf
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

"""### Загрузка данных"""

data = pd.read_csv('drive/MyDrive/Курсовая/code/ticks2021.csv', sep=';')
data.head()

data = data.set_index('TRADEDATE')

"""### Возвраты"""

returns=data.to_log_returns()
# returns.style.background_gradient(cmap='winter')

"""### Корреляция"""

corr = returns.corr()
# corr.style.background_gradient(cmap='winter')

"""### Ковариация"""

cov = returns.cov()
# cov.style.background_gradient(cmap='winter')

"""### Вычисление доходности, Риска и Коэффициента Шарпа"""

data_param = pd.DataFrame(columns={'Доходность', 'Риск', 'Коэффициент Шарпа'}, index = cov.index)
data_param['Доходность'] = returns.mean()
data_param['Риск'] = [(cov[i][i]**0.5) for i in cov.index]
data_param['Коэффициент Шарпа'] = data_param['Доходность'] / data_param['Риск']
data_param.sort_values(by=['Коэффициент Шарпа']).style.background_gradient(cmap='winter')

"""### Выделение акций с положительным коэффициентом Шарпа"""

Sharp_positive = pd.DataFrame(data_param[data_param['Коэффициент Шарпа'] > 0])
Sharp_positive

Sharp_positive_corr = pd.DataFrame(corr, index=Sharp_positive.index, columns=Sharp_positive.index)

# Sharp_positive_corr.style.background_gradient(cmap='winter')

Sharp_positive_cov = pd.DataFrame(cov, index=Sharp_positive.index, columns=Sharp_positive.index)

# Sharp_positive_cov.style.background_gradient(cmap='winter')

"""### Построение гистограммы кореляции"""

sns.set_theme()

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline

buff = []
for i in corr.index:
    for j in corr.index:
        if i == j:
            break
        buff.append(corr[i][j])
corr_coef = pd.DataFrame(buff)
fig, ax = plt.subplots()
ax.hist(buff, bins=45)
plt.show()

print(corr_coef.mean()[0], corr_coef.var()[0])

"""### Функция вычисляющая максимальное независимое множество"""

import networkx as nx

corr_coef.shape

#G=nx.convert_matrix.from_pandas_edgelist(corr_coef)
stocks = Sharp_positive_corr.index.values
cor_matrix = np.asmatrix(Sharp_positive_corr)
G = nx.from_numpy_matrix(cor_matrix)
G = nx.relabel_nodes(G, lambda x: stocks[x])
G.remove_edges_from(nx.selfloop_edges(G))
G.edges(data=True)

def create_corr_network_1(G):
    #crates a list for edges and for the weights
    edges,weights = zip(*nx.get_edge_attributes(G,'weight').items())

    #positions
    positions=nx.circular_layout(G)
    
    #Figure size
    plt.figure(figsize=(15,15))

    #draws nodes
    nx.draw_networkx_nodes(G,positions,node_color='#DA70D6',
                           node_size=500, alpha=0.8)
    
    #Styling for labels
    nx.draw_networkx_labels(G, positions, font_size=8, 
                            font_family='sans-serif')
    
    #draws the edges
    nx.draw_networkx_edges(G, positions,style='solid')
    
    # displays the graph without axis
    plt.axis('off')
    #saves image
    plt.savefig("part1.png", format="PNG")
    plt.show()

def create_corr_network_2(G, corr_direction, threshold = 0):
    ##Creates a copy of the graph
    H = G.copy()
    
    ##Checks all the edges and removes some based on corr_direction
    for stock1, stock2, weight in G.edges(data=True):
        ##if we only want to see the positive correlations we then delete the edges with weight smaller than 0
        if corr_direction == "positive":
            if weight["weight"] < threshold:
                H.remove_edge(stock1, stock2)
        ##this part runs if the corr_direction is negative and removes edges with weights equal or largen than 0
        else:
            if weight["weight"] >= 0:
                H.remove_edge(stock1, stock2)

    
    #crates a list for edges and for the weights
    edges,weights = zip(*nx.get_edge_attributes(H,'weight').items())

    #positions
    positions=nx.circular_layout(H)
    
    #Figure size
    plt.figure(figsize=(15,15))

    #draws nodes
    nx.draw_networkx_nodes(H,positions,node_color='#DA70D6',
                           node_size=500,alpha=0.8)
    
    #Styling for labels
    nx.draw_networkx_labels(H, positions, font_size=8, 
                            font_family='sans-serif')
        
    #draws the edges
    nx.draw_networkx_edges(H, positions,style='solid')
    
    # displays the graph without axis
    plt.axis('off')
    #saves image
    plt.savefig("part2" + corr_direction + ".png", format="PNG")
    plt.show() 
    return H

G1 = create_corr_network_2(G, corr_direction="positive", threshold = 0.3)

create_corr_network_1(G1)

mis = nx.maximal_independent_set(G1)
mis, len(mis)

"""## Построение портфеля на основе MIS"""

Sharp_positive.loc[mis]

"""#### Pearson"""

def create_corr_network_pirson(returns: pd.DataFrame, threshold = 0, gamma = 0):
    ##Creates a copy of the graph
    cols = returns.columns
    G = nx.empty_graph(n = len(cols))
    K = nx.relabel_nodes(G, lambda x: cols[x])
    H = K.copy()

    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            if not pirson_hypothesis(returns[cols[i]], returns[cols[j]], gamma, threshold):
                H.add_edge(cols[i], cols[j])

    positions=nx.circular_layout(H)
    
    #Figure size
    plt.figure(figsize=(15,15))

    #draws nodes
    nx.draw_networkx_nodes(H,positions,node_color='#DA70D6',
                           node_size=500,alpha=0.8)
    
    #Styling for labels
    nx.draw_networkx_labels(H, positions, font_size=8, 
                            font_family='sans-serif')
        
    #draws the edges
    nx.draw_networkx_edges(H, positions,style='solid')
    
    # displays the graph without axis
    plt.axis('off')
    #saves image
    # plt.savefig("part2" + corr_direction + ".png", format="PNG")
    plt.show() 
    return H

"""#### Sign"""

def create_corr_network_sign(returns: pd.DataFrame, threshold = 0, gamma = 0.1):
    ##Creates a copy of the graph
    cols = returns.columns
    G = nx.empty_graph(n = len(cols))
    K = nx.relabel_nodes(G, lambda x: cols[x])
    H = K.copy()

    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            if not sign_hypothesis(returns[cols[i]], returns[cols[j]], gamma, threshold):
                H.add_edge(cols[i], cols[j])

    positions=nx.circular_layout(H)
    
    #Figure size
    plt.figure(figsize=(15,15))

    #draws nodes
    nx.draw_networkx_nodes(H,positions,node_color='#DA70D6',
                           node_size=500,alpha=0.8)
    
    #Styling for labels
    nx.draw_networkx_labels(H, positions, font_size=8, 
                            font_family='sans-serif')
        
    #draws the edges
    nx.draw_networkx_edges(H, positions,style='solid')
    
    # displays the graph without axis
    plt.axis('off')
    #saves image
    # plt.savefig("part2" + corr_direction + ".png", format="PNG")
    plt.show() 
    return H

"""#### Kendal"""

def create_corr_network_kendal(returns: pd.DataFrame, threshold = 0, gamma = 0):
    ##Creates a copy of the graph
    cols = returns.columns
    G = nx.empty_graph(n = len(cols))
    K = nx.relabel_nodes(G, lambda x: cols[x])
    H = K.copy()

    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            if not kendal_hypothesis(returns[cols[i]], returns[cols[j]], gamma, threshold):
                H.add_edge(cols[i], cols[j])

    positions=nx.circular_layout(H)
    
    #Figure size
    plt.figure(figsize=(15,15))

    #draws nodes
    nx.draw_networkx_nodes(H,positions,node_color='#DA70D6',
                           node_size=500,alpha=0.8)
    
    #Styling for labels
    nx.draw_networkx_labels(H, positions, font_size=8, 
                            font_family='sans-serif')
        
    #draws the edges
    nx.draw_networkx_edges(H, positions,style='solid')
    
    # displays the graph without axis
    plt.axis('off')
    #saves image
    # plt.savefig("part2" + corr_direction + ".png", format="PNG")
    plt.show() 
    return H

"""### Hypothesis"""

from math import *
def phi(x):
    #'Cumulative distribution function for the standard normal distribution'
    return (1.0 + erf(x / sqrt(2.0))) / 2.0

"""#### Pirson"""

# from numpy.core.arrayprint import format_float_scientific
def pirson_hypothesis(x_return, y_return, gamma, alpha):

    notNullReturn = pd.DataFrame(x_return)
    notNullReturn[y_return.name] = y_return
    notNullReturn.dropna(inplace = True)

    x_return = notNullReturn[x_return.name]
    y_return = notNullReturn[y_return.name]
    x_mean = x_return.mean()
    y_mean = y_return.mean()
    x_denominator = 0
    y_denominator = 0
    numerator = 0
    for i in range(len(x_return)):
        x_denominator = x_denominator + (x_return[i] - x_mean)**2
        y_denominator = y_denominator + (y_return[i] - y_mean)**2
        numerator = numerator + (x_return[i] - x_mean) * (y_return[i] - y_mean)
    r = numerator / (x_denominator * y_denominator)**0.5

    T = len(x_return)**0.5 * (0.5 * np.log((1 + r) / (1 - r)) - 0.5 * np.log((1 + gamma) / (1 - gamma)))
    p = 1 - phi(T)

    if p < alpha:
        return False
    else:
        return True

"""#### Sign"""

import scipy.stats

def sign_hypothesis(x_return, y_return, gamma, alpha):
    notNullReturn = pd.DataFrame(x_return)
    notNullReturn[y_return.name] = y_return
    notNullReturn.dropna(inplace = True)

    x_return = [1 if i >= 0 else 0 for i in notNullReturn[x_return.name]]
    y_return = [1 if i >= 0 else 0 for i in notNullReturn[y_return.name]]
    x_mean = np.mean(x_return)
    y_mean = np.mean(y_return)

    T = 0
    for i in range(len(x_return)):
        if (x_return[i] - x_mean) * (y_return[i] - y_mean) >= 0:
            T += 1
    
    T_n = (T - len(x_return) * gamma) / (len(x_return) * gamma * (1 - gamma))**0.5
    p = 1 - phi(T_n)
    if p < alpha:
        return False
    else:
        return True

sign_hypothesis(returns['NKNC'], returns['FESH'], 0.5, 0.01)

"""#### Kendal"""

from scipy.stats import kendalltau

def kendal_hypothesis(x_return, y_return, gamma, alpha):
    notNullReturn = pd.DataFrame(x_return)
    notNullReturn[y_return.name] = y_return
    notNullReturn.dropna(inplace = True)

    x_return = notNullReturn[x_return.name]
    y_return = notNullReturn[y_return.name]

    # I = []
    # sum = 0
    # x_count = [0, 0]
    # num = 0
    # for i in range(len(notNullReturn)):    
    #     for j in range(len(notNullReturn)):
    #         if i == j: continue 
    #         if ((x_return[i] - x_return[j]) * (y_return[i] - y_return[j])) >= 0:
    #             I.append(1)
    #             sum += 1
    #             num += 1
    #         else:
    #             sum -= 1
    #             I.append(-1)
    # print(np.sum(I), sum / (len(I)*(len(I) - 1)))
    # pcc = (num / len(I))**3 + ((len(I) - num) / len(I))**3
    # corr = sum / (len(x_return) * (len(x_return) - 1))
    # pc = (corr + 1) / 2
    # print(corr, pc)
    # print(pcc, pc, pc**2)
    # T = len(y_return) * (corr - gamma) / (4 * (pcc - pc**2)**0.5)
    # p = 1 - phi(T)

    tau, p = kendalltau(x_return, y_return)

    if p < alpha:
        return False
    else:
        return True

G1 = create_corr_network_kendal(returns = returns[Sharp_positive.index], threshold = 0.01, gamma = 0)
mis = nx.maximal_independent_set(G1)
print(mis, len(mis))

from pypfopt.efficient_frontier import EfficientFrontier 
from pypfopt import risk_models 
from pypfopt import expected_returns
from pypfopt.cla import CLA
import pypfopt.plotting as pplt
from matplotlib.ticker import FuncFormatter
import scipy.stats as sps
# import scipy.stats.multivariate_t as t_sample

"""### Функция построения портфеля"""

data_copy = data

"""#### Функция построения портфеля с оптимальным Шарпом"""

def investmentPortfolio(expected_returns, covariation_matrix, weights = None):
    ef = EfficientFrontier(expected_returns, covariation_matrix, weight_bounds=(0,1)) 
    if weights:
        ef.set_weights(weights)
    else:
        sharpe_pfolio = ef.max_sharpe() # May use add objective to ensure minimum zero weighting to individual stocks
    
    sharpe_pwt = ef.clean_weights()

    print(sharpe_pwt)
    print(ef.portfolio_performance(verbose=True))
    print([(i, sharpe_pwt[i]) for i in sharpe_pwt if sharpe_pwt[i] > 0])

    cl_obj = CLA(expected_returns, covariation_matrix)
    ax = pplt.plot_efficient_frontier(cl_obj, showfig = False, show_assets = False, )
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: '{:.0%}'.format(x)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
    plt.show()
    return sharpe_pwt

"""#### Функция создания портфеля с данным риском"""

def investmentPortfolioByGivenRisk(expected_returns, covariation_matrix, given_risk = 0.01):
    ef = EfficientFrontier(expected_returns, covariation_matrix, weight_bounds=(0, 1))
    risk_pfolio = ef.efficient_risk(given_risk)
    sharpe_pwt = ef.clean_weights()
    print(ef.portfolio_performance(verbose=True))
    return sharpe_pwt,  risk_pfolio

test = investmentPortfolio(expected_returns.mean_historical_return(data_copy[mis], 
                           log_returns=True), 
                           Sharp_positive_cov.loc[mis][mis])

"""# Функция построения оптимального портфеля инвестиций"""

def createPorfolio(data: pd.DataFrame,  MISThreshold, correletion_type = "pearson", threshold = 0.01, gamma = 0.1):
    returns = expected_returns.returns_from_prices(data, log_returns=True)

    data_cov = returns.cov()
    data_param = pd.DataFrame()
    data_param["Доходность"] = expected_returns.mean_historical_return(data, log_returns=True)
    data_param['Риск'] = [(data_cov[i][i]**0.5) for i in data_cov.index]
    data_param['Коэффициент Шарпа'] = data_param['Доходность'] / data_param['Риск']

    sharp_positive = pd.DataFrame(data_param[data_param['Коэффициент Шарпа'] > 0])
    sharp_positive_index = sharp_positive.index
    if correletion_type == "sign":
        G = create_corr_network_sign(returns[sharp_positive_index], threshold = threshold, gamma = gamma)
    elif correletion_type == "pearson":
        G = create_corr_network_pirson(returns[sharp_positive_index], threshold = threshold, gamma = gamma)
    else:
        G = create_corr_network_kendal(returns[sharp_positive_index], threshold = threshold, gamma = gamma)
    sharp_positive_cov = returns[sharp_positive_index].cov()


    mis = nx.maximal_independent_set(G)
    print(f"MIS size: {len(mis)}")
    # Построение портфеля на основе исторических данных

    print("\nHistorical\n")

    result = investmentPortfolio(expected_returns.mean_historical_return(data[mis], 
                           log_returns=True), 
                           data_cov.loc[mis][mis])


    # TODO Проверка на устойчивость!?

    # Построение портфеля на основе нормального распределения доходностей

    print("\nNormal Distribution\n")

    sample = sps.multivariate_normal(mean = expected_returns.mean_historical_return(data[mis], 
                                            log_returns=True),
                                            cov = data_cov.loc[mis][mis]).rvs(size = 252)

    return_normal = pd.DataFrame(sample, columns = mis)
    # cov_normal = return_normal.cov()
    cov_normal = data_cov.loc[mis][mis]
    result_normal = investmentPortfolio(return_normal.mean(), 
                                 cov_normal)



    # Построение портфеля на основе распределения Стьюдента
    
    print("\nT-Distribution\n")

    sample = sps.multivariate_t(expected_returns.mean_historical_return(data[mis], 
                                            log_returns=True),
                                df = 2)
    sample.cov_info = data_cov.loc[mis][mis]
    sample = sample.rvs(size = 252)
    return_t = pd.DataFrame(sample, columns = mis)
    # cov_t = return_t.cov()
    cov_t = data_cov.loc[mis][mis]
    result_t = investmentPortfolio(return_t.mean(), 
                                 cov_t)

    nonNullResults = [(i, result[i]) for i in result if result[i] > 0]
    return nonNullResults

"""## Sign measure"""

def sign_measure(returns: pd.DataFrame):
    corr = pd.DataFrame(columns=returns.columns, index = returns.columns)
    cols = returns.columns
    for i in range(len(cols)):
        for j in range(i, len(cols)):
            probadility = len([k for k in returns.index if returns[cols[i]][k] * returns[cols[j]][k] > 0]) / len(returns.index)
            corr[cols[i]][cols[j]] = probadility
            corr[cols[j]][cols[i]] = probadility
            if i == j:
                corr[cols[i]][cols[j]] = 1
                corr[cols[j]][cols[i]] = 1
    return corr

"""## Pearson"""

createPorfolio(data, 0.25, "pearson", 0.01, 0.1)

"""# Kendall"""

createPorfolio(data, 0.25, 'kendall', 0.01, 0.1)

"""# Sign"""

createPorfolio(data, 0.25, 'sign', threshold = 0.01, gamma = 0.1)

"""# Проверка на устойчивость

## Генерация смеси
"""

def generate_distribution(data, data_cov, gamma):
    normal = sps.multivariate_normal(mean = expected_returns.mean_historical_return(data, 
                                    log_returns=True),
                                    cov = data_cov).rvs(size = 252)

    TDistr = sps.multivariate_t(expected_returns.mean_historical_return(data, 
                                log_returns=True),
                                df = 2)
    TDistr.cov_info = data_cov
    TDistr = TDistr.rvs(size = 252)
    
    return gamma * normal + (1 - gamma) * TDistr

"""## Построение портфелей для разных мер зависимости"""

def get_MIS(G):
    MIS = []
    for i in range(10):
        mis = nx.maximal_independent_set(G)
        if len(mis) > len(MIS):
            MIS = mis
    return MIS

def generate_tests(data, threshold, gamma_0 = 0.5):
    # сгенерировать максимальное независимое множество на основе всех типов корреляций
    # спрогнозировать цены акций из MIS c параметром gamma
    # построить портфели на основе прогнозов, вычислить среднюю доходность при заданном риске
    # сравнить данные портфели с историческими
    G_sign = create_corr_network_sign(data, threshold, gamma_0)
    G_pirson = create_corr_network_pirson(data, threshold, gamma_0)
    G_kendal = create_corr_network_kendal(data, threshold, gamma_0)

    mis_sign = get_MIS(G_sign)
    mis_pirson = get_MIS(G_pirson)
    mis_kendal = get_MIS(G_kendal)

    

    pass

