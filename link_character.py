import pickle
import re

ALL_CHARACTERS = [5, 8, 9, 18, 29, 30, 35, 42, 48, 50, 51, 58, 59, 71, 75, 94, 96, 98, 99, 100, 105, 108, 132, 133, 136, 138, 150, 152, 167, 168, 169, 171, 183, 184, 195, 196, 197, 200, 202, 204, 205, 210, 213, 216, 219, 228, 230, 240, 242, 248, 250, 257, 265, 268, 273, 274, 280, 282, 283, 284, 292, 302, 306, 317, 321, 329, 335, 339, 342, 345, 354, 355, 358, 380, 387, 396, 397]
MAIN_CHARACTERS = [59, 183, 248, 292, 306, 335]

ENAME_TO_ID = {}
EID_TO_NAME = {}

def get_eid_by_mention(mention, speaker):
    #first-person pronoun match
    if (mention in ['I', 'my', 'me', 'mine']):
        if (speaker in ENAME_TO_ID):
            return ENAME_TO_ID[speaker]

    mention = re.sub(r'[^\w]', ' ', mention).replace(' ', '').lower()

    # all_match
    for ename_key in ENAME_TO_ID:
        r_ename_key = re.sub(r'[^\w]', ' ', ename_key).replace(' ', '').lower()
        if (mention == r_ename_key):
            return ENAME_TO_ID[ename_key]

    # first_name_match
    for ename_key in ENAME_TO_ID:
        names = ename_key.split()
        if (len(names) > 1):
            r_ename_key = re.sub(r'[^\w]', ' ', names[0]).replace(' ', '').lower()
            if (mention == r_ename_key):
                return ENAME_TO_ID[ename_key]
    return 0

# entity_map
f = open('data/friends_entity_map.txt')
for line in f:
    eid, ename = line.strip().split('\t')
    eid = int(eid)
    if (eid not in ALL_CHARACTERS):
        continue
    ENAME_TO_ID[ename] = eid
    EID_TO_NAME[eid] = ename
f.close()


# Parse Prediction
with open('evaluate_result.pickle', 'rb') as handle:
    data = pickle.load(handle)
    predict_data = data['prediction']

# Parse Gold Data and
f = open('data/test.english.v4_gold_conll','r',encoding='utf-8')
key = ''
nlp_datas = {}
gold_datas = []
for line in f:
    if ('#begin document' in line):
        key = line[17:32] + '_' + line[-2:-1]
        nlp_datas[key] = []
    elif ('#end document' not in line and len(line) > 1):
        items = line.strip().split()
        nlp_datas[key].append({'word':items[3],
                                'lemma':items[6],
                                'speaker': items[9].replace('_',' ')})

        entityid = items[-1]
        if ('(' in entityid):
            gold_datas.append({'st':len(nlp_datas[key]) - 1,
                               'en':-1,
                               'entityid':int(entityid.replace('(','').replace(')','')),
                               'doc_key':key})
        if (')' in entityid):
            gold_datas[-1]['en'] = len(nlp_datas[key]) - 1
f.close()

# majority voting
for doc_key, cluster_list in predict_data.items():
    for cluster_idx,cluster in enumerate(cluster_list):
        eid_list = []
        for i,boundary in enumerate(cluster):
            st = boundary[0]
            en = boundary[1]
            speaker = nlp_datas[doc_key][st]['speaker']
            mention = ''
            for j in range(st,en+1):
                mention = mention + nlp_datas[doc_key][j]['word'] + ' '
            mention = mention.strip()

            eid_list.append(get_eid_by_mention(mention,speaker))

        non_zero=False
        for eid in eid_list:
            if (eid > 0):
                non_zero = True
                break

        # set most common id to cluster id, unless all are 0
        cluster_eid =  max(set(eid_list), key=eid_list.count) if non_zero else 0
        predict_data[doc_key][cluster_idx] = {'cluster_eid':cluster_eid,
                                              'cluster':cluster}


f_out = open('data/sys.out','w',encoding='utf-8')
for index,item in enumerate(gold_datas):
    doc_key = item['doc_key']
    st = item['st']
    en = item['en']
    speaker = nlp_datas[doc_key][st]['speaker']
    mention = ''
    for j in range(st, en + 1):
        mention = mention + nlp_datas[doc_key][j]['word'] + ' '
    mention = mention.strip()

    e_id = -1
    for cluster in predict_data[doc_key]:
        for boundary in cluster['cluster']:
            if (boundary[0] == st and boundary[1] == en):
                e_id = cluster['cluster_eid']
                break
        if (e_id >= 0):
            break
    if (e_id < 0):
        e_id = get_eid_by_mention(mention, speaker)

    f_out.write(str(e_id))
    if (index < len(gold_datas)-1):
        f_out.write('\n')

f.close()