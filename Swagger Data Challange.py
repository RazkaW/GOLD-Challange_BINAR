#flask API, Swagger UI 

import re
import pandas as pd
from flasgger import swag_from
from flask import request, Flask, jsonify
from flasgger import Swagger, LazyString, LazyJSONEncoder


app = Flask(__name__)

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info = {
        'title': LazyString(lambda:'Data Processing and Modeling'),
        'version': LazyString(lambda:'by Al Rizky Maulana'),
        'description': LazyString(lambda:'Dokumentasi API untuk Data Processing dan Modeling')
        }, host = LazyString(lambda: request.host)
    )

swagger_config = {
        "headers":[],
        "specs":[
            {
            "endpoint":'docs',
            "route":'/docs.json'
            }
        ],
        "static_url_path":"/flasgger_static",
        "swagger_ui":True,
        "specs_route":"/docs/"
    }

swagger = Swagger(app, template=swagger_template, config=swagger_config)
@swag_from("hello_world.yml", methods=['GET'])
@app.route('/', methods=['GET'])
def hello_world():
    json_response = { 
        'status_code':200, 
        'description':'menyapa hello world', 
        'data': "Hello World"
        }

    response_data = jsonify(json_response)
    return response_data


@swag_from("text_processing.yml", methods=['POST'])
@app.route('/text_processing', methods=['POST'])
def text_processing():
    text = request.form.get('text')

    json_response = { 
        'status_code':200, 
        'description':'teks yang sudah diproses', 
        'data': re.sub(r'[^a-zA-Z0-9]', ' ', text)
        }
    response_data = jsonify(json_response)
    return response_data

@swag_from("text_processing_file.yml", methods=['POST'])
@app.route('/text_processing_file', methods=['POST'])
def text_processing_file():
    text = request.files.getlist('upfile')[0]

    # TODO : manfaatkan abusive_dictionary
    abusive_dictionary = pd.read_csv('abusive.csv')

    alay_dict = pd.read_csv('new_kamusalay.csv', encoding='iso-8859-1', header=None)
    alay_dict = alay_dict.rename(columns={0: "Original", 1: "Replacement"})

    def lowercase(text):
        return text.lower() 

    def remove_unnecessary_char(text):
        text = re.sub('\n',' ',text) # Remove every '\n'
        text = re.sub('rt',' ',text) # Remove every retweet symbol
        text = re.sub('user',' ',text) # Remove every username
        text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text) # Remove every URL
        text = re.sub('  +', ' ', text) # Remove extra spaces
        text = re.sub(r'pic.twitter.com.[\w]+', '', text) # Remove every pic 
        text = re.sub('gue','saya',text) # replace gue - saya
        text = re.sub(r':', '', text) #Remove symbol 
        text = re.sub(r'‚Ä¶', '', text) #Remove symbol Ä¶
        return text

    def remove_nonaplhanumeric(text):
        text = re.sub('[^0-9a-zA-Z]+', ' ', text) 
        return text

    #Merubah alay dataframe menjadi dictionary
    alay_dict_map = dict(zip(alay_dict['Original'], alay_dict['Replacement']))

    #Merubah kata-kata alay menjadi kata baku
    def normalize_alay(text):
        return ' '.join([alay_dict_map[word] if word in alay_dict_map else word for word in text.split(' ')])

    def preprocess(text):
        text = lowercase(text)
        text = remove_unnecessary_char(text)
        text = remove_nonaplhanumeric(text)
        text = normalize_alay(text)
        return text

    #original data
    df_new = pd.DataFrame()
    df_data = pd.read_csv(text, encoding='iso-8859-1')
    df_new['Old_tweet'] = df_data['Tweet']

    #Menjalankan fungsi process
    df_data['Tweet'] = df_data['Tweet'].apply(preprocess)
    df_new['New_Tweet'] = df_data['Tweet']

    df_new.to_csv('output_cleansing.csv', index=False, sep=',')

    json_response = { 
        'status_code':200, 
        'description':'text yang sudah di proses', 
        'data': "succes"
        }

    response_data = jsonify(json_response)
    return response_data
if __name__ == '__main__':
    app.run()