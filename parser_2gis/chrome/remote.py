from __future__ import annotations

import base64
import json
import queue
import re
import threading
from typing import TYPE_CHECKING, Any, Callable, Dict

import pychrome
import requests
from requests.exceptions import RequestException
from websocket import WebSocketException

from ..common import wait_until_finished
from .browser import ChromeBrowser
from .dom import DOMNode
from .exceptions import ChromeException

if TYPE_CHECKING:
    from .options import ChromeOptions

    Request = Dict[str, Any]
    Response = Dict[str, Any]


class ChromeRemote:
    """Wrapper for Chrome DevTools Protocol Interface.

    Args:
        chrome_options: ChromeOptions parameters.
        response_patterns: Repsonse URL patterns to capture.
    """
    def __init__(self, chrome_options: ChromeOptions, response_patterns: list[str]) -> None:
        self._chrome_options: ChromeOptions = chrome_options
        self._chrome_browser: ChromeBrowser
        self._chrome_interface: pychrome.Browser
        self._chrome_tab: pychrome.Tab
        self._response_patterns: list[str] = response_patterns
        self._response_queues: dict[str, queue.Queue[Response]] = {x: queue.Queue() for x in response_patterns}
        self._requests: dict[str, Request] = {}  # _requests[rquest_id] = <Request>
        self._requests_lock = threading.Lock()

    @wait_until_finished(timeout=60)
    def _connect_interface(self, port: int) -> bool:
        """Establish connection to Chrome and open new tab.

        Args:
            port: Remote's Chrome port.

        Returns:
            `True` on success, `False` on failure.
        """
        try:
            self._chrome_interface = pychrome.Browser(url=f'http://127.0.0.1:{port}')
            self._chrome_tab = self._chrome_interface.new_tab()
            self._chrome_tab.start()
            return True
        except (RequestException, WebSocketException):
            return False

    def start(self) -> None:
        """Open browser, create new tab, setup remote interface."""
        # Open browser
        self._chrome_browser = ChromeBrowser(self._chrome_options)

        # Connect browser with CDP
        self._connect_interface(self._chrome_browser.remote_port)

        self._setup_tab()
        self._init_tab_monitor()

    def _setup_tab(self) -> None:
        """Hide webdriver, enable requests/response interception, fix UA."""
        # Fix user agent for headless browser
        original_useragent = self.execute_script('navigator.userAgent')
        fixed_useragent = original_useragent.replace('Headless', '')
        self._chrome_tab.Network.setUserAgentOverride(userAgent=fixed_useragent)

        # Hide webdriver traces
        self.add_start_script(r'''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        ''')

        # def requestPaused(**kwargs):
        #     """Modify outgoing headers."""
        #     def headers_contain(name):
        #         return any(x for x in headers.keys() if x.lower() == name)

        #     request_id = kwargs['requestId']
        #     headers = kwargs['request']['headers']

        #     if not headers_contain('referer'):
        #         headers['referer'] = 'https://google.com'
        #         request_headers = [dict(name=k, value=v) for k, v in headers.items()]
        #         self._chrome_tab.Fetch.continueRequest(requestId=request_id, headers=request_headers)
        #     else:
        #         self._chrome_tab.Fetch.continueRequest(requestId=request_id)

        def responseReceived(**kwargs) -> None:
            """Gather responses."""
            response = kwargs.pop('response')
            response['meta'] = kwargs
            request_id = kwargs['requestId']
            resource_type = kwargs.get('type')

            # Skip preflights
            if resource_type == 'Preflight':
                return

            # Add response
            with self._requests_lock:
                if request_id in self._requests:
                    request = self._requests[request_id]
                    response['request'] = request
                    request['response'] = response

            # If response is desired, put it in the queue
            for pattern in self._response_patterns:
                if re.match(pattern, response['url']):
                    self._response_queues[pattern].put(response)

        def loadingFailed(**kwargs) -> None:
            error_text = kwargs.get('errorText')
            blocked_reason = kwargs.get('blockedReason')
            status_text = ''

            if error_text:
                status_text = 'error: %s' % error_text
            if blocked_reason:
                if status_text:
                    status_text += ', '
                status_text += 'blocked_reason: %s' % blocked_reason

            request_id = kwargs.get('requestId')
            response = {
                'status': -1,
                'statusText': status_text,
            }

            # Add response
            request_url = None
            with self._requests_lock:
                if request_id in self._requests:
                    request = self._requests[request_id]
                    response['request'] = request
                    request['response'] = response
                    request_url = request['url']

            if request_url:
                # If response is desired, put it in the queue
                for pattern in self._response_patterns:
                    if re.match(pattern, request_url):
                        self._response_queues[pattern].put(response)

        def requestWillBeSent(**kwargs) -> None:
            request = kwargs.pop('request')
            request['meta'] = kwargs
            request_id = kwargs['requestId']
            resource_type = kwargs.get('type')

            # Skip preflights
            if resource_type == 'Preflight':
                return

            # Add request
            with self._requests_lock:
                self._requests[request_id] = request

        self._chrome_tab.Network.responseReceived = responseReceived
        self._chrome_tab.Network.loadingFailed = loadingFailed
        self._chrome_tab.Network.requestWillBeSent = requestWillBeSent
        # self._chrome_tab.Fetch.requestPaused = requestPaused

        self._chrome_tab.Network.enable()
        self._chrome_tab.DOM.enable()
        self._chrome_tab.Page.enable()
        self._chrome_tab.Runtime.enable()
        self._chrome_tab.Log.enable()
        # self._chrome_tab.Fetch.enable()

    def _init_tab_monitor(self) -> None:
        """Monitor Chrome tab health."""
        tab_detached = False

        def monitor_tab() -> None:
            """V8 OOM could crash Chrome's tab and keep websocket functional
            like nothing bad happend, so we better monitor tabs index page
            and check if our tab is still alive."""
            while not self._chrome_tab._stopped.is_set():
                ret = requests.get('%s/json' % self._chrome_interface.dev_url, json=True)
                if not any(x['id'] == self._chrome_tab.id for x in ret.json()):
                    nonlocal tab_detached
                    tab_detached = True
                    self._chrome_tab._stopped.set()

                self._chrome_tab._stopped.wait(0.5)

        self._ping_thread = threading.Thread(target=monitor_tab, daemon=True)
        self._ping_thread.start()

        def get_send_with_reraise() -> Callable[..., Any]:
            """Reraise "Tab has been stopped" instead of `UserAbortException` in
            case of tab detach detected."""
            original_send = self._chrome_tab._send

            def wrapped_send(*args, **kwargs) -> Any:
                try:
                    return original_send(*args, **kwargs)
                except pychrome.UserAbortException:
                    if tab_detached:
                        raise pychrome.RuntimeException('Tab has been stopped')
                    else:
                        raise
            return wrapped_send

        self._chrome_tab._send = get_send_with_reraise()

    def navigate(self, url: str, referer: str = '', timeout: int = 60) -> None:
        """Navigate to URL.

        Args:
            referer: Set referer header.
            timeout: Wait timeout.

        Returns:
            None on success, error message on failure.
        """
        ret = self._chrome_tab.Page.navigate(url=url, _timeout=timeout, referrer=referer)
        error_message = ret.get('errorText', None)
        if error_message:
            raise ChromeException(error_message)

    @wait_until_finished(timeout=30, throw_exception=False)
    def wait_response(self, response_pattern: str) -> Response | None:
        """Wait for specified response with pre-defined pattern.

        Args:
            response_pattern: Repsonse URL pattern.

        Returns:
            Response or None in case of timeout.
        """
        try:
            if self._chrome_tab._stopped.is_set():
                raise pychrome.RuntimeException('Tab has been stopped')
            return self._response_queues[response_pattern].get(block=False)
        except queue.Empty:
            return None

    def clear_requests(self) -> None:
        """Clear all collected responses."""
        with self._requests_lock:
            self._requests = {}

    @wait_until_finished(timeout=15, throw_exception=False)
    def get_response_body(self, response: Response) -> Response:
        """Get and set response body.

        Args:
            response: Response without body.
        """
        try:
            request_id = response['meta']['requestId']
            response_data = self._chrome_tab.call_method('Network.getResponseBody',
                                                         requestId=request_id)
            if response_data['base64Encoded']:
                response_data['body'] = base64.b64decode(response_data['body']).decode('utf-8')

            response_body = json.loads(response_data['body'])
            response['body'] = response_body
            return response_body
        except pychrome.CallMethodException:
            # Nothing, response body not found
            return {}

    @wait_until_finished(timeout=None, throw_exception=False)
    def get_responses(self) -> list[Response]:
        """Get gathered responses."""
        with self._requests_lock:
            return [x['response'] for x in self._requests.values() if 'response' in x]

    def get_requests(self) -> list[Request]:
        """Get recorded requests."""
        with self._requests_lock:
            return [*self._requests.values()]

    def get_document(self, full: bool = True) -> DOMNode:
        """Get Document DOM tree.

        Args:
            full: Flag wheather to return full DOM or only root.

        Returns:
            Root DOM node.
        """
        tree = self._chrome_tab.DOM.getDocument(depth=-1 if full else 1)
        return DOMNode(**tree['root'])

    def add_start_script(self, source: str) -> None:
        """Add script that evaluates on every new page.

        Args:
            source: Text of the script.
        """
        self._chrome_tab.Page.addScriptToEvaluateOnNewDocument(source=source)

    def add_blocked_requests(self, urls: list[str]) -> bool:
        """Block unwanted requests.

        Args:
            urls: URL patterns to block. Wildcards ('*') are allowed.

        Returns:
            `True` on success, `False` on failure.
        """
        try:
            self._chrome_tab.Network.setBlockedURLs(urls=urls)
            return True
        except pychrome.CallMethodException:
            # Oops! Looks like an old browser, pass
            return False

    def execute_script(self, expression: str) -> Any:
        """Execute script.

        Args:
            expression: Text of the expression.

        Returns:
            Result value.
        """
        eval_result = self._chrome_tab.Runtime.evaluate(expression=expression,
                                                        returnByValue=True)
        return eval_result['result'].get('value', None)

    def perform_click(self, dom_node: DOMNode) -> None:
        """Perform mouse click on DOM node.

        Args:
            dom_node: DOMNode element.
        """
        resolved_node = self._chrome_tab.DOM.resolveNode(backendNodeId=dom_node.backend_id)
        object_id = resolved_node['object']['objectId']
        self._chrome_tab.Runtime.callFunctionOn(objectId=object_id, functionDeclaration='''
            (function() { this.scrollIntoView({ block: "center",  behavior: "instant" }); this.click(); })
        ''')

    def wait(self, timeout: float | None = None) -> None:
        """Idle for `timeout` seconds."""
        self._chrome_tab.wait(timeout)

    def stop(self) -> None:
        """Close browser, dissconnect interface."""
        # Close tab and browser
        if self._chrome_tab:
            try:
                self._chrome_tab.stop()
                self._chrome_interface.close_tab(self._chrome_tab)
            except (pychrome.RuntimeException, RequestException):
                pass

        if self._chrome_browser:
            self._chrome_browser.close()

        self.clear_requests()
        self._response_queues = {}

    def __enter__(self) -> ChromeRemote:
        self.start()
        return self

    def __exit__(self, *exc_info) -> None:
        self.stop()

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return f'{classname}(options={self._chrome_options!r}, response_patterns={self._response_patterns!r})'
