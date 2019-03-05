import json
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

def get_text_length_in_byte(text):
    '''text가 몇 Byte인지 반환'''
    return len(str.encode(text))


if __name__ == "__main__":
    get_nlp_parse_result("안녕하세요 나는 사과를 좋아합니다.")
