import pickle
import argparse
import jsonlines
import os
import json
import pronoun_detect_2 as pd2
import urllib.request
from urllib.parse import quote

def get_nlp_parse_result(text):
    '''
    주어진 텍스트에 대해서 ETRI 텍스트 분석 결과를 반환한다. 
    '''
    etri_pos_url = 'http://143.248.135.20:22334/controller/service/etri_parser'
    #etri_pos_url = 'http://143.248.135.20:31235/etri_parser'
    text = quote(text).replace('%20', '+')
    data = "sentence="+text
    try:
        req = urllib.request.Request(etri_pos_url, data=data.encode('utf-8'))
        response = urllib.request.urlopen(req)
        result = response.read().decode('utf-8')
        result = json.loads(result)
    except Exception as e:
        #print (str(e))
        return None
    return result['sentence']

def jsonlines_to_json(file_path, output_path, input_file):
    print(input_file)
    datas = []
    with open(input_file, "r") as file:
        for obj in file:
            datas.append(json.loads(obj))
    
    for data in datas:
        coref_indices = data['predicted_clusters']
        file_name = data['doc_key'].split("/")[-1]
        file_name1 = file_name[:-2]
        file_name = file_path + file_name1
        print(file_name1)
        f = open(file_name, "r", encoding='utf-8')
        json_file = json.load(f)
        f.close()


        pd = pd2.PronounDetector()
        result = pd._set_position_character(get_nlp_parse_result(json_file['ModifiedText'].replace("_", " ")))
        result_morp = []

        sentence_length = 0
        for sentence in result:
            for morp in sentence['morp']:
    #             morp['st'] += sentence_length
    #             morp['en'] += sentence_length
                result_morp.append(morp)
    #         sentence_length = len(sentence['text'])+1
        coref_num = 0
        for coref_index in coref_indices:
            coref_num += 1
            entity_name = ""
            for mention in coref_index:
                st = mention[0]
                en = mention[1]
                st_mention = result_morp[st]['st']
                en_mention = result_morp[en]['en']

                for entities in json_file['entities']:
                    if entities['st_modified'] == st_mention and \
                    entities['en_modified'] == en_mention:
                        entities['predicted_coref_index'] = coref_num

            if entity_name == "":
                st = coref_index[0][0]
                en = coref_index[0][1]
                st_mention = result_morp[st]['st']
                en_mention = result_morp[en]['en']

                for entities in json_file['entities']:
                    if entities['st_modified'] == st_mention and \
                    entities['en_modified'] == en_mention:
                        entity_name = entities['surface']
                        entities['predicted_coref_index'] = coref_num

            for mention in coref_index:
                st = mention[0]
                en = mention[1]
                st_mention = result_morp[st]['st']
                en_mention = result_morp[en]['en']
                for entities in json_file['entities']:
                    if entities['st_modified'] == st_mention and \
                    entities['en_modified'] == en_mention:
                        entities['predicted_coref_index'] = coref_num

                for pronouns in json_file['pronoun_candidate']:
                    if pronouns['st_modified'] == st_mention and \
                    pronouns['en_modified'] == en_mention:
                        pronouns['predicted_coref_index'] = coref_num
                
                for za in json_file['ZA_candidate']:
                    if za['st_modified'] == st_mention and \
                    za['en_modified'] == en_mention:
                        za['predicted_coref_index'] = coref_num

        for pronouns in json_file['pronoun_candidate']:
            if 'predicted_coref_index' in pronouns:
                index = pronouns['predicted_coref_index']
                WIKILINK_dic = {}
                ELU_dic = {}
                NEW_dic = {}

                for entities in json_file['entities']:
                    if 'predicted_coref_index' in entities:
                        if entities['predicted_coref_index'] == index:
                            if entities['eType'] == 'WIKILINK':
                                if entities['entityName'] not in WIKILINK_dic:
                                    WIKILINK_dic[entities['entityName']] = 1
                                else:
                                    WIKILINK_dic[entities['entityName']] += 1
                            elif entities['eType'] == 'ELU':
                                if entities['entityName'] not in ELU_dic:
                                    ELU_dic[entities['entityName']] = 1
                                else:
                                    ELU_dic[entities['entityName']] += 1
                            else:
                                if entities['entityName'] not in NEW_dic:
                                    NEW_dic[entities['surface']] = 1
                                else:
                                    NEW_dic[entities['surface']] += 1

                if len(WIKILINK_dic) == 1:
                    pronouns['entityName'] = list(WIKILINK_dic.keys())[0]
                    pronouns['eType'] = 'WIKILINK'
                elif len(WIKILINK_dic) == 0 and len(ELU_dic) == 1:
                    pronouns['entityName'] = list(ELU_dic.keys())[0]
                    pronouns['eType'] = 'ELU'
                elif len(WIKILINK_dic) == 0 and len(ELU_dic) == 0 and len(NEW_dic) == 1:
                    pronouns['entityName'] = list(NEW_dic.keys())[0]
                    pronouns['eType'] = 'NEW'
        for za in json_file['ZA_candidate']:
            if 'predicted_coref_index' in za:
                index = za['predicted_coref_index']
                WIKILINK_dic = {}
                ELU_dic = {}
                NEW_dic = {}
                
                for entities in json_file['entities']:
                  if 'predicted_coref_index' in entities:
                    if entities['predicted_coref_index'] == index:
                        if entities['eType'] == 'WIKILINK':
                            if entities['entityName'] not in WIKILINK_dic:
                                WIKILINK_dic[entities['entityName']] = 1
                            else:
                                WIKILINK_dic[entities['entityName']] += 1
                        elif entities['eType'] == 'ELU':
                            if entities['entityName'] not in ELU_dic:
                                ELU_dic[entities['entityName']] = 1
                            else:
                                ELU_dic[entities['entityName']] += 1
                        else:
                            if entities['entityName'] not in NEW_dic:
                                NEW_dic[entities['surface']] = 1
                            else:
                                NEW_dic[entities['surface']] += 1
                if len(WIKILINK_dic) == 1:
                   za['entityName'] = list(WIKILINK_dic.keys())[0]
                   za['eType'] = 'WIKILINK'
                elif len(WIKILINK_dic) == 0 and len(ELU_dic) == 1:
                   za['entityName'] = list(ELU_dic.keys())[0]
                   za['eType'] = 'ELU'
                elif len(WIKILINK_dic) == 0 and len(ELU_dic) == 0 and len(NEW_dic) == 1:
                   za['entityName'] = list(NEW_dic.keys())[0]
                   za['eType'] = 'NEW'
                elif len(WIKILINK_dic) == 0 and len(ELU_dic) == 0:
                   coref_index_grouping = []
                   for entities in json_file['entities']:
                       if 'predicted_coref_index' in entities:
                           if entities['eType'] == 'NEW':
                                for keys in NEW_dic:
                                     if keys == entities['surface']:
                                          if entities['predicted_coref_index'] not in coref_index_grouping:
                                               coref_index_grouping.append(entities['predicted_coref_index'])
                   if len(coref_index_grouping) == 1:
                       max_length = 0
                       for keys in NEW_dic:
                           if len(keys) > max_length:
                               za['entityName'] = keys
                               za['eType'] = 'NEW'
                               max_length = len(keys)
                       
        PronounExchangedText = json_file['ModifiedText']
        for za in json_file['ZA_candidate']:
            za['st_exchanged'] = za['st_modified']
            za['en_exchanged'] = za['en_modified']
        for pronouns in json_file['pronoun_candidate']:
            pronouns['st_exchanged'] = pronouns['st_modified']
            pronouns['en_exchanged'] = pronouns['en_modified']
        for entities in json_file['entities']:
            entities['st_exchanged'] = entities['st_modified']
            entities['en_exchanged'] = entities['en_modified']
        
        for za in json_file['ZA_candidate']:
            if PronounExchangedText[za['st_exchanged']:za['en_exchanged']] == za['surface']:
                if 'entityName' in za or 'predicted_coref_index' not in za:
                    if 'entityName' in za:
                       beforeText = PronounExchangedText[:za['st_exchanged']]
                       afterText = PronounExchangedText[za['en_exchanged']:]
                       mark = za['en_exchanged']
                       PronounExchangedText = beforeText + za['entityName'] + afterText
                       pronoun_sum = len(za['entityName']) - len(za['surface'])
                       za['en_exchanged'] = za['st_exchanged'] + len(za['entityName'])
                    elif 'predicted_coref_index' not in za:
                       PronounExchangedText = PronounExchangedText[:za['st_exchanged']] + PronounExchangedText[za['en_exchanged']+1:]
                       pronoun_sum = -2
                       mark = za['en_exchanged']
                       za['isTarget'] = False
                    for entities in json_file['entities']:
                        if entities['st_exchanged'] >= mark:
                            entities['st_exchanged'] += pronoun_sum
                            entities['en_exchanged'] += pronoun_sum
                    for pronouns in json_file['pronoun_candidate']:
                        if pronouns['st_exchanged'] >= mark:
                            pronouns['st_exchanged'] += pronoun_sum
                            pronouns['en_exchanged'] += pronoun_sum
                    for za in json_file['ZA_candidate']:
                        if za['st_exchanged'] >= mark:
                            za['st_exchanged'] += pronoun_sum
                            za['en_exchanged'] += pronoun_sum

        for pronouns in json_file['pronoun_candidate']:    
            if PronounExchangedText[pronouns['st_exchanged']:pronouns['en_exchanged']] == pronouns['text'] and 'entityName' in pronouns:
                beforeText = PronounExchangedText[:pronouns['st_exchanged']]
                afterText = PronounExchangedText[pronouns['en_exchanged']:]
                mark = pronouns['en_exchanged']
                PronounExchangedText = beforeText + pronouns['entityName'] + afterText
                pronoun_sum = len(pronouns['entityName']) - len(pronouns['text'])
                pronouns['en_exchanged'] = pronouns['st_exchanged'] + len(pronouns['entityName'])

                for entities in json_file['entities']:
                    if entities['st_exchanged'] >= mark:
                        entities['st_exchanged'] += pronoun_sum
                        entities['en_exchanged'] += pronoun_sum
                for pronouns in json_file['pronoun_candidate']:
                    if pronouns['st_exchanged'] >= mark:
                        pronouns['st_exchanged'] += pronoun_sum
                        pronouns['en_exchanged'] += pronoun_sum
                for za in json_file['ZA_candidate']:
                    if za['st_exchanged'] >= mark:
                        za['st_exchanged'] += pronoun_sum
                        za['en_exchanged'] += pronoun_sum
        for entities in json_file['entities']:
            if PronounExchangedText[entities['st_exchanged']:entities['en_exchanged']] != entities['surface']:
                PronounExchangedText = PronounExchangedText[:entities['st_exchanged']]+ entities['surface'] + PronounExchangedText[entities['en_exchanged']:]
        json_file['PronounExchangedText'] = PronounExchangedText        
        with open(output_path+file_name1, 'w', encoding='utf-8') as make_file:
            json.dump(json_file, make_file, ensure_ascii=False, indent='\t')
                

if __name__ ==  "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--input_path', type=str, default=None,
                        metavar='input_path',
                        help = 'input_path')
    parser.add_argument('--output_path', type=str, default=None,
                        metavar='output_path',
                        help = 'output_path')
    parser.add_argument('--input_file', type=str, default=None,
                        metavar='input_file',
                        help = 'input_file')
    args = parser.parse_args()
    input_path = args.input_path
    output_path = args.output_path
    input_file = args.input_file
   
    jsonlines_to_json(input_path, output_path, input_file)
    print("[Done jsonlines to json]")
