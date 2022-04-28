import requests
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from .forms import PromptForm
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel
#from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eyf4-DEN34-3v!dD' 

@app.route("/", methods=['GET', 'POST'])
def index():
    prompt = PromptForm()
    generated='18'
    if request.method =='POST':
        return generate_article(prompt)
    return render_template('index.html', prompt_form=prompt, generated=generated)

def generate_article(prompt):
    tokenizer = PreTrainedTokenizerFast.from_pretrained("A2/kogpt2-taf",
                    bos_token='</s>', eos_token='</s>', unk_token='<unk>',
                    pad_token='<pad>', mask_token='<mask>')
    model = GPT2LMHeadModel.from_pretrained('A2/kogpt2-taf')
    model.eval()
    generated =''
    #if prompt.validate_on_submit():
    newspaper = prompt.newspaper.data
    lead = prompt.lead.data
    if newspaper != '':
        user_prompt = newspaper+':'+lead
    else:
        user_prompt = lead
    input_ids = tokenizer.encode(user_prompt, return_tensors='pt')
    gen_ids = model.generate(input_ids,
                        max_length=128,
                        repetition_penalty=2.0,
                        pad_token_id=tokenizer.pad_token_id,
                        eos_token_id=tokenizer.eos_token_id,
                        bos_token_id=tokenizer.bos_token_id,
                        use_cache=True)
    generated = tokenizer.decode(gen_ids[0])
    if generated.startswith(newspaper):
        generated.replace(newspaper+':', '')
    else:
        generated = generated[1:] # 앞에 : 제거
    return render_template('index.html', prompt_form=prompt, generated=generated)


if __name__ == '__main__':
    app.run()