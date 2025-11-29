import os

from detectron2.engine import DefaultTrainer, DefaultPredictor
from detectron2.config import CfgNode
from detectron2.data import transforms as T
from detectron2.data import (
    MetadataCatalog,
    DatasetMapper,
    build_detection_train_loader,
    DatasetCatalog
)
from detectron2.evaluation import COCOEvaluator, DatasetEvaluators
from detectron2.utils.events import CommonMetricPrinter, JSONWriter
from detectron2.utils.visualizer import Visualizer, ColorMode

import random
import cv2


class AugmentedTrainer(DefaultTrainer):

    @classmethod
    def build_train_loader(cls, cfg: CfgNode):
        augmentations = [
            T.RandomBrightness(0.8, 1.2),
            T.RandomContrast(0.8, 1.2),
            T.RandomSaturation(0.8, 1.2),
            T.RandomLighting(0.7),
            T.RandomFlip(prob=0.5, horizontal=True),
            T.RandomRotation(angle=[-10, 10], expand=False),
            T.RandomExtent(scale_range=(0.9, 1.1), shift_range=(0.05, 0.05)),
            T.Resize((800, 800)),
        ]
        mapper: DatasetMapper = DatasetMapper(cfg, is_train=True, augmentations=augmentations)
        return build_detection_train_loader(cfg, mapper=mapper)

    @classmethod
    def build_evaluator(
        cls, cfg: CfgNode, dataset_name: str, output_folder: str = None
    ):
        if output_folder is None:
            output_folder = os.path.join(cfg.OUTPUT_DIR, "inference")
        evaluator_type = MetadataCatalog.get(dataset_name).evaluator_type
        evaluators = []

        if evaluator_type == "coco":
            evaluators.append(COCOEvaluator(dataset_name, cfg, False, output_folder))

        if len(evaluators) == 1:
            return evaluators[0]
        return DatasetEvaluators(evaluators)

    def build_writers(self):
        return [
            CommonMetricPrinter(self.max_iter),
            JSONWriter(os.path.join(self.cfg.OUTPUT_DIR, "metrics.json")),
        ]
    
    def train(self):
        super().train()
        return
    

def visualize_random_val_samples(cfg, num_samples: int = 4):
    val_name = cfg.DATASETS.TEST[0]
    dataset_dicts = DatasetCatalog.get(val_name)
    metadata = MetadataCatalog.get(val_name)

    final_weights = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")
    if os.path.exists(final_weights):
        cfg.MODEL.WEIGHTS = final_weights

    predictor = DefaultPredictor(cfg)

    os.makedirs(os.path.join(cfg.OUTPUT_DIR, "vis_val"), exist_ok=True)

    samples = random.sample(dataset_dicts, k=min(num_samples, len(dataset_dicts)))

    for i, d in enumerate(samples):
        img_path = d["file_name"]
        img = cv2.imread(img_path)
        if img is None:
            print(f"[WARN] Nie mogę wczytać obrazu: {img_path}")
            continue

        outputs = predictor(img)

        v = Visualizer(
            img[:, :, ::-1],
            metadata=metadata,
            scale=0.7,
            instance_mode=ColorMode.IMAGE_BW,
        )

        out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
        out_img = out.get_image()[:, :, ::-1]

        out_path = os.path.join(cfg.OUTPUT_DIR, "vis_val", f"val_vis_{i}.png")
        cv2.imwrite(out_path, out_img)
        print(f"[INFO] Zapisano wizualizację: {out_path}")