import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
import torch.nn.functional as F
from PIL import Image
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ResNet50FeatureExtractor(nn.Module):
    """
    ResNet50-based feature extractor for fashion images.

    Uses ImageNet pre-trained weights and extracts 2048-dimensional features
    from the global average pooling layer (before the final classifier).
    """

    def __init__(self, normalize: bool = True, device: str = "cpu"):
        super().__init__()
        self.device = torch.device(device)

        # Load pre-trained ResNet50
        self.backbone = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)

        # Remove the final classification layer
        self.backbone = nn.Sequential(*list(self.backbone.children())[:-1])

        # Move to device and set to eval mode
        self.backbone = self.backbone.to(self.device)
        self.backbone.eval()

        # Freeze parameters for inference
        for param in self.backbone.parameters():
            param.requires_grad = False

        self.normalize = normalize

        # Define the standard ImageNet transforms
        self.transforms = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],  # ImageNet means
                    std=[0.229, 0.224, 0.225],  # ImageNet stds
                ),
            ]
        )

        logger.info(f"ResNet50 Feature Extractor initialized on {self.device}")

    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Preprocess a PIL image for ResNet50 input."""
        if image.mode != "RGB":
            image = image.convert("RGB")
        return self.transforms(image)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Extract features from a batch of images."""
        with torch.no_grad():
            # Extract features: (batch_size, 2048, 1, 1)
            features = self.backbone(x)
            # Flatten: (batch_size, 2048)
            features = features.view(features.size(0), -1)

            # L2 normalize for cosine similarity
            if self.normalize:
                features = F.normalize(features, p=2, dim=1)

        return features

    def extract_from_url(self, image_url: str, timeout: int = 10) -> torch.Tensor:
        """Extract features from an image URL."""
        try:
            response = requests.get(image_url, timeout=timeout)
            response.raise_for_status()

            # Validate content type
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                raise ValueError(f"Invalid content type: {content_type}")

            image = Image.open(requests.get(image_url, stream=True).raw)
            return self.extract_from_image(image)

        except Exception as e:
            logger.error(f"Failed to extract features from URL {image_url}: {e}")
            raise

    def extract_from_image(self, image: Image.Image) -> torch.Tensor:
        """Extract features from a PIL image."""
        try:
            # Preprocess and add batch dimension
            img_tensor = self.preprocess_image(image).unsqueeze(0).to(self.device)

            # Extract features
            features = self.forward(img_tensor)
            return features.cpu()

        except Exception as e:
            logger.error(f"Failed to extract features from image: {e}")
            raise

    def extract_batch(self, images: list[Image.Image]) -> torch.Tensor:
        """Extract features from a batch of PIL images."""
        try:
            # Preprocess all images
            tensors = []
            for img in images:
                tensor = self.preprocess_image(img)
                tensors.append(tensor)

            # Stack into batch
            batch_tensor = torch.stack(tensors).to(self.device)

            # Extract features
            features = self.forward(batch_tensor)
            return features.cpu()

        except Exception as e:
            logger.error(f"Failed to extract features from batch: {e}")
            raise

    def get_model_info(self) -> dict:
        """Get information about the model."""
        return {
            "model_name": "ResNet50",
            "weights": "IMAGENET1K_V2",
            "embedding_dim": 2048,
            "normalize": self.normalize,
            "device": str(self.device),
            "input_size": (224, 224),
            "preprocessing": "ImageNet standard normalization",
        }
