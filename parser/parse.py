import os
import hashlib
import pandas as pd
from datetime import datetime
from parser.Drain.Drain import LogParser, Node, Logcluster
from parser.PILAR.DictionarySetUp import GramDict
from parser.PILAR.Parser import Parser
from parser.PILAR.Common import Preprocess, RegexGenerator


class GramDict_Content(GramDict):
    def __init__(self, log_content_path, separator, logformat, regex, ratio):
        super().__init__(log_content_path, separator, logformat, regex, ratio)

    def tokenize_content(self, content, regex):

        line = Preprocess(content,regex)
        tokens = line.strip().split()
    # print(tokens)
        return tokens

    def DictionarySetUp(self):
        loglines = open(self.logfile, encoding= 'ISO-8859-1').readlines()
        num = (int) (len(loglines) * (self.ratio))

        tokenslist = []
        i = 0

        for line in loglines:
            tokens = self.tokenize_content(line, self.regex)
            if tokens == None:
                pass
            else:
                tokenslist.append(tokens)
                if i <= num:
                    self.GramBuilder(tokens)
                i = i+1

        return tokenslist, self.singledict, self.doubledict, self.tridict

class PILARParse():
    def __init__(self, logName, log_format, log_content_path, outdir, rex, separator = ' ', ratio=1, threshold=0.1) -> None:
        self.logName = logName
        self.log_format = log_format
        self.log_content_path = log_content_path
        self.rex = rex
        self.outdir = outdir
        self.separator = separator
        self.ratio = ratio
        self.threshold = threshold


    def parse(self):
        # A modified GramDict class targeting content files only
        gramdict = GramDict_Content(
            log_content_path=self.log_content_path,
            separator=self.separator, 
            logformat=self.log_format,
            regex=self.rex, 
            ratio=self.ratio)
        # tokenslist, singledict, doubledict, tridict, fourdict = gramdict.DictionarySetUp()
        tokenslist, singledict, doubledict, tridict= gramdict.DictionarySetUp()

        parser = Parser(
            tokenslist=tokenslist, 
            singledict=singledict, 
            doubledict=doubledict, 
            tridict=tridict, 
            threshold=self.threshold,
            outpath_base = os.path.join(self.outdir, self.logName)
            )
        return parser.Parse()

class DrainParse(LogParser):
    def __init__(self, logName, log_format, log_content_path, outdir="./result", depth=4, st=0.4, maxChild=100, rex=..., keep_para=True):
        indir = os.path.dirname(log_content_path)
        super().__init__(log_format, indir, outdir, depth, st, maxChild, rex, keep_para)
        self.logName = logName
        self.log_content_path = log_content_path

    
    def outputResult(self, logClustL):
        log_templates = [0] * self.df_log.shape[0]
        log_templateids = [0] * self.df_log.shape[0]
        df_events = []

        f_events_output = os.path.join(self.savePath, self.logName + "_events.csv")
        f_templates_output = os.path.join(self.savePath, self.logName + "_templates.csv")

        for logClust in logClustL:
            template_str = " ".join(logClust.logTemplate)
            occurrence = len(logClust.logIDL)
            template_id = hashlib.md5(template_str.encode("utf-8")).hexdigest()[0:8]
            for logID in logClust.logIDL:
                logID -= 1
                log_templates[logID] = template_str
                log_templateids[logID] = template_id
            df_events.append([template_id, template_str, occurrence])

        df_event = pd.DataFrame(
            df_events, columns=["EventId", "EventTemplate", "Occurrences"]
        )
        self.df_log["EventId"] = log_templateids
        self.df_log["EventTemplate"] = log_templates
        if self.keep_para:
            self.df_log["ParameterList"] = self.df_log.apply(
                self.get_parameter_list, axis=1
            )
        self.df_log.to_csv(f_events_output, index=False)

        occ_dict = dict(self.df_log["EventTemplate"].value_counts())
        df_event = pd.DataFrame()
        df_event["EventTemplate"] = self.df_log["EventTemplate"].unique()
        df_event["EventId"] = df_event["EventTemplate"].map(
            lambda x: hashlib.md5(x.encode("utf-8")).hexdigest()[0:8]
        )
        df_event["Occurrences"] = df_event["EventTemplate"].map(occ_dict)
        df_event.to_csv(f_templates_output, index=False,
            columns=["EventId", "EventTemplate", "Occurrences"],
        )

        return f_events_output, f_templates_output
    
    
    def parse(self):
        print("Parsing file: " + self.log_content_path)
        start_time = datetime.now()
        rootNode = Node()
        logCluL = []

        #content_lines = open(self.log_content_path, 'r').readlines()
        self.df_log = pd.read_table(self.log_content_path, header=None, names=['Content'])
        self.df_log.insert(0, 'LineId', self.df_log.index + 1)

        count = 0
        for idx, line in self.df_log.iterrows():
            logID = line['LineId']
            logmessageL = self.preprocess(line['Content']).strip().split()
            matchCluster = self.treeSearch(rootNode, logmessageL)

            # Match no existing log cluster
            if matchCluster is None:
                newCluster = Logcluster(logTemplate=logmessageL, logIDL=[logID])
                logCluL.append(newCluster)
                self.addSeqToPrefixTree(rootNode, newCluster)

            # Add the new log message to the existing cluster
            else:
                newTemplate = self.getTemplate(logmessageL, matchCluster.logTemplate)
                matchCluster.logIDL.append(logID)
                if " ".join(newTemplate) != " ".join(matchCluster.logTemplate):
                    matchCluster.logTemplate = newTemplate

            count += 1
            if count % 1000 == 0 or count == len(self.df_log):
                print(
                    "Processed {0:.1f}% of log lines.".format(
                        count * 100.0 / len(self.df_log)
                    )
                )

        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath)


        print("Parsing done. [Time taken: {!s}]".format(datetime.now() - start_time))

        return self.outputResult(logCluL)