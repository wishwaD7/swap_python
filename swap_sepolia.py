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
web3 = Web3(Web3.HTTPProvider('https://1rpc.io/sepolia'))
# web3 = Web3(Web3.HTTPProvider('https://public.stackup.sh/api/v1/node/bsc-testnet'))

# Check if connected
if not web3.is_connected():
    print("Failed to connect to the blockchain.")
    exit()

print(f"Connected to blockchain, chain id is {web3.eth.chain_id}. the latest block is {web3.eth.block_number}")

# V2 router contract address and ABI
router_address = '0xC532a74256D3Db42D0Bf7a0400fEFDbad7694008'
router_abi = router_abi_json

print("V2 compatible router at", router_address)
print("Your address is", wallet_address)

# Erc20 Token ABI
erc20_token_abi = erc20_token_abi_json

# Create router contract instance
router = web3.eth.contract(address=router_address, abi=router_abi)

# Call to the read function
try:
    native_token_address = router.functions.WETH().call()
    # print("Native token address:", native_token_address)
except Exception as e:
    print("Error calling WETH function:", e) 

# Create contract instance for the native token & fetch native token details
native_token_contract = web3.eth.contract(address=native_token_address, abi=erc20_token_abi)
# print("Native token address:", native_token_address)
native_token_symbol= native_token_contract.functions.symbol().call()
native_token_decimal = native_token_contract.functions.decimals().call()

# Fetch the native token balance
native_token_wei_balance = native_token_contract.functions.balanceOf(wallet_address).call()
native_token_formated_balance = native_token_wei_balance*10**-native_token_decimal
# native_token_formated_balance = web3.from_wei(native_token_wei_balance, 'ether')

# Define tokens
tokens = {
    "1": ("Blockgal", "0xa8e3C7fE1085C4A78EC28d7dc4E6FE86e45Dec65"),
    "2": ("Gadol", "0x4DF72Fc4365b3302eB6CE4F6a9ad6B90c0F260a9"),
    "3": ("DOGE R", "0x56FFd26bfa5126abA724e33252cB55dB110B60Fa"),
}

# Define function to get user selected token
def get_user_token_choice(tokens):
    print(f"Select one of the following token to swap with ETH:")
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
erc20_token_decimal = erc20_token_contract.functions.decimals().call()

# print("ERC20 token details:", erc20_token_address, erc20_token_symbol, erc20_token_decimal)

# Fetch balance of Eth
eth_balance_wei = web3.eth.get_balance(wallet_address)
eth_balance = web3.from_wei(eth_balance_wei, 'ether')

# Add liquidity to the router

# Amount of ERC20 tokens to add to the liquidity pool
# token_amount_to_add = web3.to_wei('500000', 'ether')  # Adjust this value as needed

# ETH amount to add to the liquidity pool
# eth_amount_to_add = web3.to_wei('0.1', 'ether')  # Adjust this value as needed

# Approve the router to spend the ERC20 tokens
# try:
#     approve_txn = erc20_token_contract.functions.approve(router_address, token_amount_to_add).build_transaction({
#         'chainId': web3.eth.chain_id,
#         'gas': 200000,
#         'nonce': web3.eth.get_transaction_count(wallet_address),
#     })

#     signed_approve_txn = web3.eth.account.sign_transaction(approve_txn, private_key)
#     approve_txn_hash = web3.eth.send_raw_transaction(signed_approve_txn.rawTransaction)
#     print(f"Approval transaction hash: {approve_txn_hash.hex()}")

#     web3.eth.wait_for_transaction_receipt(approve_txn_hash)
#     print("Approval transaction confirmed.")
# except Exception as e:
#     print("Error during token approval:", e)
#     sys.exit()

# # Adding liquidity
# try:
#     deadline = int((datetime.datetime.now() + datetime.timedelta(minutes=10)).timestamp())
#     print("check passed value", deadline, erc20_token_address, token_amount_to_add, wallet_address, deadline,eth_amount_to_add)
#     liquidity_txn = router.functions.addLiquidityETH(
#         erc20_token_address,
#         token_amount_to_add,
#         0,  # Min amount of tokens to add (adjust for slippage)
#         0,  # Min amount of ETH to add (adjust for slippage)
#         wallet_address,
#         deadline
#     ).build_transaction({
#         'from': wallet_address,
#         'value': eth_amount_to_add,
#         'gas': 500000,
#         'nonce': web3.eth.get_transaction_count(wallet_address),
#     })

#     signed_liquidity_txn = web3.eth.account.sign_transaction(liquidity_txn, private_key)
#     liquidity_txn_hash = web3.eth.send_raw_transaction(signed_liquidity_txn.rawTransaction)
#     print(f"Liquidity transaction hash: {liquidity_txn_hash.hex()}")

