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


class FeatureMap(IntelliType[Tensor], Generic[T]):
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


class AudioFeature(IntelliType[Tensor], Generic[T]):
    """
    VggishOutput representation.

    Shape: (batch_size, 1, channels)
    - channels: Number of audio features

    Input Audio Waves -> AudioFeature
    """


class AudioQuery(IntelliType[Tensor], Generic[T]):
    """
    Audio query for cross-modal attention.
    (Note: Distinct from the Query used in the Audio-Visual Mixer)

    Shape: (batch_size, n_head, 1, channels // n_head)
    - n_head: Number of attention heads
    - channels: Total number of features
    """


class ImageKey(IntelliType[Tensor], Generic[T]):
    """
    Image key for cross-modal attention.

    Shape: (batch_size, n_head, height * width, channels // n_head)
    - n_head: Number of attention heads
    - height, width: Spatial dimensions of the feature map
    - channels: Total number of features
    """


class ImageValue(IntelliType[Tensor], Generic[T]):
    """
    Image value for cross-modal attention.

    Shape: (batch_size, n_head, height * width, channels // n_head)
    - n_head: Number of attention heads
    - height, width: Spatial dimensions of the feature map
    - channels: Total number of features
    """


class Attn(IntelliType[Tensor], Generic[T]):
    """
    It filters ImageValue out where the AudioQuery and ImageKey are not related.

    Shape: (batch_size, n_head, 1, channels // n_heads)
        - n_head: Number of attention heads
    """


class QueriedValue(IntelliType[Tensor], Generic[T]):
    """
    The channel values play the role of filter preferring to the features more related to the AudioQuery.

    Shape: (batch_size, channels)
        - n_head: Number of attention heads
    """


class FusionMap(IntelliType[Tensor], Generic[T]):
    """
    Represents the fused feature map after applying cross-modal attention.

    Shape: (batch_size, channels, height, width)
        - channels: Number of features
        - height, width: Spatial dimensions of the feature map

    This is the output of the CrossModalMixer, combining information from
    the original FeatureMap and the audio-guided attention.
    """


MULTI_HEAD_ATTENTION_NOTE = """
Note on Multi-Head Attention:

Performance effects:
- Allows the model to jointly attend to information from different representation
  subspaces at different positions.
- Expands the model's ability to focus on different portions of the input.
- Enables capturing multiple different relationships between modalities.
- Provides a form of ensemble learning within the attention mechanism.

Computational considerations:
- Theoretically, the overall computational complexity remains O(n^2 * d_model),
  regardless of the number of heads (n_heads).
- Each head operates on reduced dimensionality: d_head = d_model / n_heads.
- In practice, increasing n_heads may lead to:
  1. Slight increase in computational cost due to parallelization overhead.
  2. Increased memory usage.
  3. Potential for improved performance, balanced against diminishing returns
     and increased resource requirements.

The choice of n_heads should be based on the specific task requirements,
available computational resources, and empirical performance evaluations.
"""


