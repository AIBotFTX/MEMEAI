def listen_pumpfun_events(k=5):
    """
    Connects to Pump.fun WebSocket and listens for token creation events.
    Processes the first `k` transactions and then stops.

    Args:
        k (int): Number of transactions to process before stopping.
    """
    import websocket
    import json

    uri = "wss://pumpportal.fun/api/data"

    print(
        f"Connecting to Pump.fun WebSocket...\nProcessing the first {k} transactions."
    )

    def format_pumpfun_event_dynamic(event_data: dict) -> str:
        """
        Formats Pump.fun WebSocket event data into a readable string.

        Args:
            event_data (dict): The raw event data from the WebSocket.

        Returns:
            str: Formatted event details.
        """
        formatted_output = ["Pump.fun Event Details:"]

        for key, value in event_data.items():
            formatted_output.append(f"{key.replace('_', ' ').title()}: {value}")

        return "\n".join(formatted_output)

    def on_message(ws, message):
        nonlocal count  # To track processed transactions
        event_data = json.loads(message)

        # Skip subscription confirmation messages
        if "message" in event_data:
            print(f"Server Response: {event_data['message']}")
            return

        # Process transaction
        formatted_event = format_pumpfun_event_dynamic(event_data)
        print(formatted_event + "\n" + "=" * 50 + "\n")

        count += 1  # Increment processed transaction count

        # Close WebSocket after processing `k` transactions
        if count >= k:
            print(f"Processed {k} transactions. Exiting.")
            ws.close()

    def on_open(ws):
        """Subscribe to new token events upon connection."""
        ws.send(json.dumps({"method": "subscribeNewToken"}))
        print("Subscribed. Waiting for transactions...\n")

    count = 0  # Track processed transactions

    ws = websocket.WebSocketApp(uri, on_message=on_message, on_open=on_open)
    ws.run_forever()


def create_pumpfun_wallet() -> dict:
    """
    Generate a new wallet on Pump.fun.

    Returns:
        dict: JSON response with the new wallet details and API key.
    """
    import requests

    def process(answer):
        result = (
            f"{70 * '='}\n"
            f"{'Wallet Created Successfully!'.center(70)}\n"
            f"{70 * '='}\n\n"
            f"API Key: {answer['apiKey']}\n"
            f"Wallet Public Key: {answer['walletPublicKey']}\n"
            f"Private Key: {answer['privateKey']}\n"
            f"{70 * '='}\n"
        )
        return result

    url = "https://pumpportal.fun/api/create-wallet"
    response = requests.get(url)

    if response.status_code == 200:
        answer = response.json()
        return process(answer)

    return {"error": "Failed to create wallet"}


def create_pumpfun_token(api_key: str, form_data: dict, image_path: str) -> str:
    """
    Create a token on Pump.fun.

    Args:
        api_key (str): API key linked to the wallet.
        form_data (dict): Token metadata details.
        image_path (str): Path to the token image.

    Returns:
        str: Transaction signature or error message.
    """
    import json
    import requests
    from solders.keypair import Keypair

    mint_keypair = Keypair()  # Generate a new keypair for the token

    metadata_response = upload_metadata_to_ipfs(form_data, image_path)

    if "metadataUri" not in metadata_response:
        return "Failed to create token: Metadata upload failed"

    token_metadata = {
        "name": form_data["name"],
        "symbol": form_data["symbol"],
        "uri": metadata_response["metadataUri"],
    }

    response = requests.post(
        "https://pumpportal.fun/api/trade",
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "action": "create",
                "tokenMetadata": token_metadata,
                "mint": str(mint_keypair.pubkey()),
                "denominatedInSol": "true",
                "amount": 1,  # Dev buy of 1 SOL
                "slippage": 10,
                "priorityFee": 0.0005,
                "pool": "pump",
            }
        ),
    )

    if response.status_code == 200:
        data = response.json()
        return f"Transaction: https://solscan.io/tx/{data['signature']}"

    return f"Error: {response.reason}"


