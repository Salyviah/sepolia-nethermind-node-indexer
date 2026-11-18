from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
CONTRACT = Web3.to_checksum_address("0x99b6ae6Dd99C2937F6cE207767311c243d5fDA23")
TOPIC = w3.keccak(text="Transfer(address,address,uint256)").hex()
ZERO = "0x0000000000000000000000000000000000000000"

latest = w3.eth.block_number
print(f"Connected to Nethermind (Latest Sepolia Block: {latest})")
logs = w3.eth.get_logs({"fromBlock": max(0, latest - 3000), "toBlock": latest, "address": CONTRACT, "topics": [TOPIC]})

for l in logs:
    s = Web3.to_checksum_address("0x" + l["topics"][1].hex()[-40:])
    r = Web3.to_checksum_address("0x" + l["topics"][2].hex()[-40:])
    tid = int(l["topics"][3].hex(), 16)
    print(f"[Block {l['blockNumber']}] {'MINT' if s == ZERO else 'TRANSFER'} | Token #{tid} | {s} -> {r}")
