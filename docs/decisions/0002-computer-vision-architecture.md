# ADR 0002: Computer Vision Architecture

## Status
Accepted

## Context
Sudoku Studio must recognize Sudoku puzzles from uploaded photographs, including blurry, rotated, poorly lit and perspective-distorted images.

## Decision

1. Use OpenCV for image preprocessing and Sudoku grid detection.
2. Detect the Sudoku board and divide it into 81 individual cells.
3. Train a custom CNN for digit recognition.
4. Export the trained model to ONNX format.
5. Use the ONNX model for digit inference in the backend.
6. Provide a manual correction interface when recognition is uncertain.
7. Keep image processing and digit recognition as separate pipeline stages.

## Consequences

- Image processing and digit recognition can be developed and tested independently.
- ONNX provides a portable model format for deployment.
- Robust preprocessing is necessary for real-world photographs.
- Recognition errors must be handled through validation and user correction.