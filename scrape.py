from impdata import load_imp_data

if __name__ == "__main__":
    imp_df = load_imp_data()

    combined_df = imp_df

    combined_df.to_csv("combined.csv")