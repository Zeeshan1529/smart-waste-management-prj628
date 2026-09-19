from pathlib import Path
import json
import random

import numpy as np
import pandas as pd
import torch
from PIL import ImageFile
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, models, transforms


ImageFile.LOAD_TRUNCATED_IMAGES = True

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "trashnet"
    / "dataset-resized"
)

MODEL_DIR = PROJECT_ROOT / "ml" / "models"
REPORT_DIR = PROJECT_ROOT / "ml" / "reports"

MODEL_PATH = MODEL_DIR / "waste_classifier_resnet18.pth"
METRICS_PATH = REPORT_DIR / "classification_metrics.json"
CONFUSION_PATH = REPORT_DIR / "confusion_matrix.csv"
REPORT_PATH = REPORT_DIR / "classification_report.csv"

BATCH_SIZE = 32
EPOCHS = 8
LEARNING_RATE = 0.0001

IMAGE_SIZE = 224


def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")

    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


def build_model(num_classes):
    weights = models.ResNet18_Weights.DEFAULT

    model = models.resnet18(weights=weights)

    # Freeze the backbone initially.
    for parameter in model.parameters():
        parameter.requires_grad = False

    # Replace the classification layer.
    in_features = model.fc.in_features

    model.fc = nn.Sequential(
        nn.Dropout(p=0.25),
        nn.Linear(in_features, num_classes),
    )

    return model


