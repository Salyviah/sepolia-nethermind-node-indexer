import json
import time
import urllib.request

RPC_URL = "http://localhost:8545"
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


def rpc_call(method: str, params: list):
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }).encode("utf-8")

    req = urllib.request.Request(
        RPC_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    latency_ms = (time.perf_counter() - start) * 1000
    return data["result"], latency_ms


def decode_address(topic_hex: str) -> str:
    return "0x" + topic_hex[-40:]


def main():
    print(f"Connecting to local Nethermind node at {RPC_URL}...\n")
    client_version, _ = rpc_call("web3_clientVersion", [])
    peer_hex, _ = rpc_call("net_peerCount", [])
    print(f"Client : {client_version}")
    print(f"Peers  : {int(peer_hex, 16)} active peers")
    print("-" * 72)

    last_seen_block = None

    while True:
        try:
            latest_hex, _ = rpc_call("eth_blockNumber", [])
            latest_num = int(latest_hex, 16)

            if last_seen_block is None or latest_num > last_seen_block:
                block, _ = rpc_call("eth_getBlockByNumber", [latest_hex, False])
                logs, logs_lat = rpc_call("eth_getLogs", [{
                    "fromBlock": latest_hex,
                    "toBlock": latest_hex,
                    "topics": [TRANSFER_TOPIC]
                }])

                tx_count = len(block["transactions"])
                gas_used = int(block["gasUsed"], 16)

                print(
                    f"[Block #{latest_num}] Txs: {tx_count:<3} | "
                    f"Gas: {gas_used:<10,} | "
                    f"Transfers: {len(logs):<3} | "
                    f"eth_getLogs: {logs_lat:.2f} ms"
                )

                for log in logs[:3]:
                    if len(log["topics"]) >= 3:
                        sender = decode_address(log["topics"])
                        recipient = decode_address(log["topics"])
                        amount = int(log["data"], 16) if log["data"] != "0x" else 0
                        print(
                            f"   └─ Token {log['address'][:10]}... | "
                            f"{sender[:8]}... -> {recipient[:8]}... | "
                            f"Raw Amount: {amount}"
                        )

                last_seen_block = latest_num

            time.sleep(3)
        except KeyboardInterrupt:
            print("\nStopped stream.")
            break
        except Exception as err:
            print(f"RPC warning: {err}")
            time.sleep(5)


if __name__ == "__main__":
    main()
