import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import json

# Token decimals mapping
TOKEN_DECIMALS = {
    "USDC": 6, "USDT": 6, "DAI": 18, "WMATIC": 18, "WETH": 18,
    "WBTC": 8, "AAVE": 18, "TUSD": 18, "CRV": 18, "GHST": 18, "BAL": 18
}

with open("user-wallet-transactions.json", "r") as f:
    transactions = json.load(f)


def normalize_amount(action_data):
    try:
        usd_price = float(action_data.get("assetPriceUSD", 1))
        amount = float(action_data.get("amount", 0))
        symbol = action_data.get("assetSymbol", "UNKNOWN").upper()
        decimals = TOKEN_DECIMALS.get(symbol, 18)
        return (amount / (10 ** decimals)) * usd_price
    except:
        return 0

def process_transactions(transactions):
    wallets = defaultdict(lambda: {
        "deposit": 0,
        "borrow": 0,
        "repay": 0,
        "num_deposit": 0,
        "num_borrow": 0,
        "num_repay": 0,
        "num_liquidations": 0,
        "timestamps": []
    })

    for tx in transactions:
        try:
            wallet = tx["userWallet"]
            action = tx["action"].lower()
            action_data = tx["actionData"]
            ts = int(tx["timestamp"])
            usd_value = normalize_amount(action_data)
            wallets[wallet]["timestamps"].append(ts)

            if action == "deposit":
                wallets[wallet]["deposit"] += usd_value
                wallets[wallet]["num_deposit"] += 1
            elif action == "borrow":
                wallets[wallet]["borrow"] += usd_value
                wallets[wallet]["num_borrow"] += 1
            elif action == "repay":
                wallets[wallet]["repay"] += usd_value
                wallets[wallet]["num_repay"] += 1
            elif action == "liquidationcall":
                wallets[wallet]["num_liquidations"] += 1
        except:
            continue

    return wallets

def score_wallets(wallet_data):
    scores = {}
    for wallet, data in wallet_data.items():
        deposit = data["deposit"]
        borrow = data["borrow"]
        repay = data["repay"]
        liq = data["num_liquidations"]

        deposit_borrow_ratio = deposit / (borrow + 1e-5)
        repay_ratio = repay / (borrow + 1e-5)
        liquidation_penalty = 1 / (1 + liq)

        timestamps = data["timestamps"]
        active_days = (max(timestamps) - min(timestamps)) / 86400 if timestamps else 0
        activity_score = min(active_days / 180, 1.0)

        score = (
            300 * min(deposit_borrow_ratio, 1.0) +
            300 * min(repay_ratio, 1.0) +
            200 * liquidation_penalty +
            200 * activity_score
        )

        scores[wallet] = min(1000, round(score))
    return scores


wallet_data = process_transactions(transactions)
wallet_scores = score_wallets(wallet_data)


df_scores = pd.DataFrame(wallet_scores.items(), columns=["wallet", "score"])
csv_path = "wallet_scores.csv"
df_scores.to_csv(csv_path, index=False)



bins = list(range(0, 1100, 100))
df_scores["score_bin"] = pd.cut(df_scores["score"], bins=bins)
plt.figure(figsize=(10, 5))
df_scores["score_bin"].value_counts().sort_index().plot(kind="bar", color="#4A90E2", rot=45)
plt.title("Wallet Score Distribution")
plt.xlabel("Score Range")
plt.ylabel("Number of Wallets")
plt.tight_layout()
plot_path = "score_distribution.png"
plt.savefig(plot_path)

csv_path, plot_path, df_scores.describe()
