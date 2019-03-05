import argparse
import csv
import json
import os
import re
import copy

def tta_result(file_path, file_name, input_file_path, output_file_path, output_file_name):
    
    f = open(file_path + file_name, 'r', encoding ='utf-8')
    rdr = csv.reader(f)
    number = 0
    sentence_dir = {}
    for line in rdr:
        temp_line = line[0].replace("<e1>", "")
        temp_line = temp_line.replace("</e1>", "")
        temp_line = temp_line.replace("<e2>", "")
        temp_line = temp_line.replace("</e2>", "")
        temp_line = temp_line.replace("\ufeff", "")
        temp_line = temp_line.replace("[1]", "<1>")
        temp_line = temp_line.replace("[2]", "<2>")
        temp_line = temp_line.replace("[3]", "<3>")
        temp_line = temp_line.replace("[4]", "<4>")
        temp_line = temp_line.replace("[5]", "<5>")
        temp_line = temp_line.replace("[", "")
        temp_line = temp_line.replace("]", "")
        temp_line = temp_line.replace("<1>", "[1]")
        temp_line = temp_line.replace("<2>", "[2]")
        temp_line = temp_line.replace("<3>", "[3]")
        temp_line = temp_line.replace("<4>", "[4]")
        temp_line = temp_line.replace("<5>", "[5]")

        if temp_line not in sentence_dir:
            number += 1
            temp_line2 = line[0].replace("\ufeff", "")
            temp_line2 = temp_line2.replace("[1]", "<1>")
            temp_line2 = temp_line2.replace("[2]", "<2>")
            temp_line2 = temp_line2.replace("[3]", "<3>")
            temp_line2 = temp_line2.replace("[4]", "<4>")
            temp_line2 = temp_line2.replace("[5]", "<5>")
            temp_line2 = temp_line2.replace("[", "")
            temp_line2 = temp_line2.replace("]", "")
            temp_line2 = temp_line2.replace("<1>", "[1]")
            temp_line2 = temp_line2.replace("<2>", "[2]")
            temp_line2 = temp_line2.replace("<3>", "[3]")
            temp_line2 = temp_line2.replace("<4>", "[4]")
            temp_line2 = temp_line2.replace("<5>", "[5]")
            sentence_dir[temp_line] = [(temp_line2, line[1])]
        else:
            temp_line2 = line[0].replace("\ufeff", "")
            temp_line2 = temp_line2.replace("[1]", "<1>")
            temp_line2 = temp_line2.replace("[2]", "<2>")
            temp_line2 = temp_line2.replace("[3]", "<3>")
            temp_line2 = temp_line2.replace("[4]", "<4>")
            temp_line2 = temp_line2.replace("[5]", "<5>")
            temp_line2 = temp_line2.replace("[", "")
            temp_line2 = temp_line2.replace("]", "")
            temp_line2 = temp_line2.replace("<1>", "[1]")
            temp_line2 = temp_line2.replace("<2>", "[2]")
            temp_line2 = temp_line2.replace("<3>", "[3]")
            temp_line2 = temp_line2.replace("<4>", "[4]")
            temp_line2 = temp_line2.replace("<5>", "[5]")
            sentence_dir[temp_line].append((temp_line2, line[1]))
    f.close()
    
    data_list = os.listdir(input_file_path)
    total_json_file = []
    for data in data_list:
        if data[0] == ".":
            continue
        f = open(input_file_path+data, "r", encoding='utf-8')
        json_file = json.load(f)
        total_json_file.append(json_file)
        f.close()
    
    result_text = []
    relation = []
    for key in sentence_dir:
        for json_file in total_json_file:
            if json_file['plainText'][:-1] == key:
                for text in sentence_dir[key]:
                    list_entities = copy.deepcopy(json_file['entities'])
                    list_ZAs = copy.deepcopy(json_file['ZA_candidate'])
                    list_pronouns = copy.deepcopy(json_file['pronoun_candidate'])
                    st_e1 = text[0].find("<e1>")
                    en_e1 = text[0].find("</e1>")
                    st_e2 = text[0].find("<e2>")
                    en_e2 = text[0].find("</e2>")
                    if st_e1 > st_e2:
                        st_e1 -= 9
                        en_e1 -= 13
                        en_e2 -= 4
                    else:
                        st_e2 -= 9
                        en_e2 -= 13
                        en_e1 -= 4
                    for entities in list_entities:
                        if entities['st'] == st_e1 and entities['en'] == en_e1:
                            e1 = entities
                        if entities['st'] == st_e2 and entities['en'] == en_e2:
                            e2 = entities
                    temp_text = json_file['PronounExchangedText']
                    temp_text = temp_text[:e1['st_exchanged']] + "<e1>" + \
                      temp_text[e1['st_exchanged']:e1['en_exchanged']] + "</e1>" + \
                      temp_text[e1['en_exchanged']:]
                    st_index = e1['st_exchanged']
                    for entities in list_entities:
                        if entities == e1:
                            e1['st_exchanged'] += 4
                            e1['en_exchanged'] += 4
                            entities['st_exchanged'] += 4
                            entities['en_exchanged'] += 4
                        else:
                            if entities['st_exchanged'] > st_index:
                                entities['st_exchanged'] += 9
                                entities['en_exchanged'] += 9
                    for pronouns in list_pronouns:
                        if pronouns['st_exchanged'] > st_index:
                            pronouns['st_exchanged'] += 9
                            pronouns['en_exchanged'] += 9
                    for ZAs in list_ZAs:
                        if ZAs['st_exchanged'] > st_index:
                            ZAs['st_exchanged'] += 9
                            ZAs['en_exchanged'] += 9

                    temp_text = temp_text[:e2['st_exchanged']] + "<e2>" + \
                      temp_text[e2['st_exchanged']:e2['en_exchanged']] + "</e2>" + \
                      temp_text[e2['en_exchanged']:]
                    st_index = e2['st_exchanged']
                    for entities in list_entities:
                        if entities == e2:
                            e2['st_exchanged'] += 4
                            e2['en_exchanged'] += 4
                            entities['st_exchanged'] += 4
                            entities['en_exchanged'] += 4
                        else:
                            if entities['st_exchanged'] > st_index:
                                entities['st_exchanged'] += 9
                                entities['en_exchanged'] += 9
                    for pronouns in list_pronouns:
                        if pronouns['st_exchanged'] > st_index:
                            pronouns['st_exchanged'] += 9
                            pronouns['en_exchanged'] += 9
                    for ZAs in list_ZAs:
                        if ZAs['st_exchanged'] > st_index:
                            ZAs['st_exchanged'] += 9
                            ZAs['en_exchanged'] += 9

                    if 'predicted_coref_index' in e1:
                        for entities in list_pronouns:
                            if 'predicted_coref_index' in entities:
                                if e1['predicted_coref_index'] == entities['predicted_coref_index']:
                                    temp_text = temp_text[:entities['st_exchanged']] + "<e1>" + \
                                      temp_text[entities['st_exchanged']:entities['en_exchanged']] + "</e1>" + \
                                      temp_text[entities['en_exchanged']:]
                                    st_index = entities['st_exchanged']

                                    for entities2 in list_entities:
                                        if entities2 == entities:
                                            entities2['st_exchanged'] += 4
                                            entities2['en_exchanged'] += 4
                                        else:
                                            if entities2['st_exchanged'] > st_index:
                                                entities2['st_exchanged'] += 9
                                                entities2['en_exchanged'] += 9
                                                if entities2 == e2:
                                                    e2['st_exchanged'] += 9
                                                    e2['en_exchanged'] += 9 
                                    for pronouns in list_pronouns:
                                        if pronouns['st_exchanged'] > st_index:
                                            pronouns['st_exchanged'] += 9
                                            pronouns['en_exchanged'] += 9
                                    for ZAs in list_ZAs:
                                        if ZAs['st_exchanged'] > st_index:
                                            ZAs['st_exchanged'] += 9
                                            ZAs['en_exchanged'] += 9


                        for entities in list_ZAs:
                            if 'predicted_coref_index' in entities:
                                if e1['predicted_coref_index'] == entities['predicted_coref_index']:
                                    temp_text = temp_text[:entities['st_exchanged']] + "<e1>" + \
                                      temp_text[entities['st_exchanged']:entities['en_exchanged']] + "</e1>" + \
                                      temp_text[entities['en_exchanged']:]
                                    st_index = entities['st_exchanged']

                                    for entities2 in list_entities:
                                        if entities2 == entities:
                                            entities2['st_exchanged'] += 4
                                            entities2['en_exchanged'] += 4
                                        else:
                                            if entities2['st_exchanged'] > st_index:
                                                entities2['st_exchanged'] += 9
                                                entities2['en_exchanged'] += 9
                                                if entities2 == e2:
                                                    e2['st_exchanged'] += 9
                                                    e2['en_exchanged'] += 9 
                                    for pronouns in list_pronouns:
                                        if pronouns['st_exchanged'] > st_index:
                                            pronouns['st_exchanged'] += 9
                                            pronouns['en_exchanged'] += 9
                                    for ZAs in list_ZAs:
                                        if ZAs['st_exchanged'] > st_index:
                                            ZAs['st_exchanged'] += 9
                                            ZAs['en_exchanged'] += 9

                    if 'predicted_coref_index' in e2:
                        for entities in list_pronouns:
                            if 'predicted_coref_index' in entities:
                                if e2['predicted_coref_index'] == entities['predicted_coref_index']:
                                    temp_text = temp_text[:entities['st_exchanged']] + "<e2>" + \
                                      temp_text[entities['st_exchanged']:entities['en_exchanged']] + "</e2>" + \
                                      temp_text[entities['en_exchanged']:]
                                    st_index = entities['st_exchanged']

                                    for entities2 in list_entities:
                                        if entities2 == entities:
                                            entities2['st_exchanged'] += 4
                                            entities2['en_exchanged'] += 4
                                        else:
                                            if entities2['st_exchanged'] > st_index:
                                                entities2['st_exchanged'] += 9
                                                entities2['en_exchanged'] += 9
                                    for pronouns in list_pronouns:
                                        if pronouns['st_exchanged'] > st_index:
                                            pronouns['st_exchanged'] += 9
                                            pronouns['en_exchanged'] += 9
                                    for ZAs in list_ZAs:
                                        if ZAs['st_exchanged'] > st_index:
                                            ZAs['st_exchanged'] += 9
                                            ZAs['en_exchanged'] += 9


                        for entities in list_ZAs:
                            if 'predicted_coref_index' in entities:
                                if e2['predicted_coref_index'] == entities['predicted_coref_index']:
                                    temp_text = temp_text[:entities['st_exchanged']] + "<e2>" + \
                                      temp_text[entities['st_exchanged']:entities['en_exchanged']] + "</e2>" + \
                                      temp_text[entities['en_exchanged']:]
                                    st_index = entities['st_exchanged']

                                    for entities2 in list_entities:
                                        if entities2 == entities:
                                            entities2['st_exchanged'] += 4
                                            entities2['en_exchanged'] += 4
                                        else:
                                            if entities2['st_exchanged'] > st_index:
                                                entities2['st_exchanged'] += 9
                                                entities2['en_exchanged'] += 9
                                    for pronouns in list_pronouns:
                                        if pronouns['st_exchanged'] > st_index:
                                            pronouns['st_exchanged'] += 9
                                            pronouns['en_exchanged'] += 9
                                    for ZAs in list_ZAs:
                                        if ZAs['st_exchanged'] > st_index:
                                            ZAs['st_exchanged'] += 9
                                            ZAs['en_exchanged'] += 9                                 
                    result_text.append(temp_text)
                    relation.append(text[1])

    count = 0
    f = open(output_file_path + output_file_name, "w", encoding='utf-8', newline='')
    for i in range(0, len(result_text)):
        count += 1
        wr = csv.writer(f)
        wr.writerow([result_text[i], relation[i]])
    f.close()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--file_path', type=str, default=None,
                        metavar='file_path',
                        help = 'file_path')
    parser.add_argument('--file_name', type=str, default=None,
                        metavar='file_name',
                       help = 'file_name')
    parser.add_argument('--input_path', type=str, default=None,
                        metavar='input_path',
                        help='input_path')
    parser.add_argument('--output_file_path', type=str, default=None,
                        metavar='output_file_path',
                        help='output_file_path')
    parser.add_argument('--output_file_name', type=str, default=None,
                        metavar='output_file_name',
                        help = 'output_file_name')

    args = parser.parse_args()
    file_path = args.file_path
    file_name = args.file_name
    input_path = args.input_path
    output_file_path = args.output_file_path
    output_file_name = args.output_file_name
    tta_result(file_path, file_name, input_path, output_file_path, output_file_name)
    print("[Done converting the model output format to csv format]")