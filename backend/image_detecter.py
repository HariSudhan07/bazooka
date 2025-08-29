# backend/image_detecter.py
import cv2
import numpy as np
import os

def non_max_suppression(detections, overlap_thresh=0.3):
    """
    Apply Non-Maximum Suppression (NMS) to remove overlapping symbol detections.
    """
    if not detections:
        return []

    boxes = np.array([
        [d["location"][0], d["location"][1],
         d["location"][0] + d["size"][0], d["location"][1] + d["size"][1]]
        for d in detections
    ])
    confidences = np.array([d["confidence"] for d in detections])
    idxs = np.argsort(confidences)[::-1]  # high → low

    keep = []
    while len(idxs) > 0:
        i = idxs[0]
        keep.append(i)

        # Compute IoU with remaining boxes
        xx1 = np.maximum(boxes[i, 0], boxes[idxs[1:], 0])
        yy1 = np.maximum(boxes[i, 1], boxes[idxs[1:], 1])
        xx2 = np.minimum(boxes[i, 2], boxes[idxs[1:], 2])
        yy2 = np.minimum(boxes[i, 3], boxes[idxs[1:], 3])

        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)
        inter = w * h

        area_i = (boxes[i, 2] - boxes[i, 0]) * (boxes[i, 3] - boxes[i, 1])
        area_rest = (boxes[idxs[1:], 2] - boxes[idxs[1:], 0]) * (boxes[idxs[1:], 3] - boxes[idxs[1:], 1])

        iou = inter / (area_i + area_rest - inter + 1e-6)

        idxs = idxs[1:][iou < overlap_thresh]

    return [detections[i] for i in keep]


def detect_kosher_symbol(image_path, templates_folder="D:/Bazooka/bazooka/symbols/", threshold=0.75, scales=None, visualize=True):
    """
    Detects Kosher symbols in an image using multi-scale template matching.
    Applies Non-Maximum Suppression (NMS) to avoid duplicate detections.
    Returns a list of detected symbols.
    Optionally saves visualization with bounding boxes.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image not found: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    H, W = gray.shape[:2]

    if scales is None:
        scales = [0.5, 0.8, 1.0, 1.2, 1.5]

    template_files = [f for f in os.listdir(templates_folder) if f.lower().endswith((".jpg", ".png"))]
    found_symbols = []

    for template_file in template_files:
        template_path = os.path.join(templates_folder, template_file)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            continue

        h, w = template.shape[:2]

        for scale in scales:
            new_w = int(w * scale)
            new_h = int(h * scale)

            if new_w < 10 or new_h < 10 or new_w > W or new_h > H:
                continue

            resized_template = cv2.resize(template, (new_w, new_h))

            result = cv2.matchTemplate(gray, resized_template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)

            for pt in zip(*locations[::-1]):
                conf = float(result[pt[1], pt[0]])
                found_symbols.append({
                    "symbol": template_file,
                    "confidence": conf,
                    "location": pt,
                    "scale": scale,
                    "size": (new_w, new_h)
                })

    # Apply Non-Maximum Suppression
    final_detections = non_max_suppression(found_symbols, overlap_thresh=0.3)

    # Draw bounding boxes for visualization
    if visualize and final_detections:
        for det in final_detections:
            x, y = det["location"]
            w, h = det["size"]
            print("x,y,w,h:", x, y, w, h)
            if w <= 30 or h <= 30:
                continue
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            label = f"{det['symbol']} ({det['confidence']:.2f})"
            cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        out_path = os.path.splitext(image_path)[0] + "_detected.jpg"
        cv2.imwrite(out_path, img)
        print(f"Visualization saved at: {out_path}")

    return final_detections if final_detections else [{"message": "No Kosher symbol detected"}]
