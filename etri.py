import urllib.request
from urllib.parse import urlencode
import json
import pprint
import socket
import struct
#from src import etri2conll

def getETRI_rest(text):
    url = "http://143.248.135.20:31235/etri_parser"
    contents = {}
    contents['text'] = text
    contents = json.dumps(contents).encode('utf-8')
    u = urllib.request.Request(url, contents)
    response = urllib.request.urlopen(u)
    result = response.read().decode('utf-8')
    result = json.loads(result)
    return result

def read_blob(sock, size):
    buf = ''
    while len(buf) != size:
        ret = sock.recv(size - len(buf))
        if not ret:
            raise Exception("Socket closed")
        ret += buf
    return buf
def read_long(sock):
    size = struct.calcsize("L")
    data = readblob(sock, size)
    return struct.unpack("L", data)

def getETRI(text):
    host = '143.248.135.60'
    port = 33222
    ADDR = (host, port)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        clientSocket.connect(ADDR)
    except Exception as e:
        return None
    try:
        clientSocket.sendall(str.encode(text))
        #clientSocket.sendall(text.encode('unicode-escape'))
        #clientSocket.sendall(text.encode('utf-8'))
        buffer = bytearray()
        while True:
            data = clientSocket.recv(1024)
            if not data:
                break
            buffer.extend(data)
        result = json.loads(buffer.decode(encoding='utf-8'))
        return result['sentence']
    except Exception as e:
        return None

def lemmatizer(word, pos):
    etri = getETRI(word)
    lemmas = etri[0]['WSD']
    lemma = word
    for i in lemmas:
        p = i['type']
        if pos == 'v' or pos == 'VV':
            if p == 'VV':
                lemma = i['text']
                break
        elif pos == 'n' or pos == 'NN' or pos == 'NNG' or pos == 'NNP' or pos =='NNB' or pos =='NR' or pos == 'NP':
            if 'NN' in p:
                lemma = i['text']
                break
        elif pos == 'adj' or pos == 'VA':
            if p == 'VA':
                lemma = i['text']
                break
        else:
            pass
    return lemma
def getPOS(word):
    etri = getETRI(word)
    pos = etri[0]['WSD'][0]['type']
    if pos.startswith('N'):
        pos = 'n'
    elif pos == 'VV':
        pos = 'v'
    elif pos == 'VA':
        pos = 'adj'
    else:
        pos == 'n'
    return pos

def getMorpEval(tid, nlp):
    result = '_'
    for i in nlp[0]['morp_eval']:
        if i['id'] == tid:
            morp = i['result']
            morps = morp.split('+')
            pos_sequence = []
            for m in morps:
                if '/' not in m:
                    pass
                else:
                    p = m.split('/')[1]
                    pos_sequence.append(p)
            pos = '+'.join(pos_sequence)
            result = pos
        else:
            pass
    return result

def getMorhWithWord(tid, nlp):
    result = '_'
    for i in nlp[0]['morp_eval']:
        if i['id'] == tid:
            morp = i['result']
            break
    return morp

def getETRI_CoNLL2006(text):
    nlp = getETRI(text)
    result = []
    for i in nlp[0]['dependency']:
        tid = i['id']
        token = i['text']
        third = getMorhWithWord(tid, nlp)
        pos = getMorpEval(tid, nlp)
        five = '_'
        arc = i['head']
        pt = i['label']
        eight = '_'
        nine = '_'
        line = [tid, token, third, pos, five, arc, pt, eight, nine]
        result.append(line)
    return result

def getETRI_CoNLL2009(text):
    nlp = getETRI(text)
    result = []
    for i in nlp[0]['dependency']:
        tid = i['id']
        token = i['text']
        third = getMorhWithWord(tid, nlp)
        plemma = token
        pos = getMorpEval(tid, nlp)
        ppos = pos
        feat = '_'
        pfeat = '_'
        head = i['head']
        phead = head
        deprel = i['label']
        pdeprel = i['label']
        line = [tid, token, third, plemma, pos, ppos, feat, pfeat, head, phead, deprel, pdeprel]
        result.append(line)
    return result


#def test():
    #conll = getETRI_CoNLL2006(text)
    #conll = getETRI_CoNLL2009(text)
    #pprint.pprint(conll)
#test()
