from gradio_client import Client, file

client = Client("JeremelleV/IDM-VTON")  # public space

def run_tryon(human_path, garment_path):
    return client.predict(
        dict={"background": file(human_path), "layers": [], "composite": None},
        garm_img=file(garment_path),
        garment_des="",
        is_checked=True,
        is_checked_crop=True,
        denoise_steps=30,
        seed=42,
        api_name="/tryon",
    )

