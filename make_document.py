import re
import os
import json
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, default=None,
                        metavar='input_path',
                        help = 'input_path')
    parser.add_argument('--output_path', type=str, default=None,
                        metavar='output_path',
                        help = 'output_path')
    parser.add_argument('--max_document_size', type=int, default=None,
                        metavar='max_document_size',
                        help = 'max_document_size')  
    args = parser.parse_args()
    gold_set_dir = args.input_path
    modified_dir = args.output_path
    max_document_size = args.max_document_size
    
    data_list = os.listdir(gold_set_dir)
    
    doc_ID = []
    for data in data_list:
        ID = data.split("_")[0]
        if ID not in doc_ID:
            doc_ID.append(ID)
    exception = []
    for doc in doc_ID:
        modified_json = {}
        modified_json['plainText'] = ""
        modified_json['docID'] = str(doc)
        modified_json['parID'] = "1"
        modified_json['globalSID'] = ""
        modified_json['pronouns'] = []
        modified_json['entities'] = []
        json_file = []
        name_list = []
        total_file_size = 0
        for i in range(1, 20):
            file_name = gold_set_dir + doc + "_" + str(i) + ".json"
            if os.path.exists(file_name):
                name_list.append(i)
                g = open(file_name, "r", encoding="utf-8")
                json_ = json.load(g)
                g.close()
                json_file.append(json_)
                total_file_size += os.path.getsize(file_name)

        if total_file_size > max_document_size:
            exception.append(doc)
            point = total_file_size / 2
            temp_file_size = 0
            middle_point = 0
            for i in name_list:
                file_name = gold_set_dir + doc + "_" + str(i) + ".json"
                if os.path.exists(file_name):
                    temp_file_size += os.path.getsize(file_name)
                    middle_point += 1
                if temp_file_size > point:
                    middle_point -= 1
                    middle_file_name = i 
                    break

        if doc in exception:
            sentence_length = 0
            entity_ID = 0
            pronoun_ID = 0
            entity_ID_list = [0] * 15
            pronoun_ID_list = [0] * 15
            for json_ in json_file[:middle_point]:
                json_parID = int(json_['parID'])
                modified_json['globalSID'] += json_['globalSID'] + ","
                modified_json['plainText'] += json_['plainText'] + " "

                for entity in json_['entities']:
                    entity['id'] = entity_ID
                    entity_ID += 1
                    entity['st'] += sentence_length
                    entity['en'] += sentence_length
                    if entity['surface'][0] == "_":
                        entity['surface'] = entity['surface'][1:]
                        entity['st'] += 1
                    if entity['surface'][-1] == "_":
                        entity['surface'] = entity['surface'][:-1]
                        entity['en'] -= 1
                    if entity['ancestor'] != '':
                        if entity['ancestor'].startswith("-") == False :
                            parID = int(entity['ancestor'].split("-")[0])
                            index = 0
                            for i in range(0, parID):
                                index += entity_ID_list[i]
                            entity_ID_ = int(entity['ancestor'].split("-")[1])
                            entity['ancestor'] = "1-" + str(index+entity_ID_)
                    modified_json['entities'].append(entity)


                for pronoun in json_['pronouns']:
                    pronoun['id'] = pronoun_ID
                    pronoun_ID += 1
                    pronoun['st'] += sentence_length
                    pronoun['en'] += sentence_length
                    if pronoun['ancestor'] != '':
                        if pronoun['ancestor'].startswith("-") == False :
                            parID = int(pronoun['ancestor'].split("-")[0])
                            index = 0
                            for i in range(0, parID):
                                index += entity_ID_list[i]
                            pronoun_ID_ = int(pronoun['ancestor'].split("-")[1])
                            pronoun['ancestor'] = "1-" + str(index+pronoun_ID_)
                    modified_json['pronouns'].append(pronoun)

                pronoun_ID_list[json_parID]= len(json_['pronouns'])
                entity_ID_list[json_parID] =len(json_['entities'])

                sentence_length += len(json_['plainText']) + 1
            modified_json['globalSID'] = modified_json['globalSID'][:-1]    
            with open(modified_dir+str(doc)+"_1"+".json", 'w', encoding='utf-8') as make_file:
                json.dump(modified_json, make_file, ensure_ascii=False, indent='\t')



            modified_json = {}
            modified_json['plainText'] = ""
            modified_json['docID'] = str(doc)
            modified_json['parID'] = "2"
            modified_json['globalSID'] = ""
            modified_json['pronouns'] = []
            modified_json['entities'] = []       
            sentence_length = 0
            entity_ID = 0
            pronoun_ID = 0
            for json_ in json_file[middle_point:]:
                json_parID = int(json_['parID'])
                modified_json['globalSID'] += json_['globalSID'] + ","
                modified_json['plainText'] += json_['plainText'] + " "

                for entity in json_['entities']:
                    entity['id'] = entity_ID
                    entity_ID += 1
                    entity['st'] += sentence_length
                    entity['en'] += sentence_length
                    if entity['surface'][0] == "_":
                        entity['surface'] = entity['surface'][1:]
                        entity['st'] += 1
                    if entity['surface'][-1] == "_":
                        entity['surface'] = entity['surface'][:-1]
                        entity['en'] -= 1
                    if entity['ancestor'] != '':
                        if entity['ancestor'].startswith("-") == False :
                            parID = int(entity['ancestor'].split("-")[0])
                            index = 0
                            if parID < middle_file_name:
                                for i in range(0, parID):
                                    index += entity_ID_list[i]
                                entity_ID_ = int(entity['ancestor'].split("-")[1])
                                entity['ancestor'] = "1-" + str(index+entity_ID_)
                            else:
                                for i in range(middle_file_name, parID):
                                    index += entity_ID_list[i]
                                entity_ID_ = int(entity['ancestor'].split("-")[1])
                                entity['ancestor'] = "2-" + str(index+entity_ID_)

                    modified_json['entities'].append(entity)


                for pronoun in json_['pronouns']:
                    pronoun['id'] = pronoun_ID
                    pronoun_ID += 1
                    pronoun['st'] += sentence_length
                    pronoun['en'] += sentence_length
                    if pronoun['ancestor'] != '':
                        if pronoun['ancestor'].startswith("-") == False :
                            parID = int(pronoun['ancestor'].split("-")[0])
                            index = 0
                            if parID < middle_file_name:
                                for i in range(0, parID):
                                    index += entity_ID_list[i]
                                pronoun_ID_ = int(pronoun['ancestor'].split("-")[1])
                                pronoun['ancestor'] = "1-" + str(index+pronoun_ID_)
                            else:
                                for i in range(middle_file_name, parID):
                                    index += entity_ID_list[i]
                                pronoun_ID_ = int(pronoun['ancestor'].split("-")[1])
                                pronoun['ancestor'] = "2-" + str(index+pronoun_ID_)
                    modified_json['pronouns'].append(pronoun)

                pronoun_ID_list[json_parID]= len(json_['pronouns'])
                entity_ID_list[json_parID] =len(json_['entities'])

                sentence_length += len(json_['plainText']) + 1
            modified_json['globalSID'] = modified_json['globalSID'][:-1]    
            with open(modified_dir+str(doc)+"_2"+".json", 'w', encoding='utf-8') as make_file:
                json.dump(modified_json, make_file, ensure_ascii=False, indent='\t')


        else:

            sentence_length = 0
            entity_ID = 0
            pronoun_ID = 0
            entity_ID_list = [0] * 15
            pronoun_ID_list = [0] * 15
            for json_ in json_file:
                json_parID = int(json_['parID'])
                modified_json['globalSID'] += json_['globalSID'] + ","
                modified_json['plainText'] += json_['plainText'] + " "

                for entity in json_['entities']:
                    entity['id'] = entity_ID
                    entity_ID += 1
                    entity['st'] += sentence_length
                    entity['en'] += sentence_length
                    if entity['surface'][0] == "_":
                        entity['surface'] = entity['surface'][1:]
                        entity['st'] += 1
                    if entity['surface'][-1] == "_":
                        entity['surface'] = entity['surface'][:-1]
                        entity['en'] -= 1
                    if entity['ancestor'] != '':
                        if entity['ancestor'].startswith("-") == False :
                            parID = int(entity['ancestor'].split("-")[0])
                            index = 0
                            for i in range(0, parID):
                                index += entity_ID_list[i]
                            entity_ID_ = int(entity['ancestor'].split("-")[1])
                            entity['ancestor'] = "1-" + str(index+entity_ID_)
                    modified_json['entities'].append(entity)


                for pronoun in json_['pronouns']:
                    pronoun['id'] = pronoun_ID
                    pronoun_ID += 1
                    pronoun['st'] += sentence_length
                    pronoun['en'] += sentence_length
                    if pronoun['ancestor'] != '':
                        if pronoun['ancestor'].startswith("-") == False :
                            parID = int(pronoun['ancestor'].split("-")[0])
                            index = 0
                            for i in range(0, parID):
                                index += entity_ID_list[i]
                            pronoun_ID_ = int(pronoun['ancestor'].split("-")[1])
                            pronoun['ancestor'] = "1-" + str(index+pronoun_ID_)
                    modified_json['pronouns'].append(pronoun)

                pronoun_ID_list[json_parID]= len(json_['pronouns'])
                entity_ID_list[json_parID] =len(json_['entities'])
                sentence_length += len(json_['plainText']) + 1
            modified_json['globalSID'] = modified_json['globalSID'][:-1]    
            with open(modified_dir+str(doc)+".json", 'w', encoding='utf-8') as make_file:
                json.dump(modified_json, make_file, ensure_ascii=False, indent='\t')


if __name__ == "__main__":
    main()
    print("[Done make_document]")
