from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image
from ultralytics import YOLO


ROOT = Path(__file__).resolve().parents[1]
DATA_YAML = ROOT / "data" / "processed" / "yolo_patchy_fog" / "data.yaml"
DATASET_DIR = ROOT / "data" / "processed" / "yolo_patchy_fog"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def validate_dataset() -> Tuple[Dict[str, int], List[str]]:
    counts: Dict[str, int] = {}
    issues: List[str] = []
    for split in ["train", "val", "test"]:
        image_dir = DATASET_DIR / "images" / split
        label_dir = DATASET_DIR / "labels" / split
        images = sorted(p for p in image_dir.glob("*") if p.suffix.lower() in IMAGE_EXTS)
        labels = sorted(p for p in label_dir.glob("*.txt"))
        counts[f"{split}_images"] = len(images)
        counts[f"{split}_labels"] = len(labels)
        if len(images) != len(labels):
            issues.append(f"{split}: image/label count mismatch: {len(images)} images vs {len(labels)} labels")
        for image_path in images:
            label_path = label_dir / f"{image_path.stem}.txt"
            if not label_path.exists():
                issues.append(f"{split}: missing label for {image_path.name}")
                continue
            try:
                with Image.open(image_path) as image:
                    width, height = image.size
                    image.verify()
                if width < 160 or height < 120:
                    issues.append(f"{split}: image too small: {image_path.name} {width}x{height}")
            except Exception as exc:
                issues.append(f"{split}: unreadable image {image_path.name}: {exc}")
                continue
            lines = label_path.read_text(encoding="utf-8").strip().splitlines()
            if not lines:
                issues.append(f"{split}: empty label {label_path.name}")
                continue
            for line in lines:
                parts = line.split()
                if len(parts) != 5:
                    issues.append(f"{split}: invalid label format {label_path.name}: {line}")
                    continue
                if parts[0] != "0":
                    issues.append(f"{split}: invalid class id {label_path.name}: {line}")
                try:
                    coords = [float(v) for v in parts[1:]]
                except ValueError:
                    issues.append(f"{split}: non-numeric coords {label_path.name}: {line}")
                    continue
                x, y, w, h = coords
                if not all(0.0 <= value <= 1.0 for value in coords):
                    issues.append(f"{split}: coords outside 0-1 {label_path.name}: {line}")
                if w <= 0.0 or h <= 0.0:
                    issues.append(f"{split}: non-positive box size {label_path.name}: {line}")
                if x - w / 2 < -0.001 or x + w / 2 > 1.001 or y - h / 2 < -0.001 or y + h / 2 > 1.001:
                    issues.append(f"{split}: box extends outside image {label_path.name}: {line}")
    return counts, issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train YOLOv8 on the patchy_fog dataset.")
    parser.add_argument("--model", default="yolov8n.pt", help="Ultralytics model checkpoint.")
    parser.add_argument("--epochs", type=int, default=30, help="Training epochs for the first baseline run.")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size.")
    parser.add_argument("--batch", type=int, default=8, help="Batch size. Adjust based on GPU memory.")
    parser.add_argument("--device", default="0", help="Training device, e.g. cpu or 0.")
    parser.add_argument("--workers", type=int, default=2, help="Data loader workers.")
    parser.add_argument("--project", default=str(ROOT / "runs" / "detect"), help="Ultralytics output project directory.")
    parser.add_argument("--name", default="patchy_fog_yolov8n", help="Run name.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    counts, issues = validate_dataset()
    print(json.dumps({"counts": counts, "issues": issues}, ensure_ascii=False, indent=2))
    if issues:
        print("Dataset validation failed; fix labels before training.")
        return 1
    model = YOLO(args.model)
    model.train(
        data=str(DATA_YAML),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        workers=args.workers,
        project=args.project,
        name=args.name,
        pretrained=True,
        seed=42,
        deterministic=True,
        patience=10,
        close_mosaic=5,
        plots=True,
        val=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
