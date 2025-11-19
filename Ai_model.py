from transformers import AutoImageProcessor

processor = AutoImageProcessor.from_pretrained(
    "google/vit-base-patch16-224",
    cache_dir="./offline_model"
)

print("Model downloaded!")
