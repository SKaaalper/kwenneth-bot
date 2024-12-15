from web3 import Web3
import time

# Wallet and Network Configuration
WALLET_ADDRESS = 'YOUR_WALLET_ADDRESS'
PRIVATE_KEY = 'YOUR_PRIVATE_KEY'
RPC_URL = 'https://bsc-dataseed1.binance.org/'  # Binance Smart Chain Mainnet
IDO_CONTRACT_ADDRESS = 'IDO_CONTRACT_ADDRESS'  # Replace with actual contract
TOKEN_AMOUNT = 1  # Amount of tokens to purchase (adjust as needed)

# Connect to Binance Smart Chain
web3 = Web3(Web3.HTTPProvider(RPC_URL))
assert web3.isConnected(), "Failed to connect to BSC!"

# Load IDO Smart Contract
IDO_CONTRACT_ABI = [
    # Add the relevant parts of the smart contract ABI here
    # For example, 'buyTokens' function signature
    {
        "inputs": [],
        "name": "buyTokens",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

ido_contract = web3.eth.contract(address=web3.toChecksumAddress(IDO_CONTRACT_ADDRESS), abi=IDO_CONTRACT_ABI)

# Gas Price Configuration
gas_price = web3.toWei('5', 'gwei')  # Adjust gas price as necessary

# Function to Buy Tokens
def buy_tokens():
    try:
        nonce = web3.eth.getTransactionCount(WALLET_ADDRESS)
        tx = ido_contract.functions.buyTokens().buildTransaction({
            'from': WALLET_ADDRESS,
            'value': web3.toWei(TOKEN_AMOUNT, 'ether'),  # Replace with actual token purchase price
            'gas': 200000,  # Adjust gas limit
            'gasPrice': gas_price,
            'nonce': nonce
        })

        # Sign the transaction
        signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)

        # Send the transaction
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(f"Transaction sent! Hash: {web3.toHex(tx_hash)}")

        # Wait for the transaction to be mined
        receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        print(f"Transaction receipt: {receipt}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    print("Starting IDO bot...")
    buy_tokens()
