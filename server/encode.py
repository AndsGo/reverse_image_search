import towhee
import os
import timm
import torch
from PIL import Image as PILImage

from timm.data.transforms_factory import create_transform
from timm.data import resolve_data_config
from timm.models.factory import create_model

class Resnet50:
    """
    Say something about the ExampleCalass...

    Args:
        args_0 (`type`):
        ...
    """
    def __init__(self):
        # model init
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = create_model("resnet50", pretrained=True, num_classes=1000)
        self.model.to(device)
        self.model.eval()
        config = resolve_data_config({}, model=self.model)
        self.tfms = create_transform(**config)

    def resnet50_extract_feat(self, img_path):
        read_image = PILImage.open(img_path)
        inputs = torch.stack([self.tfms(read_image)])
        features = self.model.forward_features(inputs)
        global_pool = torch.nn.AdaptiveAvgPool2d(1)
        features = global_pool(features)
        features = features.flatten(1)
        os.remove(img_path)
        return features.squeeze(0).detach().numpy()
