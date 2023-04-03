import logging
from pathlib import Path

import click
import numpy as np
from scipy.io import savemat
from tqdm import tqdm
from pprint import pprint
import torch
from torch.utils.data import DataLoader

from loaders import UnlabelledImageFolder
from models import get_model

logging.basicConfig(level=logging.INFO)


def save_features(arr: np.array, path: Path, format: str) -> None:
    if format == "csv":
        np.savetxt(path, arr, delimiter=",")
    elif format == "npy":
        np.save(path, arr)
    elif format == "mat":
        savemat(path, {"features": arr, "label": "embeddings"})

def encode_images(model, preprocess, input_dir: Path, batch_size: int, device: str) -> np.array:
    dataset = UnlabelledImageFolder(input_dir, preprocess)
    loader = DataLoader(dataset, batch_size, num_workers=128)
    features = [model(xs.to(device)).detach().cpu().numpy() for xs in tqdm(loader)]
    return np.concatenate(features)


@click.command()
@click.argument("input_dir", type=click.Path(exists=False))
@click.argument("output_path", type=click.Path(exists=False))
@click.argument("model_name", type=click.STRING)
@click.argument("batch_size", type=click.INT, default=64)
@click.option("--dirs", "-d", is_flag=True, help="Expect a directory of directories.")
@click.option(
    "--format",
    type=click.Choice(["csv", "npy", "mat"]),
    default="csv",
    help="output format",
)
def encode(input_dir, output_path, model_name, batch_size, dirs, format):
    logging.info("Welcome to Simcoder.")

    Path(output_path).mkdir()

    # find all the directories to look for images in
    if dirs:
        image_dirs = [f for f in Path(input_dir).iterdir() if f.is_dir()]
        image_dirs = sorted(image_dirs, key=lambda p: int(p.name))
    else:
        image_dirs = input_dir
    logging.info(f"Found {len(image_dirs)} image directories.")

    # get the model from torchvision
    logging.info(f"Loading {model_name} model.")
    model, preprocess = get_model(model_name)
    logging.info(model)

    # setup the pytorch device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logging.info(f"Running on device: {device}")
    model.to(device)

    # iterate over the input dirs, encoding and outputting to disk
    for image_dir in image_dirs:
        logging.info(f"Encoding {image_dir}")
        features = encode_images(model, preprocess, image_dir, batch_size, device)
        filepath = Path(output_path, image_dir.stem).with_suffix(f".{format}")
        logging.info(f"Saving embeddings to {filepath}.")
        save_features(features, filepath, format)

    logging.info("Complete.")
