Grepp Programmers KDT 인공지능 데브 코스 3기 A2 팀 프로젝트.

같은 정치적 이슈라도 언론사에 따라 미세하게 다른 논조를 보인다는 점에 착안하여, SKT의 KoGPT2를 5대 일간지(조선일보, 동아일보, 한겨레, 중앙일보, 경향신문)의 사설(일간지별 각 만여개)로 파인튜닝한 생성모델을 생성.

**KoGPT-taf Tokenizer 사양**
| vocab size | max_length | class | special tokens |
| :---: | :---: | :---: | :---: |
| 51,213 | 128 | PreTrainedTokenizerFast (from HuggingFace) | \</s>,  \<unk>, \<pad>, \<mask> |

SKT의 KoGPT2의 사전(51,200)에 13개의 정치적으로 주요한 개체명을 추가함. (추가한 토큰: "박근혜", "트럼프", "김정은", "문재인", "안철수", "윤석열", "이명박", "코로나", "세월호", "사드", "새누리당", "4대강", "청와대")

**Model**
| model type | # of hidden | # of layers and heads | 최대 생성 길이 |
| :---: | :---: | :---: | :---: |
| GPT2 | 768 | 12 | 128 토큰 |





<!--![project architecture drawio (2)](https://user-images.githubusercontent.com/83438381/163582843-4e0869d0-67dd-4dc9-889e-fe034b784275.png)-->
