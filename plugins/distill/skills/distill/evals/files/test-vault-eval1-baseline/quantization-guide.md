# A Visual Guide to Quantization

**Source:** https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-quantization
**Tags:** ml
**Saved:** 2024-03-31

## What and Why

Quantization reduces model parameter precision from higher bit-widths (e.g., FP32) to lower ones (e.g., INT8). A 70B parameter model in FP32 requires ~280GB of memory. Quantization makes deployment on consumer hardware feasible.

## Core Methods

### Symmetric (Absmax)
Maps the range around zero using the highest absolute value. Formula: `s = (2^(b-1) - 1) / max_abs_value`. Simple but wastes range when data is skewed.

### Asymmetric (Zero-Point)
Maps min/max asymmetrically with both a scaling factor and zero-point offset. More efficient use of available bit-width for skewed distributions.

## Precision Levels

| Format | Compression | Notes |
|--------|------------|-------|
| FP16/BF16 | 2x from FP32 | BF16 maintains FP32's range |
| INT8 | 4x from FP32 | Standard quantization target |
| GPTQ | 8x (4-bit) | Layer-by-layer with inverse-Hessian weighting |
| GGUF | Variable | Block-wise, enables CPU/GPU hybrid inference |
| BitNet 1.58b | ~20x | Ternary weights {-1, 0, 1} |

## Two Approaches

**Post-Training Quantization (PTQ):** Applied after training. Fast and practical but less accurate since training didn't account for quantization effects.

**Quantization Aware Training (QAT):** Incorporates quantization during training via "fake quants" (quantize then dequantize to FP32). Weights settle into flatter loss minima that better tolerate quantization error. Higher quality but requires retraining.

## Weight vs. Activation Quantization

- **Weights** are static and known pre-inference, enabling sophisticated calibration (percentile selection, MSE minimization, KL divergence).
- **Activations** vary per input, requiring either dynamic per-layer calculation or static pre-calibration with representative data.

## BitNet 1.58b: The Extreme End

Adding zero to 1-bit representations enables "feature filtering" - weights can ignore values rather than always add or subtract. Ternary weights eliminate multiplication entirely, replacing it with addition/subtraction. A 13B BitNet 1.58b model beats a 3B FP16 LLM in latency, memory usage, and energy consumption.

## Key Takeaway

Quantization is most effective on larger models where the performance gap between quantized and full-precision narrows significantly. For practical deployment: start with GGUF/GPTQ for immediate gains, consider QAT if you can afford retraining.
