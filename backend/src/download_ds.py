from roboflow import Roboflow
import os

def download_ds():
    rf = Roboflow(api_key=os.getenv("ROBOFLOW_KEY", None))
    rf.workspace("davide-1zkpi").project("blood-difns").version(1).download("coco")