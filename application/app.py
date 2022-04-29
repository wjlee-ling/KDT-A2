import requests
from flask import Flask, render_template, redirect, url_for, request
from .forms import PromptForm
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eyf4-DEN34-3v!dD' 

tokenizer = PreTrainedTokenizerFast.from_pretrained("A2/kogpt2-taf",
        bos_token='</s>', eos_token='</s>', unk_token='<unk>',
        pad_token='<pad>', mask_token='<mask>')
model = GPT2LMHeadModel.from_pretrained('A2/kogpt2-taf')
model.eval()


@app.route("/", methods=['GET', 'POST'])
def index():
    prompt = PromptForm()
    generated=''
    if request.method =='POST':
        return generate_article(prompt)
    return render_template('index.html', prompt_form=prompt, generated=generated)

def generate_article(prompt):

    #newspaper = prompt.newspaper.data
    lead = prompt.lead.data
    generated_ls = []
    newspaper_ls = ['', '조선일보', '중앙일보', '동아일보', '한겨레', '경향신문']
    for newspaper in newspaper_ls:
    
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
            generated = generated.replace(newspaper+':', '').strip('</s>')
        generated_ls.append(generated)

    return render_template('generate.html', prompt_form=prompt, zip=zip, generated_ls=generated_ls, newspaper_ls=newspaper_ls)


if __name__ == '__main__':
    app.run(debug=True)