from stem.process import launch_tor

print("🔥 Starting Tor... Anonymity engaged.")

tor_process = launch_tor(
    tor_cmd="/usr/bin/tor",
    config={
        "SocksPort": "9050",
        "ControlPort": "9051",
        "HashedControlPassword": "16:87FDC8633B37247F3C703C8643365499781D8E5196E624BF7C0B9645B3",
    },
    init_msg_handler=lambda line: print(line) if "Bootstrapped" in line else None,
)
