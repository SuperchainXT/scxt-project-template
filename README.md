# scxt-project-template

A sample project using the scxt library

## Installation

Install the required dependencies using [uv](https://github.com/astral-sh/uv):

```bash
uv sync --frozen
```

## Setup

1. Copy the `.env.example` file to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your configuration:
   ```
   PRIVATE_KEY=your_private_key_here
   CHAIN_10_RPC=your_optimism_rpc_url_here
   ```

To add any additional RPC URLs, you can add them using the same format as `CHAIN_10_RPC` in the `.env` file. For example:

```
CHAIN_8435_RPC=<base mainnet url here>
```

## Usage

Run any of the example scripts using uv:

```bash
# Read-only scripts (no private key required)
uv run scripts/synthetix_v2_read.py
uv run scripts/odos_read.py

# Transaction scripts (require private key)
uv run scripts/synthetix_v2_transact.py
uv run scripts/odos_transact.py
```

## Resources

- SCXT Library: [GitHub Repository](https://github.com/SuperchainXT/scxt)
- Documentation: [SCXT Docs](https://superchainxt.github.io/scxt/)
