from settings import *
import analyze_cascade

raw_data_file='./data/raw_data_anon.csv'
regression_file='./data/regression_data_anon.txt'
metadata_file='./data/metadata_anon.txt'
emotions_file='./data/emotions_anon.csv'
topics_file='./data/topics_anon.csv'


def convert_raw_data_to_metadata():
    print "Converting raw data to metadata..."
    with open(raw_data_file,'rb') as f:
        reader=csv.reader(f)
        next(reader, None) #skippingthe header
        reader = sorted(reader, key=lambda row: (row[2],row[5])) #Sort by cascade id
        row_num=0
        last_cascade_id=None
        #resetting files...
        fout=open(metadata_file,'w')
        fout.close()
        for row in reader:
            tid=int(row[0])
            veracity=str(row[1])
            cascade_id=int(row[2])
            rumor_id=str(row[3])
            rumor_category=str(row[4])
            parent_tid=int(row[5])
            tweet_date=parser.parse(row[6])
            user_account_age=eval(row[7])
            user_verified=eval(row[8])
            user_followers=eval(row[9])
            user_followees=eval(row[10])
            user_engagement=float(row[11])
            cascade_root_tid=eval(row[12])
            was_retweeted=int(row[13])
            ##
            if cascade_id!=last_cascade_id: #New cascade
                ###Extracting metadata from the previous cascade graph
                if last_cascade_id!=None:
                    mt=analyze_cascade.get_metadata(graph)
                    metadata.update(mt)
                    fout=open(metadata_file,'a')
                    fout.write(repr((last_cascade_id,metadata))+'\n')
                    fout.close()
                ###Creating a new graph using networkx to extract metadata
                metadata={}
                metadata['veracity']=veracity
                metadata['rumor_id']=rumor_id
                metadata['rumor_category']=rumor_category
                graph=nx.DiGraph()
                last_cascade_id=cascade_id
                last_tid=tid
            graph.add_node(tid,date=tweet_date,is_root=True if parent_tid==-1 else False,followers=user_followers, followees=user_followees,
                       verified=user_verified,account_age=user_account_age,engagement=user_engagement)
            if parent_tid!=-1: #add an edge between parent node and child node if one exists
                graph.add_edge(parent_tid,tid)
            if row_num%10000==0:
                print row_num,"rows read"
            row_num+=1

    #Saving the last remaining cascade
    mt=analyze_cascade.get_metadata(graph)
    metadata.update(mt)
    fout=open(metadata_file,'a')
    fout.write(repr((last_cascade_id,metadata))+'\n')
    fout.close()

