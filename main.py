import os
import sys
if not os.path.dirname(__file__) in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))

import yaml
import warnings
import pandas as pd
from log_processing.log_sampler import log_sampler
from parser.parse import DrainParse, PILARParse
from template_processing.template_match_result_generation import TemplateMatching
from template_processing.template_process import refine_templates_from_file, merge_events_templates, build_groundtruth, verify_templates
from utils import timeit, parse_args, getlogger

warnings.filterwarnings('ignore')

def load_yaml(f):
    # Load the configuration file
    with open(f, "r") as file:
        config = yaml.safe_load(file)
    return config

@timeit
def parse(f_log: str, logName: str, parserName:str, iteration:int, output_dir:str):
    """Parse logs with selected parser

    Args:
        f_log (str): _description_
        logName (str): _description_
        parserName (str): _description_
        iteration (int): _description_
    """
    f_config = f'parser/config/{parserName}_config.yaml'
    config = load_yaml(f_config)
    if parserName.lower() == "drain":
        parser = DrainParse(
            logName=logName,
            log_format=config['log_settings'][logName]['log_format'], 
            log_content_path=f_log,
            outdir=os.path.join(output_dir, parserName), 
            depth=config['log_settings'][logName]['depth'],
            st=config['log_settings'][logName]['st'],
            rex=config['log_settings'][logName]['regex'],
            keep_para=False
        )
        
    elif parserName.upper() == "PILAR":
        parser = PILARParse(
            logName=logName,
            log_format=config['log_settings'][logName]['log_format'], 
            log_content_path=f_log,
            outdir=os.path.join(output_dir, parserName), 
            rex=config['log_settings'][logName]['regex'], 
            separator = config['separator'], 
            ratio=config['ratio'], 
            threshold=config['threshold']
        )
    return parser.parse()


def get_log_path(logName: str, iteration: int, output_res_basedir: str='./result') -> str:
    """Get path of log content according to the current iteration

    Args:
        logName (str): name of the log
        iteration (int): Number of current iteration. 
        output_res_basedir (str): directory of log output home folder. Defaults to './result'.
        israwlog (bool, optional): if getting path of raw logs. Defaults to False. 

    Raises:
        FileExistsError: Content file not found

    Returns:
        str: path of log
    """
    if iteration == 1:
        # If first iteration, get raw logs
        log_path = f'logs/{logName}/{logName}_content_cleaned.log'
        if not os.path.isfile(log_path):
            log_path = f'logs/{logName}/{logName}_content.log'
    else:
        # If not first iteration, get unmatched logs from previous iteration
        log_path = os.path.join(*[output_res_basedir, logName, f'iteration_{iteration-1}', 'matching', f'{logName}_content_unmatched.log'])
    
    if not os.path.isfile(log_path):
        raise FileExistsError(f'Content file of log {logName} for interation {iteration} not found at {log_path}')
    
    return log_path

        
         

if __name__ == "__main__":

    args, _ = parse_args()
    logger = getlogger()
    logger.info(f'Running command: {args}')
    logName = args.logname
    output_res_basedir = "./result"

    # Define the id of current iteration
    iteration = args.iteration

    num_logsamples = 20000
    num_logs_per_template_for_review = 1


    output_res_dir = os.path.join(*[output_res_basedir, logName, f'iteration_{iteration}'])

    f_template_merged = os.path.join(output_res_dir, f'{logName}_events_merged.xlsx')

    log_path = get_log_path(logName, iteration)


    f_log_sample = os.path.join(output_res_dir, f'{logName}_content_iter{iteration}.log')

    if args.stage.lower() == 'parse':    
        # Generate Samples 
        log_sampler(log_path=log_path, output_log_path=f_log_sample, num_sample=num_logsamples)

        # Parse log with parsers
        f_drain_events, f_drain_templates = parse(f_log_sample, logName, parserName="Drain", iteration=iteration, output_dir=output_res_dir)
        f_pilar_events, f_pilar_templates = parse(f_log_sample, logName, parserName="PILAR", iteration=iteration, output_dir=output_res_dir)

        # Merge output        
        merge_events_templates(
            f_drain_events=f_drain_events, 
            f_pilar_events=f_pilar_events, 
            f_drain_templates=f_drain_templates,
            f_pilar_templates=f_pilar_templates,
            f_out=f_template_merged,
            enrich_output=True,
            rand_sample_per_template=num_logs_per_template_for_review
        )


    if args.stage.lower() == 'match':
        
        ## Verifies the output for manually labeled templates can match corresponding logs 
        ismatching = verify_templates(
            f_template_table=f_template_merged,
            template_key='Refined Template',
            sheet_name='templates_refine'
        )
        
        if not ismatching:
            logger.error('Terminating matching process as unmatched templates detected during verification.')
            raise RuntimeError('Unmatched log templates found. Please fix them and rerun the matching step command.')
        
        # Get refined templates
        f_refined_template = refine_templates_from_file(
            logName=logName,
            f_template_table=f_template_merged,
            # template_key=['EventTemplate_Drain', 'EventTemplate_PILAR'],
            template_key='Refined Template',
            sheet_name='templates_refine'
        )
        
        # Read templates
        origin_log_path = get_log_path(
            logName=logName, iteration=iteration)
        matcher = TemplateMatching(
            logName=logName,
            logpath=origin_log_path,
            save_dir=os.path.join(output_res_dir, 'matching'),
            f_template_table=f_refined_template,
            template_key='EventTemplate'
        )

        num_unmatched_rows = matcher.match()

        if num_unmatched_rows == 0:
            print('Ready to build groundtruth.')
            f_groundtruth = build_groundtruth(
                outputdir=os.path.join(output_res_basedir, logName),
                current_iteration=iteration,
                logName=logName,
                #template_key=['EventTemplate_Drain', 'EventTemplate_PILAR'],
                template_key='EventTemplate',
            )
            print(f'Finished building groundtruth at: {f_groundtruth}')
        else:
            print(f'{num_unmatched_rows} unmatched logs detected. Please proceed to the "parse" stage of next iteration: {iteration + 1}')
