"""
Face Detector Evaluation Service

Evaluates face detectors using:
    - Ground-truth bounding boxes
    - IoU-based matching
    - TP / FP / FN
    - Image-level TN
    - Precision
    - Recall
    - F1-score
    - Accuracy
    - Processing time

IMPORTANT:
    TP / FP / FN are calculated from actual detector predictions.
    TN is calculated at IMAGE LEVEL because ordinary object/face
    detection does not have a meaningful per-face TN.
"""

import cv2
import numpy as np
import time

from app.models import (
    TestImage,
    GroundTruthAnnotation,
    DetectorEvaluation,
    EvaluationRun
)

from app.services.face_detection import (
    detect_faces_mtcnn,
    detect_faces_haar,
    detect_faces_dnn,
    detect_faces_retinaface
)

from app import db
from datetime import datetime


class DetectorEvaluator:
    """Evaluate face detectors against ground-truth annotations."""

    # ============================================================
    # IoU
    # ============================================================

    @staticmethod
    def calculate_iou(box1, box2):
        """
        Calculate IoU between two boxes.

        Expected format:
            [x, y, width, height]

        Returns:
            float between 0.0 and 1.0
        """

        try:
            x1, y1, w1, h1 = map(float, box1)
            x2, y2, w2, h2 = map(float, box2)
        except Exception:
            return 0.0

        # Invalid boxes
        if w1 <= 0 or h1 <= 0 or w2 <= 0 or h2 <= 0:
            return 0.0

        # Convert to x1,y1,x2,y2
        box1_x1 = x1
        box1_y1 = y1
        box1_x2 = x1 + w1
        box1_y2 = y1 + h1

        box2_x1 = x2
        box2_y1 = y2
        box2_x2 = x2 + w2
        box2_y2 = y2 + h2

        # Intersection
        inter_x1 = max(box1_x1, box2_x1)
        inter_y1 = max(box1_y1, box2_y1)
        inter_x2 = min(box1_x2, box2_x2)
        inter_y2 = min(box1_y2, box2_y2)

        inter_width = max(0.0, inter_x2 - inter_x1)
        inter_height = max(0.0, inter_y2 - inter_y1)

        intersection_area = inter_width * inter_height

        # Areas
        area1 = w1 * h1
        area2 = w2 * h2

        union_area = area1 + area2 - intersection_area

        if union_area <= 0:
            return 0.0

        return intersection_area / union_area

    # ============================================================
    # Box normalization
    # ============================================================

    @staticmethod
    def normalize_box(box):
        """
        Convert a bounding box into:

            [x, y, width, height]

        Supported common formats:
            - list / tuple / numpy array
            - dictionary containing x,y,w,h
            - dictionary containing x,y,width,height
            - dictionary containing x1,y1,x2,y2

        NOTE:
            For a plain 4-value list, the evaluator assumes
            [x, y, width, height], matching the existing project.
        """

        try:

            # ----------------------------------------------------
            # Dictionary
            # ----------------------------------------------------
            if isinstance(box, dict):

                # x,y,w,h
                if all(k in box for k in ("x", "y", "w", "h")):
                    x = float(box["x"])
                    y = float(box["y"])
                    w = float(box["w"])
                    h = float(box["h"])

                    return [
                        int(round(x)),
                        int(round(y)),
                        int(round(w)),
                        int(round(h))
                    ]

                # x,y,width,height
                if all(k in box for k in ("x", "y", "width", "height")):
                    x = float(box["x"])
                    y = float(box["y"])
                    w = float(box["width"])
                    h = float(box["height"])

                    return [
                        int(round(x)),
                        int(round(y)),
                        int(round(w)),
                        int(round(h))
                    ]

                # x1,y1,x2,y2
                if all(k in box for k in ("x1", "y1", "x2", "y2")):
                    x1 = float(box["x1"])
                    y1 = float(box["y1"])
                    x2 = float(box["x2"])
                    y2 = float(box["y2"])

                    return [
                        int(round(x1)),
                        int(round(y1)),
                        int(round(x2 - x1)),
                        int(round(y2 - y1))
                    ]

                # bbox nested inside dictionary
                if "bbox" in box:
                    return DetectorEvaluator.normalize_box(box["bbox"])

                return None

            # ----------------------------------------------------
            # Numpy / list / tuple
            # ----------------------------------------------------
            values = list(box)

            if len(values) != 4:
                return None

            x, y, w, h = map(float, values)

            if w <= 0 or h <= 0:
                return None

            return [
                int(round(x)),
                int(round(y)),
                int(round(w)),
                int(round(h))
            ]

        except Exception as e:
            print(f"WARNING: Could not normalize box {box}: {e}")
            return None

    # ============================================================
    # Matching
    # ============================================================

    @staticmethod
    def match_predictions_to_ground_truth(
        predicted_boxes,
        ground_truth_boxes,
        iou_threshold=0.5
    ):
        """
        Match predictions to ground truth using greedy highest-IoU
        matching.

        Rules:

            IoU >= threshold:
                prediction + GT = TP

            Unmatched prediction:
                FP

            Unmatched GT:
                FN
        """

        # Safety
        predicted_boxes = predicted_boxes or []
        ground_truth_boxes = ground_truth_boxes or []

        # --------------------------------------------------------
        # No ground truth
        # --------------------------------------------------------
        if len(ground_truth_boxes) == 0:

            return {
                "true_positives": 0,
                "false_positives": len(predicted_boxes),
                "false_negatives": 0,
                "matched_pairs": []
            }

        # --------------------------------------------------------
        # No predictions
        # --------------------------------------------------------
        if len(predicted_boxes) == 0:

            return {
                "true_positives": 0,
                "false_positives": 0,
                "false_negatives": len(ground_truth_boxes),
                "matched_pairs": []
            }

        # --------------------------------------------------------
        # IoU matrix
        # --------------------------------------------------------
        iou_matrix = np.zeros(
            (
                len(predicted_boxes),
                len(ground_truth_boxes)
            ),
            dtype=float
        )

        for pred_index, pred_box in enumerate(predicted_boxes):

            for gt_index, gt_box in enumerate(ground_truth_boxes):

                iou_matrix[pred_index, gt_index] = (
                    DetectorEvaluator.calculate_iou(
                        pred_box,
                        gt_box
                    )
                )

        # --------------------------------------------------------
        # Debug IoU matrix
        # --------------------------------------------------------
        print("\nIoU MATRIX:")

        for i in range(len(predicted_boxes)):

            values = [
                f"{iou_matrix[i, j]:.3f}"
                for j in range(len(ground_truth_boxes))
            ]

            print(
                f"Prediction {i}: "
                + ", ".join(values)
            )

        # --------------------------------------------------------
        # Greedy matching
        # --------------------------------------------------------
        matched_predictions = set()
        matched_ground_truth = set()

        matched_pairs = []

        iou_pairs = []

        for pred_index in range(len(predicted_boxes)):

            for gt_index in range(len(ground_truth_boxes)):

                iou = iou_matrix[
                    pred_index,
                    gt_index
                ]

                if iou >= iou_threshold:

                    iou_pairs.append(
                        (
                            pred_index,
                            gt_index,
                            float(iou)
                        )
                    )

        # Highest IoU first
        iou_pairs.sort(
            key=lambda x: x[2],
            reverse=True
        )

        for pred_index, gt_index, iou in iou_pairs:

            if pred_index in matched_predictions:
                continue

            if gt_index in matched_ground_truth:
                continue

            matched_predictions.add(pred_index)
            matched_ground_truth.add(gt_index)

            matched_pairs.append(
                (
                    pred_index,
                    gt_index,
                    iou
                )
            )

        # --------------------------------------------------------
        # Final TP / FP / FN
        # --------------------------------------------------------

        tp = len(matched_pairs)

        fp = (
            len(predicted_boxes)
            - tp
        )

        fn = (
            len(ground_truth_boxes)
            - tp
        )

        return {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "matched_pairs": matched_pairs
        }

    # ============================================================
    # Metrics
    # ============================================================

    @staticmethod
    def calculate_metrics(tp, fp, fn, tn=0):
        """
        Calculate standard classification metrics.

        Precision:
            TP / (TP + FP)

        Recall:
            TP / (TP + FN)

        F1:
            harmonic mean of precision and recall

        Accuracy:
            (TP + TN) /
            (TP + TN + FP + FN)
        """

        # Precision
        precision = (
            tp / (tp + fp)
            if (tp + fp) > 0
            else 0.0
        )

        # Recall
        recall = (
            tp / (tp + fn)
            if (tp + fn) > 0
            else 0.0
        )

        # F1
        f1_score = (
            2 * precision * recall /
            (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        # Standard accuracy
        total = tp + tn + fp + fn

        accuracy = (
            (tp + tn) / total
            if total > 0
            else 0.0
        )

        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "accuracy": accuracy
        }

    # ============================================================
    # Evaluate detector on one image
    # ============================================================

    @staticmethod
    def evaluate_detector_on_image(
        detector_func,
        image_path,
        ground_truth_boxes,
        min_confidence=0.7,
        iou_threshold=0.5
    ):
        """
        Evaluate one detector on one image.
        """

        # --------------------------------------------------------
        # Load image
        # --------------------------------------------------------

        image = cv2.imread(image_path)

        if image is None:

            print(
                f"ERROR: Could not load image: "
                f"{image_path}"
            )

            return None

        # --------------------------------------------------------
        # Convert BGR -> RGB
        # --------------------------------------------------------

        rgb_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        # --------------------------------------------------------
        # Run detector
        # --------------------------------------------------------

        start_time = time.time()

        try:

            detected_faces = detector_func(
                rgb_image,
                min_confidence=min_confidence
            )

        except TypeError:

            # Some detector functions may not accept
            # min_confidence.
            try:

                detected_faces = detector_func(
                    rgb_image
                )

            except Exception as e:

                print(
                    f"ERROR running detector: {e}"
                )

                return None

        except Exception as e:

            print(
                f"ERROR running detector: {e}"
            )

            return None

        processing_time = (
            time.time() - start_time
        ) * 1000

        if detected_faces is None:
            detected_faces = []

        # --------------------------------------------------------
        # Normalize predicted boxes
        # --------------------------------------------------------

        predicted_boxes = []

        print("\n----------------------------------------")
        print("RAW DETECTOR OUTPUT")
        print("----------------------------------------")
        print(detected_faces)

        for face_index, face_data in enumerate(
            detected_faces
        ):

            try:

                # ------------------------------------------------
                # Existing project format:
                #
                # face_data[1] = bounding box
                #
                # Keep compatibility with your existing code.
                # ------------------------------------------------

                box = None

                if isinstance(face_data, dict):

                    box = face_data.get(
                        "bbox",
                        face_data
                    )

                elif isinstance(
                    face_data,
                    (list, tuple, np.ndarray)
                ):

                    # Existing format appears to be:
                    #
                    # [confidence, box]
                    #
                    # If second item is itself a box,
                    # use it.

                    if (
                        len(face_data) >= 2
                        and isinstance(
                            face_data[1],
                            (
                                list,
                                tuple,
                                np.ndarray,
                                dict
                            )
                        )
                    ):

                        box = face_data[1]

                    elif len(face_data) == 4:

                        box = face_data

                normalized_box = (
                    DetectorEvaluator.normalize_box(
                        box
                    )
                )

                if normalized_box is None:
                    print(
                        f"WARNING: Invalid prediction "
                        f"#{face_index}: {face_data}"
                    )
                    continue

                predicted_boxes.append(
                    normalized_box
                )

            except Exception as e:

                print(
                    f"WARNING parsing detection "
                    f"#{face_index}: {e}"
                )

        # --------------------------------------------------------
        # Normalize ground truth
        # --------------------------------------------------------

        normalized_gt = []

        for gt_index, box in enumerate(
            ground_truth_boxes or []
        ):

            normalized_box = (
                DetectorEvaluator.normalize_box(
                    box
                )
            )

            if normalized_box is None:

                print(
                    f"WARNING: Invalid GT box "
                    f"#{gt_index}: {box}"
                )

                continue

            normalized_gt.append(
                normalized_box
            )

        # --------------------------------------------------------
        # Basic debug
        # --------------------------------------------------------

        print("\n========================================")
        print("DETECTION EVALUATION")
        print("========================================")

        print(
            f"Ground Truth Faces : "
            f"{len(normalized_gt)}"
        )

        print(
            f"Predicted Faces    : "
            f"{len(predicted_boxes)}"
        )

        print(
            f"IoU Threshold      : "
            f"{iou_threshold}"
        )

        print(
            f"Confidence         : "
            f"{min_confidence}"
        )

        print("\nGT BOXES:")

        for i, box in enumerate(normalized_gt):
            print(f"  GT {i}: {box}")

        print("\nPREDICTED BOXES:")

        for i, box in enumerate(predicted_boxes):
            print(f"  PRED {i}: {box}")

        # --------------------------------------------------------
        # IoU matching
        # --------------------------------------------------------

        result = (
            DetectorEvaluator
            .match_predictions_to_ground_truth(
                predicted_boxes,
                normalized_gt,
                iou_threshold
            )
        )

        # --------------------------------------------------------
        # TP / FP / FN
        # --------------------------------------------------------

        tp = result["true_positives"]
        fp = result["false_positives"]
        fn = result["false_negatives"]

        # --------------------------------------------------------
        # IMAGE-LEVEL TN
        #
        # TN exists only when:
        #
        #     image has NO GT face
        #     AND
        #     detector predicts NO face
        #
        # Then this image is a true negative.
        #
        # This avoids incorrectly treating missed faces as TN.
        # --------------------------------------------------------

        has_ground_truth_face = (
            len(normalized_gt) > 0
        )

        detector_found_face = (
            len(predicted_boxes) > 0
        )

        tn = 1 if (
            not has_ground_truth_face
            and
            not detector_found_face
        ) else 0

        # --------------------------------------------------------
        # Debug result
        # --------------------------------------------------------

        print("\nRESULT:")

        print(f"  TP = {tp}")
        print(f"  FP = {fp}")
        print(f"  FN = {fn}")
        print(f"  TN = {tn}")

        print(
            f"  TP + FN = "
            f"{tp + fn}"
        )

        print(
            f"  GT      = "
            f"{len(normalized_gt)}"
        )

        print(
            f"  TP + FP = "
            f"{tp + fp}"
        )

        print(
            f"  Predictions = "
            f"{len(predicted_boxes)}"
        )

        # --------------------------------------------------------
        # Return
        # --------------------------------------------------------

        return {
            "processing_time_ms": processing_time,

            "num_detected": len(
                predicted_boxes
            ),

            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,

            "matched_pairs": result[
                "matched_pairs"
            ],

            "predicted_boxes": predicted_boxes,

            "ground_truth_boxes": normalized_gt
        }

    # ============================================================
    # Run complete evaluation
    # ============================================================

    @staticmethod
    def run_evaluation(
        detector_name="all",
        iou_threshold=0.5,
        confidence_threshold=0.7,
        dataset_name="default"
    ):
        """
        Run evaluation on all annotated test images.

        detector_name:
            mtcnn
            haar
            dnn
            retinaface
            all
        """

        # --------------------------------------------------------
        # Get annotated test images
        # --------------------------------------------------------

        test_images = (
            TestImage.query
            .filter_by(is_annotated=True)
            .all()
        )

        if not test_images:

            return {
                "error": "No annotated test images found",
                "message": (
                    "Please upload and annotate "
                    "test images first"
                )
            }

        # --------------------------------------------------------
        # Create evaluation run
        # --------------------------------------------------------

        run = EvaluationRun(
            run_name=(
                f"Evaluation_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            ),
            dataset_name=dataset_name,
            num_images=len(test_images),
            iou_threshold=iou_threshold
        )

        db.session.add(run)

        try:

            db.session.commit()

        except Exception as e:

            db.session.rollback()

            print(
                f"Error creating evaluation run: "
                f"{e}"
            )

            return {
                "error": "Database error",
                "message": str(e)
            }

        # --------------------------------------------------------
        # Total GT faces
        # --------------------------------------------------------

        total_gt_faces = 0

        for img in test_images:

            total_gt_faces += (
                img.annotations.count()
            )

        run.num_ground_truth_faces = (
            total_gt_faces
        )

        try:

            db.session.commit()

        except Exception as e:

            db.session.rollback()

            print(
                f"Error updating GT count: {e}"
            )

        # --------------------------------------------------------
        # Detectors
        # --------------------------------------------------------

        detectors = {

            "mtcnn":
                detect_faces_mtcnn,

            "haar":
                detect_faces_haar,

            "dnn":
                detect_faces_dnn,

            "retinaface":
                detect_faces_retinaface
        }

        # --------------------------------------------------------
        # Select detector
        # --------------------------------------------------------

        if detector_name != "all":

            if detector_name not in detectors:

                return {
                    "error":
                        f"Unknown detector: "
                        f"{detector_name}"
                }

            detectors = {
                detector_name:
                    detectors[detector_name]
            }

        results = {}

        # ========================================================
        # Evaluate every detector
        # ========================================================

        for det_name, det_func in detectors.items():

            print("\n")
            print("=" * 60)
            print(
                f"EVALUATING {det_name.upper()}"
            )
            print("=" * 60)

            # ----------------------------------------------------
            # Totals
            # ----------------------------------------------------

            total_tp = 0
            total_fp = 0
            total_fn = 0
            total_tn = 0

            total_time = 0
            total_detected = 0

            processing_times = []

            successful_images = 0

            # ----------------------------------------------------
            # Every image
            # ----------------------------------------------------

            for image_index, test_img in enumerate(
                test_images,
                start=1
            ):

                print("\n")
                print(
                    f"Processing image "
                    f"{image_index}/"
                    f"{len(test_images)}: "
                    f"{test_img.filename}"
                )

                # ------------------------------------------------
                # Ground truth
                # ------------------------------------------------

                gt_boxes = []

                for ann in test_img.annotations:

                    try:

                        gt_boxes.append(
                            ann.get_box()
                        )

                    except Exception as e:

                        print(
                            f"WARNING: Could not "
                            f"read annotation: {e}"
                        )

                # ------------------------------------------------
                # Evaluate image
                # ------------------------------------------------

                result = (
                    DetectorEvaluator
                    .evaluate_detector_on_image(
                        det_func,
                        test_img.filepath,
                        gt_boxes,
                        min_confidence=(
                            confidence_threshold
                        ),
                        iou_threshold=(
                            iou_threshold
                        )
                    )
                )

                if result is None:

                    print(
                        f"FAILED: "
                        f"{test_img.filename}"
                    )

                    continue

                successful_images += 1

                # ------------------------------------------------
                # Accumulate
                # ------------------------------------------------

                total_tp += (
                    result["true_positives"]
                )

                total_fp += (
                    result["false_positives"]
                )

                total_fn += (
                    result["false_negatives"]
                )

                total_tn += (
                    result["true_negatives"]
                )

                total_time += (
                    result["processing_time_ms"]
                )

                total_detected += (
                    result["num_detected"]
                )

                processing_times.append(
                    result["processing_time_ms"]
                )

                # ------------------------------------------------
                # Per-image summary
                # ------------------------------------------------

                print(
                    "\nIMAGE SUMMARY:"
                )

                print(
                    f"  GT : "
                    f"{len(gt_boxes)}"
                )

                print(
                    f"  Pred : "
                    f"{result['num_detected']}"
                )

                print(
                    f"  TP : "
                    f"{result['true_positives']}"
                )

                print(
                    f"  FP : "
                    f"{result['false_positives']}"
                )

                print(
                    f"  FN : "
                    f"{result['false_negatives']}"
                )

                print(
                    f"  TN : "
                    f"{result['true_negatives']}"
                )

                print(
                    f"  Time : "
                    f"{result['processing_time_ms']:.1f} ms"
                )

            # ----------------------------------------------------
            # Metrics
            # ----------------------------------------------------

            metrics = (
                DetectorEvaluator
                .calculate_metrics(
                    total_tp,
                    total_fp,
                    total_fn,
                    total_tn
                )
            )

            # ----------------------------------------------------
            # Average processing time
            # ----------------------------------------------------

            avg_time = (
                total_time / successful_images
                if successful_images > 0
                else 0.0
            )

            # ----------------------------------------------------
            # Overall summary
            # ----------------------------------------------------

            print("\n")
            print("=" * 60)
            print(
                f"{det_name.upper()} FINAL RESULTS"
            )
            print("=" * 60)

            print(
                f"Images evaluated : "
                f"{successful_images}"
            )

            print(
                f"Ground truth     : "
                f"{total_gt_faces}"
            )

            print(
                f"Predictions      : "
                f"{total_detected}"
            )

            print(
                f"TP               : "
                f"{total_tp}"
            )

            print(
                f"FP               : "
                f"{total_fp}"
            )

            print(
                f"FN               : "
                f"{total_fn}"
            )

            print(
                f"TN               : "
                f"{total_tn}"
            )

            print(
                f"Precision        : "
                f"{metrics['precision'] * 100:.2f}%"
            )

            print(
                f"Recall           : "
                f"{metrics['recall'] * 100:.2f}%"
            )

            print(
                f"F1 Score         : "
                f"{metrics['f1_score'] * 100:.2f}%"
            )

            print(
                f"Accuracy         : "
                f"{metrics['accuracy'] * 100:.2f}%"
            )

            print(
                f"Average Time     : "
                f"{avg_time:.2f} ms/image"
            )

            # ----------------------------------------------------
            # Save DB result
            # ----------------------------------------------------

            evaluation = DetectorEvaluation(

                detector_name=det_name,

                dataset_name=dataset_name,

                num_images=len(test_images),

                num_ground_truth_faces=(
                    total_gt_faces
                ),

                num_detected_faces=(
                    total_detected
                ),

                iou_threshold=iou_threshold,

                confidence_threshold=(
                    confidence_threshold
                ),

                true_positives=total_tp,

                false_positives=total_fp,

                false_negatives=total_fn,

                precision=metrics[
                    "precision"
                ],

                recall=metrics[
                    "recall"
                ],

                f1_score=metrics[
                    "f1_score"
                ],

                accuracy=metrics[
                    "accuracy"
                ],

                avg_processing_time_ms=(
                    avg_time
                ),

                total_processing_time_ms=(
                    total_time
                )
            )

            db.session.add(evaluation)

            try:

                db.session.commit()

            except Exception as e:

                db.session.rollback()

                print(
                    f"ERROR saving "
                    f"{det_name}: {e}"
                )

                continue

            # ----------------------------------------------------
            # Results dictionary
            # ----------------------------------------------------

            results[det_name] = {

                "true_positives":
                    total_tp,

                "false_positives":
                    total_fp,

                "false_negatives":
                    total_fn,

                "true_negatives":
                    total_tn,

                "precision":
                    metrics["precision"],

                "recall":
                    metrics["recall"],

                "f1_score":
                    metrics["f1_score"],

                "accuracy":
                    metrics["accuracy"],

                "avg_processing_time_ms":
                    avg_time,

                "total_processing_time_ms":
                    total_time,

                "num_detected_faces":
                    total_detected
            }

        # ========================================================
        # Mark run completed
        # ========================================================

        run.completed = True

        try:

            db.session.commit()

        except Exception as e:

            db.session.rollback()

            print(
                f"Error marking run completed: "
                f"{e}"
            )

        # ========================================================
        # Final return
        # ========================================================

        return {

            "success": True,

            "run_id": run.id,

            "dataset_name": dataset_name,

            "num_images": len(test_images),

            "num_ground_truth_faces":
                total_gt_faces,

            "iou_threshold":
                iou_threshold,

            "confidence_threshold":
                confidence_threshold,

            "results":
                results
        }

    # ============================================================
    # Latest results
    # ============================================================

    @staticmethod
    def get_latest_evaluation_results():
        """
        Get latest stored evaluation for every detector.
        """

        results = {}

        for detector_name in [
            "mtcnn",
            "haar",
            "dnn",
            "retinaface"
        ]:

            latest = (
                DetectorEvaluation.query
                .filter_by(
                    detector_name=detector_name
                )
                .order_by(
                    DetectorEvaluation
                    .timestamp
                    .desc()
                )
                .first()
            )

            if latest:

                results[detector_name] = {

                    "precision":
                        latest.precision * 100
                        if latest.precision is not None
                        else 0,

                    "recall":
                        latest.recall * 100
                        if latest.recall is not None
                        else 0,

                    "f1_score":
                        latest.f1_score * 100
                        if latest.f1_score is not None
                        else 0,

                    "accuracy":
                        latest.accuracy * 100
                        if latest.accuracy is not None
                        else 0,

                    "avg_speed":
                        latest.avg_processing_time_ms
                        / 1000
                        if latest.avg_processing_time_ms
                        else 0,

                    "true_positives":
                        latest.true_positives,

                    "false_positives":
                        latest.false_positives,

                    "false_negatives":
                        latest.false_negatives,

                    "num_images":
                        latest.num_images,

                    "timestamp":
                        latest.timestamp
                }

            else:

                results[detector_name] = None

        return results