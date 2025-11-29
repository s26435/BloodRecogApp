import os
from PIL import Image
from detectron2.config import get_cfg, CfgNode
from detectron2.engine import DefaultPredictor
from detectron2.data import MetadataCatalog
from detectron2.utils.visualizer import ColorMode, VisImage, Visualizer


def run_inference_on_image(
    predictor: DefaultPredictor, cfg: CfgNode, img: Image
) -> VisImage:
    outputs = predictor(img)

    metadata = MetadataCatalog.get(cfg.DATASETS.TEST[0])
    v = Visualizer(
        img[:, :, ::-1],
        metadata=metadata,
        scale=1.0,
        instance_mode=ColorMode.IMAGE_BW,
    )
    return v.draw_instance_predictions(outputs["instances"].to("cpu"))


def build_predictor(out_dir: str) -> DefaultPredictor:
    cfg: CfgNode = get_cfg()
    cfg.merge_from_file(f"{out_dir}/config.yaml")

    trained_weights = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")
    if not os.path.exists(trained_weights):
        raise FileNotFoundError(f"Brak wag w {trained_weights}")

    infer_cfg = cfg.clone()
    infer_cfg.MODEL.WEIGHTS = trained_weights
    infer_cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
    infer_cfg.DATASETS.TEST = ("val",)

    predictor = DefaultPredictor(infer_cfg)
    return predictor, infer_cfg