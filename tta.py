import csv
import json
import argparse


def tta(file_path, file_name, entity_type_file_path, entity_type_file_name, output_file_path):

    f = open(file_path + file_name, "r", encoding='utf-8-sig')
    rdr = csv.reader(f)
    number = 0
    sentence = []
    
    for line in rdr:
        temp_line = line[0].replace("<e1>", "[")
        temp_line = temp_line.replace("</e1>", "]")
        temp_line = temp_line.replace("<e2>", "[")
        temp_line = temp_line.replace("</e2>", "]")
        temp_line = temp_line.replace("[1]", "<1>")
        temp_line = temp_line.replace("[2]", "<2>")
        temp_line = temp_line.replace("[3]", "<3>")
        temp_line = temp_line.replace("[4]", "<4>")
        temp_line = temp_line.replace("[5]", "<5>")
        temp_line = temp_line.replace("\ufeff", "")

        if temp_line not in sentence:
            sentence.append(temp_line)
            number += 1
    f.close()
    
    f = open(entity_type_file_path + entity_type_file_name, "r", encoding='utf-8')
    lines = f.readlines()
    f.close()
    type_dic = {}
    for line in lines:
        e1 = line.split("\t")[0]
        e2 = line.split("\t")[1]
        if e2 == "Person\n" or e2 == "Event\n" or e2 == "Place\n" or e2 == "TimePeriod\n" or e2 == "Organisation\n":
            type_dic[e1] = e2
    json_file = []
    
    
    doc_number = 0
    for sen in sentence:
        doc_number += 1
        globalSID = doc_number
        parID = 1
        pronouns = []
        en_text = sen
        entities = []

        minus_index = 0
        temp_entity_name = ""
        st_index = 0
        en_index = 0
        idx = 0
        for i in range(0, len(sen)):
            if sen[i] == '[':
                minus_index += 1
                st_index = i
            elif sen[i] ==  ']':
                minus_index += 1
                en_index = i
                temp_entity_name = sen[st_index+1:en_index]
                st_index = st_index - minus_index + 2
                en_index = en_index - minus_index + 1
                temp_dic = {}
                temp_dic['kbox_types'] = []
                temp_dic['st'] = st_index
                temp_dic['eType'] = 'WIKILINK'
                temp_dic['is_target'] = True
                temp_dic['id'] = idx
                idx += 1
                if temp_entity_name not in type_dic:
                    temp_dic['ne_type'] = "ETC"
                else:
                    if type_dic[temp_entity_name] == "Person\n":
                        temp_dic['ne_type'] = "PERSON"
                    elif type_dic[temp_entity_name] == "Event\n":
                        temp_dic['ne_type'] = "EVENT"
                    elif type_dic[temp_entity_name] == "Place\n":
                        temp_dic['ne_type'] = "LOCATION"
                    elif type_dic[temp_entity_name] == "TimePeriod\n":
                        temp_dic['ne_type'] = "TIME"
                    elif type_dic[temp_entity_name] == "Organisation\n":
                        temp_dic['ne_type'] = "ORGANIZATION"


                temp_dic['en'] = en_index
                temp_dic['ancestor'] = ''
                temp_dic['surface'] = temp_entity_name
                temp_dic['entityName'] = temp_entity_name
                entities.append(temp_dic)
        big_dic = {}
        big_dic['docID'] = str(doc_number)
        big_dic['globalSID'] = str(globalSID)
        big_dic['pronouns'] = pronouns
        big_dic['parID'] = "1"
        big_dic['entities'] = entities
        sen = sen.replace("[", "")
        sen = sen.replace("]", "")
        sen = sen.replace("<1>", "[1]")
        sen = sen.replace("<2>", "[2]")
        sen = sen.replace("<3>", "[3]")
        sen = sen.replace("<4>", "[4]")
        sen = sen.replace("<5>", "[5]")
        big_dic['plainText'] = sen
        json_file.append(big_dic)
        
    for file in json_file:
        docID = file['docID']
        parID = file['parID']
        f = open(output_file_path+docID+"_"+parID+".json", "w", encoding='utf-8')
        json.dump(file, f, ensure_ascii=False, indent='\t')
        f.close()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--file_path', type=str, default=None,
                        metavar='file_path',
                        help = 'file_path')
    parser.add_argument('--file_name', type=str, default=None,
                        metavar='file_name',
                       help = 'file_name')
    parser.add_argument('--entity_type_file_path', type=str, default=None,
                        metavar='entity_type_file_path',
                        help='entity_type_file_path')
    parser.add_argument('--entity_type_file_name', type=str, default=None,
                        metavar='entity_type_file_name',
                        help='entity_type_file_name')
    parser.add_argument('--output_file_path', type=str, default=None,
                        metavar='output_file_path',
                        help = 'output_file_path')
    args = parser.parse_args()
    file_path = args.file_path
    file_name = args.file_name
    entity_type_file_path = args.entity_type_file_path
    entity_type_file_name = args.entity_type_file_name
    output_file_path = args.output_file_path
    tta(file_path, file_name, entity_type_file_path, entity_type_file_name, output_file_path)
    print("[Done converting tta data to input format]")