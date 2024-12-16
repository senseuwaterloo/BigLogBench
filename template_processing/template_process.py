import os
import re
import pandas as pd
import random
from utils import timeit
from typing import Union, List
from utils import getlogger

logger = getlogger()

def read_templates(f_template_table: str, template_key: Union[str, List[str]], sheet_name: str = None) -> List[str]:
    """Read templates from refined table file
        Sheet name is required when processing excel files
    Args:
        f_template_table (str): _description_
        template_key (Union[str, List[str]]): _description_
        sheet_name (str, optional): _description_. Defaults to None.

    Returns:
        List[str]: _description_
    """
    ext = os.path.basename(f_template_table).split('.')[-1]
    if ext == 'csv':
        if isinstance(template_key, str):
            templates = pd.read_csv(f_template_table)[template_key].dropna().to_list()
        elif isinstance(template_key, list):
            df = pd.read_csv(f_template_table)
            templates = []
            for column in template_key:
                if column in df.columns:
                    templates += df[column].dropna().tolist()
        else:
            raise TypeError("Invalid template_key type. Expected str or list of str.")
    elif ext == 'xlsx':
        if isinstance(template_key, str):
            templates = pd.read_excel(f_template_table, sheet_name=sheet_name)[template_key].dropna().to_list()
        elif isinstance(template_key, list):
            df = pd.read_excel(f_template_table, sheet_name=sheet_name)
            templates = []
            for column in template_key:
                if column in df.columns:
                    templates += df[column].dropna().tolist()
        else:
            raise TypeError("Invalid template_key type. Expected str or list of str.")
    else:
        raise TypeError(f'Unknown document type: {ext}. Only accepts xlsx or csv formats.')
    # Ignore empty cells 
    return [x for x in templates if x and x.strip() != '']


def template_to_regex(template):
    regex = template
    regex = regex.replace("\\", "\\\\")
    regex = regex.replace(".", "\.")
    regex = regex.replace("*", "\*")

    regex = regex.replace("<\*>", ".*")

    regex = regex.replace("(", "\(")
    regex = regex.replace(")", "\)")

    regex = regex.replace("[","\[")
    regex = regex.replace("]","\]")

    regex = regex.replace("|","\|")

    regex = regex.replace("+", "\+")
    regex = regex.replace("?", "\?")
    regex = regex.replace("$", "\$")
    regex = regex.replace("@", "\@")
    regex = regex.replace("^", "\^")

    #regex = regex.replace(":", "\:")
    #regex = regex.replace("\"", "\\\"")


    regex = regex + '$'

    return regex


def tmp0_match_tmp1(tmp0, tmp1):
    regex0 = template_to_regex(tmp0)
    match = re.search(regex0, tmp1)
    if(match):
        return True
    else:
        return False

def insertTemplate(tmp, tmplist):
    index = 0
    for idx, t in enumerate(tmplist):
        if((tmp0_match_tmp1(t, tmp) == True) and (tmp0_match_tmp1(tmp, t) == False)):
            return index
        else:
            index = index+1
    return -1

@timeit
def build_groundtruth(outputdir:str, current_iteration: int, logName: str, template_key: str) -> str:
    templates = []
    f_groundtruth = os.path.join(outputdir, f'{logName}_templates_groundtruth.csv')
    for it in range(1, current_iteration + 1):
        # Find templates in prior iteration
        f_template_table = os.path.join(
            outputdir,
            f'iteration_{it}/'
            f'{logName}_templates_refined.csv'
        )
        if not os.path.isfile(f_template_table):
            raise FileExistsError(f'Template file of iteration {it} is not found: missing {f_template_table};' + f'Make sure your iterations are continuous and complete required steps for each iteration.')
        
        templates += read_templates(f_template_table, template_key)
    
    templates_refined = refine_templates(templates)
    save_templates(templates_refined, f_groundtruth)
    return f_groundtruth