def generate_figures():
    print "Reading metadata..."
    fin=open(metadata_file,'r')
    lines=fin.readlines()
    fin.close()
    cascade_id2metadata={}
    for line in lines:
        line=line.replace('\n','')
        item=eval(line)
        cascade_id2metadata[item[0]]=item[1]

    print "Reading regresstion data..."
    fin=open(regression_file,'r')
    lines=fin.readlines()
    fin.close()
    regression_data=[] #[cluster,was_retweeted,folllowers,followees,verified,account_age,engagement,falsehood]
    for line in lines:
        line=line.replace('\n','')
        regression_data.append(eval(line))

    print "Reading emotion data..."
    tid2emotion2score={}
    with open(emotions_file,'rb') as f:
        reader=csv.reader(f)
        row_num=0
        for row in reader:
            if row_num==0:
                header=row
            else:
                tid=int(row[0])
                tid2emotion2score[tid]={}
                for col in range(1,len(header)):
                    emotion=header[col]
                    tid2emotion2score[tid][emotion]=float(row[col])
            row_num+=1

    print "Reading topic/novelty data..."
    tid2rid_veracity_tweettopics_backgroundtopics={}
    with open(topics_file,'rb') as f:
        reader=csv.reader(f)
        row_num=0
        for row in reader:
            if row_num==0:
                header=row
            else:
                tid=int(row[0])
                rid=row[1]
                veracity=row[2]
                tweet_topics=[]
                background_topics=[]
                for i in range(3,201):
                    tweet_topics.append(float(row[i]))
                for i in range(203,401):
                    background_topics.append(float(row[i]))
                tid2rid_veracity_tweettopics_backgroundtopics[tid]=(rid,veracity,tweet_topics,background_topics)
            row_num+=1

    veracity2number_of_cascades={}
    unique_rumors=set([])
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        rid=metadata['rumor_id']
        unique_rumors.add(rid)
        number_of_cascades=veracity2number_of_cascades.get(veracity,0)
        number_of_cascades+=1
        veracity2number_of_cascades[veracity]=number_of_cascades
    print "Number of unique rumors:",len(unique_rumors)
    total_number_of_cascades=0
    for veracity,number_of_cascades in veracity2number_of_cascades.items():
        print "Number of",veracity,"cascades:",number_of_cascades
        total_number_of_cascades+=number_of_cascades
    print "Total number of cascades:",total_number_of_cascades
    '''
    FIGURE 1B
    CCDF of number of cascades per rumor for different veracities for all rumors
    '''
    print "Preparing figure 1B"
    ax = plt.subplot(111)
    ax.set_xscale('log')
    ax.set_yscale('log')
    formatter = plt.FuncFormatter(log_10_product)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    veracity2rid2count={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        rid=metadata['rumor_id']
        rid2count=veracity2rid2count.get(veracity,{})
        count=rid2count.get(rid,0)
        count+=1
        rid2count[rid]=count
        veracity2rid2count[veracity]=rid2count
    for veracity,rid2count in veracity2rid2count.items():
        rid_count=rid2count.items()
        rid_count.sort(key=lambda x:x[1], reverse=True)
        y=[count for rid,count in rid_count]
        total=float(len(rid_count))
        xf=[]
        pf=[]
        y.sort()
        counts=list(set(y))
        counts.sort()
        for d in counts:
            ind=y.index(d)
            count=len(y[ind:])
            p=(count/float(total)) * 100
            xf.append(d)
            pf.append(p)
            ax.plot(xf,pf,'-',color=veracity2color[veracity],linewidth=lw)
    plt.xlabel("Number of Cascades",fontsize=fs*(5.0/6))
    plt.ylabel("CCDF (% Rumors)",fontsize=fs*(5.0/6))
    ax.tick_params(axis='both', which='major', labelsize=fs_2*(5.0/6))
    plt.xticks(rotation='horizontal')
    plt.savefig('./figures/fig_1B.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 1C
    Number of cascader over time for all veracities
    '''
    print "Preparing figure 1C..."
    ax = plt.subplot(111)
    formatter = plt.FuncFormatter(year)
    ax.xaxis.set_major_formatter(formatter)
    veracity2date2count={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        date=quarter_year(metadata['start_date'])
        date2count=veracity2date2count.get(veracity,{})
        count=date2count.get(date,0)
        count+=1
        date2count[date]=count
        veracity2date2count[veracity]=date2count
    for veracity,date2count in veracity2date2count.items():
        date_count=date2count.items()
        date_count.sort(key=lambda x:x[0])
        x=[d for d,c in date_count if (d.year!=2016 or d.month<10)]
        y=[c for d,c in date_count if (d.year!=2016 or d.month<10)]
        plt.plot(x,y,color=veracity2color[veracity],linewidth=lw)
    plt.xlabel('Year',fontsize=fs*(5.0/6))
    plt.ylabel("Count (All Cascades)",fontsize=fs*(5.0/6))
    ax.tick_params(axis='both', which='major', labelsize=fs_2*(5.0/6))
    plt.savefig('./figures/fig_1C.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 1D
    CCDF of number of political cascades per rumor for different veracities
    '''
    print "Preparing figure 1D..."
    ax = plt.subplot(111)
    ax.set_xscale('log')
    ax.set_yscale('log')
    formatter = plt.FuncFormatter(log_10_product)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    veracity2rid2count={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        rid=metadata['rumor_id']
        category=metadata['rumor_category']
        if category!='Politics':
            continue
        rid2count=veracity2rid2count.get(veracity,{})
        count=rid2count.get(rid,0)
        count+=1
        rid2count[rid]=count
        veracity2rid2count[veracity]=rid2count
    for veracity,rid2count in veracity2rid2count.items():
        rid_count=rid2count.items()
        rid_count.sort(key=lambda x:x[1], reverse=True)
        y=[count for rid,count in rid_count]
        total=float(len(rid_count))
        xf=[]
        pf=[]
        y.sort()
        counts=list(set(y))
        counts.sort()
        for d in counts:
            ind=y.index(d)
            count=len(y[ind:])
            p=(count/float(total)) * 100
            xf.append(d)
            pf.append(p)
            ax.plot(xf,pf,'-',color=veracity2color[veracity],linewidth=lw)
    plt.xlabel("Number of Political Cascades",fontsize=fs*(5.0/6))
    plt.ylabel("CCDF (% Rumors)",fontsize=fs*(5.0/6))
    ax.tick_params(axis='both', which='major', labelsize=fs_2*(5.0/6))
    plt.xticks(rotation='horizontal')
    plt.savefig('./figures/fig_1D.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 1E
    Number of political cascader over time for all veracities
    '''
    print "Preparing figure 1E..."
    ax = plt.subplot(111)
    formatter = plt.FuncFormatter(year)
    ax.xaxis.set_major_formatter(formatter)
    veracity2date2count={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        category=metadata['rumor_category']
        if category!='Politics':
            continue
        date=quarter_year(metadata['start_date'])
        date2count=veracity2date2count.get(veracity,{})
        count=date2count.get(date,0)
        count+=1
        date2count[date]=count
        veracity2date2count[veracity]=date2count
    for veracity,date2count in veracity2date2count.items():
        date_count=date2count.items()
        date_count.sort(key=lambda x:x[0])
        x=[d for d,c in date_count if (d.year!=2016 or d.month<10)]
        y=[c for d,c in date_count if (d.year!=2016 or d.month<10)]
        plt.plot(x,y,color=veracity2color[veracity],linewidth=lw)
    plt.xlabel('Year',fontsize=fs*(5.0/6))
    plt.ylabel("Count (Political Cascades)",fontsize=fs*(5.0/6))
    ax.tick_params(axis='both', which='major', labelsize=fs_2*(5.0/6))
    plt.xticks(rotation='horizontal')
    plt.savefig('./figures/fig_1E.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 1F
    Number of cascades per topic
    '''
    print "Preparing figure 1F..."
    category2count={}
    for cascade,metadata in cascade_id2metadata.items():
        category=metadata['rumor_category']
        count=category2count.get(category,0)
        count+=1
        category2count[category]=count
    cat_count=category2count.items()
    cat_count.sort(key=lambda x:x[1], reverse=True)
    y=[count for cat,count in cat_count]
    x=['Politics','Urban Legends','Business','Terrorism & War','Science & Technology','Entertainment','Natural Disasters']
    x.reverse()
    y.reverse()
    width = 0.015
    pos=[ 0.17 , 0.19 , 0.21 , 0.23 , 0.25 , 0.27 , 0.29]
    ax = plt.subplot(111)
    formatter = plt.FuncFormatter(kit)
    ax.xaxis.set_major_formatter(formatter)
    ax.barh(pos,y,width, align='center',color ='#486E7F' )
    plt.yticks(pos, x,fontsize=fs)
    plt.ylim([0.155,0.305])
    ax.tick_params(axis='both', which='major', labelsize=fs_2-3)
    plt.xlabel("Number of Cascades",fontsize=fs-1)
    plt.xticks(rotation='horizontal')
    ax.set_xticks([0, 10000, 20000,30000,40000,50000])
    plt.savefig('./figures/fig_1F.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 2A
    CCDF of depth for all rumors
    '''
    print "Preparing figure 2A..."
    ax = plt.subplot(111)
    ax.set_xscale('log')
    ax.set_yscale('log')
    formatter = plt.FuncFormatter(log_10_product)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    veracity2depths={}
    veracity2clusters={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        rid=metadata['rumor_id']
        depth=metadata['depth']+1 #adding one for smoothing purposes
        depths=veracity2depths.get(veracity,[])
        depths.append(depth)
        veracity2depths[veracity]=depths
        clusters=veracity2clusters.get(veracity,[])
        clusters.append(rid)
        veracity2clusters[veracity]=clusters
    print '##############################'
    print 'Depth Stats. FALSE/TRUE/MIXED'
    print 'Mean (log)',np.mean(np.log10(veracity2depths['FALSE'])),np.mean(np.log10(veracity2depths['TRUE'])),np.mean(np.log10(veracity2depths['MIXED']))
    print 'Robust SEM (log)',calc_robust_sem(np.log10(veracity2depths['FALSE']),veracity2clusters['FALSE']),\
        calc_robust_sem(np.log10(veracity2depths['TRUE']),veracity2clusters['TRUE']),\
        calc_robust_sem(np.log10(veracity2depths['MIXED']),veracity2clusters['MIXED'])
    print  "KS test (false and true):",stats.ks_2samp(veracity2depths['FALSE'],veracity2depths['TRUE'])
    for veracity,depths in veracity2depths.items():
        if veracity=='MIXED':
            continue
        total=float(len(depths))
        xf=[]
        pf=[]
        depths.sort()
        counts=list(set(depths))
        counts.sort()
        for d in counts:
            ind=depths.index(d)
            count=len(depths[ind:])
            p=(count/float(total)) * 100
            xf.append(d)
            pf.append(p)
        ax.plot(xf,pf,color=veracity2color[veracity],linewidth=lw)
    plt.xlabel("Cascade Depth",fontsize=fs)
    plt.ylabel("CCDF (%)",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.xticks(rotation='horizontal')
    plt.savefig('./figures/fig_2A.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 2B
    CCDF of size for all rumors
    '''
    print "Preparing figure 2B..."
    ax = plt.subplot(111)
    ax.set_xscale('log')
    ax.set_yscale('log')
    formatter = plt.FuncFormatter(log_10_product)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    veracity2sizes={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        size=metadata['size']
        sizes=veracity2sizes.get(veracity,[])
        sizes.append(size)
        veracity2sizes[veracity]=sizes
    print '##############################'
    print 'Size Stats. FALSE/TRUE/MIXED'
    print 'Mean (log)',np.mean(np.log10(veracity2sizes['FALSE'])),np.mean(np.log10(veracity2sizes['TRUE'])),np.mean(np.log10(veracity2sizes['MIXED']))
    print 'Robust SEM (log)',calc_robust_sem(np.log10(veracity2sizes['FALSE']),veracity2clusters['FALSE']),\
        calc_robust_sem(np.log10(veracity2sizes['TRUE']),veracity2clusters['TRUE']),\
        calc_robust_sem(np.log10(veracity2sizes['MIXED']),veracity2clusters['MIXED'])
    print  "KS test (false and true):",stats.ks_2samp(veracity2sizes['FALSE'],veracity2sizes['TRUE'])
    for veracity,sizes in veracity2sizes.items():
        if veracity=='MIXED':
            continue
        total=float(len(sizes))
        xf=[]
        pf=[]
        sizes.sort()
        counts=list(set(sizes))
        counts.sort()
        for d in counts:
            ind=sizes.index(d)
            count=len(sizes[ind:])
            p=(count/float(total)) * 100
            xf.append(d)
            pf.append(p)
        ax.plot(xf,pf,color=veracity2color[veracity],linewidth=lw)
    plt.xlabel("Cascade Size",fontsize=fs)
    plt.ylabel("CCDF (%)",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.xticks(rotation='horizontal')
    plt.savefig('./figures/fig_2B.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 2C
    CCDF of max-breadth for all rumors
    '''
    print "Preparing figure 2C..."
    ax = plt.subplot(111)
    ax.set_xscale('log')
    ax.set_yscale('log')
    formatter = plt.FuncFormatter(log_10_product)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    veracity2breadths={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        breadth=metadata['max_breadth']
        breadths=veracity2breadths.get(veracity,[])
        breadths.append(breadth)
        veracity2breadths[veracity]=breadths
    print '##############################'
    print 'Max-Breadth Stats. FALSE/TRUE/MIXED'
    print 'Mean (log)',np.mean(np.log10(veracity2breadths['FALSE'])),np.mean(np.log10(veracity2breadths['TRUE'])),np.mean(np.log10(veracity2breadths['MIXED']))
    print 'Robust SEM (log)',calc_robust_sem(np.log10(veracity2breadths['FALSE']),veracity2clusters['FALSE']),\
        calc_robust_sem(np.log10(veracity2breadths['TRUE']),veracity2clusters['TRUE']),\
        calc_robust_sem(np.log10(veracity2breadths['MIXED']),veracity2clusters['MIXED'])
    print  "KS test (false and true):",stats.ks_2samp(veracity2breadths['FALSE'],veracity2breadths['TRUE'])
    for veracity,breadths in veracity2breadths.items():
        if veracity=='MIXED':
            continue
        total=float(len(breadths))
        xf=[]
        pf=[]
        breadths.sort()
        counts=list(set(breadths))
        counts.sort()
        for d in counts:
            ind=breadths.index(d)
            count=len(breadths[ind:])
            p=(count/float(total)) * 100
            xf.append(d)
            pf.append(p)
        ax.plot(xf,pf,color=veracity2color[veracity],linewidth=lw)
    plt.xlabel("Cascade Max-Breadth",fontsize=fs)
    plt.ylabel("CCDF (%)",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.xticks(rotation='horizontal')
    plt.savefig('./figures/fig_2C.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 2D
    CCDF of strucural virality for all rumors
    '''
    print "Preparing figure 2D..."
    ax = plt.subplot(111)
    ax.set_xscale('log')
    ax.set_yscale('log')
    formatter = plt.FuncFormatter(log_10_product)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    veracity2viralities={}
    veracity2virality_clusters={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        virality=metadata['virality']
        rid=metadata['rumor_id']
        viralities=veracity2viralities.get(veracity,[])
        viralities.append(virality)
        veracity2viralities[veracity]=viralities
        if virality!=None:
            virality_clusters=veracity2virality_clusters.get(veracity,[])
            virality_clusters.append(rid)
            veracity2virality_clusters[veracity]=virality_clusters

    print '##############################'
    print 'Virality Stats. FALSE/TRUE/MIXED'
    print 'Mean (log)',np.mean(np.log10([e for e in veracity2viralities['FALSE'] if e!=None])),\
        np.mean(np.log10([e for e in veracity2viralities['TRUE'] if e!=None])),np.mean(np.log10([e for e in veracity2viralities['MIXED'] if e!=None]))
    print 'Robust SEM (log)',calc_robust_sem(np.log10([e for e in veracity2viralities['FALSE'] if e!=None]),veracity2virality_clusters['FALSE']),\
        calc_robust_sem(np.log10([e for e in veracity2viralities['TRUE'] if e!=None]),veracity2virality_clusters['TRUE']),\
        calc_robust_sem(np.log10([e for e in veracity2viralities['MIXED'] if e!=None]),veracity2virality_clusters['MIXED'])
    print  "KS test (false and true):",stats.ks_2samp([e for e in veracity2viralities['FALSE'] if e!=None],[e for e in veracity2viralities['TRUE'] if e!=None])
    for veracity,viralities in veracity2viralities.items():
        if veracity=='MIXED':
            continue
        xf=[]
        pf=[]
        viralities=[e if e!=None else 0 for e in viralities]
        total=float(len(viralities))
        viralities.sort()
        counts=[]
        c=min(viralities)
        step=0.25
        while c<max(viralities)+step:
            counts.append(c)
            c+=step
        counts.sort()
        for d in counts:
            ind=bisect.bisect_left(viralities,d)
            count=len(viralities[ind:])
            p=(count/float(total)) * 100
            xf.append(d)
            pf.append(p)
        ax.plot(xf,pf,color=veracity2color[veracity],linewidth=lw)
    plt.xlabel("Structural Virality",fontsize=fs)
    plt.ylabel("CCDF (%)",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.xticks(rotation='horizontal')
    plt.xlim([1,100])
    plt.savefig('./figures/fig_2D.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 2E
    depth vs time for all rumors
    '''
    print "Preparing figure 2E..."
    ax = plt.subplot(111)
    formatter = plt.FuncFormatter(lognormal)
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    veracity2depth2times={}
    veracity2depth2clusters={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        rid=metadata['rumor_id']
        depth2time=metadata['depth2time']
        depth2times=veracity2depth2times.get(veracity,{})
        depth2clusters=veracity2depth2clusters.get(veracity,{})
        for depth,time_ in depth2time.items():
            times=depth2times.get(depth,[])
            times.append(time_)
            depth2times[depth]=times
            clusters=depth2clusters.get(depth,[])
            clusters.append(rid)
            depth2clusters[depth]=clusters
        veracity2depth2times[veracity]=depth2times
        veracity2depth2clusters[veracity]=depth2clusters
    for veracity in ['TRUE','FALSE']:
        depth2times=veracity2depth2times[veracity]
        x=[]
        y=[]
        errors=[]
        for d,times in depth2times.items():
            if len(times)>thresh: #thresh is set to 2 in settings.py. There needs to be at least two points for each depth
                x.append(d)
                times=np.array(times)/60.0 ##convert to minutes
                y.append(np.mean(np.log10(times)))
                ##Calculting robust SEM##
                clusters=veracity2depth2clusters[veracity][d]
                y_r=np.log10(times)
                robust_sem=calc_robust_sem(y_r,clusters)
                ####
                errors.append(robust_sem)
        y=np.array(y)
        x=np.array(x)
        errors=np.array(errors)
        plt.plot(x,y,color=veracity2color[veracity],linewidth=lw)
        plt.fill_between(x, y-errors, y+errors,alpha=0.2,color=veracity2color[veracity])
    plt.xlabel('Depth',fontsize=fs)
    plt.ylabel("Mean Minutes",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.savefig('./figures/fig_2E.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 2F
    unique users vs time for all rumors
    '''
    print "Preparing figure 2F..."
    ax = plt.subplot(111)
    formatter = plt.FuncFormatter(lognormal)
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    formatter_x = plt.FuncFormatter(log_10_product)
    ax.xaxis.set_major_formatter(formatter_x)
    veracity2uu2times={}
    veracity2uu2clusters={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        rid=metadata['rumor_id']
        uu2time=metadata['uu2time']
        uu2times=veracity2uu2times.get(veracity,{})
        uu2clusters=veracity2uu2clusters.get(veracity,{})
        for uu,time_ in uu2time.items():
            times=uu2times.get(uu,[])
            times.append(time_)
            uu2times[uu]=times
            clusters=uu2clusters.get(uu,[])
            clusters.append(rid)
            uu2clusters[uu]=clusters
        veracity2uu2times[veracity]=uu2times
        veracity2uu2clusters[veracity]=uu2clusters
    for veracity in ['TRUE','FALSE']:
        uu2times=veracity2uu2times[veracity]
        x=[]
        y=[]
        errors=[]
        max_uu=max(uu2times.keys())
        for uu,times in uu2times.items():
            if len(times)>thresh:
                if uu%100!=0 and uu!=max_uu: #we are binning every 100 , otherwise there would be too many points in the plot and it would not load quickly.
                    continue
                x.append(uu)
                times=np.array(times)/60.0 #convert to minutes
                y.append(np.mean(np.log10(times)))
                ##Robust SEM##
                clusters=veracity2uu2clusters[veracity][uu]
                y_r=np.log10(times)
                robust_sem=calc_robust_sem(y_r,clusters)
                ####
                errors.append(robust_sem)
        y=np.array(y)
        x=np.array(x)
        errors=np.array(errors)
        ax.plot(x,y,color=veracity2color[veracity],linewidth=lw)
        ax.fill_between(x, y-errors, y+errors,alpha=0.2,color=veracity2color[veracity])
    plt.xlabel('Unique Users',fontsize=fs)
    plt.ylabel("Mean Minutes",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    ax.xaxis.set_ticks(np.arange(0,45000,10000))
    formatter=plt.FuncFormatter(kit2)
    ax.xaxis.set_major_formatter(formatter)
    plt.savefig('./figures/fig_2F.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 2G
    depth vs unique users for all rumors
    '''
    print "Preparing figure 2G..."
    ax = plt.subplot(111)
    formatter = plt.FuncFormatter(lognormal)
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    veracity2depth2uus={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        depth2uu=metadata['depth2uu']
        depth2uus=veracity2depth2uus.get(veracity,{})
        for depth,uu in depth2uu.items():
            uus=depth2uus.get(depth,[])
            uus.append(uu)
            depth2uus[depth]=uus
        veracity2depth2uus[veracity]=depth2uus
    for veracity in ['TRUE','FALSE']:
        depth2uus=veracity2depth2uus[veracity]
        x=[]
        y=[]
        errors=[]
        for d,uus in depth2uus.items():
            if len(uus)>thresh:
                x.append(d)
                uus=np.array(uus)
                y.append(np.mean(np.log10(uus)))
                ##Robust SEM##
                clusters=veracity2depth2clusters[veracity][d]
                y_r=np.log10(uus)
                robust_sem=calc_robust_sem(y_r,clusters)
                ####
                errors.append(robust_sem)
        y=np.array(y)
        x=np.array(x)
        errors=np.array(errors)
        plt.plot(x,y,color=veracity2color[veracity],linewidth=lw)
        plt.fill_between(x, y-errors, y+errors,alpha=0.2,color=veracity2color[veracity])
    plt.xlabel('Depth',fontsize=fs)
    plt.ylabel("Mean Unique Users",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.savefig('./figures/fig_2G.pdf', bbox_inches='tight', format='pdf')
    plt.figure()
    '''
    FIGURE 2H
    depth vs mean max-breadth for all rumors
    '''
    print "Preparing figure 2H..."
    ax = plt.subplot(111)
    formatter = plt.FuncFormatter(lognormal2)
    ax.yaxis.set_major_formatter(formatter)

    veracity2depth2breadths={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        depth2breadth=metadata['depth2breadth']
        depth2breadths=veracity2depth2breadths.get(veracity,{})
        for depth,breadth in depth2breadth.items():
            breadths=depth2breadths.get(depth,[])
            breadths.append(breadth)
            depth2breadths[depth]=breadths
        veracity2depth2breadths[veracity]=depth2breadths
    for veracity in ['TRUE','FALSE']:
        depth2breadths=veracity2depth2breadths[veracity]
        x=[]
        y=[]
        errors=[]
        for d,breadths in depth2breadths.items():
            if len(breadths)>thresh:
                x.append(d)
                breadths=np.array(breadths)
                y.append(np.mean(np.log10(breadths)))
                ##Robust SEM##
                clusters=veracity2depth2clusters[veracity][d]
                y_r=np.log10(breadths)
                robust_sem=calc_robust_sem(y_r,clusters)
                ####
                errors.append(robust_sem)
        y=np.array(y)
        x=np.array(x)
        errors=np.array(errors)
        plt.plot(x,y,color=veracity2color[veracity],linewidth=lw)
        plt.fill_between(x, y-errors, y+errors,alpha=0.2,color=veracity2color[veracity])
    plt.xlabel('Depth',fontsize=fs)
    plt.ylabel("Mean Breadth",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.savefig('./figures/fig_2H.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 3A
    CCDF of depth for political and non-political false rumors
    '''
    print "Preparing figure 3A..."
    ax = plt.subplot(111)
    ax.set_xscale('log')
    ax.set_yscale('log')
    formatter = plt.FuncFormatter(log_10_product)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    category2depths={}
    category2clusters={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        rid=metadata['rumor_id']
        if veracity!='FALSE':
            continue
        category=metadata['rumor_category']
        if category!='Politics':
            category='Other'
        depth=metadata['depth']+1 #adding one for smoothing purposes
        depths=category2depths.get(category,[])
        depths.append(depth)
        category2depths[category]=depths
        clusters=category2clusters.get(category,[])
        clusters.append(rid)
        category2clusters[category]=clusters

    print '##############################'
    print 'Depth Stats. False Political/Non-political'
    print 'Mean (log)',np.mean(np.log10(category2depths['Politics'])),np.mean(np.log10(category2depths['Other']))
    print 'Robust SEM (log)',calc_robust_sem(np.log10(category2depths['Politics']),category2clusters['Politics']),\
        calc_robust_sem(np.log10(category2depths['Other']),category2clusters['Other'])
    print  "KS test:",stats.ks_2samp(category2depths['Politics'],category2depths['Other'])
    for category,depths in category2depths.items():
        total=float(len(depths))
        xf=[]
        pf=[]
        depths.sort()
        counts=list(set(depths))
        counts.sort()
        for d in counts:
            ind=depths.index(d)
            count=len(depths[ind:])
            p=(count/float(total)) * 100
            xf.append(d)
            pf.append(p)
        ax.plot(xf,pf,category2linestyle[category],color=veracity2color['FALSE'],linewidth=lw)
    plt.xlabel("Cascade Depth",fontsize=fs)
    plt.ylabel("CCDF (%)",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.xticks(rotation='horizontal')
    plt.savefig('./figures/fig_3A.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 3B
    CCDF of size for political and non-political false rumors
    '''
    print "Preparing figure 3B..."
    ax = plt.subplot(111)
    ax.set_xscale('log')
    ax.set_yscale('log')
    formatter = plt.FuncFormatter(log_10_product)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    category2sizes={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        if veracity!='FALSE':
            continue
        category=metadata['rumor_category']
        if category!='Politics':
            category='Other'
        size=metadata['size']
        sizes=category2sizes.get(category,[])
        sizes.append(size)
        category2sizes[category]=sizes

    print '##############################'
    print 'Size Stats. False Political/Non-political'
    print 'Mean (log)',np.mean(np.log10(category2sizes['Politics'])),np.mean(np.log10(category2sizes['Other']))
    print 'Robust SEM (log)',calc_robust_sem(np.log10(category2sizes['Politics']),category2clusters['Politics']),\
        calc_robust_sem(np.log10(category2sizes['Other']),category2clusters['Other'])
    print  "KS test:",stats.ks_2samp(category2sizes['Politics'],category2sizes['Other'])
    for category,sizes in category2sizes.items():
        total=float(len(sizes))
        xf=[]
        pf=[]
        sizes.sort()
        counts=list(set(sizes))
        counts.sort()
        for d in counts:
            ind=sizes.index(d)
            count=len(sizes[ind:])
            p=(count/float(total)) * 100
            xf.append(d)
            pf.append(p)
        ax.plot(xf,pf,category2linestyle[category],color=veracity2color['FALSE'],linewidth=lw)
    plt.xlabel("Cascade Size",fontsize=fs)
    plt.ylabel("CCDF (%)",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.xticks(rotation='horizontal')
    plt.savefig('./figures/fig_3B.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 3C
    CCDF of max-breadth for political and non-political false rumors
    '''
    print "Preparing figure 3C..."
    ax = plt.subplot(111)
    ax.set_xscale('log')
    ax.set_yscale('log')
    formatter = plt.FuncFormatter(log_10_product)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    category2breadths={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        if veracity!='FALSE':
            continue
        category=metadata['rumor_category']
        if category!='Politics':
            category='Other'
        breadth=metadata['max_breadth']
        breadths=category2breadths.get(category,[])
        breadths.append(breadth)
        category2breadths[category]=breadths

    print '##############################'
    print 'Max-Breadth Stats. False Political/Non-political'
    print 'Mean (log)',np.mean(np.log10(category2breadths['Politics'])),np.mean(np.log10(category2breadths['Other']))
    print 'Robust SEM (log)',calc_robust_sem(np.log10(category2breadths['Politics']),category2clusters['Politics']),\
        calc_robust_sem(np.log10(category2breadths['Other']),category2clusters['Other'])
    print  "KS test:",stats.ks_2samp(category2breadths['Politics'],category2breadths['Other'])
    for category,breadths in category2breadths.items():
        total=float(len(breadths))
        xf=[]
        pf=[]
        breadths.sort()
        counts=list(set(breadths))
        counts.sort()
        for d in counts:
            ind=breadths.index(d)
            count=len(breadths[ind:])
            p=(count/float(total)) * 100
            xf.append(d)
            pf.append(p)
        ax.plot(xf,pf,category2linestyle[category],color=veracity2color['FALSE'],linewidth=lw)
    plt.xlabel("Cascade Max-Breadth",fontsize=fs)
    plt.ylabel("CCDF (%)",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.xticks(rotation='horizontal')
    plt.savefig('./figures/fig_3C.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 3D
    CCDF of strucural virality for all rumors
    '''
    print "Preparing figure 3D..."
    ax = plt.subplot(111)
    ax.set_xscale('log')
    ax.set_yscale('log')
    formatter = plt.FuncFormatter(log_10_product)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    category2viralities={}
    category2virality_clusters={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        if veracity!='FALSE':
            continue
        category=metadata['rumor_category']
        if category!='Politics':
            category='Other'
        virality=metadata['virality']
        rid=metadata['rumor_id']
        viralities=category2viralities.get(category,[])
        viralities.append(virality)
        category2viralities[category]=viralities
        if virality!=None:
            virality_clusters=category2virality_clusters.get(category,[])
            virality_clusters.append(rid)
            category2virality_clusters[category]=virality_clusters

    print '##############################'
    print 'Virality Stats. False Political/Non-political'
    print 'Mean (log)',np.mean(np.log10([e for e in category2viralities['Politics'] if e!=None])),np.mean(np.log10([e for e in category2viralities['Other'] if e!=None]))
    print 'Robust SEM (log)',calc_robust_sem(np.log10([e for e in category2viralities['Politics'] if e!=None]),category2virality_clusters['Politics']),\
        calc_robust_sem(np.log10([e for e in category2viralities['Other'] if e!=None]),category2virality_clusters['Other'])
    print  "KS test:",stats.ks_2samp([e for e in category2viralities['Politics'] if e!=None],[e for e in category2viralities['Other'] if e!=None])
    for category,viralities in category2viralities.items():
        xf=[]
        pf=[]
        viralities=[e if e!=None else 0 for e in viralities]
        total=float(len(viralities))
        viralities.sort()
        counts=[]
        c=min(viralities)
        step=0.25
        while c<max(viralities)+step:
            counts.append(c)
            c+=step
        counts.sort()
        for d in counts:
            ind=bisect.bisect_left(viralities,d)
            count=len(viralities[ind:])
            p=(count/float(total)) * 100
            xf.append(d)
            pf.append(p)
        ax.plot(xf,pf,category2linestyle[category],color=veracity2color['FALSE'],linewidth=lw)
    plt.xlabel("Structural Virality",fontsize=fs)
    plt.ylabel("CCDF (%)",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.xticks(rotation='horizontal')
    plt.xlim([1,100])
    plt.savefig('./figures/fig_3D.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 3E
    depth vs time for political and non-political false rumors
    '''
    print "Preparing figure 3E..."
    ax = plt.subplot(111)
    formatter = plt.FuncFormatter(lognormal)
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    category2depth2times={}
    category2depth2clusters={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        if veracity!='FALSE':
            continue
        category=metadata['rumor_category']
        if category!='Politics':
            category='Other'
        rid=metadata['rumor_id']
        depth2time=metadata['depth2time']
        depth2times=category2depth2times.get(category,{})
        depth2clusters=category2depth2clusters.get(category,{})
        for depth,time_ in depth2time.items():
            times=depth2times.get(depth,[])
            times.append(time_)
            depth2times[depth]=times
            clusters=depth2clusters.get(depth,[])
            clusters.append(rid)
            depth2clusters[depth]=clusters
        category2depth2times[category]=depth2times
        category2depth2clusters[category]=depth2clusters
    for category in ['Politics','Other']:
        depth2times=category2depth2times[category]
        x=[]
        y=[]
        errors=[]
        for d,times in depth2times.items():
            if len(times)>thresh:
                x.append(d)
                times=np.array(times)/60.0 ##convert to minutes
                y.append(np.mean(np.log10(times)))
                ##Calculting robust SEM##
                clusters=category2depth2clusters[category][d]
                y_r=np.log10(times)
                robust_sem=calc_robust_sem(y_r,clusters)
                ####
                errors.append(robust_sem)
        y=np.array(y)
        x=np.array(x)
        errors=np.array(errors)
        plt.plot(x,y,category2linestyle[category],color=veracity2color['FALSE'],linewidth=lw)
        plt.fill_between(x, y-errors, y+errors,alpha=0.2,color=veracity2color['FALSE'])
    plt.xlabel('Depth',fontsize=fs)
    plt.ylabel("Mean Minutes",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.savefig('./figures/fig_3E.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 3F
    unique users vs time for political and non-political false rumors
    '''
    print "Preparing figure 3F..."
    ax = plt.subplot(111)
    formatter = plt.FuncFormatter(lognormal)
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    formatter_x = plt.FuncFormatter(log_10_product)
    ax.xaxis.set_major_formatter(formatter_x)
    category2uu2times={}
    category2uu2clusters={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        if veracity!='FALSE':
            continue
        category=metadata['rumor_category']
        if category!='Politics':
            category='Other'
        rid=metadata['rumor_id']
        uu2time=metadata['uu2time']
        uu2times=category2uu2times.get(category,{})
        uu2clusters=category2uu2clusters.get(category,{})
        for uu,time_ in uu2time.items():
            times=uu2times.get(uu,[])
            times.append(time_)
            uu2times[uu]=times
            clusters=uu2clusters.get(uu,[])
            clusters.append(rid)
            uu2clusters[uu]=clusters
        category2uu2times[category]=uu2times
        category2uu2clusters[category]=uu2clusters
    for category in ['Politics','Other']:
        uu2times=category2uu2times[category]
        x=[]
        y=[]
        errors=[]
        max_uu=max(uu2times.keys())
        for uu,times in uu2times.items():
            if len(times)>thresh:
                if uu%100!=0 and uu!=max_uu: #we are binning every 100 , otherwise there would be too many points in the plot and it would not load quickly.
                    continue
                x.append(uu)
                times=np.array(times)/60.0 #convert to minutes
                y.append(np.mean(np.log10(times)))
                ##Robust SEM##
                clusters=category2uu2clusters[category][uu]
                y_r=np.log10(times)
                robust_sem=calc_robust_sem(y_r,clusters)
                ####
                errors.append(robust_sem)
        y=np.array(y)
        x=np.array(x)
        errors=np.array(errors)
        ax.plot(x,y,category2linestyle[category],color=veracity2color['FALSE'],linewidth=lw)
        ax.fill_between(x, y-errors, y+errors,alpha=0.2,color=veracity2color['FALSE'])
    plt.xlabel('Unique Users',fontsize=fs)
    plt.ylabel("Mean Minutes",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    ax.xaxis.set_ticks(np.arange(0,45000,10000))
    formatter=plt.FuncFormatter(kit2)
    ax.xaxis.set_major_formatter(formatter)
    plt.savefig('./figures/fig_3F.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 3G
    depth vs unique users for political and non-political false rumors
    '''
    print "Preparing figure 3G..."
    ax = plt.subplot(111)
    formatter = plt.FuncFormatter(lognormal)
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    category2depth2uus={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        if veracity!='FALSE':
            continue
        category=metadata['rumor_category']
        if category!='Politics':
            category='Other'
        depth2uu=metadata['depth2uu']
        depth2uus=category2depth2uus.get(category,{})
        for depth,uu in depth2uu.items():
            uus=depth2uus.get(depth,[])
            uus.append(uu)
            depth2uus[depth]=uus
        category2depth2uus[category]=depth2uus
    for category in ['Politics','Other']:
        depth2uus=category2depth2uus[category]
        x=[]
        y=[]
        errors=[]
        for d,uus in depth2uus.items():
            if len(uus)>thresh:
                x.append(d)
                uus=np.array(uus)
                y.append(np.mean(np.log10(uus)))
                ##Robust SEM##
                clusters=category2depth2clusters[category][d]
                y_r=np.log10(uus)
                robust_sem=calc_robust_sem(y_r,clusters)
                ####
                errors.append(robust_sem)
        y=np.array(y)
        x=np.array(x)
        errors=np.array(errors)
        plt.plot(x,y,category2linestyle[category],color=veracity2color['FALSE'],linewidth=lw)
        plt.fill_between(x, y-errors, y+errors,alpha=0.2,color=veracity2color['FALSE'])
    plt.xlabel('Depth',fontsize=fs)
    plt.ylabel("Mean Unique Users",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.savefig('./figures/fig_3G.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 3H
    depth vs mean max-breadth for political and non-political false rumors
    '''
    print "Preparing figure 3H..."
    ax = plt.subplot(111)
    formatter = plt.FuncFormatter(lognormal2)
    ax.yaxis.set_major_formatter(formatter)
    category2depth2breadths={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        if veracity!='FALSE':
            continue
        category=metadata['rumor_category']
        if category!='Politics':
            category='Other'
        depth2breadth=metadata['depth2breadth']
        depth2breadths=category2depth2breadths.get(category,{})
        for depth,breadth in depth2breadth.items():
            breadths=depth2breadths.get(depth,[])
            breadths.append(breadth)
            depth2breadths[depth]=breadths
        category2depth2breadths[category]=depth2breadths
    for category in ['Politics','Other']:
        depth2breadths=category2depth2breadths[category]
        x=[]
        y=[]
        errors=[]
        for d,breadths in depth2breadths.items():
            if len(breadths)>thresh:
                x.append(d)
                breadths=np.array(breadths)
                y.append(np.mean(np.log10(breadths)))
                ##Robust SEM##
                clusters=category2depth2clusters[category][d]
                y_r=np.log10(breadths)
                robust_sem=calc_robust_sem(y_r,clusters)
                ####
                errors.append(robust_sem)
        y=np.array(y)
        x=np.array(x)
        errors=np.array(errors)
        plt.plot(x,y,category2linestyle[category],color=veracity2color['FALSE'],linewidth=lw)
        plt.fill_between(x, y-errors, y+errors,alpha=0.2,color=veracity2color['FALSE'])
    plt.xlabel('Depth',fontsize=fs)
    plt.ylabel("Mean Breadth",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.savefig('./figures/fig_3H.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    '''
    FIGURE 4A
    user stats for false and true cascades
    '''
    print "Preparing figure 4A..."
    veracity2followers={}
    veracity2followees={}
    veracity2account_age={}
    veracity2engagement={}
    veracity2verified={}

    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']

        followers=metadata['num_followers_list']
        followers=[e+epsilon for e in followers if e!=None] #smoothing
        followers_list=veracity2followers.get(veracity,[])
        followers_list.extend(followers)
        veracity2followers[veracity]=followers_list

        followees=metadata['num_followees_list']
        followees=[e+epsilon for e in followees if e!=None] #smoothing
        followees_list=veracity2followees.get(veracity,[])
        followees_list.extend(followees)
        veracity2followees[veracity]=followees_list

        account_age=metadata['accountage_list']
        account_age=[e for e in account_age if e!=None] #smoothing
        account_age_list=veracity2account_age.get(veracity,[])
        account_age_list.extend(account_age)
        veracity2account_age[veracity]=account_age_list

        engagement=metadata['engagement_list']
        engagement=[e+epsilon for e in engagement if e!=None] #smoothing
        engagement_list=veracity2engagement.get(veracity,[])
        engagement_list.extend(engagement)
        veracity2engagement[veracity]=engagement_list

        verified=metadata['verified_list']
        verified=[e for e in verified if e!=None] #smoothing
        verified_list=veracity2verified.get(veracity,[])
        verified_list.extend(verified)
        veracity2verified[veracity]=verified_list

    D,p=stats.ks_2samp(veracity2followers['FALSE'],veracity2followers['TRUE'])
    row1=[np.median(veracity2followers['FALSE']),np.median(veracity2followers['TRUE']),
         np.mean(veracity2followers['FALSE']),np.mean(veracity2followers['TRUE']),
         np.mean(np.log10(veracity2followers['FALSE'])),np.mean(np.log10(veracity2followers['TRUE'])),
         np.std(np.log10(veracity2followers['FALSE'])),np.std(np.log10(veracity2followers['TRUE'])),
         D,p]

    D,p=stats.ks_2samp(veracity2followees['FALSE'],veracity2followees['TRUE'])
    row2=[np.median(veracity2followees['FALSE']),np.median(veracity2followees['TRUE']),
         np.mean(veracity2followees['FALSE']),np.mean(veracity2followees['TRUE']),
         np.mean(np.log10(veracity2followees['FALSE'])),np.mean(np.log10(veracity2followees['TRUE'])),
         np.std(np.log10(veracity2followees['FALSE'])),np.std(np.log10(veracity2followees['TRUE'])),
         D,p]

    D,p=stats.ks_2samp(veracity2verified['FALSE'],veracity2verified['TRUE'])
    row3=[np.median(veracity2verified['FALSE']),np.median(veracity2verified['TRUE']),
         np.mean(veracity2verified['FALSE']),np.mean(veracity2verified['TRUE']),
         np.mean(np.log10(veracity2verified['FALSE'])),np.mean(np.log10(veracity2verified['TRUE'])),
         np.std(np.log10(veracity2verified['FALSE'])),np.std(np.log10(veracity2verified['TRUE'])),
         D,p]

    D,p=stats.ks_2samp(veracity2engagement['FALSE'],veracity2engagement['TRUE'])
    row4=[np.median(veracity2engagement['FALSE']),np.median(veracity2engagement['TRUE']),
         np.mean(veracity2engagement['FALSE']),np.mean(veracity2engagement['TRUE']),
         np.mean(np.log10(veracity2engagement['FALSE'])),np.mean(np.log10(veracity2engagement['TRUE'])),
         np.std(np.log10(veracity2engagement['FALSE'])),np.std(np.log10(veracity2engagement['TRUE'])),
         D,p]

    D,p=stats.ks_2samp(veracity2account_age['FALSE'],veracity2account_age['TRUE'])
    row5=[np.median(veracity2account_age['FALSE']),np.median(veracity2account_age['TRUE']),
         np.mean(veracity2account_age['FALSE']),np.mean(veracity2account_age['TRUE']),
         np.mean(np.log10(veracity2account_age['FALSE'])),np.mean(np.log10(veracity2account_age['TRUE'])),
         np.std(np.log10(veracity2account_age['FALSE'])),np.std(np.log10(veracity2account_age['TRUE'])),
         D,p]

    table=np.array([np.array(row1),np.array(row2),np.array(row3),np.array(row4),np.array(row5)])
    table=pd.DataFrame(table,["followers","followees","verified","engagement","account age"],
                       ["median-false","median-true","mean-false","mean-true","mean(log)-false","mean(log)-true","stdv(log)-false","stdv(log)-true","D","p"])
    print table

    '''
    FIGURE 4B
    logistic regression
    '''
    print "Preparing figure 4B..."
    y=[]
    followers_list=[]
    followees_list=[]
    verified_list=[]
    account_age_list=[]
    engagement_list=[]
    falsehood_list=[]
    intercept_list=[]
    clusters_list=[]
    for row in regression_data:
        clusters_list.append(row[0])
        y.append(row[1])
        followers_list.append(row[2])
        followees_list.append(row[3])
        verified_list.append(row[4])
        account_age_list.append(row[5])
        engagement_list.append(row[6])
        falsehood_list.append(row[7])
        intercept_list.append(1)

    x={'followers':pd.Series(followers_list),
       'followees':pd.Series(followees_list),
       'verified':pd.Series(verified_list),
       'account_age':pd.Series(account_age_list),
       'engagement':pd.Series(engagement_list),
       'falsehood':pd.Series(falsehood_list),
       'intercept':pd.Series(intercept_list)}
    x=pd.DataFrame(x)
    print "fitting model..."
    logit = sm.Logit(y, x)
    result=logit.fit(cov_type='cluster',cov_kwds={'groups': clusters_list})
    print result.summary()
    print "odds ratios:"
    print np.exp(result.params)
    ###Goodness of fit checks
    formula = "y ~ followers+followees+verified+account_age+engagement+falsehood"
    logit = smf.glm(formula=formula, data=x, family=sm.families.Binomial())
    result=logit.fit(cov_type='cluster',cov_kwds={'groups': clusters_list})
    print  "Deviance stats",1 - stats.chi2.cdf(result.deviance, result.df_resid)

    '''
    FIGUREs 4C, 4E
    Novelty
    '''
    print "Preparing figures 4C and 4E..."
    veracity2novelty_metric2scores={}
    veracity2clusters_novelty={}
    for tweet_id,rid_veracity_tweettopics_backgroundtopics in tid2rid_veracity_tweettopics_backgroundtopics.items():
        veracity=rid_veracity_tweettopics_backgroundtopics[1]
        rumor_id=rid_veracity_tweettopics_backgroundtopics[0]
        tweettopics=rid_veracity_tweettopics_backgroundtopics[2]
        backgroundtopics=rid_veracity_tweettopics_backgroundtopics[3]

        iu=calc_inf_uniq(backgroundtopics,tweettopics)
        klv=(calc_kl(backgroundtopics,tweettopics)+calc_kl(tweettopics,backgroundtopics))/2.0
        bhs=calc_bhatta(backgroundtopics,tweettopics)

        novelty_metrics2scores=veracity2novelty_metric2scores.get(veracity,{})
        scores=novelty_metrics2scores.get('IU',[])
        scores.append(iu)
        novelty_metrics2scores['IU']=scores

        scores=novelty_metrics2scores.get('KL',[])
        scores.append(klv)
        novelty_metrics2scores['KL']=scores

        scores=novelty_metrics2scores.get('BD',[])
        scores.append(bhs)
        novelty_metrics2scores['BD']=scores
        veracity2novelty_metric2scores[veracity]=novelty_metrics2scores

        clusters_novelty=veracity2clusters_novelty.get(veracity,[])
        clusters_novelty.append(rumor_id)
        veracity2clusters_novelty[veracity]=clusters_novelty

    ax = plt.subplot(111)
    formatter = plt.FuncFormatter(no_zero)
    ax.xaxis.set_major_formatter(formatter)
    offset=0
    max_kls=max(max(veracity2novelty_metric2scores['TRUE']['KL']),max(veracity2novelty_metric2scores['FALSE']['KL']))
    for veracity in ['TRUE','FALSE']:
        ius=veracity2novelty_metric2scores[veracity]['IU']
        kls=veracity2novelty_metric2scores[veracity]['KL']
        kls_scaled=np.array(kls)/max_kls
        bahs=veracity2novelty_metric2scores[veracity]['BD']
        means=np.array([np.mean(ius),np.mean(kls_scaled),np.mean(bahs)]) #for visualization purposes we rescale the KL
        ##Robust SEM##
        clusters= veracity2clusters_novelty[veracity]
        y_r=ius
        ius_robust_sem=calc_robust_sem(y_r,clusters)
        y_r=kls_scaled
        kls_robust_sem=calc_robust_sem(y_r,clusters)
        y_r=bahs
        bahs_robust_sem=calc_robust_sem(y_r,clusters)
        errors=np.array([ius_robust_sem,kls_robust_sem,bahs_robust_sem])
        ####
        y=[2+offset,1+offset,0+offset]
        offset-=0.30
        ax.scatter(means,y,s=50,color=veracity2color[veracity])
        ax.errorbar(means, y, xerr=errors,fmt='.',color=veracity2color[veracity],elinewidth=3,capsize=6,capthick=3)
    labels = ['IU','KL \n (rescaled)','BD']
    plt.yticks([2,1,0], labels,fontsize=fs)
    plt.xlabel("Novelty",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.ylim([-.4,2.3])
    plt.xlim([.42,.908])
    plt.savefig('./figures/fig_4C.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    table=[]
    for metric in ['IU','KL','BD']:
        D,p=stats.ks_2samp(veracity2novelty_metric2scores['FALSE'][metric],veracity2novelty_metric2scores['TRUE'][metric])
        row=[np.mean(veracity2novelty_metric2scores['FALSE'][metric]),np.mean(veracity2novelty_metric2scores['TRUE'][metric]),
             np.var(veracity2novelty_metric2scores['FALSE'][metric]),np.var(veracity2novelty_metric2scores['TRUE'][metric]),
             D,p]
        table.append(np.array(row))
    table=np.array(table)
    table=pd.DataFrame(table,['iu','kl','bd'],
                       ["mean-false","mean-true","var-false","var-true","D","p"])
    print table

    '''
    FIGUREs 4D, 4F
    Novelty
    '''
    print "Preparing figures 4D and 4F..."
    veracity2emotion2scores={}
    veracity2clusters_emotion={}
    for cascade,metadata in cascade_id2metadata.items():
        veracity=metadata['veracity']
        root_tid=metadata['root_tid']
        rumor_id=metadata['rumor_id']
        emotion2score=tid2emotion2score.get(root_tid)
        if emotion2score!=None:
            emotion2percs=veracity2emotion2scores.get(veracity,{})
            for emotion,score in emotion2score.items():
                percs=emotion2percs.get(emotion,[])
                percs.append(score)
                emotion2percs[emotion]=percs
            veracity2emotion2scores[veracity]=emotion2percs
            clusters_emotion=veracity2clusters_emotion.get(veracity,[])
            clusters_emotion.append(rumor_id)
            veracity2clusters_emotion[veracity]=clusters_emotion

    ax = plt.subplot(111)
    formatter = plt.FuncFormatter(no_zero)
    ax.xaxis.set_major_formatter(formatter)
    offset=0
    for veracity in ['TRUE','FALSE']:
        emotion2percs=veracity2emotion2scores[veracity]
        means=[]
        errors=[]
        for emotion in ['trust','joy','anticipation','sadness','anger','fear','disgust','surprise']:
            percs=emotion2percs[emotion]
            ##Robust SEM##
            clusters=veracity2clusters_emotion[veracity]
            y_r=percs
            robust_sem=calc_robust_sem(y_r,clusters)
            ####
            means.append(np.mean(percs))
            errors.append(robust_sem)
        means=np.array(means)
        errors=np.array(errors)
        y=[0+offset,1+offset,2+offset,3+offset,4+offset,5+offset,6+offset,7+offset]
        offset-=0.30
        ax.scatter(means,y,s=50,color=veracity2color[veracity])
        ax.errorbar(means, y, xerr=errors,fmt='.',color=veracity2color[veracity],elinewidth=3,capsize=6,capthick=3)

    labels = ['Trust','Joy','Anticipation','Sadness','Anger','Fear','Disgust','Surprise']
    plt.yticks([0,1,2,3,4,5,6,7], labels,fontsize=fs)
    plt.xlabel("% User Responses",fontsize=fs)
    ax.tick_params(axis='both', which='major', labelsize=fs_2)
    plt.ylim([-.51,7.45])
    plt.xlim([-.02,.25])
    plt.savefig('./figures/fig_4D.pdf', bbox_inches='tight', format='pdf')
    plt.figure()

    table=[]
    for emotion in reversed(['trust','joy','anticipation','sadness','anger','fear','disgust','surprise']):
        D,p=stats.ks_2samp(veracity2emotion2scores['FALSE'][emotion],veracity2emotion2scores['TRUE'][emotion])
        row=[np.mean(veracity2emotion2scores['FALSE'][emotion]),np.mean(veracity2emotion2scores['TRUE'][emotion]),
             np.var(veracity2emotion2scores['FALSE'][emotion]),np.var(veracity2emotion2scores['TRUE'][emotion]),
             D,p]
        table.append(np.array(row))
    table=np.array(table)
    table=pd.DataFrame(table,reversed(['trust','joy','anticipation','sadness','anger','fear','disgust','surprise']),
                       ["mean-false","mean-true","var-false","var-true","D","p"])
    print table



#convert_raw_data_to_metadata()  ##Warning: This take a long time to run!
generate_figures()