from web3 import Web3
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Wallet and Network Configuration
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')  # Your wallet address
PRIVATE_KEY = os.getenv('PRIVATE_KEY')        # Your private key
RPC_URL = 'https://arb1.arbitrum.io/rpc'      # Arbitrum RPC URL
IDO_CONTRACT_ADDRESS = os.getenv('IDO_CONTRACT_ADDRESS')  # IDO contract address
USDC_ADDRESS = '0xff970a61a04b1ca14834a43f5de4533ebddb5cc8'  # USDC contract address on Arbitrum

# Token purchase configuration
BUY_AMOUNT_USDC = float(os.getenv('BUY_AMOUNT_USDC', 1))  # Amount of USDC to spend (default 1 USDC)

# Connect to the Arbitrum network
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Check if Web3 is connected
try:
    latest_block = web3.eth.get_block('latest')
    print("Successfully connected to Arbitrum. Latest block:", latest_block['number'])
except Exception as e:
    print("Failed to connect to Arbitrum!")
    print(f"Error: {e}")
    exit(1)

# Load IDO Smart Contract ABI (simplified for purchase)
IDO_CONTRACT_ABI = [
    {
        "inputs": [],
        "name": "purchase",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

# Correct checksum address call
ido_contract_address = Web3.toChecksumAddress(IDO_CONTRACT_ADDRESS)  # Use toChecksumAddress explicitly

ido_contract = web3.eth.contract(address=ido_contract_address, abi=IDO_CONTRACT_ABI)

# USDC contract ABI to interact with the USDC token
USDC_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
]

# Initialize USDC contract
usdc_contract = web3.eth.contract(address=Web3.toChecksumAddress(USDC_ADDRESS), abi=USDC_ABI)

# Gas Price Configuration
gas_price = Web3.toWei('30', 'gwei')  # Adjust gas price as necessary

# Function to Buy Tokens
def buy_tokens():
    try:
        # Convert USDC amount to correct decimal format (USDC uses 6 decimals)
        buy_amount_in_wei = int(BUY_AMOUNT_USDC * 10**6)

        # Check USDC balance before attempting purchase
        usdc_balance = usdc_contract.functions.balanceOf(WALLET_ADDRESS).call()
        print(f"USDC balance: {usdc_balance / 10**6} USDC")

        # Make sure the wallet has enough USDC to buy tokens
        if usdc_balance < buy_amount_in_wei:
            print(f"Not enough USDC to purchase {BUY_AMOUNT_USDC} USDC worth of tokens.")
            return

        # Approve the sale contract to spend USDC on behalf of the wallet
        approve_tx = usdc_contract.functions.approve(IDO_CONTRACT_ADDRESS, buy_amount_in_wei).buildTransaction({
            'from': WALLET_ADDRESS,
            'gas': 100000,
            'gasPrice': gas_price,
            'nonce': web3.eth.getTransactionCount(WALLET_ADDRESS),
        })
        signed_approve_tx = web3.eth.account.sign_transaction(approve_tx, PRIVATE_KEY)
        tx_hash = web3.eth.sendRawTransaction(signed_approve_tx.rawTransaction)
        print(f"Approval transaction sent! Hash: {web3.toHex(tx_hash)}")

        # Wait for the approval to be mined
        web3.eth.waitForTransactionReceipt(tx_hash)

        # Purchase tokens using the approved USDC
        purchase_tx = ido_contract.functions.purchase().buildTransaction({
            'from': WALLET_ADDRESS,
            'gas': 200000,
            'gasPrice': gas_price,
            'nonce': web3.eth.getTransactionCount(WALLET_ADDRESS) + 1,  # Ensure unique nonce
            'value': 0  # Assuming the function does not require ETH payment
        })

        # Sign the purchase transaction
        signed_purchase_tx = web3.eth.account.sign_transaction(purchase_tx, PRIVATE_KEY)

        # Send the transaction
        tx_hash = web3.eth.sendRawTransaction(signed_purchase_tx.rawTransaction)
        print(f"Purchase transaction sent! Hash: {web3.toHex(tx_hash)}")

        # Wait for the transaction to be mined
        receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        print(f"Purchase receipt: {receipt}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    print("Starting IDO bot on Arbitrum with USDC...")
    buy_tokens()

