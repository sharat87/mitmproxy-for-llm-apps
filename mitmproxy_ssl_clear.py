from mitmproxy import command
from mitmproxy.net.tls import create_proxy_server_context


class SSLClear:
    @command.command("ssl.clear")
    def clear(self) -> None:
        create_proxy_server_context.cache_clear()


addons = [SSLClear()]