def upload_metadata_to_ipfs(form_data: dict, image_path: str) -> dict:
    """
    Uploads token metadata and image to Pump.fun's IPFS.

    Args:
        form_data (dict): Token metadata details.
        image_path (str): Path to the token image.

    Returns:
        dict: JSON response with metadata URI.
    """
    import requests

    with open(image_path, "rb") as f:
        file_content = f.read()

    files = {"file": (image_path, file_content, "image/png")}
    response = requests.post("https://pump.fun/api/ipfs", data=form_data, files=files)

    if response.status_code == 200:
        return response.json()

    return {"error": "Failed to upload metadata"}


def create_local_pumpfun_token(
    private_key: str, form_data: dict, image_path: str, rpc_url: str
) -> str:
    """
    Create a token locally and sign the transaction.

    Args:
        private_key (str): Base58 private key of the signer.
        form_data (dict): Token metadata details.
        image_path (str): Path to the token image.
        rpc_url (str): Solana RPC URL.

    Returns:
        str: Transaction signature or error message.
    """
    import requests
    import json
    from solders.keypair import Keypair
    from solders.transaction import VersionedTransaction
    from solders.commitment_config import CommitmentLevel
    from solders.rpc.requests import SendVersionedTransaction
    from solders.rpc.config import RpcSendTransactionConfig

    signer_keypair = Keypair.from_base58_string(private_key)
    mint_keypair = Keypair()

    metadata_response = upload_metadata_to_ipfs(form_data, image_path)

    if "metadataUri" not in metadata_response:
        return "Failed to create token: Metadata upload failed"

    token_metadata = {
        "name": form_data["name"],
        "symbol": form_data["symbol"],
        "uri": metadata_response["metadataUri"],
    }

    response = requests.post(
        "https://pumpportal.fun/api/trade-local",
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "publicKey": str(signer_keypair.pubkey()),
                "action": "create",
                "tokenMetadata": token_metadata,
                "mint": str(mint_keypair.pubkey()),
                "denominatedInSol": "true",
                "amount": 1,
                "slippage": 10,
                "priorityFee": 0.0005,
                "pool": "pump",
            }
        ),
    )

    tx = VersionedTransaction(
        VersionedTransaction.from_bytes(response.content).message,
        [mint_keypair, signer_keypair],
    )
    commitment = CommitmentLevel.Confirmed
    config = RpcSendTransactionConfig(preflight_commitment=commitment)

    response = requests.post(
        url=rpc_url,
        headers={"Content-Type": "application/json"},
        data=SendVersionedTransaction(tx, config).to_json(),
    )

    tx_signature = response.json().get("result", "Transaction failed")
    return f"Transaction: https://solscan.io/tx/{tx_signature}"


def buy(
    api_key: str,
    mint: str,
    amount: int,
    denominated_in_sol: bool,
    slippage: int,
    priority_fee: float,
    pool: str,
):
    """
    Executes a buy trade on the Pump.fun platform.

    Args are the same as `trade`, with `action="buy"` pre-set.
    """
    import requests

    url = f"https://pumpportal.fun/api/trade?api-key={api_key}"

    response = requests.post(
        url,
        data={
            "action": "buy",
            "mint": mint,
            "amount": amount,
            "denominatedInSol": str(denominated_in_sol).lower(),
            "slippage": slippage,
            "priorityFee": priority_fee,
            "pool": pool,
        },
    )

    return response.json()


def sell(
    api_key: str,
    mint: str,
    amount: int,
    denominated_in_sol: bool,
    slippage: int,
    priority_fee: float,
    pool: str,
):
    """
    Executes a sell trade on the Pump.fun platform.

    Args are the same as `trade`, with `action="sell"` pre-set.
    """
    import requests

    url = f"https://pumpportal.fun/api/trade?api-key={api_key}"

    response = requests.post(
        url,
        data={
            "action": "sell",
            "mint": mint,
            "amount": amount,
            "denominatedInSol": str(denominated_in_sol).lower(),
            "slippage": slippage,
            "priorityFee": priority_fee,
            "pool": pool,
        },
    )

    return response.json()
