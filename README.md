# README

# Introduction

Log parsing is an essential step towards automated log analysis for software system performance assurance, failure debugging, anomaly detection. The accuracy of parsing results are critical to the success of log analysis procedures that are built upon it. 

In this repo, we propose a pipeline that generates log templates for generating templates for any log data.

# Dataset
We provide both raw log and labeled log data of our baseline benchmark in a Zenodo dataset. 
Please find the complete dataset from this [link](https://zenodo.org/records/13756047).


# Steps

## 1. Repo setup

First, clone the repo and install required dependencies using the following commands.

```bash
pip install -r requirements.txt
```

## 2. Download logs

Follow the instructions [here](logs/README.md) to download logs. We provide three logs at different sizes for testing purposes. 

- Apache (small size)
- BGL (medium size)
- Spark (large size)

You may also use your own specific logs and update the configuration.

## 3. Extract content

This step can be skipped as the extracted log content files have been provided in the downloaded logs.

## 4. Sample and parse logs

We will use two state-of-the-art log parsing tools to process the same log sample. The log sample contains randomly picked log lines throughout the entire log content, the default sample size is 20,000.

In this step, you will need to execute the following command:

```bash
python main.py -l <LogName> -s parse -i 1
```

The output of this step will be provided in the console log, as shown as follows:

```
Output written to ./result/Apache/iteration_1/Apache_events_merged.xlsx. Please refine the templates now in the "templates_refine" sheet.
```

Now you will need to open this file and review the templates manually.

## 5. Templates review

Open the Excel spreadsheet and navigate to **templates_refine** sheet.

You will need to manaully identify the dynamic information in the **Refined Template** column (highlighted in gray) and replace dynamic information with this symbol: `<*>`

During the labeling process, you may use the templates generated from Drain and PILAR as references. But do not use these templates directly, as their information might not be complete (e.g., puctuation missing).

When it’s done, remember to **SAVE your changes**.


## 6. Match logs with refined templates

Next, run the following script to match logs with refined templates.

```
python main.py -l <LogName> -s match -i 1
```


This script will first verify whether the manual curated templates can successfully match the corresponding logs. 
If the verification fails, you need to fix the templates as printed in the console log and rerun the above-listed command.


Next, follow the instructions in the console log.

## 7. Build Ground-truth

- If all logs are matched with refined template: the pipeline will generate the ground-truth templates directly at default location: `./result/<LOGNAME>/<LOGNAME>_templates_groundtruth.csv`
- If not all logs are matched:
    - Follow the instruction in Step 6
    - Increase iteration number by one (`iteration+=1`)
    - Repeat Step 4 to 6 until all logs are matched by refined templates
    - The ground-truth templates will be generated at the above-mentioned location

# Miscancelleous

## Accepted Args of the pipeline

Specifically, three argument keys are accepted here:

- `-l`/`—-logname`: The name of the input log (e.g., Apache, BGL, Spark)
- `-s`/`—-stage`: The current stage of the pipeline. This pipeline accepts three stages:
    - `extract`: extract content from logs (skipped)
    - `parse`: sample and parse log contents
    - `match`: refine generated log templates and use them to match log files
- `-i`/`—-iteration`: The number of current iteration. The iteration number starts with 1 and increase by 1 in every time the pipeline is re-executed.

## Record elapsed time of the pipeline

The elapsed time of the steps in the pipeline is logged at: `./runtime.log`
