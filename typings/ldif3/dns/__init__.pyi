from typing import Any

import dns.asyncbackend
import dns.name
import dns.rdataclass
import dns.rdatatype
import dns.resolver

"""Asynchronous DNS stub resolver."""
_udp = ...
_tcp = ...

class Resolver(dns.resolver.BaseResolver):
    async def resolve(
        self,
        qname: dns.name.Name | str,
        rdtype: dns.rdatatype.RdataType | str = ...,
        rdclass: dns.rdataclass.RdataClass | str = ...,
        tcp: bool = ...,
        source: str | None = ...,
        raise_on_no_answer: bool = ...,
        source_port: int = ...,
        lifetime: float | None = ...,
        search: bool | None = ...,
        backend: dns.asyncbackend.Backend | None = ...,
    ) -> dns.resolver.Answer: ...
    async def resolve_address(
        self, ipaddr: str, *args: Any, **kwargs: Any
    ) -> dns.resolver.Answer: ...
    async def resolve_name(
        self, name: dns.name.Name | str, family: int = ..., **kwargs: Any
    ) -> dns.resolver.HostAnswers: ...
    async def canonical_name(self, name: dns.name.Name | str) -> dns.name.Name: ...
    async def try_ddr(self, lifetime: float = ...) -> None: ...

default_resolver = ...

def get_default_resolver() -> Resolver: ...
def reset_default_resolver() -> None: ...
async def resolve(
    qname: dns.name.Name | str,
    rdtype: dns.rdatatype.RdataType | str = ...,
    rdclass: dns.rdataclass.RdataClass | str = ...,
    tcp: bool = ...,
    source: str | None = ...,
    raise_on_no_answer: bool = ...,
    source_port: int = ...,
    lifetime: float | None = ...,
    search: bool | None = ...,
    backend: dns.asyncbackend.Backend | None = ...,
) -> dns.resolver.Answer: ...
async def resolve_address(
    ipaddr: str, *args: Any, **kwargs: Any
) -> dns.resolver.Answer: ...
async def resolve_name(
    name: dns.name.Name | str, family: int = ..., **kwargs: Any
) -> dns.resolver.HostAnswers: ...
async def canonical_name(name: dns.name.Name | str) -> dns.name.Name: ...
async def try_ddr(timeout: float = ...) -> None: ...
async def zone_for_name(
    name: dns.name.Name | str,
    rdclass: dns.rdataclass.RdataClass = ...,
    tcp: bool = ...,
    resolver: Resolver | None = ...,
    backend: dns.asyncbackend.Backend | None = ...,
) -> dns.name.Name: ...
async def make_resolver_at(
    where: dns.name.Name | str,
    port: int = ...,
    family: int = ...,
    resolver: Resolver | None = ...,
) -> Resolver: ...
async def resolve_at(
    where: dns.name.Name | str,
    qname: dns.name.Name | str,
    rdtype: dns.rdatatype.RdataType | str = ...,
    rdclass: dns.rdataclass.RdataClass | str = ...,
    tcp: bool = ...,
    source: str | None = ...,
    raise_on_no_answer: bool = ...,
    source_port: int = ...,
    lifetime: float | None = ...,
    search: bool | None = ...,
    backend: dns.asyncbackend.Backend | None = ...,
    port: int = ...,
    family: int = ...,
    resolver: Resolver | None = ...,
) -> dns.resolver.Answer: ...
