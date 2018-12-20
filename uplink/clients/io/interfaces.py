# Standard library imports
import collections


class IllegalRequestStateTransition(RuntimeError):
    """An improper request state transition was attempted."""

    def __init__(self, state, transition):
        self._state = state
        self._transition = transition

    def __str__(self):
        return (
            "Illegal transition [%s] from request state [%s]: this is "
            "possibly due to a badly designed RequestTemplate."
            % (self._transition, self._state)
        )


class SendCallback(object):
    """
    Callbacks to continue the running request execution after sending
    the request.
    """

    def on_success(self, response):
        """
        Handles a successful request.

        Args:
            response: The server's response.
        """
        raise NotImplementedError

    def on_failure(self, exc_type, exc_val, exc_tb):
        """
        Handles a failed request.

        Args:
            exc_type: The exception class.
            exc_val: The exception object.
            exc_tb: The exception's stacktrace.
        """
        raise NotImplementedError


class SleepCallback(object):
    """
    Callbacks to continue the running request execution after an
    intended pause.
    """

    def on_success(self):
        """Handles a successful pause."""
        raise NotImplementedError

    def on_failure(self, exc_type, exc_val, exc_tb):
        """
        Handles a failed pause.

        Args:
            exc_type: The exception class.
            exc_val: The exception object.
            exc_tb: The exception's stacktrace.
        """
        raise NotImplementedError


class Executable(collections.Iterator):
    """An abstraction for iterating over the execution of a request."""

    def __next__(self):
        return self.execute()

    def execute(self):
        """Start or continue the request's execution."""
        raise NotImplementedError


class ExecutionContext(Executable):
    """A state machine representing the execution lifecycle of a request."""

    @property
    def state(self):
        """The current state of the request."""
        raise NotImplementedError

    def send(self, request, callback):
        """
        Sends the given request.

        Args:
            request: The intended request data to be sent.
            callback (SendCallback): A callback that resumes execution
                after the request is sent.
        """
        raise NotImplementedError

    def sleep(self, duration, callback):
        """
        Pauses the execution for the allotted duration.

        Args:
            duration: The number of seconds to delay execution.
            callback (:obj:`SleepCallback`): A callback that resumes
                execution after the delay.
        """
        raise NotImplementedError

    def finish(self, response):
        """
        Completes the execution.

        Args:
            response: The object to return to the execution's invoker.
        """
        raise NotImplementedError

    def fail(self, exc_type, exc_val, exc_tb):
        """
        Fails the execution with a specific error.

        Args:
            exc_type: The exception class.
            exc_val: The exception object.
            exc_tb: The exception's stacktrace.
        """
        raise NotImplementedError

    def execute(self):
        """Performs the next sequence of steps in the execution."""
        raise NotImplementedError

    def before_request(self, request):
        """Handles transitioning the execution before the request is sent."""
        raise NotImplementedError

    def after_response(self, request, response):
        """Handles transitioning the execution after a successful request."""
        raise NotImplementedError

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        """Handles transitioning the execution after a failed request."""
        raise NotImplementedError


class RequestState(object):
    @property
    def request(self):
        raise NotImplementedError

    def send(self, request):
        raise IllegalRequestStateTransition(self, "send")

    def prepare(self, request):
        raise IllegalRequestStateTransition(self, "prepare")

    def sleep(self, duration):
        raise IllegalRequestStateTransition(self, "sleep")

    def finish(self, response):
        raise IllegalRequestStateTransition(self, "finish")

    def fail(self, exc_type, exc_val, exc_tb):
        raise IllegalRequestStateTransition(self, "fail")

    def execute(self, context):
        raise NotImplementedError


class RequestTemplate(object):
    """
    Hooks for managing the lifecycle of a request.

    To modify behavior of a specific part of the request, override the
    appropriate hook and return the intended transition from
    :mod:`uplink.clients.io.transitions`.

    To fallback to the default behavior, either don't override the hook
    or return :obj:`None` instead, in case of conditional overrides
    (e.g., retry the request if it has failed less than a certain number
    of times).
    """

    def before_request(self, request):
        """
        Handles the request before it is sent.

        Args:
            request: The prospective request data.

        Returns:
            ``None`` or a transition from
            :mod:`uplink.clients.io.transitions`.
        """

    def after_response(self, request, response):
        """
        Handles the response after a successful request.

        Args:
            request: The data sent to the server.
            response: The response returned by server.

        Returns:
            ``None`` or a transition from
            :mod:`uplink.clients.io.transitions`.
        """

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        """
        Handles the error after a failed request.

        Args:
            request: The attempted request.
            exc_type: The exception class.
            exc_val: The exception object.
            exc_tb: The exception's stacktrace.

        Returns:
            ``None`` or a transition from
            :mod:`uplink.clients.io.transitions`.
        """


class Client(object):
    """An HTTP Client implementation."""

    def send(self, request):
        """
        Sends the given request.

        Args:
            request: The intended request data to be sent.
        """


class ExecutionStrategy(object):
    """An adapter for a specific I/O model."""

    def send(self, client, request, callback):
        """
        Sends the given request using the provided client.

        Args:
            client (Client): An HTTP client that should abide by the
                I/O framework of this strategy.
            request: The intended request data to be sent.
            callback (:obj:`SendCallback`): A callback that resumes
                execution after the request is sent.
        """
        raise NotImplementedError

    def sleep(self, duration, callback):
        """
        Pauses the execution for the allotted duration.

        Args:
            duration: The number of seconds to delay execution.
            callback (:obj:`SleepCallback`): A callback that resumes
                execution after the delay.
        """
        raise NotImplementedError

    def finish(self, response):
        """
        Completes the execution.

        Args:
            response: The object to return to the execution's invoker.
        """
        raise NotImplementedError

    def fail(self, exc_type, exc_val, exc_tb):
        """
        Fails the execution with a specific error.

        Args:
            exc_type: The exception class.
            exc_val: The exception object.
            exc_tb: The exception's stacktrace.
        """
        # TODO: Reraise properly
        raise exc_val

    def execute(self, executable):
        """
        Runs a request's execution to completion using the I/O framework
        of this strategy.
        """
        raise NotImplementedError
