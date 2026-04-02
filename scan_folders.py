import os

def scan():
    print(f"current directory: {os.getcwd()}\n")
    
    # 1. list everything in root
    print("--- root contents ---")
    print(os.listdir('.'))
    
    # 2. check 'src' folder
    if os.path.exists('src'):
        print("\n--- inside 'src' ---")
        print(os.listdir('src'))
        if os.path.exists('src/live_trading'):
            print("\n--- inside 'src/live_trading' ---")
            print(os.listdir('src/live_trading'))
    else:
        print("\n❌ 'src' folder NOT FOUND in root.")

    # 3. check 'sentiment' folder
    # note: checking for both dash and underscore
    for folder in ['sentiment-analysis-worker', 'sentiment_analysis_worker']:
        if os.path.exists(folder):
            print(f"\n--- inside '{folder}' ---")
            print(os.listdir(folder))
        else:
            print(f"\n❌ '{folder}' folder NOT FOUND.")

if __name__ == "__main__":
    scan()