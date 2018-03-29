from imp import load_imp_data

if __name__ == "__main__":
    df = load_imp_data()
    df.to_csv("imp.csv")