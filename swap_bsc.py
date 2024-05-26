from web3 import Web3
from dotenv import load_dotenv
import os
import json
import datetime
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
    print("Failed to connect to the BSC testnet.")
    exit()

print("Connected to the BSC testnet.")

# V2 router contract address and ABI
router_address = '0x9bC24Ea4EfCaFF2f1DDad85aEE5fA2100E21beEe'
router_abi = router_abi_json

# Create contract instance
router = web3.eth.contract(address=router_address, abi=router_abi)
print("Router instance created.")

# Token details
# erc20_token_address = '0xab1a4d4f1d656d2450692d237fdd6c7f9146e814'
erc20_token_abi = erc20_token_abi_json

# Create contract instance for the ERC20 token
# erc20_token = web3.eth.contract(address=erc20_token_address, abi=erc20_token_abi)
print("ERC20 token instance created.")

# Define tokens
tokens = {
    "1": ("AGDL", "0x7eB601804cD8Ac6ED586aE4F67f528Cf81058Ff0"),
    "2": ("ABGL", "0x937F59039A370c67e73D1809CFE8FD996095d16d"),
    "3": ("BUSD", "0xab1a4d4f1d656d2450692d237fdd6c7f9146e814"),
}

def get_user_token_choice(tokens):
    print("Select one of the following tokens:")
    for key, value in tokens.items():
        print(f"{key}. {value[0]} ({value[1]})")

    choice = input("Enter the number of your choice: ")

    while choice not in tokens:
        print("Invalid choice. Please choose again.")
        choice = input("Enter the number of your choice: ")

    return tokens[choice]

selectedToken= get_user_token_choice(tokens)
erc20_token_address =selectedToken[1] 
erc20_token_symbol = selectedToken[0]

print("Selected ERC20 token address:", erc20_token_symbol)

user_input = input("Enter the amount: ")
float_value = float(user_input)
print(f"The input native token amount is: {float_value}")

# Amount of BNB to swap (in Wei)
amount_in_wei = web3.to_wei(float_value, 'ether')
# print("Amount in Wei:", amount_in_wei)
# print("Wallet address:", wallet_address)

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

# Fetch the current exchange rate and calculate the minimum amount of tokens to accept (for slippage tolerance)
try:
    path = [web3.to_checksum_address(weth_address), web3.to_checksum_address(erc20_token_address)]
    amounts_out = router.functions.getAmountsOut(amount_in_wei, path).call()
    amount_out_min = amounts_out[1]
    print(f"Output {erc20_token_symbol} amount is :", amount_out_min)
except Exception as e:
    print("Error calling getAmountsOut function:", e)



# Adjust for slippage tolerance
amount_out_min = int(amount_out_min * (1 - slippage_tolerance / 100))
amount_out=web3.to_wei(amount_out_min, 'ether')
# print("Amount out:", amount_out)

# print('tx value:',amount_in_wei,amount_out,path,wallet_address,deadline)

# Build the transaction
try:
    txn = router.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
    amount_out,
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
