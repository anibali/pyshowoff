from concurrent.futures import Future
from threading import Lock


def _then(future: Future, on_fulfilled, on_rejected):
    next_future = Promise()

    def callback(prev_future: Future):
        if prev_future.cancelled() or not prev_future.done():
            next_future.cancel()
            return

        if prev_future.exception() is not None:
            if on_rejected is None:
                next_future.set_exception(prev_future.exception())
            else:
                next_future.set_result(on_rejected(prev_future.exception()))
            return

        try:
            result = prev_future.result()
            if on_fulfilled is not None:
                result = on_fulfilled(result)
                if isinstance(result, Future):
                    result = result.result()
            next_future.set_result(result)
        except BaseException as ex:
            if on_rejected is None:
                next_future.set_exception(ex)
            else:
                next_future.set_result(on_rejected(ex))

    future.add_done_callback(callback)
    return next_future


class Promise(Future):
    @staticmethod
    def resolve(value):
        if isinstance(value, Future):
            return _then(value, None, None)
        promise = Promise()
        promise.set_result(value)
        return promise

    @staticmethod
    def reject(reason):
        promise = Promise()
        promise.set_exception(reason)
        return promise

    @staticmethod
    def all(iterable):
        lock = Lock()
        promise = Promise()
        results = {}
        n = len(iterable)
        def abort(reason):
            with lock:
                promise.set_exception(reason)
        def insert_result(index, result):
            with lock:
                results[index] = result
                if len(results) == n:
                    promise.set_result([results[i] for i in range(n)])
        for i, future in enumerate(iterable):
            Promise.resolve(future).then(lambda v: insert_result(i, v)).catch(abort)
        return promise

    @staticmethod
    def race(iterable):
        lock = Lock()
        promise = Promise()
        def abort(reason):
            with lock:
                if not promise.done():
                    promise.set_exception(reason)
        def resolve(result):
            with lock:
                if not promise.done():
                    promise.set_result(result)
        for future in iterable:
            Promise.resolve(future).then(resolve).catch(abort)
        return promise

    def then(self, on_fulfilled, on_rejected=None):
        return _then(self, on_fulfilled, on_rejected)

    def catch(self, on_rejected):
        return _then(self, None, on_rejected)
