import os
import etri

data_path = "./data/"
data_list = os.listdir(data_path)

g = open("./data/wo_postag.txt", "w", encoding='utf-8')

sentence = ""
line_index = 0

for file_name in data_list:
    f = open(data_path+file_name, 'r', encoding = 'utf-8')
    lines = f.readlines()
    for line in lines:
        sentence = ""
        if line_index % 1000 == 0:
            print(line_index)
        etri_info = etri.getETRI(line)
        if etri_info == None:
            continue
        wsd = etri_info[0]['WSD']
        if wsd == None:
            continue
        for token in wsd:
            sentence += token['text']+ " "
        sentence = sentence[:-1]+"\n"
        line_index += 1
        g.write(sentence)


