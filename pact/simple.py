import networkx as nx
from pact.graphwrapper import GraphWrapper
import pandas as pd
from pact.balgowrapper import balgo_multitry_for_cheapest_decomp
from pact.planner import node_to_ops
from pact.treedecomp import td_nodes_it
from pact.naive_exec import naive_pandas_plan_exec, naive_pandas_homcount, naive_pandas_plan_exec_weighted



def _Graph2DF(G):
    nxG = G.graph
    edges = [{'s': a, 't': b} for a,b in nxG.edges()] + [{'s': b, 't': a} for a,b in nxG.edges()]
    host_df = pd.DataFrame(edges).drop_duplicates()
    return host_df


            
def _guarantee_v_in_root(td, v):
    def _find_v_in_childbag(td, v):
        for u in td_nodes_it(td):
            for c in u.children:
                if v in c.bag:
                    return u,c
        return None

    def _find_parent(td, c):
        for u in td_nodes_it(td):
            if c in u.children:
                return u
        return None

    if v in td.bag:
        return td
    p, c = _find_v_in_childbag(td, v)
    newroot = c
    
    while p is not None:
        # delete c from p.children, add p into c.children
        p.children.remove(c)
        c.children.append(p)
        
        # repeat upwards
        c = p
        p = _find_parent(td, c)
    return newroot


def setup_pattern_for_homcount(F, threads=1, retries=5):
    if type(F) == nx.Graph:
        F = GraphWrapper(F)
    assert type(F) == GraphWrapper
    F.td, _ = balgo_multitry_for_cheapest_decomp(F, times=retries, threads=threads)
    F.plan = node_to_ops(F.td)
    return F


def count_homs(F, G, weight_df=None, per_vertex=True):
    if type(F) == nx.Graph:
        F = GraphWrapper(F)
    if type(G) == nx.Graph:
        G = GraphWrapper(G)
    assert type(F) == GraphWrapper and type(G) == GraphWrapper

    if F.plan is None:
        F = setup_pattern_for_homcount(F)

    dfG = _Graph2DF(G)


    if per_vertex:

        if weight_df is not None:
            state, empty = naive_pandas_plan_exec_weighted(F.plan, dfG, weights=weight_df, debug=False)
        else:
            state, empty = naive_pandas_plan_exec(F.plan, dfG, sliced_eval={})
        if empty:
            return 0
        
        finalcount = state['node$0']
        cols = list(finalcount.columns)
        cols.remove('count')
        key = cols[0]
        return finalcount.groupby(key)['count'].sum().to_dict()
    else:
        if weight_df is not None:
            state, emtpy = naive_pandas_plan_exec_weighted(F.plan, dfG, weights=weight_df)
            finalcount = state['node$0']['count']
            return finalcount.sum()
        else:
            return naive_pandas_homcount(F, dfG)
