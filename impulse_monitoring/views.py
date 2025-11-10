from django.shortcuts import render, redirect
from django.http import HttpResponse
import subprocess
import os
import glob
import sys
# Import the analysis logic directly to avoid another subprocess call
from .views import analyze_eeg_file, STATE_MAP 

# --- NEW VIEW FOR SYNCHRONOUS RECORDING AND ANALYSIS ---
def run_full_eeg_process(request):
    """
    Synchronously runs the EEG recording and analysis.
    WARNING: This will block the user's request for > 60 seconds!
    """
    if request.method == 'POST':
        try:
            # 1. Start Recording (60 seconds)
            # Use sys.executable to ensure the correct Python environment
            recording_command = [
                sys.executable, 
                os.path.join(os.path.dirname(__file__), 'EEG_recording.py')
            ]
            
            print("Starting 60s EEG Recording...")
            recording_process = subprocess.run(
                recording_command, 
                capture_output=True, # Capture stdout/stderr for logging
                text=True,
                check=True # Raise an exception if the script fails
            )
            print("Recording script finished.")

            # 2. Find the newest generated CSV file
            list_of_files = glob.glob('eeg_session_*.csv')
            if not list_of_files:
                raise FileNotFoundError("EEG_recording.py failed to create a session file.")

            filename_to_analyze = max(list_of_files, key=os.path.getctime)
            print(f"Analyzing file: {filename_to_analyze}")

            # 3. Perform Analysis (Simulated In-Memory Analysis from analyze_eeg_file)
            # Note: The original eeg_analyzer.py is a CLI, but you already have the 
            # core logic imported as `analyze_eeg_file` in your original views.py.
            with open(filename_to_analyze, 'rb') as f:
                 # Django File object handling is simulated here with file handle
                dominant_band, inferred_state, avg_power = analyze_eeg_file(f)
            
            # 4. Clean up the temporary file
            os.remove(filename_to_analyze)

            # 5. Render Results
            context = {
                'eeg_results': {
                    'dominant_band': dominant_band,
                    'inferred_state': inferred_state,
                    'avg_power': f"{avg_power:.4f}",
                    'file_name': filename_to_analyze
                },
                'analysis_successful': True
            }
            return render(request, 'vton_demo.html', context)

        except subprocess.CalledProcessError as e:
            error_message = f"EEG Recording/Muselsl failed. Stderr: {e.stderr}"
            print(error_message)
            return render(request, 'vton_demo.html', {'error': error_message})
        except Exception as e:
            error_message = f"An analysis error occurred: {e}"
            print(error_message)
            return render(request, 'vton_demo.html', {'error': error_message})

    # Redirect to the main page if accessed via GET
    return redirect('/')