#     receipt=web3.eth.wait_for_transaction_receipt(liquidity_txn_hash)
#     if receipt["status"]==1:
#         print("Liquidity transaction success.")
#     else:
#         print("Liquidity transaction failed.", receipt)    
# except Exception as e:
#     print("Error during adding liquidity:", e)


# Fetch balance of ERC20 token
erc20_token_wei_balance = erc20_token_contract.functions.balanceOf(wallet_address).call()
# print("Balance of ERC20 token:", erc20_token_wei_balance)
erc20_token_formated_balance=erc20_token_wei_balance*10**-erc20_token_decimal
# erc20_token_formated_balance = web3.from_wei(erc20_token_wei_balance, erc20_token_decimal)

print("Selected ERC20 token:", erc20_token_address + " " + erc20_token_symbol)

print(f"You have {eth_balance} ETH")

# print(f"You have {native_token_formated_balance} {native_token_symbol}")

print(f"You have {erc20_token_formated_balance} {erc20_token_symbol}")

# Prompt the user to enter the amount of native token to swap
# user_input = input(f"How many {native_token_symbol} tokens you wish to swap to {erc20_token_symbol}? ")

user_input = input(f"How many ETH tokens you wish to swap to {erc20_token_symbol}? ")

float_value = float(user_input)
# print(f"The input {native_token_symbol} amount is: {float_value} {native_token_symbol}")

# Amount of input token to swap (in Wei)
user_input_amount_in_wei = web3.to_wei(float_value, 'ether')
# print("input Amount in wei:", user_input_amount_in_wei)

# Fetch the current exchange rate and calculate the minimum amount of tokens to accept (for slippage tolerance)
try:
    path = [web3.to_checksum_address(native_token_address), web3.to_checksum_address(erc20_token_address)]
    amounts_out = router.functions.getAmountsOut(user_input_amount_in_wei, path).call()
    amounts_out_in_eth = web3.from_wei(amounts_out[1], 'ether')
    erc20_token_amount_out_in_wei = amounts_out[1]
    output_token_amount = amounts_out_in_eth
    # print(f"Output {erc20_token_symbol} amount is :", amount_out_min)

except Exception as e:
    print("Error calling getAmountsOut function:", e)

# Prompt the user to confirm the swap amount
confirm = input(f"Confirm swap amount {float_value} ETH to {output_token_amount} {erc20_token_symbol}(y/n)? ")

# Check if the user confirmed the swap
if confirm.lower().startswith("y"):
    print(f"Confirmed! Swapping {float_value} ETH to {output_token_amount} {erc20_token_symbol}")
else:
    print("Swap aborted")
    sys.exit()

# Approve the router to spend the WETH tokens
try:
    approve_txn = erc20_token_contract.functions.approve(router_address, erc20_token_amount_out_in_wei).build_transaction({
        'chainId': web3.eth.chain_id,
        'gas': 500000,
        # 'gasPrice': web3.to_wei('5', 'gwei'),
        'nonce': web3.eth.get_transaction_count(wallet_address),
    })

    signed_approve_txn = web3.eth.account.sign_transaction(approve_txn, private_key)
    approve_txn_hash = web3.eth.send_raw_transaction(signed_approve_txn.rawTransaction)
    print(f"Approval transaction hash: {approve_txn_hash.hex()}")

    web3.eth.wait_for_transaction_receipt(approve_txn_hash)
    print("Approval transaction confirmed.")
except Exception as e:
    print("Error during token approval:", e)
    sys.exit()

# Retrieve the current time
try:
    deadline = int((datetime.datetime.now() + datetime.timedelta(minutes=10)).timestamp())
except Exception as e:
    print(f"Error getting latest time: {e}")   

# Set the slippage tolerance for the transaction
slippage_tolerance = 0.5 / 100  # 0.5%

# Adjust for slippage tolerance
min_tokens_out = int(erc20_token_amount_out_in_wei * (1 - slippage_tolerance))

# Build the swap transaction
try:
    txn = router.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
        min_tokens_out,
        path,
        wallet_address,
        deadline
    ).build_transaction({
        'value': user_input_amount_in_wei,
        'from': wallet_address,
        'gas': 500000,  # Adjusted gas limit for the swap
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

        # Fetch balance of ETH
        eth_balance_wei = web3.eth.get_balance(wallet_address)
        eth_balance = web3.from_wei(eth_balance_wei, 'ether')

        # Fetch balance of ERC20 token
        erc20_token_wei_balance = erc20_token_contract.functions.balanceOf(wallet_address).call()
        erc20_token_formatted_balance = erc20_token_wei_balance * 10**-erc20_token_decimal

        print(f"After swap, you have {eth_balance} ETH")
        print(f"After swap, you have {erc20_token_formatted_balance} {erc20_token_symbol}")
    else:
        print("Swap failed!")
        print("Transaction receipt:", tx_receipt)
except Exception as e:
    print("Error during the transaction process:", e)