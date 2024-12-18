import pandas as pd
import os
import re
import pathlib


def cha_txt_to_dataframe(file_name):
    """
    Returns a dataframe that converts single .cha (.txt) file to a dataframe.
    :param file_name: .txt file containing (cha formatted).
    :return: pandas dataframe
    """
    f = open(file_name, "r", encoding="utf-8")
    lines = f.readlines()

    scenarios = []
    current_scenario = "N/A"

    line_type = ["*INV", "*PAR", "%wor", "%mor", "%gra", "%exp", "*IN1", "*IN2"]
    current_line_type = "N/A"

    line_number = []
    text = []

    i = 0
    for line in lines:
        if line[:3] == "@G:":  # Adding scenario information
            line = re.sub("\n", "", line)
            line = re.sub("\t", " ", line)
            current_scenario = line[3:].strip()
        scenarios.append(current_scenario)

        if line[:4] in line_type:
            if line[:4] != current_line_type:
                current_line_type = line[:4]
                i += 1
        line_number.append(i)

        line = re.sub("\n", "", line)
        line = re.sub("\t", " ", line)
        text.append(line)

    columns = ['line_number', 'scenario', 'text', 'line_information', 'utterance_count']
    df = pd.DataFrame(columns=columns)
    df['line_number'], df['scenario'], df['text'] = line_number, scenarios, text
    df = df.groupby(['line_number', 'scenario'])['text'].apply(' '.join).reset_index()
    df['line_information'] = df['text'].astype(str).str[:4]
    df['text'] = df['text'].str[6:]
    df = df.loc[df['line_information'] != "@Beg"]
    df = df.loc[df['line_information'] != "@G: "]
    df = df.loc[df['line_information'] != "@UTF"]

    utterance_number = []
    utterance_count = 0

    for info in df['line_information']:
        participants = ["*INV", "*PAR", "*IN1", "*IN2"]
        if info in participants:
            utterance_count += 1

        utterance_number.append(utterance_count)

    df['utterance_count'] = utterance_number

    return df


def cha_txt_files_to_csv(data_dir, file_name, fnames=None):
    """
    Uses a directory containing .cha based .txt files to convert to .csv file.
    :param data_dir: Directory in which .txt files are located.
    :param file_name: .CSV file save data in.
    :param fnames: EDITED file names which we are interested in
    :return: Returns true if completed.
    """
    columns = ['line_number', 'scenario', 'text', 'line_information', 'utterance_count', 'source_file']
    df = pd.DataFrame(columns=columns)
    count = 0

    for subdir, dirs, files in os.walk(data_dir):
        for file in files:
            if fnames is not None:
                fnames = [pathlib.Path("../" + str(path)) for path in fnames]
                print(fnames)
            if fnames is None:  # EDITED if we are interested in all files
                if str(subdir + '\\' + file).endswith(".cha"):
                    file_df = cha_txt_to_dataframe(subdir + '\\' + file)
                    file_df['source_file'] = file
                    df = pd.concat([df, file_df], ignore_index=True)

            elif pathlib.Path(subdir + "\\" + file) in fnames:  # EDITED to add files only we are interested in
                if str(data_dir + file).endswith(".cha"):
                    file_df = cha_txt_to_dataframe(subdir + "\\" + file)
                    file_df['source_file'] = file
                    df = pd.concat([df, file_df], ignore_index=True)
                    # break

    if not df.empty:
        print("Saved: " + str(file_name) + " at " + str(pathlib.Path().resolve()))
        df.to_csv(file_name, index=False, encoding="utf-8")
    else:
        print("Empty df")
    return True


def main():
    aphasia_type = ['wernicke', 'conduction', 'anomic', 'not aphasic']
    fnames = pd.read_csv('../../ab_data/filepaths.csv')
    for x in aphasia_type:
        data_dir = "../../ab_data/all_cha/"
        paths = fnames[fnames["WAB Type"] == x]["path"].to_list()
        filename = "../../ab_data/processed_data/rawdata_" + x + ".csv"
        print(x)
        cha_txt_files_to_csv(data_dir, filename, paths)
        print()

    fp = "../../ab_data/data_control/"
    filename = "../../ab_data/processed_data/rawdata_control.csv"
    cha_txt_files_to_csv(fp, filename, None)


main()
