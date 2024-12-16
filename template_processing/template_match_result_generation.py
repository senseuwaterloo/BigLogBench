# 2. 

import pandas as pd
import re
import os
from template_processing.template_process import template_to_regex, read_templates
from utils import timeit
from tqdm import tqdm

class TemplateMatching:
    
    def __init__(
            self, 
            logName: str,
            logpath: str, # Path to logs
            f_template_table:str, # Path to template table
            save_dir: str,
            template_key: str = 'EventTemplate',
            sheet_name: str = 'templates_refine'
        ):
        self.logpath = logpath
        self.templates = read_templates(f_template_table, template_key, sheet_name)
        self.regex_list = []
        self.tmp_ori_list = []
        self.constant_list = []

        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)

        self.event_match_file = os.path.join(save_dir, f'{logName}_content_event.csv')
        self.unmatched_file = os.path.join(save_dir, f'{logName}_content_unmatched.log')
        self.template_match_file = os.path.join(save_dir, f'{logName}_content_template.csv')

        self._prep()

    def _prep(self):
        for tmp in self.templates:
            if(str(tmp).__contains__('<*>')):
                regex = template_to_regex(tmp)
                regex = '^' + regex
                self.regex_list.append(regex)
                self.tmp_ori_list.append(str(tmp))
            else:
                self.constant_list.append(str(tmp))
                    

    @timeit
    def match(self) -> int:
        print("Begin regular expression match process")
        with open(self.logpath, 'r') as r:
            logs = r.readlines()               
        event_heads = ['Content', 'EventTemplate']
        #event_csv_writer.writerow(event_heads)
        event_rows = []
                
        freq_dict_regex = {}
        freq_dict_constant = {}
        unmatched_logs = []
        for log in tqdm(logs):
            log = log.replace('\n', '')
            if(log in self.constant_list):
                constant_index = self.constant_list.index(log)
                if(constant_index in freq_dict_constant.keys()):
                    freq_dict_constant[constant_index] = freq_dict_constant[constant_index]+1
                else:
                    freq_dict_constant[constant_index] = 1
                log_info = log
                template_info = log
                row_info = [log_info, template_info]
                #event_csv_writer.writerow(row_info)
                event_rows.append(row_info)
            else:
                regex_index = 0
                while(regex_index < len(self.regex_list)):
                    regex = self.regex_list[regex_index]
                    match = re.search(regex, log)
                    if (match):
                        if(regex_index in freq_dict_regex.keys()):
                            freq_dict_regex[regex_index] = freq_dict_regex[regex_index]+1
                        else:
                            freq_dict_regex[regex_index] = 1
                        break
                    else:
                        regex_index = regex_index+1
                if(regex_index == len(self.regex_list)):
                    unmatched_logs.append(log)
                else:
                    template_info = self.tmp_ori_list[regex_index]
                    log_info = log
                    row_info = [log_info, template_info]
                    #event_csv_writer.writerow(row_info)
                    event_rows.append(row_info)
                
        print(f"Number of unmatched logs are " + str(len(unmatched_logs)))
        with open(self.unmatched_file, "w") as w:
            w.write('\n'.join(unmatched_logs))

        num_unmatched = len(unmatched_logs)
        del unmatched_logs

        df_event = pd.DataFrame(event_rows, columns=event_heads)
        df_event.to_csv(self.event_match_file, index=False)    # Dump matched events
        del event_rows

        # Save matched templates
        template_heads = ['Template', 'Occurrence']
        template_rows = []
        #template_csv_writer.writerow(template_heads)
        index = 0
        while(index < len(self.constant_list)):
            if(index in freq_dict_constant.keys()):
                template_info = self.constant_list[index].replace("\n", "")
                frequency_info = freq_dict_constant[index]
                row_info = [template_info, frequency_info]
                #template_csv_writer.writerow(row_info)
                template_rows.append(row_info)
            else:
                pass
            index = index + 1
        index = 0
        while(index < len(self.tmp_ori_list)):
            if(index in freq_dict_regex.keys()):
                template_info = self.tmp_ori_list[index].replace("\n", "")
                frequency_info = freq_dict_regex[index]
                row_info = [template_info, frequency_info]
                #template_csv_writer.writerow(row_info)
                template_rows.append(row_info)
            else:
                pass
            index = index+1

        df_template = pd.DataFrame(template_rows, columns=template_heads)
        df_template.to_csv(self.template_match_file, index=False)    # Dump matched templates
        
        return num_unmatched
        
