"""A sample script displaying how to execute token swaps using Odos DEX aggregator.

Prerequisites:
1. Environment setup:
   - A .env file with a PRIVATE_KEY for your wallet
   - Example: PRIVATE_KEY=0xYourPrivateKeyHere
   - Example: OPTIMISM_RPC=https://mainnet.optimism.io (or any Optimism RPC)

2. Account requirements:
   - You need to have tokens in your wallet on Optimism (chain ID 10)
   - For this example, we'll swap WETH to USDC
   - Make sure you have some ETH for gas fees
"""

import os
import time
from scxt.exchanges import Odos
from scxt import ChainClient
from scxt.constants import PUBLIC_RPCS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if private key is available
if not os.getenv("PRIVATE_KEY"):
    raise ValueError(
        "No PRIVATE_KEY found in environment. Please add it to your .env file."
    )

# Check if RPC URL is available, if not, use the default public RPC
if not os.getenv("CHAIN_10_RPC"):
    print("No CHAIN_10_RPC found in environment. Using default public RPC from scxt.")
    os.environ["CHAIN_10_RPC"] = PUBLIC_RPCS[10]  # Optimism


def main():
    # Initialize the Odos client
    chain_config = {
        "chain_id": 10,  # Optimism
        "rpc_url": os.environ["CHAIN_10_RPC"],
        "private_key": os.getenv("PRIVATE_KEY"),
    }
    chain = ChainClient(chain_config)
    exchange = Odos({"chain": chain})
    print(f"Initialized {exchange.name} exchange on chain {exchange.chain.chain_id}")
    print(f"Connected wallet address: {exchange.chain.address}")

    # Load supported currencies
    currencies = exchange.fetch_currencies()
    print(f"\nLoaded {len(currencies)} tokens from Odos")

    # Specify the trading pair and direction
    base_symbol = "WETH"
    quote_symbol = "USDC"
    trading_pair = f"{base_symbol}/{quote_symbol}"
    swap_direction = "sell"  # sell WETH to get USDC, or use "buy" to buy WETH with USDC

    print(f"\nTrading on {trading_pair} with direction: {swap_direction}")

    # 1. Check token balances before swap
    try:
        weth_balance_before = exchange.fetch_balance(base_symbol)
        weth_amount = weth_balance_before.balances[base_symbol].free
        print(f"{base_symbol} balance: {weth_amount}")

        usdc_balance_before = exchange.fetch_balance(quote_symbol)
        usdc_amount = usdc_balance_before.balances[quote_symbol].free
        print(f"{quote_symbol} balance: {usdc_amount}")
    except Exception as e:
        print(f"Error fetching balances: {e}")
        print("Continuing with the script...")

    # 2. Set the amount to swap (this will be input token amount)
    swap_amount = 0.001  # Small amount of WETH for the example
    input_token = base_symbol if swap_direction == "sell" else quote_symbol
    output_token = quote_symbol if swap_direction == "sell" else base_symbol

    print(f"\nPreparing to swap {swap_amount} {input_token} to {output_token}")

    # 3. Approve the token for Odos router (if needed)
    print(f"\nApproving {input_token} for Odos router...")

    # Get the token address from currencies
    input_token_address = currencies[input_token].info["address"]

    try:
        # Approve the token
        approval_tx = exchange.approve_router(
            token_address=input_token_address,
            send=True,
        )
        print(f"Approval transaction sent: {approval_tx.hex()}")
        print("Waiting for approval transaction to confirm...")

        receipt = exchange.chain.wait_for_transaction_receipt(approval_tx)
        print(
            f"Approval transaction confirmed. Status: {'Success' if receipt['status'] == 1 else 'Failed'}"
        )
    except Exception as e:
        print(f"Error during approval: {e}")
        print(
            "You may need to check if you already have approved tokens for Odos router"
        )

    # 4. Create and execute the swap order
    print(f"\nCreating {swap_direction} order for {swap_amount} {input_token}...")

    try:
        # Prepare the swap parameters
        slippage = 0.005  # 0.5% slippage tolerance

        # Create the order
        order = exchange.create_order(
            symbol=trading_pair,
            side=swap_direction,
            amount=swap_amount,
            order_type="market",
            params={"slippage_tolerance": slippage},
            send=False,  # We'll send it manually after reviewing
        )

        # Show order details
        print("\nOrder prepared with the following details:")
        print(f"  Input: {swap_amount} {order.info['input_token']}")
        print(f"  Output: {order.info['output_token']}")
        print(f"  Slippage Tolerance: {slippage * 100}%")

        # Send the transaction
        tx_hash = exchange.chain.send_transaction(order.tx_params)
        print(f"Swap transaction sent: {tx_hash.hex()}")
        print("Waiting for transaction to be confirmed...")

        # Wait for confirmation
        receipt = exchange.chain.wait_for_transaction_receipt(tx_hash)
        print(
            f"Swap transaction confirmed. Status: {'Success' if receipt['status'] == 1 else 'Failed'}"
        )

        # 5. Check balances after the swap
        print("\nChecking balances after swap...")

        try:
            weth_balance_after = exchange.fetch_balance(base_symbol)
            weth_new_amount = weth_balance_after.balances[base_symbol].free
            weth_diff = weth_new_amount - weth_amount

            usdc_balance_after = exchange.fetch_balance(quote_symbol)
            usdc_new_amount = usdc_balance_after.balances[quote_symbol].free
            usdc_diff = usdc_new_amount - usdc_amount

            print(f"{base_symbol} balance: {weth_new_amount} ({weth_diff:+.6f})")
            print(f"{quote_symbol} balance: {usdc_new_amount} ({usdc_diff:+.6f})")
        except Exception as e:
            print(f"Error fetching updated balances: {e}")

    except Exception as e:
        print(f"Error creating or sending order: {e}")

    print("\nScript completed. Check the output above for transaction details.")


if __name__ == "__main__":
    main()