def save_templates(templates: list, savepath:str):
    pd.DataFrame({'EventTemplate' : templates}).to_csv(savepath, index=False)
    print(f'Finished template refinement; new templates saved at: {savepath}')

    
@timeit
def refine_templates_from_file(logName: str, f_template_table: str, template_key: str, sheet_name:str = None) -> str:
    f_refined_templates = os.path.join(
        os.path.dirname(f_template_table),
        f'{logName}_templates_refined.csv'
    )
    templates = read_templates(f_template_table, template_key, sheet_name)
    templates_new = refine_templates(templates)
    save_templates(templates_new, f_refined_templates)
    return f_refined_templates


def template_log_matching(template_str: str, log_str:str):
    """Check if tempalte can match logs

    Args:
        template_str (str): tempalte string
        log_str (str): log content string

    Returns:
        _type_: if matches
    """
    if '<*>' in template_str:
        regex = template_to_regex(template_str)
        regex = '^' + regex
        match = re.search(regex, log_str)
        return match
    else:
        return template_str == log_str


@timeit
def verify_templates(f_template_table: str, template_key: str, sheet_name:str = None, log_content_key: str = "Content") -> bool:
    """Verifies the output for manually labeled templates can 
        1) match corresponding logs 
        2) no logs can be matched by two different templates
    Args:
        f_template_table (str): path to verfied template table (xlsx format)
        template_key (List[str]): Column names of event templates
        sheet_name (str, optional): Name of the sheet where refined templates are. Defaults to None.
        log_content_key (str): Name of the log content column. Defaults to "Content".
    Returns:
        bool: is valid
    """
    print('Verifying refined templates, check if they can match the associate logs')
    df_templates_refined = pd.read_excel(f_template_table, sheet_name=sheet_name)
    unmatched_idx = []
    for idx, row in df_templates_refined.iterrows():
        template = row['Refined Template']
        log = row['Content']
        
        # Empty row
        if pd.isna(template) and pd.isna(log):
            continue
        
        # Check match
        match = template_log_matching(template_str=template, log_str=log)
        
        if not match:
            print(f'Unmatched template found at line {idx + 2}: template {template}; log: {log}')
            unmatched_idx.append(idx + 2)
            
    print(f'In total {len(unmatched_idx)} templates fail to match.')
    
    if len(unmatched_idx) != 0:
        logger.error(f'In total {len(unmatched_idx)} unmatched logs detected when checking manually refined templates.')
    return len(unmatched_idx) == 0
            
        
        
        

# @timeit
def refine_templates(templates: list):
    templates_new = []
    for index in range(0,len(templates)):
        if(templates[index] in templates_new):
            pass
        else:
            pos = insertTemplate(templates[index], templates_new)
            if(pos == -1):
                templates_new.append(templates[index])
            else:
                templates_new.insert(pos, templates[index])

    return templates_new



def find_random_log_by_template(df:pd.DataFrame, by_key_val:str, by_key: str,get_key: str, rand_samples:int):
    if pd.isna(by_key_val):
        return None
    vals = list(df.loc[df[by_key] == by_key_val][get_key].sample(rand_samples).values)
    return '\n'.join(vals)

