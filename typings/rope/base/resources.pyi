from __future__ import annotations


class Resource:
    path: str
    real_path: str

    def read(self) -> str: ...


class File(Resource): ...

