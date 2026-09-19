from functools import lru_cache
from pathlib import Path

import torch
from PIL import Image
from torchvision import models, transforms


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "waste_classifier_resnet18.pth"
)


CLASS_NAMES = [
    "cardboard",
    "glass",
    "metal",
    "paper",
    "plastic",
    "trash",
]


RECOVERY_STREAM = {
    "cardboard": "RECYCLABLE",
    "glass": "RECYCLABLE",
    "metal": "RECYCLABLE",
    "paper": "RECYCLABLE",
    "plastic": "RECYCLABLE",
    "trash": "RESIDUAL_WASTE",
}


HIGH_CONFIDENCE_THRESHOLD = 0.70
MEDIUM_CONFIDENCE_THRESHOLD = 0.50


def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")

    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


def build_model():
    model = models.resnet18(weights=None)

    in_features = model.fc.in_features

    model.fc = torch.nn.Sequential(
        torch.nn.Dropout(p=0.25),
        torch.nn.Linear(
            in_features,
            len(CLASS_NAMES),
        ),
    )

    return model


@lru_cache(maxsize=1)
def load_classifier():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Classifier model not found at {MODEL_PATH}"
        )

    device = get_device()

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device,
    )

    model = build_model()

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(device)
    model.eval()

    class_names = checkpoint.get(
        "class_names",
        CLASS_NAMES,
    )

    return model, class_names, device


TRANSFORM = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[
                0.485,
                0.456,
                0.406,
            ],
            std=[
                0.229,
                0.224,
                0.225,
            ],
        ),
    ]
)


def get_confidence_level(confidence: float) -> str:
    if confidence >= HIGH_CONFIDENCE_THRESHOLD:
        return "HIGH"

    if confidence >= MEDIUM_CONFIDENCE_THRESHOLD:
        return "MEDIUM"

    return "LOW"


def classify_image(image: Image.Image):
    model, class_names, device = load_classifier()

    image = image.convert("RGB")

    tensor = TRANSFORM(image)
    tensor = tensor.unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(tensor)

        probabilities = torch.softmax(
            outputs,
            dim=1,
        )[0]

    top_k = min(
        3,
        len(class_names),
    )

    top_values, top_indices = torch.topk(
        probabilities,
        k=top_k,
    )

    top_predictions = []

    for value, index in zip(
        top_values.tolist(),
        top_indices.tolist(),
    ):
        top_predictions.append(
            {
                "class_name": class_names[index],
                "confidence": round(
                    float(value),
                    4,
                ),
            }
        )

    predicted_class = top_predictions[0]["class_name"]
    confidence = top_predictions[0]["confidence"]

    confidence_level = get_confidence_level(
        confidence
    )

    return {
        "class_name": predicted_class,
        "confidence": confidence,
        "confidence_level": confidence_level,
        "needs_review": confidence < HIGH_CONFIDENCE_THRESHOLD,
        "top_predictions": top_predictions,
        "recovery_stream": RECOVERY_STREAM.get(
            predicted_class,
            "UNSPECIFIED",
        ),
    }