@timeit
def merge_events_templates_old(
    f_drain_events: str, 
    f_drain_templates: str, 
    f_pilar_events: str, 
    f_pilar_templates: str, 
    f_out: str,
    enrich_output: bool = True,
    rand_sample_per_template: int = 1
    ):
    df_drain_events = pd.read_csv(f_drain_events)
    df_pilar_events = pd.read_csv(f_pilar_events)

    df_merged_events = pd.merge(
        df_drain_events, 
        df_pilar_events,
        on='LineId',
        how='left',
        suffixes=('_Drain', '_PILAR')
    )

    df_drain_templates = pd.read_csv(f_drain_templates)
    df_pilar_templates = pd.read_csv(f_pilar_templates)

    df_merged_templates = pd.merge(
        df_drain_templates,
        df_pilar_templates,
        on=['EventTemplate', 'Occurrences'],
        how='outer',
        suffixes=('_Drain', '_PILAR')
    )
    # Move template IDs together
    df_merged_templates = df_merged_templates.iloc[:, [0, -1] + list(range(1, df_merged_templates.shape[1] - 1))]

    
    if enrich_output:
        # If matches
        df_merged_templates['IsMatching'] = df_merged_templates.apply(
            lambda row: (not pd.isna(row['EventId_Drain'])) and not (pd.isna(row['EventId_PILAR'])), axis=1
        )

        random.seed('gundam')
        # Find matching log
        sample_logs = []
        for _, row in df_merged_templates.iterrows():
            temp_logs = []
            for parser in ['Drain', 'PILAR']:
                log_sample_str = find_random_log_by_template(
                    df=df_merged_events,
                    by_key_val=row[f'EventId_{parser}'],
                    by_key=f'EventId_{parser}',
                    get_key='Content',
                    rand_samples=rand_sample_per_template
                )
                temp_logs.append(log_sample_str)
            sample_logs.append(temp_logs)
        
        df_merged_templates = pd.concat(
            [
                df_merged_templates,
                pd.DataFrame(
                    sample_logs, 
                    columns=[f'SampledMatchingLogs_{parser}' for parser in ['Drain', 'PILAR']]
                )
            ],
            axis=1
        )
        df_merged_templates.sort_values(by=['IsMatching', 'EventTemplate'], inplace=True)

    with pd.ExcelWriter(f_out) as writer:
        df_merged_events.to_excel(writer, 'events', index=False)
        df_drain_templates.to_excel(writer, 'templates_Drain', index=False)
        df_pilar_templates.to_excel(writer, 'templates_PILAR', index=False)
        df_merged_templates.to_excel(writer, 'templates_backup', index=False)
        df_merged_templates.to_excel(writer, 'templates_refine', index=False)
    
    print(f'Output written to {f_out}. Please refine the templates now in the "templates_refine" sheet. ')


