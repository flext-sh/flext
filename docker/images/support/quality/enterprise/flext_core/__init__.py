# Mock flext_core
import logging


class r:
    def __init__(self, success, data=None, error=None):
        self.success = success
        self.is_failure = not success
        self.data = data
        self.error = error

    @classmethod
    def ok(cls, data=None):
        return cls(True, data=data)

    @classmethod
    def fail(cls, error):
        return cls(False, error=error)


def FlextLogger(name):
    return logging.getLogger(name)


class FlextContainer:
    def __init__(self):
        self._services = {}

    def register(self, name, service):
        self._services[name] = service
        return r.ok(None)

    def get(self, name):
        return (
            r.ok(self._services[name])
            if name in self._services
            else r.fail(f"Service {name} not found")
        )
