from web3 import Web3
from dotenv import load_dotenv
import os
import json
import datetime
from decimal import Decimal
import sys
# from blockchain.abi import router_abi_json,erc20_token_abi_json

# Load environment variables from .env file
load_dotenv()

# Get environment variables
wallet_address = os.getenv('WALLET_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')
router_abi_json = os.getenv('ROUTER_ABI_JSON')
erc20_token_abi_json = os.getenv('ERC20_TOKEN_ABI_JSON')

# Connect to the BSC testnet
web3 = Web3(Web3.HTTPProvider('https://data-seed-prebsc-1-s1.binance.org:8545/'))

# Check if connected
if not web3.is_connected():
    print("Failed to connect to the blockchain.")
    exit()

print(f"Connected to blockchain, chain id is {web3.eth.chain_id}. the latest block is {web3.eth.block_number}")

# V2 router contract address and ABI
router_address = '0x9bC24Ea4EfCaFF2f1DDad85aEE5fA2100E21beEe'
router_abi = router_abi_json

print("V2 compatible router at", router_address)
print("Your address is", wallet_address)

# Token details
# erc20_token_address = '0xab1a4d4f1d656d2450692d237fdd6c7f9146e814'
erc20_token_abi = erc20_token_abi_json

# Create contract instance
router = web3.eth.contract(address=router_address, abi=router_abi)

# Call to the read function
try:
    weth_address = router.functions.WETH().call()
    # print("WETH address:", weth_address)
except Exception as e:
    print("Error calling WETH function:", e) 

weth_contract = web3.eth.contract(address=weth_address, abi=erc20_token_abi)

# Fetch the WETH balance
balance_weth_wei = weth_contract.functions.balanceOf(wallet_address).call()
balance_weth_eth = web3.from_wei(balance_weth_wei, 'ether')

weth_symbol= weth_contract.functions.symbol().call()

# Define tokens
tokens = {
    "1": ("AGDL", "0x7eB601804cD8Ac6ED586aE4F67f528Cf81058Ff0"),
    "2": ("ABGL", "0x937F59039A370c67e73D1809CFE8FD996095d16d"),
    # "3": ("BUSD", "0xab1a4d4f1d656d2450692d237fdd6c7f9146e814"),
}

def get_user_token_choice(tokens):
    print(f"Select one of the following token to swap with {weth_symbol}:")
    for key, value in tokens.items():
        print(f"{key}. {value[0]} ({value[1]})")

    choice = input("Enter the number of your choice: ")

    while choice not in tokens:
        print("Invalid choice. Please choose again.")
        choice = input("Enter the number of your choice: ")

    return tokens[choice]

selectedToken= get_user_token_choice(tokens)
erc20_token_address = selectedToken[1]

# Create contract instance for the ERC20 token
erc20_token_contract = web3.eth.contract(address=erc20_token_address, abi=erc20_token_abi)
erc20_token_symbol = erc20_token_contract.functions.symbol().call()

# Fetch balance of ERC20 token
balance_erc20_wei = erc20_token_contract.functions.balanceOf(wallet_address).call()
balance_erc20_eth = web3.from_wei(balance_erc20_wei, 'ether')

print("Selected ERC20 token:", erc20_token_address + " " + erc20_token_symbol)

print(f"You have {balance_weth_eth} {weth_symbol}")

print(f"You have {balance_erc20_eth} {erc20_token_symbol}")

user_input = input(f"How many {weth_symbol} tokens you wish to swap to {erc20_token_symbol}? ")

float_value = float(user_input)
# print(f"The input {weth_symbol} amount is: {float_value} {weth_symbol}")

# Amount of input token to swap (in Wei)
amount_in_wei = web3.to_wei(Decimal(float_value), 'ether')

# Fetch the current exchange rate and calculate the minimum amount of tokens to accept (for slippage tolerance)
try:
    path = [web3.to_checksum_address(weth_address), web3.to_checksum_address(erc20_token_address)]
    amounts_out = router.functions.getAmountsOut(amount_in_wei, path).call()
    amounts_out_in_eth=web3.from_wei(amounts_out[1], 'ether')
    output_token_amount = amounts_out_in_eth
    # print(f"Output {erc20_token_symbol} amount is :", amount_out_min)
except Exception as e:
    print("Error calling getAmountsOut function:", e)

# Prompt the user to confirm the swap amount
confirm = input(f"Confirm swap amount {float_value} {weth_symbol} to {output_token_amount} {erc20_token_symbol}(y/n)? ")

# Check if the user confirmed the swap
if confirm.lower().startswith("y"):
    print(f"Confirmed! Swapping {float_value} {weth_symbol} to {output_token_amount} {erc20_token_symbol}")
else:
    print("Swap aborted")
    sys.exit()



# print("Amount in:", amount_in_wei)

# Define the transaction parameters
# transaction = {
#     'from': wallet_address,
#     'value': amount_in_wei,
#     'gas': 2000000,
#     'gasPrice': web3.to_wei('5', 'gwei'),
#     'nonce': web3.eth.get_transaction_count(wallet_address)
# }
# print("Transaction:", transaction)

# Set the slippage tolerance and deadline for the transaction
slippage_tolerance = 0.5  # 0.5%

try:
    # Retrieve the current time
    now = datetime.datetime.now()
    current_time_str = now.strftime("%H:%M:%S.%f")
    # print(f"Current time: {current_time_str}")

    # Calculate the deadline (10 minutes from now)
    deadline_timestamp = now + datetime.timedelta(minutes=10)
    deadline = int(deadline_timestamp.timestamp())
    # print(f"Deadline (10 minutes from now): {deadline} (timestamp)")

except Exception as e:
    print(f"Error getting latest time: {e}")

# Call to the read function
try:
    weth_address = router.functions.WETH().call()
    # print("WETH address:", weth_address)
except Exception as e:
    print("Error calling WETH function:", e)    

# try:
#     # Get WETH balance
#     weth_balance = weth_address.functions.balanceOf(wallet_address).call()
#     weth_balance_ether = web3.fromWei(weth_balance, 'ether')
#     print(f"Native Token Balance: {weth_balance_ether} WETH")

#     # Get ERC20 token balance
#     erc20_balance = erc20_contract.functions.balanceOf(wallet_address).call()
#     # Assuming the ERC20 token has 18 decimals (most ERC20 tokens do)
#     erc20_balance_ether = web3.fromWei(erc20_balance, 'ether')
#     print(f"ERC20 Token Balance: {erc20_balance_ether} Tokens")



amounts_out_in_wei = web3.to_wei(Decimal(output_token_amount), 'ether')

# Adjust for slippage tolerance
amount_into_wei = int(amounts_out_in_wei * (1 - slippage_tolerance / 100))
amount_out=web3.to_wei(amount_into_wei, 'ether')

# Build the transaction
try:
    txn = router.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
    amounts_out_in_wei,
    path,
    wallet_address,
    deadline
).build_transaction({
    'value': amount_in_wei,
    'from': wallet_address,
    'gas': 2000000,
    'gasPrice': web3.to_wei('5', 'gwei'),
    'nonce': web3.eth.get_transaction_count(wallet_address)
})
    # Sign the transaction
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)

    # Send the transaction
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

    # Wait for the transaction to be mined
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    print(f'Transaction successful with hash: {tx_hash.hex()}')
except Exception as e:
    print("Error during the transaction process:", e)
