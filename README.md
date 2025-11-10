# 🧠💻 NeuroStyle: EEG-Driven Virtual Try-On Platform

## Overview

NeuroStyle is an ambitious, full-stack web application built on **Django** that seamlessly integrates **Virtual Try-On (VTON)** technology with **Brain-Computer Interface (BCI)** data processing. The core mission is to explore how a user's real-time cognitive state, captured via Electroencephalography (EEG), can influence or personalize a virtual clothing try-on experience.

## Key Features

* **Virtual Try-On (VTON) Core:** Utilizes a computer vision model (likely a Hugging Face model, based on testing scripts) to accurately composite new garment images onto a target person's photo. A dedicated HTML page (`vton_demo.html`) serves as the primary front-end for this feature.
* **Django Web Application:** Provides a robust and scalable web framework for the entire platform, handling user interactions, data storage (`db.sqlite3`), and the presentation layer.
* **EEG/BCI Integration:** Processes physiological data by acquiring, handling, and analyzing EEG signals (specifically **Delta, Theta, Alpha, Beta, Gamma** band powers). Dependencies on `muselsl` confirm support for streaming data from devices like the Muse headset. This data is the unique layer informing the "NeuroStyle" experience.

## Setup and Development

This project requires a Python environment managed by **Pipenv** (using `Pipfile`).

1.  **Clone the Repository:**
    ```bash
    git clone [Your Repository URL]
    ```
2.  **Install Dependencies:**
    ```bash
    pipenv install
    pipenv shell
    ```
3.  **Run the Django Server:**
    ```bash
    python manage.py runserver
    ```

## Data and Modeling

EEG band power data is present (`eeg_band_powers*.csv`), indicating a focus on analyzing cognitive states. The application logic connects the VTON outputs to this neuro-data, paving the way for research into personalized digital commerce or cognitive feedback systems.