class CrossModalMixer(nn.Module):
    """
    Audio-Visual Mixer for cross-modal attention between audio and visual features.

    This module implements a multi-head attention mechanism to fuse information
    from audio and visual modalities. The key components are:

    1. Query projection for audio features
    2. Key-Value projection for visual features
    3. Multi-head attention computation
    4. Output projection and dropout

    Args:
        dim (int): The input and output dimension of features
        n_heads (int): Number of attention heads
        qkv_bias (bool): If True, adds a learnable bias to query, key, value projections
        dropout (float): Dropout rate applied after attention and final projection

    Note:
    This mixer is designed to work with preprocessed audio and visual features.
    The audio features should be of shape (batch_size, 1, dim) and the visual
    features should be of shape (batch_size, height * width, dim).

    For detailed information about multi-head attention and its implications,
    refer to the MULTI_HEAD_ATTENTION_NOTE.
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
        Executes the cross-modal mixing process, fusing audio and visual information.

        This method orchestrates the entire attention mechanism:
        1. Prepares queries from audio and keys/values from visual features
        2. Computes cross-modal attention
        3. Applies attention to aggregate relevant visual information
        4. Fuses the original visual features with audio-guided information

        The result is a feature map enhanced by audio context, potentially
        highlighting visual elements that are most relevant to the audio input.

        Note:
        - This is the main entry point for the CrossModalMixer module
        - The process is end-to-end differentiable, allowing for gradient flow
        between modalities during training
        - The output can be further processed by subsequent layers in a larger
        audio-visual model architecture
        """
        q: AudioQuery[Tensor] = self.compute_query(audio_feature)
        key_and_value = self.compute_key_value(feature_map)
        k: ImageKey[Tensor] = key_and_value[0]
        v: ImageValue[Tensor] = key_and_value[1]
        attn: Attn[Tensor] = self.compute_attention(q, k)
        x: QueriedValue[Tensor] = self.apply_attention(attn, v)
        fusion_map: FusionMap[Tensor] = self.fuse_modalities(feature_map, x)
        return fusion_map

    def _flatten_feature_map(self, feature_map: FeatureMap[Tensor]) -> Tensor:
        return feature_map.flatten(2).transpose(1, 2)

    def compute_query(self, audio_feature: AudioFeature[Tensor]) -> AudioQuery[Tensor]:
        """
        Transforms audio features into multi-head query for cross-modal attention.

        Key operations:
        1. Linear projection of audio features
        2. Reshaping for multi-head attention
        3. Permuting dimensions for compatibility with attention mechanism

        The output query encodes audio content, prepped for computing relevance
        with image features in the attention mechanism.
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
        Transforms the image feature map into key and value tensors for multi-head attention.

        This function performs several crucial steps:
        1. Spatial flattening: Collapses the 2D spatial structure into a sequence of features.
        2. Linear projection: Applies a learned transformation to create a joint key-value representation.
        3. Multi-head splitting: Reshapes the projection for parallel attention heads.
        4. Key-Value separation: Splits the joint representation into distinct key and value tensors.

        The resulting key and value pair encodes the image content in a form that's
        conducive to cross-attention with the audio query. The key tensor will be used
        to compute attention scores, while the value tensor will be used to aggregate
        relevant visual information.
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
        Computes scaled dot-product attention between audio query and image key.

        This function performs three key steps:
        1. Similarity computation: Calculates dot product between query and key.
        2. Scaling: Applies scaling factor to stabilize gradients during training.
        3. Normalization: Uses softmax to convert raw scores into a probability distribution.

        The resulting attention map indicates which spatial locations in the image
        are most relevant to the audio query, enabling cross-modal information exchange.
        """
        attn = (q @ k.transpose(-2, -1)) * self.scale
        return attn.softmax(dim=-1)

    def apply_attention(
        self, attn: Attn[Tensor], v: ImageValue[Tensor]
    ) -> QueriedValue[Tensor]:
        """
        Applies audio-guided attention to image values and processes the result.

        This function performs three key steps:
        1. Attention application: Weights image values based on audio-visual relevance.
        2. Dimensionality reduction: Collapses the spatial dimensions into a single channel.
        3. Feature emphasis: Applies sigmoid to produce a channel-wise importance map.

        The output represents a compact audio-contextualized representation of the image,
        highlighting features that are most relevant to the audio query.
        """
        B, _, _, C = v.shape
        x = (attn @ v).transpose(1, 2).reshape(B, 1, C * self.n_heads)
        x = self.proj_drop(self.proj(x))
        return x.sigmoid().squeeze()

    def fuse_modalities(
        self, feature_map: FeatureMap[Tensor], queried_value: QueriedValue[Tensor]
    ) -> FusionMap[Tensor]:
        """
        Enhances visual features with audio-guided attention.

        This operation amplifies or attenuates each channel of the feature map
        based on its relevance to the audio query. The result is a feature map
        that emphasizes visual elements that are most pertinent to the audio context.
        """
        return torch.einsum("bchw,bc->bchw", feature_map, queried_value)
