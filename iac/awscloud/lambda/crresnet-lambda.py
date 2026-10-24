import io
import json
import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
# the lambda file system is read-only except /tmp
os.environ.setdefault("KERAS_HOME", "/tmp/.keras")

import boto3
import cv2
import numpy as np
import skimage.io
from botocore.exceptions import ClientError
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import decode_predictions

label_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagenet_class_index.json")
RESNET50_INPUT_DIMENSIONS = (224, 224)
PREDICT_PATH = "/api/v1/predict"
DEFAULT_FOLDER = "test-image"

# s3 key prefixes inside the bucket, same names as the local folders
IMAGE_FOLDERS = ("test-image", "image", "adversarial", "filter")

IMAGE_BUCKET = os.environ["AllImageFolderS3Bucket"]
# key prefix of the image folders inside the bucket
IMAGE_PREFIX = os.environ.get("AllImageFolderS3Prefix", "storage/").strip("/")

s3 = boto3.client("s3")

# loaded once per execution environment, reused by warm invocations
model = ResNet50(weights="imagenet")

with open(label_path) as f:
    imagenet_classes = {labels[1]: int(idx) for (idx, labels) in json.load(f).items()}


class HttpError(Exception):
    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def get_class_idx(label):
    """obtain imagenet id by label"""
    return imagenet_classes.get(label, None)


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def load_image(folder, image_name):
    key = "/".join(p for p in (IMAGE_PREFIX, folder, image_name) if p)
    try:
        obj = s3.get_object(Bucket=IMAGE_BUCKET, Key=key)
    except ClientError as e:
        if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
            raise HttpError(404, "image not found")
        raise
    return np.array(skimage.io.imread(io.BytesIO(obj["Body"].read())))


def predict(image_name, folder):
    if folder not in IMAGE_FOLDERS:
        raise HttpError(400, f"invalid folder, must be one of {list(IMAGE_FOLDERS)}")

    # reject any path component so only keys directly under the folder prefix are readable
    if image_name != os.path.basename(image_name) or image_name in ("", ".", ".."):
        raise HttpError(400, "invalid image name")

    image = load_image(folder, image_name)
    image = cv2.resize(image, RESNET50_INPUT_DIMENSIONS)
    image = np.expand_dims(image, axis=0)

    predictions = model.predict(image, verbose=0)
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


def lambda_handler(event, context):
    """Handles Function URL / API Gateway HTTP API (v2) and REST API (v1) events: POST /api/v1/predict?image_name=..&folder=.."""
    http = (event.get("requestContext") or {}).get("http") or {}
    method = http.get("method") or event.get("httpMethod")
    path = event.get("rawPath") or event.get("path")

    try:
        if method is not None and method != "POST":
            raise HttpError(405, "method not allowed")
        if path is not None and not path.rstrip("/").endswith(PREDICT_PATH):
            raise HttpError(404, "not found")

        params = event.get("queryStringParameters") or {}
        image_name = params.get("image_name")
        if not image_name:
            raise HttpError(422, "image_name is required")

        return response(200, predict(image_name, params.get("folder") or DEFAULT_FOLDER))
    except HttpError as e:
        return response(e.status_code, {"detail": e.detail})
