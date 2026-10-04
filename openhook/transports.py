"""Own inbound SMTP and authoritative DNS listeners. Neither relays traffic."""

from __future__ import annotations

import asyncio
import logging
import struct
from email import policy
from email.parser import BytesParser
from uuid import UUID

from aiosmtpd.controller import Controller
from dnslib import A, DNSRecord, NS, QTYPE, RCODE, RR, SOA

from openhook.store import InboxError, Store

logger = logging.getLogger(__name__)


class MailReceiver:
    def __init__(self, store: Store):
        self.store = store

    def identifier(self, address: str) -> str:
        local, _, domain = address.rpartition("@")
        if domain.lower() != self.store.settings.email_domain:
            raise InboxError("Mail relay is disabled.")
        identifier = str(UUID(local))
        self.store.public_info(identifier)
        return identifier

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        if len(envelope.rcpt_tos) >= 10:
            return "452 Too many recipients"
        try:
            self.identifier(address)
        except (InboxError, ValueError):
            return "550 No such inbox; relay disabled"
        envelope.rcpt_tos.append(address)
        return "250 Accepted"

    async def handle_DATA(self, server, session, envelope):
        raw = envelope.original_content
        message = BytesParser(policy=policy.default).parsebytes(raw)
        text = []
        for part in message.walk():
            if part.get_content_type() == "text/plain" and part.get_content_disposition() != "attachment":
                try:
                    text.append(part.get_content())
                except (LookupError, UnicodeError):
                    text.append((part.get_payload(decode=True) or b"").decode(errors="replace"))
        headers = {}
        for name, value in message.items():
            headers.setdefault(name.lower(), []).append(str(value))
        try:
            for address in set(envelope.rcpt_tos):
                identifier = self.identifier(address)
                self.store.capture(identifier, raw, kind="email", method="SMTP", headers=headers,
                                   ip=str(session.peer[0]), url=f"mailto:{address}",
                                   extra={"text_content": "\n".join(text), "sender": envelope.mail_from,
                                          "recipient": address, "subject": str(message.get("Subject", ""))})
        except InboxError as exc:
            if exc.status == 429:
                return "452 Temporary storage capacity reached"
            return "552 Event too large" if exc.status == 413 else "550 Inbox unavailable"
        return "250 Stored by Openhook"


class DNSReceiver(asyncio.DatagramProtocol):
    def __init__(self, store: Store):
        self.store = store
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def answer(self, data: bytes, peer: str) -> bytes | None:
        if len(data) > 4096:
            return None
        try:
            request = DNSRecord.parse(data)
            if len(request.questions) != 1:
                return None
            reply = request.reply()
            reply.header.ra = 0
            reply.header.aa = 1
            name = str(request.q.qname).lower().rstrip(".")
            domain = self.store.settings.dns_domain
            if not (name == domain or name.endswith("." + domain)):
                reply.header.rcode = RCODE.REFUSED
                return reply.pack()
            if name not in {domain, "ns." + domain}:
                local = name[:-(len(domain) + 1)].split(".")[-1]
                try:
                    identifier = str(UUID(local))
                    self.store.capture(identifier, data, kind="dns", method=QTYPE[request.q.qtype],
                                       url=name, ip=peer, extra={"query_name": name, "query_type": QTYPE[request.q.qtype]})
                except InboxError as exc:
                    reply.header.rcode = RCODE.SERVFAIL if exc.status == 429 else RCODE.NXDOMAIN
                    return reply.pack()
                except ValueError:
                    reply.header.rcode = RCODE.NXDOMAIN
                    return reply.pack()
            nameserver = "ns." + domain
            if request.q.qtype == QTYPE.A:
                reply.add_answer(RR(request.q.qname, QTYPE.A, ttl=0, rdata=A(self.store.settings.dns_address)))
            elif request.q.qtype == QTYPE.NS and name == domain:
                reply.add_answer(RR(domain, QTYPE.NS, ttl=300, rdata=NS(nameserver)))
            elif request.q.qtype == QTYPE.SOA:
                reply.add_answer(RR(domain, QTYPE.SOA, ttl=300,
                                    rdata=SOA(nameserver, "hostmaster." + domain, (1, 300, 60, 86400, 0))))
            return reply.pack()
        except Exception:
            logger.debug("Ignored malformed DNS datagram", exc_info=True)
            return None

    def datagram_received(self, data, addr):
        reply = self.answer(data, addr[0])
        if reply is not None:
            self.transport.sendto(reply, addr)

    async def handle_tcp(self, reader, writer):
        try:
            while True:
                size = struct.unpack("!H", await asyncio.wait_for(reader.readexactly(2), 5))[0]
                if size > 4096:
                    break
                data = await asyncio.wait_for(reader.readexactly(size), 5)
                reply = self.answer(data, writer.get_extra_info("peername")[0])
                if reply:
                    writer.write(struct.pack("!H", len(reply)) + reply)
                    await writer.drain()
        except (asyncio.IncompleteReadError, TimeoutError, ConnectionError):
            pass
        finally:
            writer.close()
            await writer.wait_closed()


class CaptureTransports:
    def __init__(self, store: Store):
        self.store = store
        self.smtp = None
        self.udp = None
        self.tcp = None

    async def start(self):
        settings = self.store.settings
        try:
            if settings.email_domain:
                self.smtp = Controller(MailReceiver(self.store), hostname="0.0.0.0", port=settings.smtp_port,
                                       data_size_limit=settings.body_limit, decode_data=False,
                                       timeout=30, auth_require_tls=True, server_hostname=settings.email_domain,
                                       ident="Openhook")
                self.smtp.start()
            if settings.dns_domain:
                receiver = DNSReceiver(self.store)
                self.udp, _ = await asyncio.get_running_loop().create_datagram_endpoint(
                    lambda: receiver, local_addr=("0.0.0.0", settings.dns_port))
                self.tcp = await asyncio.start_server(receiver.handle_tcp, "0.0.0.0", settings.dns_port, limit=8192)
        except BaseException:
            await self.stop()
            raise

    async def stop(self):
        if self.smtp:
            self.smtp.stop()
        if self.udp:
            self.udp.close()
        if self.tcp:
            self.tcp.close()
            await self.tcp.wait_closed()
