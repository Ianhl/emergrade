from django.shortcuts import render, redirect
from .models import EEGSession
import pandas as pd
import numpy as np
import io
import os # Need this for file deletion

# --- 1. CORE ANALYSIS LOGIC ---

STATE_MAP = {
    'Delta': "YOU ARE TIRED! This is the signature of deep sleep. I'm genuinely not sure how you're still awake, let alone shopping. Shut the screens and rest immediately.",
    'Theta': "A BIT SLEEPY: You're in a deeply relaxed or drowsy state, which is great for meditation, but terrible for big decisions. This is **not** the best time to shop—come back later!",
    'Alpha': "NICE AND CALM: You have a relaxed, focused state. This is ideal for browsing and light tasks. You are calm, but maybe not sharp enough for complex financial decisions.",
    'Beta': "ACTIVE AND FOCUSED: Your brain is engaged and alert! This is your peak concentration zone. This is the **PERFECT** time for critical thinking and complex work.",
    'Gamma': "HIGHER PROCESSING: Intense mental activity or problem-solving. You are fully engaged, likely on a complex task. Keep that mental momentum going!"
}
BANDS = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']

def analyze_eeg_file(file_handle):
    """ Analyzes the EEG CSV data from an uploaded file handle. """
    try:
        # Load the file directly from the Django file handle
        df = pd.read_csv(file_handle)
        df = df.drop(columns=['Timestamp'], errors='ignore')
        
        average_powers = {}
        
        for band in BANDS:
            band_cols = [col for col in df.columns if col.startswith(band)]
            
            if not band_cols:
                return "Error", "CSV file format is incorrect or missing expected band columns.", 0.0

            avg_power = df[band_cols].mean().mean()
            average_powers[band] = avg_power

        dominant_band = max(average_powers, key=average_powers.get)
        dominant_power = average_powers[dominant_band]
        inferred_state = STATE_MAP.get(dominant_band, 'Analysis failed.')

        return dominant_band, inferred_state, dominant_power

    except Exception as e:
        return "Analysis Error", f"Failed to process CSV file: {e}", 0.0


# --- 2. DJANGO VIEW FUNCTION FOR ANALYSIS ---

def analyze_upload(request):
    """
    Handles file upload, analysis, saving results, and cleans up the file.
    """
    if request.method == 'POST':
        if 'eeg_file' in request.FILES:
            uploaded_file = request.FILES['eeg_file']
            
            # 1. Analyze the file (occurs in memory, very fast)
            dominant_band, inferred_state, avg_power = analyze_eeg_file(uploaded_file)
            
            # Reset file pointer for saving
            uploaded_file.seek(0)

            # 2. Save the file and results to the model (for persistence)
            session = EEGSession(
                csv_file=uploaded_file, 
                dominant_band=dominant_band, 
                inferred_state=inferred_state, 
                avg_power=avg_power
            )
            session.save()
            
            # --- FILE DELETION LOGIC ---
            try:
                # Use os.path.join with MEDIA_ROOT to get the absolute path
                file_path = session.csv_file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                    session.csv_file.name = '' 
                    session.save()
                    print(f"Successfully deleted temporary file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {session.csv_file.name}: {e}")
            # --- END FILE DELETION ---
            
            # 3. Store results in the session for display on the front end
            request.session['eeg_analysis_results'] = {
                'dominant_band': dominant_band,
                'inferred_state': inferred_state,
                'avg_power': f"{avg_power:.4f}",
                'file_name': uploaded_file.name
            }
            
            # Redirect back to the source page
            next_url = request.POST.get('next', '/')
            return redirect(next_url)

    return redirect('/')

# NOTE: You MUST update your existing view (the one rendering vton_demo.html)
# to retrieve the results from the session like this:
"""
def vton_demo_view(request):
    # This is the essential part: grab the results and clear the session.
    eeg_results = request.session.pop('eeg_analysis_results', None) 
    
    context = {
        'eeg_results': eeg_results,
        # ... your existing context variables (companies, product_id, etc.)
    }
    return render(request, 'vton_demo.html', context)
"""