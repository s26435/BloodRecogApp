import torch
import os
from detectron2.config import get_cfg, CfgNode
from detectron2.data.datasets import register_coco_instances
from detectron2 import model_zoo
from src.augmented_trainer import AugmentedTrainer, visualize_random_val_samples # noqa: F401


def train_new_model(output_dir: str, datset_dir: str = ""):
    model: str = "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"
    cfg: CfgNode = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file(model))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.0
    cfg.MODEL.WEIGHTS = (
            model_zoo.get_checkpoint_url(model)
        )
    cfg.INPUT.FORMAT = "BGR"
    cfg.DATALOADER.NUM_WORKERS = 8
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 4
    cfg.SOLVER.AMP.ENABLED = True
    cfg.SOLVER.CHECKPOINT_PERIOD = 1000000
    cfg.TEST.EVAL_PERIOD = 500
    #cfg.SOLVER.LOGGING_PERIOD = 1
    cfg.SOLVER.NESTEROV = True
    cfg.SOLVER.CLIP_GRADIENTS.ENABLED = True
    cfg.SOLVER.CLIP_GRADIENTS.CLIP_TYPE = "norm"
    cfg.SOLVER.CLIP_GRADIENTS.CLIP_VALUE = 1.0
    cfg.SOLVER.CLIP_GRADIENTS.NORM_TYPE = 2.0
    cfg.SOLVER.LR_SCHEDULER_NAME = "WarmupCosineLR"
    cfg.SOLVER.WARMUP_FACTOR = 1.0 / 1000
    cfg.SOLVER.WARMUP_ITERS = 100
    cfg.SOLVER.WARMUP_METHOD = "linear"
    cfg.SOLVER.BASE_LR_END = 1e-7
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128
    train: str = f"{datset_dir}Blood-1/train"
    val: str = f"{datset_dir}Blood-1/valid"
    register_coco_instances(
                "train", {}, f"{train}/_annotations.coco.json", f"{train}"
            )
    register_coco_instances(
                "val", {}, f"{val}/_annotations.coco.json", f"{val}"
            )
    cfg.DATASETS.TRAIN = ("train",)
    cfg.DATASETS.TEST = ("val",)
    cfg.SOLVER.MAX_ITER = 3500 #200 mi wystarczy do testow dzialania strony
    cfg.OUTPUT_DIR = output_dir
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    cfg.MODEL.DEVICE = device
    with open(os.path.join(cfg.OUTPUT_DIR, "config.yaml"), "w") as f:
        f.write(cfg.dump())
    trainer = AugmentedTrainer(cfg)
    trainer.resume_or_load(resume=False)
    trainer.train()