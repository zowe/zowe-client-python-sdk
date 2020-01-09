'''
Copyright 2020 Guilherme Cartier de Palma

Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at 
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software 
distributed under the License is distributed on an "AS IS" BASIS, 
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
See the License for the specific language governing permissions and 
limitations under the License. 
'''

from ..utilities import ZosmfApi

class Tso(ZosmfApi):

    def __init__(self, connection):
        super().__init__(connection, '/zosmf/tsoApp/tso')
        self.session_not_found = self.constants['TsoSessionNotFound']

    def issue_command(self, command):
        pass

    def start_tso_session(self, proc='IZUFPROC',chset='697',cpage='1047',rows='204',cols='160',rsize='4096',acct='DEFAULT'):
        params = {'proc': proc, 'chset': chset, 'cpage': cpage, 'rows': rows, 'cols': cols, 'rsize': rsize, 'acct': acct}
        self.request_arguments['params'] = params
        response_json = self.request_handler.perform_request('post', self.request_arguments)
        return response_json['servletKey']

    def send_tso_message(self, session_key, message):
        pass

    def ping_tso_session(self, session_key):
        request_url = '{}/{}/{}'.format(self.request_endpoint, 'ping', session_key)
        self.request_arguments['url'] = request_url
        response_json = self.request_handler.perform_request('put', self.request_arguments)
        message_id_list = self.parse_message_ids(response_json)
        return "Ping successful" if self.session_not_found not in message_id_list else "Ping failed"

    def end_tso_session(self, session_key):
        request_url = '{}/{}'.format(self.request_endpoint, session_key)
        self.request_arguments['url'] = request_url
        response_json = self.request_handler.perform_request('delete', self.request_arguments)
        message_id_list = self.parse_message_ids(response_json)
        return "Session ended" if self.session_not_found not in message_id_list else "Session already ended"

    def parse_message_ids(self, response_json):
        return [message['messageId'] for message in response_json['msgData']] if 'msgData' in response_json else []
