from web3 import Web3
from dotenv import load_dotenv
import os
import json
import datetime
from decimal import Decimal
import sys

# Load environment variables from .env file
load_dotenv()

# Get environment variables
wallet_address = os.getenv('WALLET_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')
router_abi_json = os.getenv('ROUTER_ABI_JSON')
erc20_token_abi_json = os.getenv('ERC20_TOKEN_ABI_JSON')

# Connect to the BSC testnet
web3 = Web3(Web3.HTTPProvider('https://1rpc.io/sepolia'))

# Check if connected
if not web3.is_connected():
    print("Failed to connect to the blockchain.")
    exit()

print(f"Connected to blockchain, chain id is {web3.eth.chain_id}. The latest block is {web3.eth.block_number}")

# Define native currency symbols for different chains
native_symbols = {
    1: "ETH",    # Ethereum Mainnet
    3: "ETH",    # Ropsten Testnet
    4: "ETH",    # Rinkeby Testnet
    5: "ETH",    # Goerli Testnet
    42: "ETH",   # Kovan Testnet
    56: "BNB",   # Binance Smart Chain Mainnet
    97: "BNB",   # Binance Smart Chain Testnet
    137: "MATIC", # Polygon Mainnet
    80001: "MATIC", # Polygon Mumbai Testnet
    43114: "AVAX", # Avalanche C-Chain Mainnet
    43113: "AVAX"  # Avalanche Fuji Testnet
}

# Get native currency symbol
eth_symbol = native_symbols.get(web3.eth.chain_id, "ETH")
print(f"Native token symbol: {eth_symbol}")

# V2 router contract address and ABI
router_address = '0xC532a74256D3Db42D0Bf7a0400fEFDbad7694008'
router_abi = json.loads(router_abi_json)

print("V2 compatible router at", router_address)
print("Your address is", wallet_address)

# Erc20 Token ABI
erc20_token_abi = json.loads(erc20_token_abi_json)

# Create router contract instance
router = web3.eth.contract(address=router_address, abi=router_abi)

# Call to the read function
try:
    native_token_address = router.functions.WETH().call()
    print("Weth token address:", native_token_address)
except Exception as e:
    print("Error calling WETH function:", e)
    sys.exit()

# Create contract instance for the native token & fetch native token details
native_token_contract = web3.eth.contract(address=native_token_address, abi=erc20_token_abi)
native_token_symbol = native_token_contract.functions.symbol().call()
native_token_decimal = native_token_contract.functions.decimals().call()

# Fetch the native token balance
native_token_wei_balance = native_token_contract.functions.balanceOf(wallet_address).call()
native_token_formated_balance = native_token_wei_balance * 10**-native_token_decimal

# Fetch balance of Eth
eth_balance_wei = web3.eth.get_balance(wallet_address)
eth_balance = web3.from_wei(eth_balance_wei, 'ether')

# Define tokens
tokens = {
    "1": ("Blockgal", "0xa8e3C7fE1085C4A78EC28d7dc4E6FE86e45Dec65"),
    "2": ("Gadol", "0x4DF72Fc4365b3302eB6CE4F6a9ad6B90c0F260a9"),
    "3": ("DOGE R", "0x56FFd26bfa5126abA724e33252cB55dB110B60Fa"),
}

# Define function to get user selected token
def get_user_token_choice(tokens):
    print(f"Select one of the following token to swap with {native_token_symbol}:")
    for key, value in tokens.items():
        print(f"{key}. {value[0]} ({value[1]})")

    choice = input("Enter the number of your choice: ")

    while choice not in tokens:
        print("Invalid choice. Please choose again.")
        choice = input("Enter the number of your choice: ")

    return tokens[choice]

selectedToken = get_user_token_choice(tokens)
erc20_token_address = selectedToken[1]

# Create contract instance for the ERC20 token
erc20_token_contract = web3.eth.contract(address=erc20_token_address, abi=erc20_token_abi)
erc20_token_symbol = erc20_token_contract.functions.symbol().call()
erc20_token_decimal = erc20_token_contract.functions.decimals().call()

# Fetch balance of ERC20 token
erc20_token_wei_balance = erc20_token_contract.functions.balanceOf(wallet_address).call()
erc20_token_formated_balance = erc20_token_wei_balance * 10**-erc20_token_decimal

print("Selected ERC20 token:", erc20_token_address + " " + erc20_token_symbol)
print(f"You have {eth_balance} ETH")
print(f"You have {erc20_token_formated_balance} {erc20_token_symbol}")

