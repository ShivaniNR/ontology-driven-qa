# prewarm.py
import pickle
from helpers.setup import initialize_resources

if __name__ == "__main__":
    print("Running pre-warming script...")
    setup_data = initialize_resources()
    
    # Save setup data to a file for later use
    with open("setup_data.pkl", "wb") as f:
        pickle.dump(setup_data, f)

    print("Pre-warming completed! Setup data saved to setup_data.pkl.")

