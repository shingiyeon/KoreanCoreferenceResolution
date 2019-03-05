#!/bin/sh
path0='./'
entity_type_path='./'
final_output_path='./'
path1='./tta_data/'
path2='./tta_data2/'
path3='./tta_data3/'
path4='./'
path5='./tta_data4/'

tta_file='tta2.csv'
entity_type_file='entity_type_kbox'
final_csv_file_name='output.csv'
file1='ttaresult181128'
file2='coref-ttaresult181128'
ZA_option='on'
ratio=1.0
mode='predict'
model='model_final'
max_document_size=100000
#recommend 100000 bytes

python tta.py --file_path $path0 --file_name $tta_file --entity_type_file_path $entity_type_path --entity_type_file_name $entity_type_file --output_file_path $path1
python make_document.py --input_path $path1 --output_path $path2 --max_document_size $max_document_size
python make_conll.py --input_path $path2 --previous_path $path2 --modified_path $path3 --output_path $path4 --output_file $file1 --mode $mode --ratio $ratio --ZA $ZA_option
python minimize.py --input_path $path4 --input_file $file1 --output_path $path4
python predict.py $model $file1.jsonlines $file2
python jsonlines_to_json.py --input_path $path3 --output_path $path5 --input_file $path4$file2
python tta_result.py --file_path $path0 --file_name $tta_file --input_path $path5 --output_file_path $final_output_path --output_file_name $final_csv_file_name
