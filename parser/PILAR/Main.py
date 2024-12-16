from parser.PILAR.DictionarySetUp import GramDict
from parser.PILAR.Parser import Parser
from parser.PILAR.evaluator import evaluate
from parser.PILAR.DictSummary import DictEvaluate
from parser.PILAR.DictSummary import DictPrint
from parser.PILAR.DictionarySetUp import EntropyOnline

import numpy as np
import statistics
from parser.PILAR.Common import cohend
from parser.PILAR.Common import cliffsDelta

logfile = 'Test/Zookeeper_2k.log'
eventoutput = 'Output/event.txt'
templateoutput = 'Output/template.csv'
separator = ' '
regex = [
        r'([\w-]+\.)+[\w-]+(:\d+)', #url
        r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', # IP
        r'(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$', # Numbers
]

HDFS_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>'  # HDFS log format
Andriod_format = '<Date> <Time>  <Pid>  <Tid> <Level> <Component>: <Content>' #Andriod log format
Spark_format = '<Date> <Time> <Level> <Component>: <Content>'#Spark log format
Zookeeper_format = '<Date> <Time> - <Level>  \[<Node>:<Component>@<Id>\] - <Content>' #Zookeeper log format
Windows_format = '<Date> <Time>, <Level>                  <Component>    <Content>' #Windows log format
Thunderbird_format = '<Label> <Timestamp> <Date> <User> <Month> <Day> <Time> <Location> <Component>(\[<PID>\])?: <Content>' #Thunderbird_format
Apache_format = '\[<Time>\] \[<Level>\] <Content>' #Apache format
BGL_format = '<Label> <Timestamp> <Date> <Node> <Time> <NodeRepeat> <Type> <Component> <Level> <Content>' #BGL format
Hadoop_format = '<Date> <Time> <Level> \[<Process>\] <Component>: <Content>' #Hadoop format
HPC_format = '<LogId> <Node> <Component> <State> <Time> <Flag> <Content>' #HPC format
Linux_format = '<Month> <Date> <Time> <Level> <Component>(\[<PID>\])?: <Content>' #Linux format
Mac_format = '<Month>  <Date> <Time> <User> <Component>\[<PID>\]( \(<Address>\))?: <Content>' #Mac format
OpenSSH_format = '<Date> <Day> <Time> <Component> sshd\[<Pid>\]: <Content>' #OpenSSH format
OpenStack_format = '<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>' #OpenStack format
HealthApp_format = '<Time>\|<Component>\|<Pid>\|<Content>'
Proxifier_format = '\[<Time>\] <Program> - <Content>'

HDFS_Regex = [r'blk_-?\d+', r'(\d+\.){3}\d+(:\d+)?']
Hadoop_Regex = [r'(\d+\.){3}\d+']
Spark_Regex = [r'(\d+\.){3}\d+', r'\b[KGTM]?B\b', r'([\w-]+\.){2,}[\w-]+']
Zookeeper_Regex = [r'(/|)(\d+\.){3}\d+(:\d+)?']
BGL_Regex = [r'core\.\d+']
HPC_Regex = [r'=\d+']
Thunderbird_Regex = [r'(\d+\.){3}\d+']
Windows_Regex = [r'0x.*?\s']
Linux_Regex = [r'(\d+\.){3}\d+', r'\d{2}:\d{2}:\d{2}']
Andriod_Regex = [r'(/[\w-]+)+', r'([\w-]+\.){2,}[\w-]+', r'\b(\-?\+?\d+)\b|\b0[Xx][a-fA-F\d]+\b|\b[a-fA-F\d]{4,}\b']
Apache_Regex = [r'(\d+\.){3}\d+']
OpenSSH_Regex = [r'(\d+\.){3}\d+', r'([\w-]+\.){2,}[\w-]+']
OpenStack_Regex = [r'((\d+\.){3}\d+,?)+', r'/.+?\s', r'\d+']
Mac_Regex = [r'([\w-]+\.){2,}[\w-]+']
HealthApp_Regex = []
Proxifier_Regex = [r'<\d+\ssec', r'([\w-]+\.)+[\w-]+(:\d+)?', r'\d{2}:\d{2}(:\d{2})*', r'[KGTM]B']
Thunderbird_Regex = [r'(\d+\.){3}\d+']

# steps = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

gramdict = GramDict(logfile, separator, Zookeeper_format, Zookeeper_Regex, 1)
# tokenslist, singledict, doubledict, tridict, fourdict = gramdict.DictionarySetUp()
tokenslist, singledict, doubledict, tridict= gramdict.DictionarySetUp()

parser = Parser(tokenslist, singledict, doubledict, tridict, 0.1)
parser.Parse()

# onlineparser = EntropyOnline(logfile, separator, Andriod_format, Andriod_Regex, 0.1)
# onlineparser.Parse()
#
# OnlineEvents = open('Output/OLevent.txt').readlines()
# OfflineEvents = open('Output/event.txt').readlines()
#
# index = 0
# num = 0
# for OLevent in OnlineEvents:
#     OFFevent = OfflineEvents[index]
#     if OLevent == OFFevent:
#         num = num + 1
#     index = index + 1
#
# ratio = num/(index + 1)
# print(ratio)

# for s in steps:
#     print(s)
#     parser = Parser(tokenslist, singledict, doubledict, tridict, s)
#     dList, sList = parser.ParseTest()
#     print("pvalue: " + str(stats.ttest_ind(dList, sList)))
#     print("cohend: " + str(cohend(sList, dList)))
#     print("mean: " + str(statistics.mean(sList) - statistics.mean(dList)))
#     print("cliff: " + str(cliffsDelta(sList,dList)))

#DictPrint(entropydict)
#evaluate('GroundTruth/Andriod_2k.log_structured.csv', 'Output/event.txt')