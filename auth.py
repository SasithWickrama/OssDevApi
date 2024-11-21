import json

from flask import jsonify, make_response
from flask_jwt_extended import create_access_token

from log import Logger

logger = Logger.getLogger('token', 'logs/token')
elogger = Logger.getLogger('error', 'logs/error')


def getAuthKey(userid):
    with open('auth.json') as f:
        data = json.load(f)
        for usr in data['user_list']:
            if usr['username'] == str(userid):
                return usr['authkey']


class Authenticate:

    def generateToken(self, ref):

        if( getAuthKey(self['username']) == self['api_key'] ):
            access_token = create_access_token(identity=self['api_key'])
            logger.info("Token : %s" % ref + " - " + str(access_token))
            return make_response(jsonify(access_token=access_token), 200)
        else :
            elogger.info("request : %s" % ref + " - " + str(self) + " - Invalid Credentials")
            return make_response(jsonify(message="Invalid Credentials"), 401)
