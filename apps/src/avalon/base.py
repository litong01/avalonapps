#!/usr/bin/python
import asyncio
import logging
from hfc.fabric.peer import create_peer
from hfc.fabric.client import Client

logger = logging.getLogger(__name__)

async def get_stream_result(stream):
    res = []
    async for v in stream:
        logger.debug('Responses of send_transaction:\n {}'.format(v))
        res.append(v)
    return res

class ClientBase:
    def __init__(self, profile, channel_name, org_name, peer_name, user_name):
        self.client = Client(profile)
        self._channel_name = channel_name
        self._org_name = org_name
        self._peer_name = peer_name
        self._user_name = user_name

        self._user = self.client.get_user(self._org_name, self._user_name)
        endpoint = self.client.get_net_info('peers', self._peer_name, 'url')
        tlscert = self.client.get_net_info('peers', self._peer_name, 'tlsCACerts', 'path')
        loop = asyncio.get_event_loop()

        peer = create_peer(endpoint=endpoint, tls_cacerts=tlscert)

        loop.run_until_complete(self.client.init_with_discovery(
            self._user, peer, self._channel_name))        

        self._channel = self.client.new_channel(self._channel_name)

    @property
    def channel_name(self):
        return self._channel_name

    @property
    def channel(self):
        return self._channel

    @property
    def org_name(self):
        return self._org_name

    @property
    def peer_name(self):
        return self._peer_name

    @property
    def user_name(self):
        return self._user_name

    @property
    def user(self):
        return self._user
