# Hadron Post-Quantum Blockchain

This ongoing MVP for a distributed ledger system aims to solve issues that first and second-generation blockchains have not been able to overcome by implementing novel concepts in mining, smart contracts, and cryptography.

- Proprietary post-quantum hashing algorithm named Qhash3512, based on SHA3-512,
- Proprietary mining algorithm, MineH, which is memory-hard, ASIC-resistant, and favors CPU mining,
- Native compatibility with fungible and non-fungible tokens, without the need for deploying smart contracts,
- WASM smart contracts implementation, meaning that smart contracts can be written in any compatible language,
- Advanced native API implementation that includes metrics,
- Parametrization with advanced controls for easy private deployment,
- Built-in CLI, console, and GUI for flexible usage in all environments,
- Coded in Python for maximum compatibility,

### Problem 1: Quantum computers may be able to break most blockchains' encryption.

Hadron implements Qhash3512, which is a post-quantum hashing algorithm, meaning it cannot be broken even by quantum computers.

### Problem 2: PoW is expensive, requires too much energy, leads to centralization.

The implementation of MineH favors energy-light mining with CPUs. The inefficiencies of using ASICs or GPUs should financially discourage miners from using such resource-intensive machines for mining activities, and MineH should mean that household computers should be able to participate on the network and mine for a long time after the main network goes public.

### Problem 3: Smart contracts are limited in scope and hard to code.

By implementing a smart contracts VM capable that is compatible with WASM deployments, Hadron will allow for smart contracts to be coded in any compatible language, including low-level languages like `C` or `Rust`. It will broaden the scope of utility for smart contracts and allow maximum flexibility.

### Problem 4: Limited APIs.

If you ever tried to calculate the total supply of ETH you know how cumbersome it can become due to the lack of any direct API endpoints to call for that specific function. I'm trying to implement more and more comprehensive API endpoints on Hadron, with metrics and other advanced functions, that will not only allow for a more comprehensive experience for developers, but also ease of use and monitoring of the blockchain state.

### Problem 5: Ease-of-use.

Hadron will be coded for users of all levels of IT literacy, with a user-friendly and easy-to-use GUI for those looking for basic blockchain interactions, a console for node managers and monitors, and a CLI interface that will allow for advanced features, including for private deployment.

## Disclaimer

This is a "side project" far from being ready, and unless you intend to contribute or want to talk about the implementation of the concepts above, I would probably recommend you not to clone or install this repository in your machine.

## Install

You will need to have Python installed in order to run this repository. To install the necessary dependencies you can run:

```
python installer.py
```

If you're on macOS or Linux, you may need to use `python3` instead of `python`.

## Run a Node

After you install all dependencies, you can run the node by running the `server.py` module.

```
python server.py
```

You can manage your node by running the `console.py` module.

```cmd
python console.py
```

I will try to find the time to write down all the available commands at some point, but for now, you can just look inside the `console.py` to see what endpoints are available. Some examples are:

- `blockchain.info` - returns information on the blockchain, such as number of blocks and difficulty,
- `blockchain.blockTime` - returns the average block time of the network,
- `blockchain.hashRate` - returns the current hash rate of the network,
- `accounts.create` - creates a new account,
- `accounts.list` - lists all accounts saved locally,
- `accounts.balance {address}` - returns the wallet balance,

⭐ **If you're on macOS or Linux, you may need to use `python3` instead of `python`.**
