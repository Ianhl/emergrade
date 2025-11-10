import pandas as pd
import numpy as np
import os
import glob
import sys

class EEGAnalyzer:
    """
    Analyzes an EEG band power CSV file (now supporting multiple channels)
    to determine the user's dominant brain wave frequency and overall state.
    """

    def __init__(self, filename):
        self.filename = filename
        self.df = None
        self.average_powers = None # Will store dict of {Band: avg_power}
        self.state_map = {
            'Delta': "YOU ARE TIRED! I'm genuinely not sure how you're still awake, let alone shopping.",
            'Theta': "A BIT SLEEPY: You're in a deeply relaxed or drowsy state, which is great for meditation, but terrible for big decisions. This is NOT the best time to shop. Come back later!",
            'Alpha': "NICE AND CALM: You have a relaxed, focused state. This is ideal for browsing and low-stress tasks. You are calm, but maybe not be the best time to buy",
            'Beta': "ACTIVE AND FOCUSED: Your brain is engaged and alert! This is your peak concentration zone. Perfect time for high-stakes shopping decisions. Might be a good time to purchase.",
            'Gamma': "HIGHER PROCESSING: Intense mental shopping achieved! Must be shopping for something important. This is a well thought out purchase"
        }

    def load_data(self):
        """Loads the CSV data into a pandas DataFrame."""
        try:
            self.df = pd.read_csv(self.filename)
            # Drop the Timestamp column for power calculation
            self.df = self.df.drop(columns=['Timestamp'], errors='ignore')
            print(f"Successfully loaded data from: {self.filename} ({len(self.df)} samples)")
        except FileNotFoundError:
            print(f"Error: File not found at {self.filename}")
            self.df = None
            return False
        except Exception as e:
            print(f"An error occurred while loading the file: {e}")
            self.df = None
            return False
        return True

    def calculate_average_frequency(self):
        """
        Calculates the average power for each frequency band across ALL channels
        and ALL time epochs in the session.
        """
        if self.df is None or self.df.empty:
            return

        bands = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']
        self.average_powers = {}
        
        # We need to average power for each band across all 4 channels and all time points.
        for band in bands:
            # Select all columns that start with the band name (e.g., 'Delta_Ch1', 'Delta_Ch2', etc.)
            band_cols = [col for col in self.df.columns if col.startswith(band)]
            
            # 1. Average across all time points (rows) for the band's channels
            # 2. Average those results across all channels to get one single average power for the band
            avg_power = self.df[band_cols].mean().mean()
            self.average_powers[band] = avg_power

        print("\n--- Overall Average Log10 Band Powers for Activity ---")
        for band, avg in self.average_powers.items():
            print(f"{band}: {avg:.4f}")

    def determine_brain_state(self):
        """
        Determines the user's brain state by finding the band with the highest overall average power.
        """
        if self.average_powers is None:
            print("Error: Average powers not calculated.")
            return "N/A", "N/A", 0

        # Find the band with the maximum average power (the most dominant frequency)
        dominant_band = max(self.average_powers, key=self.average_powers.get)
        dominant_power = self.average_powers[dominant_band]

        mental_state = self.state_map.get(dominant_band, 'Unknown State')

        return dominant_band, mental_state, dominant_power

    def run_analysis(self):
        """Runs the complete analysis workflow."""
        if not self.load_data():
            return

        self.calculate_average_frequency()
        dominant_band, mental_state, power = self.determine_brain_state()

        print("\n=============================================")
        print(f"Activity Analysis Complete for: {self.filename}")
        print("=============================================")
        print(f"1. Overall Duration: {len(self.df)} time recorded (approx. {len(self.df)} seconds)")
        print(f"2. DOMINANT BRAIN WAVE: {dominant_band}")
        #print(f"   (Overall Avg Log Power: {power:.4f})")
        print(f"3. INFERRED MENTAL STATE: {mental_state}")
        print("=============================================")


# --- Script Execution Example ---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # User provided a filename as an argument
        filename_to_analyze = sys.argv[1]
    else:
        # No filename provided, try to find the newest one
        try:
            list_of_files = glob.glob('eeg_session_*.csv')
            if not list_of_files:
                print("Usage: python eeg_analyzer.py <filename.csv>")
                print("OR: No 'eeg_session_*.csv' files found. Please run the recording script first.")
                sys.exit(1)
            
            filename_to_analyze = max(list_of_files, key=os.path.getctime)
            print(f"No filename provided. Found and using latest session file: {filename_to_analyze}")

        except Exception as e:
            print(f"Error during file search: {e}")
            sys.exit(1)

    try:
        analyzer = EEGAnalyzer(filename_to_analyze)
        analyzer.run_analysis()
    except Exception as e:
        print(f"Analysis failed: {e}")