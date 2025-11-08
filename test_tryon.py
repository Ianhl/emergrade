# test_hf_tryon.py
from vton.hf_tryon import run_tryon

# paths to test images
person_img = "vton/test_img/person.jpg"
garment_img = "vton/test_img/garment.jpg"

# call the function
out_path, masked_path = run_tryon(person_img, garment_img)

print("Try-on completed!")
print("Output image saved at:", out_path)
print("Masked image saved at:", masked_path)