def main():
    device = get_device()

    print(f"Using device: {device}")
    print(f"Dataset: {DATA_DIR}")

    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_DIR}"
        )

    train_transform = transforms.Compose(
        [
            transforms.Resize(
                (IMAGE_SIZE, IMAGE_SIZE)
            ),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ColorJitter(
                brightness=0.15,
                contrast=0.15,
                saturation=0.15,
            ),
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

    eval_transform = transforms.Compose(
        [
            transforms.Resize(
                (IMAGE_SIZE, IMAGE_SIZE)
            ),
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

    base_dataset = datasets.ImageFolder(
        root=str(DATA_DIR),
    )

    class_names = base_dataset.classes

    print(f"Classes: {class_names}")
    print(f"Total images: {len(base_dataset)}")

    targets = np.array(
        base_dataset.targets
    )

    indices = np.arange(
        len(base_dataset)
    )

    # 80% training, 20% temporary.
    train_indices, temp_indices = train_test_split(
        indices,
        test_size=0.20,
        random_state=SEED,
        stratify=targets,
    )

    # Split temporary 50/50 -> 10% validation, 10% test.
    temp_targets = targets[temp_indices]

    validation_indices, test_indices = train_test_split(
        temp_indices,
        test_size=0.50,
        random_state=SEED,
        stratify=temp_targets,
    )

    train_dataset_full = datasets.ImageFolder(
        root=str(DATA_DIR),
        transform=train_transform,
    )

    eval_dataset_full = datasets.ImageFolder(
        root=str(DATA_DIR),
        transform=eval_transform,
    )

    train_dataset = Subset(
        train_dataset_full,
        train_indices,
    )

    validation_dataset = Subset(
        eval_dataset_full,
        validation_indices,
    )

    test_dataset = Subset(
        eval_dataset_full,
        test_indices,
    )

    print(
        f"Train images: {len(train_dataset)}"
    )
    print(
        f"Validation images: {len(validation_dataset)}"
    )
    print(
        f"Test images: {len(test_dataset)}"
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )

    model = build_model(
        num_classes=len(class_names)
    ).to(device)

    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.AdamW(
        model.fc.parameters(),
        lr=LEARNING_RATE,
        weight_decay=1e-4,
    )

    best_validation_accuracy = 0.0

    history = []

    for epoch in range(EPOCHS):
        model.train()

        running_loss = 0.0
        train_correct = 0
        train_total = 0

        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            outputs = model(images)

            loss = criterion(
                outputs,
                labels,
            )

            loss.backward()
            optimizer.step()

            running_loss += (
                loss.item()
                * images.size(0)
            )

            predictions = outputs.argmax(
                dim=1
            )

            train_correct += (
                (predictions == labels)
                .sum()
                .item()
            )

            train_total += labels.size(0)

        train_loss = (
            running_loss / train_total
        )

        train_accuracy = (
            train_correct / train_total
        )

        model.eval()

        validation_correct = 0
        validation_total = 0

        with torch.no_grad():
            for images, labels in validation_loader:
                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)

                predictions = outputs.argmax(
                    dim=1
                )

                validation_correct += (
                    (predictions == labels)
                    .sum()
                    .item()
                )

                validation_total += labels.size(0)

        validation_accuracy = (
            validation_correct
            / validation_total
        )

        print(
            f"Epoch {epoch + 1}/{EPOCHS} | "
            f"Train Loss: {train_loss:.4f} | "
            f"Train Acc: {train_accuracy:.4f} | "
            f"Val Acc: {validation_accuracy:.4f}"
        )

        history.append(
            {
                "epoch": epoch + 1,
                "train_loss": train_loss,
                "train_accuracy": train_accuracy,
                "validation_accuracy": validation_accuracy,
            }
        )

        if (
            validation_accuracy
            > best_validation_accuracy
        ):
            best_validation_accuracy = (
                validation_accuracy
            )

            MODEL_DIR.mkdir(
                parents=True,
                exist_ok=True,
            )

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "class_names": class_names,
                    "image_size": IMAGE_SIZE,
                },
                MODEL_PATH,
            )

    # Reload best model.
    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

    all_predictions = []
    all_labels = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)

            outputs = model(images)

            predictions = outputs.argmax(
                dim=1
            )

            all_predictions.extend(
                predictions.cpu().numpy().tolist()
            )

            all_labels.extend(
                labels.numpy().tolist()
            )

    test_accuracy = accuracy_score(
        all_labels,
        all_predictions,
    )

    report_dict = classification_report(
        all_labels,
        all_predictions,
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )

    matrix = confusion_matrix(
        all_labels,
        all_predictions,
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics = {
        "model": "ResNet18 transfer learning",
        "dataset": "TrashNet",
        "classes": class_names,
        "total_images": len(base_dataset),
        "training_images": len(train_dataset),
        "validation_images": len(validation_dataset),
        "test_images": len(test_dataset),
        "best_validation_accuracy": round(
            best_validation_accuracy,
            4,
        ),
        "test_accuracy": round(
            float(test_accuracy),
            4,
        ),
        "macro_precision": round(
            float(
                report_dict["macro avg"]["precision"]
            ),
            4,
        ),
        "macro_recall": round(
            float(
                report_dict["macro avg"]["recall"]
            ),
            4,
        ),
        "macro_f1": round(
            float(
                report_dict["macro avg"]["f1-score"]
            ),
            4,
        ),
    }

    with open(
        METRICS_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {
                "metrics": metrics,
                "history": history,
            },
            file,
            indent=2,
        )

    report_df = pd.DataFrame(
        report_dict
    ).transpose()

    report_df.to_csv(
        REPORT_PATH
    )

    confusion_df = pd.DataFrame(
        matrix,
        index=class_names,
        columns=class_names,
    )

    confusion_df.to_csv(
        CONFUSION_PATH
    )

    print()
    print("Training complete.")
    print(
        f"Best validation accuracy: "
        f"{best_validation_accuracy:.4f}"
    )
    print(
        f"Test accuracy: "
        f"{test_accuracy:.4f}"
    )
    print(
        f"Macro precision: "
        f"{metrics['macro_precision']:.4f}"
    )
    print(
        f"Macro recall: "
        f"{metrics['macro_recall']:.4f}"
    )
    print(
        f"Macro F1: "
        f"{metrics['macro_f1']:.4f}"
    )
    print()
    print(f"Model: {MODEL_PATH}")
    print(f"Metrics: {METRICS_PATH}")
    print(f"Report: {REPORT_PATH}")
    print(f"Confusion matrix: {CONFUSION_PATH}")


if __name__ == "__main__":
    main()
