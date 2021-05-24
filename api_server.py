from flask_restful import Resource, reqparse, Api
from flask import Flask, make_response
from flask_cors import CORS
from module.aladinV2 import Aladin
from module.yes24V2 import Yes24
# import module.aladin as Aladin
#import module.yes24 as Yes24
import json


class Search(Resource):
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('word', required=True,
                                type=str, help='Please enter word')
            parser.add_argument('mode', required=True,
                                type=int, help='Please enter mode')
            args = parser.parse_args()
            result = ''
            if args['mode'] == 0:
                aladin = Aladin(args['word'])
                result = aladin.result()
            elif args['mode'] == 1:
                yes24 = Yes24(args['word'])
                result = yes24.result()
            """
            elif args['mode'] == "common":
            """
            resp = make_response(json.dumps(result, ensure_ascii=False))
            return resp
        except Exception as e:
            return {'error': str(e)}


app = Flask('api_offbookstore')
CORS(app)
app.config['JSON_AS_ASCII'] = False
api = Api(app)
api.add_resource(Search, '/search')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
