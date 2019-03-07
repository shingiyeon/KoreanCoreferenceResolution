# Korean Co-reference Resolution End-to-End Learning using Bi-LSTM with Mention Features

## Introduction
KBP 단계에서 한국어 상호참조해결을 통한 DS data 증강

## Definition
1. 개체 목록이 주어진 문서에서 대명사와 지시관형사를 탐지
2. 주격이 생략된 대상을 ETRI Dependency Tree로 파악
3. 생략된 주어, 대명사, 지시관형사, 혹은 멘션들이 어떠한 개체를 참조하는지 확인

## Input
지식베이스 개체가 될 수 있는 멘션 후보 (NER Module의 output)
(예시 폴더를 참조해주세요.)

## Output
감지된 대명사나 생략된 주어가 개체를 가르킬 경우 해당 개체로 변환된 문장 생성
(예시 폴더를 참조해주세요.)

## 실행 방법
./coreference.sh

## Reference
By Higher-order Coreference Resolution with Coarse-to-fine Inference

This repository contains the code for replicating results from

* [Higher-order Coreference Resolution with Coarse-to-fine Inference](https://arxiv.org/abs/1804.05392)
* [Kenton Lee](http://kentonl.com/), [Luheng He](https://homes.cs.washington.edu/~luheng), and [Luke Zettlemoyer](https://www.cs.washington.edu/people/faculty/lsz)
* In NAACL 2018

## 제작
신기연 (Giyeon Shin)
nuclear852@kaist.ac.kr
nuclear852@gmail.com

## 서비스
Semantic Web Research Center
