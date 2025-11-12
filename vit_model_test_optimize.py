import onnxruntime as ort  # type: ignore
from PIL import Image
from transformers import AutoImageProcessor
import numpy as np
import torch

so = ort.SessionOptions()
so.intra_op_num_threads = 4
so.inter_op_num_threads = 1
so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
so.execution_mode = ort.ExecutionMode.ORT_PARALLEL

session = ort.InferenceSession("ai_detector_v2_optimized.onnx", so, providers=["CPUExecutionProvider"])

processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224")
img = Image.open("fallen.jpg").convert("RGB")
inputs = processor(img, return_tensors="np")

outputs = session.run(None, {"pixel_values": inputs["pixel_values"]})
logits = torch.tensor(outputs[0])
probs = torch.nn.functional.softmax(logits, dim=-1)

labels = ["real", "fake"]
label_id = torch.argmax(probs).item()
print(f"Prediction: {labels[label_id]} (confidence: {probs[0][label_id]:.4f})")
