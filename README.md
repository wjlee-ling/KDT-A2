A2 팀 프로젝트

앱 Tone & Fact 이용은 [여기](http://13.58.98.48:8080/).

**KoGPT-taf Tokenizer 사양**
| vocab size | max_length | class | special tokens |
| :---: | :---: | :---: | :---: |
| 51,213 | 128 | PreTrainedTokenizerFast (from HuggingFace) | \</s>,  \<unk>, \<pad>, \<mask> |

**Model**
| model type | # of hidden | # of layers and heads | 최대 생성 길이 |
| :---: | :---: | :---: | :---: |
| GPT2 | 768 | 12 | 128 토큰 |

![project architecture drawio (2)](https://user-images.githubusercontent.com/83438381/163582843-4e0869d0-67dd-4dc9-889e-fe034b784275.png)
