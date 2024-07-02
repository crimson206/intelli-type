import torch
import torch.nn as nn
from torch import Tensor
from typing import Tuple
from crimson.intelli_type import IntelliType
from typing import TypeVar, Generic

T = TypeVar("T")


process = """
Process:
    attn: (b, n_h, 1, c/n_h) = audio_query: (b, n_h, 1, c/n_h) * image_key: (b, n_h, w*h, c/n_h)
    queried_value: (b, c) = ( attn: (b, n_h, 1, c/n_h) * v: (b, n_h, h*w, c/n_h) ).reshape
    output: (b, c, h, w) = feature_map: (b, c, h, w) * queried_value(b, c).extend
"""


class FeatureMap(IntelliType, Tensor, Generic[T]):
    """
    Represents a feature map extracted from an image.

    Shape: (batch_size, channels, height, width)
        - channels: Number of features
        ...

    Input Frames ->
    Visual Backbone ->
    Transformer Encoder ->
    [Reshape & Upsample] ->
    FeatureMap
    """


class AudioFeature(IntelliType, Tensor, Generic[T]):
    """
    It is VggishOutput.

    Shape: (batch_size, 1, channels)
        - channels: Number of features

    Input Audio Waves ->
    AudioFeature
    """


class AudioQuery(IntelliType, Tensor, Generic[T]):
    """
    Notice : It is not the AudioQuery from the Audio-Visual Mixer.

    Shape: (batch_size, n_head, 1, channels/n_heads)
        - n_head: Number of attention heads
    """


class ImageKey(IntelliType, Tensor, Generic[T]):
    """
    Represents an image key.

    Shape: (batch_size, n_head, height*width, channels/n_heads)
        - n_head: Number of attention heads
    """


class ImageValue(IntelliType, Tensor, Generic[T]):
    """
    Represents an image value.

    Shape: (batch_size, n_head, height*width, channels/n_heads)
        - n_head: Number of attention heads
    """


class Attn(IntelliType, Tensor, Generic[T]):
    """
    It filters ImageValue out where the AudioQuery and ImageKey are not related.

    Shape: (batch_size, n_head, 1, channels/n_heads)
        - n_head: Number of attention heads
    """


class QueriedValue(IntelliType, Tensor, Generic[T]):
    """
    The channel values play the role of filter preferring to the features more related to the AudioQuery.

    Shape: (batch_size, channels)
        - n_head: Number of attention heads
    """


class FusionMap(IntelliType, Tensor, Generic[T]):
    """
    Represents the output of the CrossModalMixer, combining visual and audio features.

    Shape: (batch_size, channels, height, width)
        - channels: Number of features
        - height, width: Spatial dimensions of the feature map

    FeatureMap, AudioFeature ->
    CrossModalMixer ->
    FusionMap
    """


class CrossModalMixer(nn.Module):
    """
    Mixes audio and visual features using cross-modal attention.
    """

    def __init__(
        self,
        dim: int = 256,
        n_heads: int = 8,
        qkv_bias: bool = False,
        dropout: float = 0.0,
    ):
        super().__init__()

        self.dim = dim
        self.n_heads = n_heads
        self.dropout = dropout
        self.scale = (dim // n_heads) ** -0.5

        self.q_proj = nn.Linear(dim, dim, bias=qkv_bias)
        self.kv_proj = nn.Linear(dim, dim * 2, bias=qkv_bias)
        self.attn_drop = nn.Dropout(dropout)
        self.proj = nn.Linear(dim, dim)
        self.proj_drop = nn.Dropout(dropout)

    def forward(
        self, feature_map: FeatureMap[Tensor], audio_feature: AudioFeature[Tensor]
    ) -> FusionMap[Tensor]:
        """
        Performs the main cross-modal mixing operation.
        """
        q = self.compute_query(audio_feature)
        k, v = self.compute_key_value(feature_map)
        attn = self.compute_attention(q, k)
        x = self.apply_attention(attn, v)
        fusion_map = self.fuse_modalities(feature_map, x)
        return fusion_map

    def _flatten_feature_map(self, feature_map: FeatureMap[Tensor]) -> Tensor:
        """
        Flattens the spatial dimensions of the feature map.
        """
        return feature_map.flatten(2).transpose(1, 2)

    def compute_query(self, audio_feature: AudioFeature[Tensor]) -> AudioQuery[Tensor]:
        """
        Computes the query from the audio feature.
        """
        B, _, C = audio_feature.shape
        q = self.q_proj.forward(audio_feature).reshape(
            B, 1, self.n_heads, C // self.n_heads
        )
        return q.permute(0, 2, 1, 3)

    def compute_key_value(
        self, feature_map: FeatureMap
    ) -> Tuple[ImageKey[Tensor], ImageValue[Tensor]]:
        """
        Computes the key and value from the feature map.
        """
        flatten_map = self._flatten_feature_map(feature_map)
        B, N, C = flatten_map.shape
        kv = self.kv_proj.forward(flatten_map).reshape(
            B, N, 2, self.n_heads, C // self.n_heads
        )
        kv = kv.permute(2, 0, 3, 1, 4)
        return kv.unbind(0)

    def compute_attention(
        self, q: AudioQuery[Tensor], k: ImageKey[Tensor]
    ) -> Attn[Tensor]:
        """
        Computes the attention scores between query and key.
        """
        attn = (q @ k.transpose(-2, -1)) * self.scale
        return attn.softmax(dim=-1)

    def apply_attention(self, attn: Attn[Tensor], v: ImageValue[Tensor]) -> QueriedValue[Tensor]:
        """
        Applies attention scores to the value and processes the result.
        """
        B, _, _, C = v.shape
        x = (attn @ v).transpose(1, 2).reshape(B, 1, C * self.n_heads)
        x = self.proj_drop(self.proj(x))
        return x.sigmoid().squeeze()

    def fuse_modalities(self, feature_map: FeatureMap[Tensor], queried_value: QueriedValue[Tensor]) -> FusionMap[Tensor]:
        """
        Fuses the original feature map with the queried value.
        """
        return torch.einsum("bchw,bc->bchw", feature_map, queried_value)
