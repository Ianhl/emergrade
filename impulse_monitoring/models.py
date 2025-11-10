from django.db import models

class EEGSession(models.Model):
    # Field to store the CSV file uploaded by the user
    csv_file = models.FileField(upload_to='eeg_data/')
    
    # Analysis fields
    dominant_band = models.CharField(max_length=100, blank=True, null=True)
    inferred_state = models.TextField(blank=True, null=True)
    avg_power = models.FloatField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.id} - {self.dominant_band}"
