from django.urls import path
from . import views # Assuming views.py is in the current app directory

urlpatterns = [
    # ... other paths ...
    path('start-eeg-sync/', views.run_full_eeg_process, name='start_eeg_sync'),
]