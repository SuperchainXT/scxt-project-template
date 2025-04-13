"""A sample script displaying how to transact on Synthetix V2 using scxt.

Prerequisites:
1. Environment setup:
   - A .env file with a PRIVATE_KEY for your wallet
   - Example: PRIVATE_KEY=0xYourPrivateKeyHere

2. Account requirements:
   - You need to have sUSD tokens in your wallet on Optimism (chain ID 10)
   - You can get sUSD on Optimism through various DEXs or bridges
"""

import os
import time
from scxt.exchanges import SynthetixV2
from scxt.constants import PUBLIC_RPCS
from scxt import ChainClient
from dotenv import load_dotenv

# Load environment variables (especially PRIVATE_KEY)
load_dotenv()

# Check if private key is available
if not os.getenv("PRIVATE_KEY"):
    raise ValueError(
        "No PRIVATE_KEY found in environment. Please add it to your .env file."
    )
# Check if RPC URL is available, if not, use the default public RPC
if not os.getenv("CHAIN_10_RPC"):
    print("No CHAIN_10_RPC found in environment. Using default public RPC from scxt.")
    os.environ["CHAIN_10_RPC"] = PUBLIC_RPCS[10]


def main():
    # Initialize the Synthetix V2 client with your private key and RPC
    chain_config = {
        "rpc_url": os.getenv("CHAIN_10_RPC"),
        "private_key": os.getenv("PRIVATE_KEY"),
    }
    chain_client = ChainClient(chain_config)
    exchange_config = {
        "chain": chain_client,
    }
    exchange = SynthetixV2(exchange_config)
    print(f"Initialized {exchange.name} exchange on chain {exchange.chain.chain_id}")
    print(f"Connected wallet address: {exchange.chain.address}")

    # Load markets and currencies
    markets = exchange.load_markets()
    currencies = exchange.fetch_currencies()
    print(f"Loaded {len(markets)} markets and {len(currencies)} currencies")

    # Specify the market we want to trade on
    market_symbol = "ETH-PERP"
    print(f"\nTrading on {market_symbol} market")

    # 1. Check sUSD balance
    susd_address = exchange.contracts["sUSD"]
    susd_balance = exchange.chain.get_balance(susd_address)
    print(f"sUSD balance: {susd_balance:.4f} sUSD")

    if susd_balance < 100:
        print(
            "WARNING: Your sUSD balance is less than 10 sUSD, which may be too low for trading."
        )

    # 2. Check current market account balance before deposit
    print("\nChecking market account balance before deposit...")
    try:
        before_balance = exchange.fetch_balance(market_symbol)
        print(
            f"Current market balance: {before_balance.balances['sUSD'].free:.4f} sUSD free"
        )
    except Exception as e:
        print(f"Could not fetch initial balance, likely no position exists: {e}")
        print("Continuing with deposit...")

    # 3. Approve sUSD spending if needed
    print("\nApproving sUSD for market contract...")
    deposit_amount = 100  # The amount we want to deposit in sUSD

    # Check if we have enough balance
    if susd_balance < deposit_amount:
        print(
            f"Not enough sUSD for deposit. Have {susd_balance:.2f}, need {deposit_amount}"
        )
        deposit_amount = float(
            input(f"Enter a deposit amount less than {susd_balance:.2f} sUSD: ")
        )

    # Approve spending
    approve_tx = exchange.approve_market(
        symbol=market_symbol,
        amount=deposit_amount,
        send=True,
    )
    print(f"Approval transaction sent: {approve_tx.hex()}")
    print("Waiting for approval transaction to confirm...")
    receipt = exchange.chain.wait_for_transaction_receipt(approve_tx)
    print(
        f"Approval transaction confirmed. Status: {'Success' if receipt['status'] == 1 else 'Failed'}"
    )

    # 4. Deposit sUSD into the market
    print(f"\nDepositing {deposit_amount} sUSD into {market_symbol}...")
    deposit_tx = exchange.deposit(
        amount=deposit_amount,
        currency="sUSD",
        send=True,
        params={"market": market_symbol},
    )
    print(f"Deposit transaction sent: {deposit_tx.hex()}")
    print("Waiting for deposit transaction to confirm...")
    receipt = exchange.chain.wait_for_transaction_receipt(deposit_tx)
    print(
        f"Deposit transaction confirmed. Status: {'Success' if receipt['status'] == 1 else 'Failed'}"
    )

    # 5. Check updated market account balance after deposit
    print("\nChecking market account balance after deposit...")
    after_balance = exchange.fetch_balance(market_symbol)
    print(
        f"Updated market balance: {after_balance.balances['sUSD'].free:.4f} sUSD free"
    )

    # 6. Get current position before opening a new one
    print("\nChecking current position...")
    position_before = exchange.fetch_position(market_symbol)
    if position_before.size != 0:
        print(f"Current position: {position_before.size:.4f} {market_symbol}")
        print(f"Current margin: {position_before.margin:.4f} sUSD")
        if position_before.liquidation_price:
            print(f"Liquidation price: ${position_before.liquidation_price:.2f}")
    else:
        print("No current position found.")

    # 7. Place an order
    # Let's use 25% of our deposited amount for a position
    position_size = 0.01  # Start with a small position size of 0.01 ETH
    side = "buy"  # or "sell" for short positions

    print(f"\nCreating a {side} order for {position_size} ETH...")
    order = exchange.create_order(
        symbol=market_symbol,
        side=side,
        amount=position_size,
        order_type="market",
        send=True,
    )

    print(f"Order transaction sent: {order.tx_hash}")
    print("Waiting for order transaction to confirm...")
    receipt = exchange.chain.wait_for_transaction_receipt(order.tx_hash)
    print(
        f"Order transaction confirmed. Status: {'Success' if receipt['status'] == 1 else 'Failed'}"
    )

    # 8. Wait a moment for the order to be executed
    print("\nWaiting for order to be executed by a keeper...")
    time.sleep(10)  # Wait for the order to be fully processed

    # 9. Check the position after the order
    print("\nChecking position after order...")
    position_after = exchange.fetch_position(market_symbol)
    if position_after.size != 0:
        print(f"Current position: {position_after.size:.4f} {market_symbol}")
        print(f"Current margin: {position_after.margin:.4f} sUSD")
        if position_after.liquidation_price:
            print(f"Liquidation price: ${position_after.liquidation_price:.2f}")
    else:
        print(
            "No position found after order. The order might still be processing or failed."
        )

    print("\nScript completed. Check the output above for transaction details.")


if __name__ == "__main__":
    main()
