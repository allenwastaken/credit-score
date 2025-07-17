Wallet Credit Scoring

This project assigns credit scores (0–1000) to DeFi wallets based on their historical transaction behavior on the Aave V2 protocol. Higher scores reflect responsible, consistent activity; lower scores reflect risk-prone or exploitative usage.

**Method Chosen**

We use a **rule-based feature engineering approach** followed by a **weighted scoring model**. Each wallet's activity is analyzed across several dimensions, such as frequency, diversity, financial value, and risk behavior. These features are normalized and aggregated to compute a final score.

## Architecture

1. **Input**: JSON file containing transaction records for all wallets on Aave V2.
2. **Processing**:
   - Extract wallet-level features
   - Normalize features
   - Apply a custom weighted scoring function
3. **Output**: CSV file with wallet addresses and their credit scores.

**Processing Flow**

1. **Data Ingestion**:
   - Load raw JSON data containing actions like `deposit`, `borrow`, `repay`, `redeemunderlying`, and `liquidationcall`.

2. **Feature Engineering**:
   - For each wallet:
     - Count and sum of deposits, borrows, repayments
     - Frequency of liquidations
     - Number of distinct asset interactions
     - Duration of protocol engagement (first-to-last transaction)
     - Total USD volume transacted

3. **Normalization**:
   - Features are scaled to a 0–1 range using Min-Max normalization to allow fair aggregation.

4. **Scoring**:
   - Each normalized feature is multiplied by a weight:
     - Deposit activity: 20%
     - Repayment behavior: 20%
     - Liquidation frequency (negative): 25%
     - Wallet age: 10%
     - Asset diversity: 10%
     - Borrow activity: 10%
     - Total volume transacted: 5%
   - Final score = weighted sum × 1000

5. **Output**:
   - A `.csv` file with wallet addresses and scores is saved for further analysis.

