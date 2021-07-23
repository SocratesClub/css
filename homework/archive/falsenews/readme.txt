If you have any questions about the data or the code (or the libraries) please contact me at soroush@mit.edu

Requires python 2.7

###########
#LIBRARIES#
###########

dependent libraries:
numpy
scipy
dateutil
pandas
matplotlib
seaborn
pylab
networkx
statsmodels

You can install all the libraries using pip (e.g., pip install pandas). If there is an issue with version, please contact me.

############
#DATA FILES#
############
All ids are anonmized (meaning that the tweet_ids don't point to actual tweets.)
Here is a description of the data files in ./data:

#emotions.csv#
Has all the emotion data for Figures 4d and 4f. Each row contains an tweet_id and the emotional breakdown of the replies.

#topics.csv#
Has all the topic data for calculating novelty for Figures 4c and 4e. Each row contains a tweet_id, the rumor_id, the rumor veracity and tweet and background topics.
The tweet and background topics are 200 dimensional vectors.

#raw_data.csv#
Has the ananomized raw_data for every single tweet and retweet. It includes infroamtion about user and the propagation path. This data can be used to recreate all cascades.
The parent_id points to the parent of a node. If parent_id is -1, the node is the root node.
Creating and processing the cascades is very time consuming, therefore we have also included the already processed file (see below):

#regression_data.txt#
Contains data for the regression model in Figure 4b

#meta_data.txt#
Is the processed version of raw_data.csv. All findings in the paper can be replicated using this file, in conjunction with topics.csv, emotions.csv and regression_data.csv.
Note that this is not a csv file, this is a text files that is evaluated by python and turned into python objects.

############
####CODE####
############
Theare are three python files: main.py, analyze_cascade.py, and setting.py

#settings.py#
This has all the parameters and helper functions, and imports all the dependent libraries.

#analyze_cascade.py#
This file has the machinary for extracting metadata from cascades.

#main.py#
This is the main code. If run, it regenrates all the figures in the main article in ./figures (the tables in Figure 4 are printed on screen).
This file has two main methods:
1) convert_raw_data_to_metadata() , which read the raw data in raw_data.csv and produces metadata.txt.
Note that this is a very time-consuming process. As such, we provide the processed metadata in metadata.txt so that you dont have to run this method.

2) generate_figures() , this method reads in emotioncs.csv, metadata.txt, topics,csv and regression_data.txt and replicated all the figures in ./figures (the tables are printed).
This is a relatively fast method, but could still take severla minutes to run due to the sheer amount of data.


##Please note that due to our agreement with Twitter, we have removed all identified bot accounts/activity from the dataset provided