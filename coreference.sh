#!/bin/sh
path1='./temp_data/'
path2='./temp_data2/'
path3='./temp_data3/'
path4='./'
path5='./temp_data4/'

file1='result181106'
file2='coref-result181106'
ZA_option='on'
ratio=1.0
mode='predict'
model='model_final'
max_document_size=100000
#recommend 100000 bytes

python make_document.py --input_path $path1 --output_path $path2 --max_document_size $max_document_size
python make_conll.py --input_path $path2 --previous_path $path2 --modified_path $path3 --output_path $path4 --output_file $file1 --mode $mode --ratio $ratio --ZA $ZA_option
python minimize.py --input_path $path4 --input_file $file1 --output_path $path4
python predict.py $model $file1.jsonlines $file2
python jsonlines_to_json.py --input_path $path3 --output_path $path5 --input_file $path4$file2

