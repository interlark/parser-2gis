# Patch pychrome, make it handle correctly empty CDP messages

import pychrome.tab
import json
import websocket
import warnings
import logging

pychrome_logger = logging.getLogger('pychrome')


def patch_pychrome():
    def _recv_loop_patched(self):
        while not self._stopped.is_set():
            try:
                self._ws.settimeout(1)
                message_json = self._ws.recv()
                if not message_json:
                    continue
                message = json.loads(message_json)
            except websocket.WebSocketTimeoutException:
                continue
            except (websocket.WebSocketException, OSError):
                if not self._stopped.is_set():
                    pychrome_logger.error('websocket exception', exc_info=True)
                    self._stopped.set()
                return

            if self.debug:  # pragma: no cover
                print('< RECV %s' % message_json)

            if 'method' in message:
                self.event_queue.put(message)

            elif 'id' in message:
                if message['id'] in self.method_results:
                    self.method_results[message['id']].put(message)
            else:  # pragma: no cover
                warnings.warn('unknown message: %s' % message)

    pychrome.tab.Tab._recv_loop = _recv_loop_patched
