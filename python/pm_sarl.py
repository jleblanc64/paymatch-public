import pandas as pd


def locataire_to_sum(pm_sarl_df):
    locataire_to_sum = {}

    # --- Block 1: A–C, starting at row 3 ---
    df_subset1 = pm_sarl_df.iloc[3:, [0, 1, 2]]
    first_empty_idx1 = df_subset1.index[df_subset1.iloc[:, 0].isna()].min()
    if not pd.isna(first_empty_idx1):
        df_subset1 = df_subset1.loc[:first_empty_idx1 - 1]
    df_subset1 = df_subset1.fillna(0)
    df_subset1.iloc[:, 0] = df_subset1.iloc[:, 0].astype(str).str.replace("\n", " ").str.strip()
    locataire_to_sum.update({
        row.iloc[0]: round((row.iloc[1] + row.iloc[2]) * 1.19, 2)
        for _, row in df_subset1.iterrows()
    })

    # --- Block 2: I–K, starting at row 5 --- NO TAX
    df_subset2 = pm_sarl_df.iloc[3:, [8, 9, 10]]
    first_empty_idx2 = df_subset2.index[df_subset2.iloc[:, 0].isna()].min()
    if not pd.isna(first_empty_idx2):
        df_subset2 = df_subset2.loc[:first_empty_idx2 - 1]
    df_subset2 = df_subset2.dropna(how="any")
    df_subset2.iloc[:, 0] = df_subset2.iloc[:, 0].astype(str).str.replace("\n", " ").str.strip()
    locataire_to_sum.update({
        row.iloc[0]: round((row.iloc[1] + row.iloc[2]), 2)
        for _, row in df_subset2.iterrows()
    })

    return locataire_to_sum

if __name__ == "__main__":
    pm_sarl_df = pd.read_excel("/home/charles/Desktop/PAY_MATCH/B.xlsx")
    print(locataire_to_sum(pm_sarl_df))
