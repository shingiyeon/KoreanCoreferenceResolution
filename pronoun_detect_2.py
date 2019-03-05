import util2 as util

class PronounDetector:
    def __init__(self):
        self.jisi_determiner_list = []
        self.pronoun_lemma_list = []
        f = open('jisi_determiner_list.txt','r',encoding='utf-8')
        for line in f:
            self.jisi_determiner_list.append(line.strip())
        f.close()

        f = open('pronoun_lemma_list.txt','r', encoding='utf-8')
        for line in f:
            self.pronoun_lemma_list.append(line.strip())
        f.close()
        pass

    def _set_position_character(self,nlp_result):
        '''
        모든 character는 길이 1로 해서 설정
        '''
        new_nlp_result = []
        last_character = 0
        last_position = 0
        char_count = 0
        curr_position = 0
        for sent in nlp_result:
            new_sent = sent
            text = sent['text']
            now_morp_idx = 0
            for char in text:
                while now_morp_idx < len(new_sent['morp']) and new_sent['morp'][now_morp_idx]['position'] <= curr_position:
                    if (new_sent['morp'][now_morp_idx]['position'] == curr_position):
                        new_sent['morp'][now_morp_idx]['st'] = char_count
                        new_sent['morp'][now_morp_idx]['en'] = char_count + len(new_sent['morp'][now_morp_idx]['lemma'])
                    now_morp_idx += 1
                curr_position += util.get_text_length_in_byte(char)
                char_count += 1
            '''
            for morp in new_sent['morp']:
                morp['st'] = last_character
                if (last_position < morp['position']):
                    morp['st'] = last_character + (morp['position']-last_position)
                elif (last_position > morp['position']):
                    morp['st'] = last_character - int((last_position-morp['position'])/3)
                else:
                    morp['st'] = last_character

                morp['en'] = morp['st'] + len(morp['lemma'])
                last_character = morp['en']
                last_position = morp['position'] + util.get_text_length_in_byte(morp['lemma'])
            '''

            new_nlp_result.append(new_sent)

        return new_nlp_result

    def _extract_pronoun_simple(self,nlp_result):
        pronoun_list = []
        for sent in nlp_result:
            open = False
            current_item = []
            for morp in sent['morp']:
                if not open:
                    if (morp['type'] == 'MM' and morp['lemma'] in self.jisi_determiner_list):
                        current_item = []
                        current_item.append(morp)
                        open = True
                    elif (morp['type'] == 'NP'):
                        pronoun_list.append({'st': morp['st'], 'en': morp['en'], 'text': morp['lemma']})

                else:
                    if (morp['type'].startswith('VC') or morp['type'].startswith('J')):
                        open = False
                        st = current_item[0]['st']
                        en = current_item[-1]['en']
                        str_st = st - sent['morp'][0]['st']
                        str_en = en - sent['morp'][0]['st']
                        text = sent['text'].strip()[str_st:str_en]
                        pronoun_list.append({'st':st,'en':en,'text':text})
                    else:
                        current_item.append(morp)


            if (open):
                st = current_item[0]['st']
                en = current_item[0]['en']
                str_st = current_item[0]['st'] - sent['morp'][0]['st']
                str_en = current_item[-1]['en'] - sent['morp'][0]['st']
                text = sent['text'][str_st:str_en]
                pronoun_list.append({'st': st, 'en': en, 'text': text})

        return pronoun_list

    def _is_candidate_eojeol(self, dep,  morps):
        if (dep['label'].startswith('NP') or dep['label'].startswith('VNP')):
            return True

    def _extract_metnion(self, nlp_result):
        mention_list = []
        tttt_count = 0
        for sent in nlp_result:
            morps = sent['morp']
            dependencies = sent['dependency']
            words = sent['word']
            ner_list = sent['NE']

            list_candidates = []

            # MODIFIER 확장해서 명사구 목록 뽑기
            for idx, dep in enumerate(dependencies):
                if( self._is_candidate_eojeol(dep, morps) ):
                    tttt_count += min(idx+1, 7)
                    modifier_extent = [idx]
                    now, end = 0, 0
                    while now <= end:
                        for modifier in dependencies[modifier_extent[now]]['mod']:
                            if (modifier not in modifier_extent):
                                if ('SBJ' not in dependencies[modifier]['label'] and 'CNJ' not in dependencies[modifier]['label']):
                                    modifier_extent.append(modifier)
                                    end += 1
                        now += 1

                    modifier_extent = sorted(modifier_extent)
                    st_modifier = modifier_extent[0]
                    for j in reversed(range(len(modifier_extent) - 1)):
                        if (modifier_extent[j] - modifier_extent[j-1] > 1):
                            st_modifier = modifier_extent[j]
                            break
                    list_candidates.append((st_modifier,idx))

            # 중심어가 같은 것 제거
            old_list_candidates = list_candidates
            list_candidates = []
            for item1 in old_list_candidates:
                isItem1OK = True
                for item2 in old_list_candidates:
                    if (item1[1] == item2[1] and item2[0] < item1[0]):
                        isItem1OK = False
                        break
                if(isItem1OK):
                    list_candidates.append(item1)

            # NER 단위보다 작은 것 제거
            old_list_candidates = list_candidates
            list_candidates = []
            for candidate in old_list_candidates:
                mention_start = words[candidate[0]]['begin']
                mention_end = words[candidate[1]]['end']
                isCandidateOK = True
                for ner in ner_list:
                    if (mention_start >= ner['begin'] and mention_end <= ner['end']):
                        if (mention_end - mention_start < ner['end'] - ner['begin']):
                            isCandidateOK = False
                            break
                if (isCandidateOK):
                    list_candidates.append(candidate)

            # 너무 긴것 제거
            old_list_candidates = list_candidates
            list_candidates = []
            for candidate in old_list_candidates:
                isCandidateOK = True
                if (candidate[1] - candidate[0] >= 8):
                    isCandidateOK = False
                if (isCandidateOK):
                    list_candidates.append(candidate)


            for item in list_candidates:

                dep_st = morps[words[item[0]]['begin']]['st']
                en_morp_idx = words[item[1]]['end']
                for i in reversed(range(words[item[1]]['begin'], words[item[1]]['end']+1)):
                    if (morps[i]['type'].startswith('J') or morps[i]['type'].startswith('VC')):
                        en_morp_idx = i-1
                        break
                dep_en = morps[en_morp_idx]['en']

                is_pronoun = False
                for dep_id in range(item[0], item[1]+1):
                    is_st_morp = True
                    for morp_id in range(words[dep_id]['begin'], words[dep_id]['end']+1):
                        if ((morps[morp_id]['type'] == 'MM' and morps[morp_id]['lemma'] in self.jisi_determiner_list) or
                            morps[morp_id]['type'] == 'NP'):
                            is_pronoun = True
                            dep_st = morps[morp_id]['st']
                            break
                        if ((morps[morp_id]['type'] == 'NNG') and (morps[morp_id]['lemma'] in self.jisi_determiner_list or morps[morp_id]['lemma'] in self.pronoun_lemma_list)
                            and is_st_morp):
                            is_pronoun = True
                            break
                        is_st_morp = False
                    if (is_pronoun):
                        break


                mention = {'st' : dep_st,
                           'en' : dep_en,
                           'text' : sent['text'].strip()[dep_st - morps[0]['st']:dep_en - morps[0]['st']],
                           'is_pronoun' : is_pronoun}
                if (mention['is_pronoun']):
                    mention_list.append(mention)
        #print (tttt_count)
        return mention_list



    def _revise_input(self,input):
        if ('nlp_result' not in input):
            if ('text' in input):
                input['nlp_result'] = util.get_nlp_parse_result(input['text'])
            else:
                return None
        if ('sentence' in input['nlp_result']):
            input['nlp_reslt'] = input['nlp_result']['sentence']
        return input

    def detect(self,input):
        try:
            input = self._revise_input(input)
            if (input == None):
                return {'pronoun_list':[]}

            nlp_result = self._set_position_character(input['nlp_result'])
            pronoun_list = self._extract_metnion(nlp_result)
            return {'pronoun_list':pronoun_list}
        except:
            return {'pronoun_list':[]}

if __name__ == '__main__':
    pronoun_detector = PronounDetector()

    sent = '생애. 1413년에 마리는 샤를_6세와 바이에른의_이자보의 다섯 번째 아들인 샤를_7세과 약혼을 했다. 1422년 4월에 그녀는 부르주에서 그녀의 사촌이였던 샤를과 혼인하였고 이후 프랑스의 왕비가 되었다. 백년_전쟁에서 남편의 승리는 마리의 가문에게서 받은 지원을 받은 덕이였으며, 특히 그녀의 어머니인 욜란다_데_아라곤이 그랬었다. 마리와 샤를이 14명의 자녀를 두었음에도, 남편의 애정은 하녀인 아녜스_소렐에게 있었다.'
    result = pronoun_detector.detect({'text':sent})
    print (result['pronoun_list'])
