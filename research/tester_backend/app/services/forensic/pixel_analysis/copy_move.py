import base64
from collections import defaultdict
from typing import Any

import cv2
import numpy as np

from app.core.schemas import BoundingBox


def run_copy_move_analysis(
    img_bgr: np.ndarray
) -> tuple[bool, int, str, list[BoundingBox], dict[str, Any]]:
    """
    Copy-Move Forgery Detection via ORB Keypoint Matching & Displacement Vector Clustering.
    Extracts up to 1500 ORB descriptors, performs Brute-Force Hamming distance matching,
    suppresses spatial neighbors (d < 24px), clusters translation vectors (dx, dy) within +-3px,
    and flags cloned pixel regions with neon-magenta vector lines if >= 4 parallel vectors exist.
    """
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 1. ORB Keypoint & Descriptor Detection
    orb = cv2.ORB_create(nfeatures=1500, fastThreshold=15)
    keypoints, descriptors = orb.detectAndCompute(gray, None)

    clone_canvas = img_bgr.copy()
    bounding_boxes: list[BoundingBox] = []

    if descriptors is None or len(descriptors) < 10:
        _, png_buf = cv2.imencode('.png', clone_canvas)
        clone_b64 = f"data:image/png;base64,{base64.b64encode(png_buf.tobytes()).decode('utf-8')}"
        return False, 0, clone_b64, [], {"keypoints_extracted": 0, "clusters_found": 0}

    # 2. Brute-Force Hamming Matching (k=4)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    raw_matches = bf.knnMatch(descriptors, descriptors, k=4)

    # 3. Filter Matches via Lowe's Ratio Test & Euclidean Constraint
    filtered_pairs = []
    for match_group in raw_matches:
        if len(match_group) < 3:
            continue
        # match_group[0] is self-match (dist 0)
        m1 = match_group[1]
        m2 = match_group[2]

        # Lowe's ratio test for distinctiveness + Hamming distance cap
        if m1.distance <= 35 and (m2.distance > 0 and (m1.distance / float(m2.distance)) <= 0.78):
            pt1 = keypoints[m1.queryIdx].pt
            pt2 = keypoints[m1.trainIdx].pt
            dist = np.hypot(pt1[0] - pt2[0], pt1[1] - pt2[1])
            # Minimum distance between cloned object and original
            if dist >= 35.0:
                pair_key = tuple(sorted([m1.queryIdx, m1.trainIdx]))
                filtered_pairs.append((pair_key, pt1, pt2, m1.distance))

    # Deduplicate pairs
    unique_pairs = {}
    for pair_key, pt1, pt2, dist in filtered_pairs:
        if pair_key not in unique_pairs:
            unique_pairs[pair_key] = (pt1, pt2, dist)

    # 4. Translation Vector Clustering:
    # Vector: (dx, dy) = (pt2_x - pt1_x, pt2_y - pt1_y)
    tolerance = 5.0  # px bin
    vector_clusters = defaultdict(list)

    for (q_idx, t_idx), (pt1, pt2, dist) in unique_pairs.items():
        dx = pt2[0] - pt1[0]
        dy = pt2[1] - pt1[1]
        
        # Normalize direction
        if dx < 0 or (dx == 0 and dy < 0):
            dx, dy = -dx, -dy
            pt1, pt2 = pt2, pt1

        bin_x = int(round(dx / tolerance))
        bin_y = int(round(dy / tolerance))
        vector_clusters[(bin_x, bin_y)].append((pt1, pt2, (dx, dy)))

    # 5. Evaluate Clusters:
    # A true copy-move object has:
    # - >= 10 parallel vectors in the same bin
    # - Localized spatial bounding box (span < 350px) at both source and destination
    significant_clusters = []
    cluster_verification = []
    for (bin_x, bin_y), matches in vector_clusters.items():
        if len(matches) >= 10:
            pts1 = [m[0] for m in matches]
            pts2 = [m[1] for m in matches]
            span1_x = max(p[0] for p in pts1) - min(p[0] for p in pts1)
            span1_y = max(p[1] for p in pts1) - min(p[1] for p in pts1)
            span2_x = max(p[0] for p in pts2) - min(p[0] for p in pts2)
            span2_y = max(p[1] for p in pts2) - min(p[1] for p in pts2)

            # Compact localized object check
            if span1_x < 350 and span1_y < 350 and span2_x < 350 and span2_y < 350:
                # Repeated glyphs can match descriptors without spanning a coherent patch.
                src=np.asarray(pts1,dtype=np.float32);dst=np.asarray(pts2,dtype=np.float32)
                if min(span1_x,span1_y,span2_x,span2_y)<12:
                    continue
                affine,inliers=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2.5,maxIters=500,confidence=.99)
                if affine is None or inliers is None:
                    continue
                accepted=inliers.ravel().astype(bool)
                if accepted.mean()<.8 or accepted.sum()<10:
                    continue
                scale=float(np.hypot(affine[0,0],affine[0,1]))
                if not .9<=scale<=1.1:
                    continue
                significant_clusters.append([m for m,ok in zip(matches,accepted) if ok])
                cluster_verification.append(float(accepted.mean()))

    clone_detected = len(significant_clusters) > 0
    total_clones = sum(len(c) for c in significant_clusters)

    # 6. Render Neon-Magenta Vector Lines on clone_b64
    # Color: Neon Magenta [255, 0, 255] in BGR
    for cluster, inlier_ratio in zip(significant_clusters, cluster_verification):
        pts1 = []
        pts2 = []
        for pt1, pt2, (dx, dy) in cluster:
            p1 = (int(round(pt1[0])), int(round(pt1[1])))
            p2 = (int(round(pt2[0])), int(round(pt2[1])))
            pts1.append(p1)
            pts2.append(p2)

            # Draw vector arrow line
            cv2.arrowedLine(clone_canvas, p1, p2, (255, 0, 255), 2, tipLength=0.2)
            cv2.circle(clone_canvas, p1, 4, (0, 255, 255), -1)  # Yellow source
            cv2.circle(clone_canvas, p2, 4, (255, 0, 255), -1)  # Magenta target

        # Compute bounding boxes enclosing source and clone clusters
        all_x1 = [p[0] for p in pts1]
        all_y1 = [p[1] for p in pts1]
        all_x2 = [p[0] for p in pts2]
        all_y2 = [p[1] for p in pts2]

        pad = 12
        b1_x = max(0, min(all_x1) - pad)
        b1_y = max(0, min(all_y1) - pad)
        b1_w = min(w - b1_x, max(all_x1) - b1_x + pad * 2)
        b1_h = min(h - b1_y, max(all_y1) - b1_y + pad * 2)

        b2_x = max(0, min(all_x2) - pad)
        b2_y = max(0, min(all_y2) - pad)
        b2_w = min(w - b2_x, max(all_x2) - b2_x + pad * 2)
        b2_h = min(h - b2_y, max(all_y2) - b2_y + pad * 2)

        conf = min(0.99, 0.65 + len(cluster) * 0.05)

        bounding_boxes.append(BoundingBox(
            x=int(b2_x),
            y=int(b2_y),
            width=int(b2_w),
            height=int(b2_h),
            points=[[b2_x, b2_y], [b2_x + b2_w, b2_y], [b2_x + b2_w, b2_y + b2_h], [b2_x, b2_y + b2_h]],
            label=f"Repeated-region candidate ({len(cluster)} verified vectors)",
            confidence=round(conf, 2),
            layer=1,
            anomaly_type="CLONED_PIXEL_REGION_DETECTED",
            details={
                "cluster_vector_count": len(cluster),
                "inlier_ratio": round(inlier_ratio, 6),
                "verification": "RANSAC translation/near-unit-scale candidate; not proof of copy-move",
                "source_region": [b1_x, b1_y, b1_w, b1_h]
            }
        ))

    # Encode clone canvas
    _, png_buf = cv2.imencode('.png', clone_canvas)
    clone_b64 = f"data:image/png;base64,{base64.b64encode(png_buf.tobytes()).decode('utf-8')}"

    details = {
        "total_keypoints": len(keypoints),
        "raw_matches": len(unique_pairs),
        "significant_clusters": len(significant_clusters),
        "cloned_keypoint_pairs": total_clones
    }

    return clone_detected, total_clones, clone_b64, bounding_boxes, details
