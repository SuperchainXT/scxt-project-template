"""A sample script displaying how to fetch and display data from Odos DEX aggregator.

Prerequisites:
1. Environment setup:
   - For read-only operations, no private key is required
   - Example: CHAIN_10_RPC=https://mainnet.optimism.io (or any Optimism RPC)

2. Understanding:
   - Odos is a DEX aggregator for efficient token swaps
   - This script only reads data and does not perform transactions
"""

import os
from scxt.exchanges import Odos
from scxt import ChainClient
from scxt.constants import PUBLIC_RPCS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if an RPC URL is available, if not, use the default public RPC
if not os.getenv("CHAIN_10_RPC"):
    print("No CHAIN_10_RPC found in environment. Using default public RPC from scxt.")
    os.environ["CHAIN_10_RPC"] = PUBLIC_RPCS[10]  # Optimism
if not os.getenv("PRIVATE_KEY"):
    print("No PRIVATE_KEY found in environment. Some operations may be limited.")


def main():
    # Initialize the Odos client
    chain_config = {
        "chain_id": 10,  # Optimism
        "rpc_url": os.environ["CHAIN_10_RPC"],
    }
    if os.getenv("PRIVATE_KEY"):
        chain_config["private_key"] = os.environ["PRIVATE_KEY"]
        print("Private key found, account will be set up for transactions.")
    chain = ChainClient(chain_config)
    exchange = Odos({"chain": chain})
    print(f"Initialized {exchange.name} exchange on chain {exchange.chain.chain_id}")

    # Display Odos router contract address
    print(f"Odos Router contract: {exchange.chain.contracts.get('OdosRouter')}")

    # Load supported currencies
    currencies = exchange.fetch_currencies()
    print(f"\nLoaded {len(currencies)} tokens from Odos")

    # Display some popular tokens
    popular_tokens = ["WETH", "USDC", "USDT", "DAI", "OP", "WBTC"]
    print("\nPopular token details:")
    for symbol in popular_tokens:
        if symbol in currencies:
            currency = currencies[symbol]
            print(f"  {symbol}: {currency.name}")
            print(f"    Address: {currency.info['address']}")
            print(f"    Decimals: {currency.precision}")
        else:
            print(f"  {symbol}: Not available")

    # Fetch balances for a specific address (if provided)
    if exchange.chain.address:
        print(f"\nFetching balances for address: {exchange.chain.address}")
        # Check balances of popular tokens
        for symbol in popular_tokens:
            if symbol in currencies:
                try:
                    balance = exchange.fetch_balance(symbol)
                    amount = balance.balances[symbol].free
                    print(f"  {symbol} Balance: {amount}")
                except Exception as e:
                    print(f"  Error fetching {symbol} balance: {e}")
    else:
        print("\nNo address connected, skipping balance checks")

    # Display information about a potential WETH/USDC swap
    print("\nSwap information for WETH/USDC:")
    try:
        # Analyze what a swap would look like
        weth_address = currencies["WETH"].info["address"]
        usdc_address = currencies["USDC"].info["address"]

        print(f"  WETH address: {weth_address}")
        print(f"  USDC address: {usdc_address}")
        print("  To execute a swap, you would need to:")
        print("  1. Approve the WETH token for spending by the Odos router")
        print("  2. Call create_order with symbol='WETH/USDC', side='sell', amount=0.1")
        print("  3. Send the transaction using the returned transaction parameters")

        # Get router contract
        router_address = exchange.chain.contracts.get("OdosRouter")
        print(f"\nOdos router would handle the swap at address: {router_address}")

        # Information about supported DEX sources
        print("\nOdos aggregates liquidity from multiple sources including:")
        print("  - Uniswap V2/V3")
        print("  - Curve")
        print("  - Balancer")
        print("  - SushiSwap")
        print("  - Velodrome")
        print("  - And many others")

    except Exception as e:
        print(f"Error generating swap information: {e}")

    print("\nScript completed successfully")


if __name__ == "__main__":
    main()
