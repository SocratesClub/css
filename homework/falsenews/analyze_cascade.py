from settings import *


def calc_depth(G,G_root):
    depth=nx.eccentricity(G,v=G_root)
    return depth

def calc_structural_viralty(G,size):
    if size==1:
        return None ##virality is not defined for cascades of size 1,
    sv=nx.average_shortest_path_length(G)  #Note: this is very time-consuming for larger cascades
    return sv

def calc_size(G):
    num_nodes=G.number_of_nodes()
    return num_nodes



def get_metadata(cascade_graph):
    cascade_graph=cascade_graph.to_undirected()
    metadata={}
    node2date=nx.get_node_attributes(cascade_graph,'date')
    root=[n for n in cascade_graph if cascade_graph.node[n]['is_root']==True][0]
    root_date=node2date[root]
    ##Static measures
    depth=calc_depth(cascade_graph,root)
    size=calc_size(cascade_graph)
    virality=calc_structural_viralty(cascade_graph, size)
    metadata['root_tid']=root
    metadata['start_date']=root_date
    metadata['size']=size
    metadata['depth']=depth
    metadata['virality']=virality
    metadata['unique_users']=size #since each user can only retweet once

    ##Dynamic measures
    metadata['depth2time']={}
    metadata['depth2uu']={}
    metadata['depth2breadth']={}
    metadata['uu2time']={}
    done_nodes=[]
    done_uids=set([])
    for dp in range(depth):
        current_dp=dp+1
        current_subgraph=nx.ego_graph(cascade_graph, root, radius=current_dp)
        current_sb_nodes=current_subgraph.nodes()
        node2date=nx.get_node_attributes(current_subgraph,'date')
        node_dates=node2date.items()
        node_dates=[(n,d) for n,d in node_dates if n not in done_nodes]
        if len(node_dates)==0:
            break
        current_depth_nodes=[n for n,d in node_dates]
        node_dates.sort(key=lambda x:x[1])
        depth_date=node_dates[0][1]
        time_elapsed=(depth_date-root_date).total_seconds()
        metadata['depth2time'][current_dp]=time_elapsed
        nodes=current_subgraph.nodes()
        for user in nodes:
            if user not in done_uids:
                done_uids.add(user)
        unique_users=len(nodes)
        metadata['depth2uu'][current_dp]=unique_users
        current_breadth=len(current_depth_nodes)
        metadata['depth2breadth'][current_dp]=current_breadth
        done_nodes=current_sb_nodes

    current_users=[]
    current_uu2time={}
    node_dates=node2date.items()
    node_dates.sort(key=lambda x:x[1])
    for node,date in node_dates:
        current_users.append(node)
        u_current_users=set(current_users)
        num_unique_users=len(u_current_users)
        uu_time=current_uu2time.get(num_unique_users)
        time_elapsed=(date-root_date).total_seconds()
        if uu_time==None:
            current_uu2time[num_unique_users]=time_elapsed
            metadata['uu2time'][num_unique_users]=time_elapsed

    breadths=metadata['depth2breadth'].values()
    maxbreadth=1 if len(breadths)==0 else max(breadths)
    metadata['max_breadth']=maxbreadth

    ##User stats
    metadata['verified_list']=[]
    metadata['num_followers_list']=[]
    metadata['num_followees_list']=[]
    metadata['accountage_list']=[]
    metadata['engagement_list']=[]
    node2verified=nx.get_node_attributes(cascade_graph,'verified')
    node2followers=nx.get_node_attributes(cascade_graph,'followers')
    node2followees=nx.get_node_attributes(cascade_graph,'followees')
    node2accage=nx.get_node_attributes(cascade_graph,'account_age')
    node2engagement=nx.get_node_attributes(cascade_graph,'engagement')
    for n in cascade_graph.nodes():
        metadata['num_followers_list'].append(node2followers[n])
        metadata['num_followees_list'].append(node2followees[n])
        metadata['accountage_list'].append(node2accage[n])
        metadata['engagement_list'].append(node2engagement[n])
        metadata['verified_list'].append(node2verified[n])
    ###
    return metadata