# Prompt the user to enter the amount of native token to swap
user_input = input(f"How many ETH tokens you wish to swap to {erc20_token_symbol}? ")

float_value = float(user_input)
user_input_amount_in_wei = web3.to_wei(float_value, 'ether')

# Check wallet ETH balance
wallet_balance_wei = web3.eth.get_balance(wallet_address)
wallet_balance_eth = web3.from_wei(wallet_balance_wei, 'ether')
print(f"Wallet balance: {wallet_balance_eth} {eth_symbol}")

if wallet_balance_wei < user_input_amount_in_wei:
    print("Insufficient funds to cover the swap amount.")
    sys.exit()

# Fetch the current exchange rate and calculate the minimum amount of tokens to accept (for slippage tolerance)
try:
    path = [web3.to_checksum_address(native_token_address), web3.to_checksum_address(erc20_token_address)]
    amounts_out = router.functions.getAmountsOut(user_input_amount_in_wei, path).call()
    amounts_out_in_eth = web3.from_wei(amounts_out[1], 'ether')
    erc20_token_amount_out_in_wei = amounts_out[1]
    output_token_amount = amounts_out_in_eth
except Exception as e:
    print("Error calling getAmountsOut function:", e)
    sys.exit()

# Retrieve the current time
try:
    deadline = int((datetime.datetime.now() + datetime.timedelta(minutes=10)).timestamp())
except Exception as e:
    print(f"Error getting latest time: {e}")      

# Set the slippage tolerance for the transaction (e.g., 1%)
slippage_tolerance = 10

# Adjust for slippage tolerance
min_tokens_out = int(erc20_token_amount_out_in_wei * (1 - slippage_tolerance / 100))

# Prompt the user to confirm the swap amount
confirm = input(f"Confirm swap amount {float_value} ETH to {output_token_amount} {erc20_token_symbol}(y/n)? ")

# Check if the user confirmed the swap
if confirm.lower().startswith("y"):
    print(f"Confirmed! Swapping {float_value} ETH to {output_token_amount} {erc20_token_symbol}")
else:
    print("Swap aborted")
    sys.exit()

# Estimate gas for the swap transaction
try:
    gas_estimate = router.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
        min_tokens_out,
        path,
        wallet_address,
        deadline
    ).estimate_gas({
        'value': user_input_amount_in_wei,
        'from': wallet_address
    })
except Exception as e:
    print("Error estimating gas:", e)
    sys.exit()

print(f"Estimated gas: {gas_estimate}")

# Ensure enough funds for gas and swap
tx_cost = user_input_amount_in_wei + gas_estimate * web3.to_wei('5', 'gwei')
if wallet_balance_wei < tx_cost:
    print(f"Insufficient funds: required {web3.from_wei(tx_cost, 'ether')} {eth_symbol}, but only {wallet_balance_eth} {eth_symbol} available.")
    sys.exit()

# Build the transaction
try:
    txn = router.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
        min_tokens_out,
        path,
        wallet_address,
        deadline
    ).build_transaction({
        'value': user_input_amount_in_wei,
        'from': wallet_address,
        'gas': gas_estimate,
        'gasPrice': web3.to_wei('5', 'gwei'),
        'nonce': web3.eth.get_transaction_count(wallet_address)
    })
    # Sign the transaction
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    # Send the transaction
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print("Swap transaction hash:", tx_hash.hex())
    # Wait for the transaction to be mined
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    if tx_receipt["status"] == 1:
        print("Swap is successful!")
        print("Transaction receipt:", tx_receipt)
        print("All ok!")
        # Fetch balance of Eth
        eth_balance_wei = web3.eth.get_balance(wallet_address)
        eth_balance = web3.from_wei(eth_balance_wei, 'ether')
        # Fetch balance of ERC20 token
        erc20_token_wei_balance = erc20_token_contract.functions.balanceOf(wallet_address).call()
        erc20_token_formated_balance = erc20_token_wei_balance * 10**-erc20_token_decimal

        print(f"After swap, you have {eth_balance} ETH")
        print(f"After swap, you have {erc20_token_formated_balance} {erc20_token_symbol}")

    if tx_receipt["status"] == 0:
        print("Swap failed!")
        print("Transaction receipt:", tx_receipt)
except Exception as e:
    print("Error during the transaction process:", e)
