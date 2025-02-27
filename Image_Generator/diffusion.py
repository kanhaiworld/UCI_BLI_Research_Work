model_id = "runwayml/stable-diffusion-v1-5"

from diffusers import StableDiffusionPipeline

from huggingface_hub import notebook_login

notebook_login()

from torch import cuda 

print(cuda.is_available())