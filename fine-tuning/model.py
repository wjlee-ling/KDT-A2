"""
SKT의 KoGPT2를 기반으로 신문사(조선일보, 한겨레)별 성향에 맞는 기사 생성하도록 미세조정하는 코드.
reference:
https://huggingface.co/docs/transformers/tasks/language_modeling

"""
import torch
from transformers import GPT2LMHeadModel,PreTrainedTokenizerFast

tokenizer = PreTrainedTokenizerFast.from_pretrained("skt/kogpt2-base-v2",
  bos_token='</s>', eos_token='</s>', unk_token='<unk>',
  pad_token='<pad>', mask_token='<mask>')

model_base = GPT2LMHeadModel.from_pretrained('skt/kogpt2-base-v2')
model_epoch2 = GPT2LMHeadModel.from_pretrained('skt/kogpt2-base-v2')
model_epoch2.load_state_dict(torch.load("/home/ubuntu/kogpt_article/trained_weights/0414_only_politics_epoch_2"))

model_base.eval()
model_epoch2.eval()

test1= "최저임금위원회가 내년도 최저임금을 5.1% 인상하기로 하자" # https://www.chosun.com/economy/industry-company/2021/07/13/HYARCEFTGVDAHIPWIE7ZGDNUHU/
test2 = "정부와 여당이 제2의 4대강 사업을 선언하자"

for test in [test1, test2]:
  for publisher in ['조선일보', '한겨레']:
    print(f'====={publisher}======')
    test_tokens = publisher + ": " + test
    test_tokens = tokenizer(test_tokens, max_length=128, add_special_tokens=True, padding=True,truncation=True, return_tensors='pt')
    
    # baseline
    generated = model_base.generate(**test_tokens, max_length = 128)
    print(tokenizer.decode(generated[0]))

    # after training 3 epochs
    generated= model_epoch2.generate(**test_tokens, max_length = 128)
    print(tokenizer.decode(generated[0]))