@timeit
def merge_events_templates(
    f_drain_events: str, 
    f_drain_templates: str, 
    f_pilar_events: str, 
    f_pilar_templates: str, 
    f_out: str,
    enrich_output: bool = True,
    rand_sample_per_template: int = 1,
    skip_if_exist: bool = True
    ):
    
    # Check if exists, if exist, then skip
    if os.path.isfile(f_out) and skip_if_exist:
        print(f'Skip generating meged template file as it already exists: {f_out}')
        return
    
    df_drain_events = pd.read_csv(f_drain_events)
    df_pilar_events = pd.read_csv(f_pilar_events)

    df_merged_events = pd.merge(
        df_drain_events, 
        df_pilar_events,
        on='LineId',
        how='left',
        suffixes=('_Drain', '_PILAR')
    )
    # Use a parser's result as a reference
    df_drain_templates = pd.read_csv(f_drain_templates)
    df_pilar_templates = pd.read_csv(f_pilar_templates)

    # df_merged_templates = pd.merge(
    #     df_drain_templates,
    #     df_pilar_templates,
    #     on=['EventTemplate', 'Occurrences'],
    #     how='outer',
    #     suffixes=('_Drain', '_PILAR')
    # )
    # # Move template IDs together
    # df_merged_templates = df_merged_templates.iloc[:, [0, -1] + list(range(1, df_merged_templates.shape[1] - 1))]

    
    if enrich_output:
        merged_template_rows = []
        random.seed('gundam')
        
        reviewed_template_ids = set()
        reviewed_log_counts = 0
        for template_ids, df_group_same_template_drain in df_merged_events.groupby(['EventId_Drain', 'EventId_PILAR']):
            rows = df_group_same_template_drain.sample(min(rand_sample_per_template, df_group_same_template_drain.shape[0]))
            row = rows.iloc[0].to_dict()
            row['Content'] = '\n'.join(rows['Content'])
            row['LineId'] = '\n'.join([str(x) for x in rows['LineId']])
            merged_template_rows.append(row)
            for id in list(template_ids):
                reviewed_template_ids.add(id)
            reviewed_log_counts += rand_sample_per_template
        df_merged_templates = pd.DataFrame(merged_template_rows)
        df_merged_templates['Occurrences_Drain'] = df_merged_templates['EventId_Drain'].map(lambda template_id: df_drain_templates['Occurrences'].loc[df_drain_templates['EventId'] == template_id].values[0])
        df_merged_templates['Occurrences_PILAR'] = df_merged_templates['EventId_PILAR'].map(lambda template_id: df_pilar_templates['Occurrences'].loc[df_pilar_templates['EventId'] == template_id].values[0])
        df_merged_templates['Refined Template'] = df_merged_templates['Content']

        df_merged_templates = df_merged_templates.reset_index()
        # Columns: LineId	Content	EventId_Drain	EventTemplate_Drain	EventId_PILAR	EventTemplate_PILAR	Occurrences_Drain	Occurrences_PILAR
        df_merged_templates = df_merged_templates[['Refined Template', 'EventId_Drain', 'EventTemplate_Drain', 'Occurrences_Drain', 'EventId_PILAR', 'EventTemplate_PILAR','Occurrences_PILAR', 'Content', 'LineId']]
        
        logger.info(f'Need to review in total {len(list(reviewed_template_ids))} templates produced by all parsers and {reviewed_log_counts} lines of logs')

    with pd.ExcelWriter(f_out) as writer:

        df_merged_events.to_excel(writer, 'events', index=False)
        df_drain_templates.to_excel(writer, 'templates_Drain', index=False)
        df_pilar_templates.to_excel(writer, 'templates_PILAR', index=False)
        #df_merged_templates.to_excel(writer, 'templates_backup', index=False)
        df_merged_templates.to_excel(writer, 'templates_refine', index=False)

        if enrich_output:
            workbook = writer.book
            worksheet = writer.sheets['templates_refine']
            merge_format = workbook.add_format({'valign': 'vcenter', 'text_wrap': True})

            for template_id in df_merged_templates['EventId_Drain'].unique():
                    # find indices and add one to account for header
                    u=df_merged_templates.loc[df_merged_templates['EventId_Drain']==template_id].index.values + 1
                    if len(u) <2: 
                        pass # do not merge cells if there is only one car name
                    else:
                        # merge cells using the first and last indices
                        for merge_column_key in ['EventId_Drain', 'EventTemplate_Drain', 'Occurrences_Drain']:
                            merge_column_idx = df_merged_templates.columns.get_loc(merge_column_key)
                            worksheet.merge_range(u[0], merge_column_idx, u[-1], merge_column_idx, df_merged_templates.loc[u[0], merge_column_key], merge_format)
            worksheet.autofit()

            # Define a format for light gray highlighting
            light_gray_format = workbook.add_format({'bg_color': '#D3D3D3'})  # Light gray background
            # Apply the format to a specific column: Refined Template (col A)
            worksheet.conditional_format('A2:A{}'.format(df_merged_templates.shape[0]+1), {'type': 'no_blanks', 'format': light_gray_format})
            
            # Hide columns: EventId_Drain(col B), 'Occurrences_Drain' (col D), 'EventId_PILAR' (col E), Occurrences_PILAR (col G)
            worksheet.set_column('B:B', None, None, {'hidden': True})
            worksheet.set_column('D:D', None, None, {'hidden': True})
            worksheet.set_column('E:E', None, None, {'hidden': True})
            worksheet.set_column('G:G', None, None, {'hidden': True})
            
            
    print(f'Output written to {f_out}. Please refine the templates now in the "templates_refine" sheet. ')
