import re

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

def RegexGenerator(logformat):
   headers = []
   splitters = re.split(r'(<[^<>]+>)', logformat)
   format = ''
   for k in range(len(splitters)):
       if k % 2 == 0:
           splitter = re.sub(' +', '\\\s+', splitters[k])
           format += splitter
       else:
           header = splitters[k].strip('<').strip('>')
           format += '(?P<%s>.*?)' % header
           headers.append(header)
   format = re.compile('^' + format + '$')
   return format

def ContentExtractor(loglines):
    contentlist = []
    format = RegexGenerator(OpenStack_format)

    for line in loglines:
        match = format.search(line.strip())
        if match == None:
            pass;
        else:
            content = match.group('Content')
            contentlist.append(content)

    return contentlist

file = '../Data/Log/OpenStack_full.log'
output = '../Data/Log/full_data/OpenStack_content.log'

loglines = open(file, 'r').readlines()
content_writer = open(output, 'w')

contentlist = ContentExtractor(loglines)
for content in contentlist:
    content = content.replace('\n', '')
    content_writer.write(content + '\n')
