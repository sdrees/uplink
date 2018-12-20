# Third-party imports
import time

# Local models
from uplink.clients.io import interfaces

__all__ = ["DefaultStrategy"]


class DefaultStrategy(interfaces.ExecutionStrategy):
    """A blocking execution strategy."""

    def send(self, client, request, callback):
        try:
            response = client.send(request)
        except Exception as error:
            # TODO: retrieve traceback
            callback.on_failure(type(error), error, None)
        else:
            callback.on_success(response)

    def sleep(self, duration, callback):
        time.sleep(duration)
        callback.on_success()

    def finish(self, response):
        return response

    def execute(self, executable):
        return executable.execute()
