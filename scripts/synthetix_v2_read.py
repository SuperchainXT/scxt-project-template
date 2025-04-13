"""A sample script to read data from the Synthetix V2 contract."""

import os
from scxt.exchanges import SynthetixV2
from dotenv import load_dotenv

load_dotenv()

# Initialize the Synthetix V2 client
exchange = SynthetixV2()
print(f"Initialized {exchange.name} exchange on chain {exchange.chain.chain_id}")

# Load markets and currencies
markets = exchange.load_markets()
currencies = exchange.fetch_currencies()
print(f"Loaded {len(markets)} markets and {len(currencies)} currencies")

# Display the contract addresses for the markets
print("\nContract Addresses:")
print(f"PerpsV2MarketData: {exchange.contracts['PerpsV2MarketData']}")
print(f"sUSD: {exchange.contracts['sUSD']}")

# Display market data for ETH and BTC
target_markets = ["ETH-PERP", "BTC-PERP"]
print("\nMarket Data:")

for symbol in target_markets:
    if symbol in markets:
        market = markets[symbol]
        print(f"\n{symbol} Market:")
        print(f"  Market Address: {market.id}")
        print(f"  Market Key: {market.info['market_key']}")
        print(f"  Max Leverage: {market.info['max_leverage']:.2f}x")
        print(f"  Market Size: {market.info['market_size']:.2f} {market.base}")
        print(f"  Market Skew: {market.info['market_skew']:.2f} {market.base}")
        print(
            f"  Current Funding Rate: {market.info['current_funding_rate'] * 100:.6f}%"
        )
        print(f"  Maker Fee: {market.maker_fee * 100:.4f}%")
        print(f"  Taker Fee: {market.taker_fee * 100:.4f}%")
    else:
        print(f"\n{symbol} market not found")
