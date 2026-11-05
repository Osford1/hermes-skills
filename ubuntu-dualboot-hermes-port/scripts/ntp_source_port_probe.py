"""NTP source-port probe: does this network accept NTP sent FROM UDP source port 123?

w32time always sends its requests from source port 123. Some ISP / campus / router
NAT filters drop port-123-to-port-123 traffic (NTP amplification prevention), which
makes every Windows resync fail with "no time data was available" while every other
NTP client on the same machine works fine. This probe proves which case you are in.

Run elevated with the Windows Time service stopped, so port 123 is free:

    net stop w32time
    python ntp_source_port_probe.py
    net start w32time

Verdict: source port 123 timeouts + ephemeral source OK = network filter. Stop
configuring w32time; correct the clock directly instead (Set-Date -Adjust).
"""
import socket
import struct
import time

SERVERS = ["ntp.aliyun.com", "ntp.tencent.com", "cn.pool.ntp.org", "203.107.6.88"]
PORT = 123


def resolve(host):
    try:
        return socket.gethostbyname(host)
    except OSError:
        return None


def probe(host, bind_port, timeout=6):
    addr = resolve(host)
    label = "source port %-4s" % (bind_port or "eph")
    if addr is None:
        print("%s -> %-18s DNS FAIL" % (label, host))
        return
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        if bind_port:
            try:
                s.bind(("", bind_port))
            except OSError as e:
                print("%s -> %-18s cannot bind port %d (%s) - stop w32time first"
                      % (label, addr, bind_port, e.errno))
                return
        s.settimeout(timeout)
        sent = time.time()
        s.sendto(b"\x1b" + 47 * b"\0", (addr, PORT))
        data, _ = s.recvfrom(1024)
        rtt = time.time() - sent
        if len(data) < 48:
            print("%s -> %-18s short reply (%d bytes)" % (label, addr, len(data)))
            return
        server_utc = struct.unpack("!12I", data)[10] - 2208988800
        print("%s -> %-18s OK   server_utc=%s  rtt=%.3fs  local offset=%+.2fs"
              % (label, addr,
                 time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(server_utc)),
                 rtt, sent - server_utc))
    except OSError as e:
        print("%s -> %-18s FAIL %s: %s" % (label, addr, type(e).__name__, e))
    finally:
        s.close()


if __name__ == "__main__":
    print("=== from UDP source port 123 (what w32time uses) ===")
    for h in SERVERS:
        probe(h, PORT)
    print("\n=== from an ephemeral port (control: any other NTP client) ===")
    for h in SERVERS:
        probe(h, None)
    print("\nIf the first block times out and the second succeeds, the network drops"
          " source-port-123 NTP: w32time cannot sync here, however it is configured.")
