import json
import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import cv2
import numpy as np
import skimage.io
from fastapi import FastAPI, HTTPException
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import decode_predictions

label_path = "imagenet_class_index.json"
RESNET50_INPUT_DIMENSIONS = (224, 224)

# folders mounted as read-only volumes in the container, see resnet50-compose.yaml
IMAGE_FOLDERS = {
    "test-image": "/resnet/test-image",
    "image": "/resnet/image",
    "adversarial": "/resnet/adversarial",
    "filter": "/resnet/filter",
}

app = FastAPI(title="tresnet")

model = ResNet50(weights="imagenet")

with open(label_path) as f:
    imagenet_classes = {labels[1]: int(idx) for (idx, labels) in json.load(f).items()}


def get_class_idx(label):
    """obtain imagenet id by label"""
    return imagenet_classes.get(label, None)


@app.post("/api/v1/predict")
def predict(image_name: str, folder: str = "test-image"):
    base_dir = IMAGE_FOLDERS.get(folder)
    if base_dir is None:
        raise HTTPException(status_code=400, detail=f"invalid folder, must be one of {list(IMAGE_FOLDERS)}")

    # reject any path component so only files inside base_dir are readable
    if image_name != os.path.basename(image_name) or image_name in ("", ".", ".."):
        raise HTTPException(status_code=400, detail="invalid image name")

    filename = os.path.join(base_dir, image_name)
    if not os.path.isfile(filename):
        raise HTTPException(status_code=404, detail="image not found")

    image = np.array(skimage.io.imread(filename))
    image = cv2.resize(image, RESNET50_INPUT_DIMENSIONS)
    image = np.expand_dims(image, axis=0)

    predictions = model.predict(image)
    decoded_predictions = decode_predictions(predictions, top=3)[0]

    back_data = {}
    for i, (imagenet_id, label, prob) in enumerate(decoded_predictions):
        back_data["n" + str(i)] = (
            imagenet_id,
            label,
            str(get_class_idx(label)),
            str(int(prob * 10000) / 100),
        )

    return {"image": image_name, "folder": folder, "predictions": back_data}
