"""
transformers의 trainer모델 사용하여 fine-tuning하기 
ref:
https://colab.research.google.com/github/huggingface/notebooks/blob/main/transformers_doc/en/pytorch/training.ipynb#scrollTo=o4SXptoqsQnr
https://huggingface.co/transformers/v3.2.0/model_doc/gpt2.html
to-do:
1. training data에서 어떤 topic 혹은 original_topic만 뽑아서 훈련시킬지 고민
2. lr-rate scheduler?
3. transformers의 trainer 사용하는 코드
4. 최적화: hyper-parameter 설정 
5. 여기서 정한 batch_size 를 dataset.py에서 임포트하기 (ImportError: cannot import name 'train_dataloader' from partially initialized module 'dataset' (most likely due to a circular import) )
6. 전처리: 이상한 문자들 예) ◇
"""
import os
import torch
from transformers import TrainingArguments, Trainer
from transformers import GPT2LMHeadModel,PreTrainedTokenizerFast
from tqdm.auto import tqdm
from dataset import train_dataloader, test_dataloader, batch_size

# hyper-parameters settings
batch_size=batch_size  
learning_rate=3e-5
num_epochs=3
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

# pretrained model and tokenizer
model = GPT2LMHeadModel.from_pretrained('skt/kogpt2-base-v2')
tokenizer = PreTrainedTokenizerFast.from_pretrained("skt/kogpt2-base-v2",
  bos_token='</s>', eos_token='</s>', unk_token='<unk>',
  pad_token='<pad>', mask_token='<mask>')

# optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

# training
model.to(device)
model.train()
print('start fine-tuning')

for epoch in range(num_epochs):
    loss_per_epoch = 0
    for batch in tqdm(train_dataloader):
        inputs = tokenizer(batch, max_length=128, add_special_tokens=True, padding=True,truncation=True, return_tensors='pt').to(device)
        outputs = model(**inputs, labels=inputs['input_ids'])
        loss = outputs.loss

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        loss_per_epoch += loss
    
    # saving trained weights 
    path = os.path.join("/home/ubuntu/kogpt_article/trained_weights", f"0414_only_politics_epoch_{epoch}")
    torch.save(model.state_dict(), path)

    print(f'Loss for this epoch : {loss_per_epoch}')

print('Fine-tuning has finished successfully')
"""
# trainer
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    weight_deca=0.01
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset['train'],
    eval_dataset=dataset['test'],
    tokenizer=tokenizer
)

trainer.train()
"""