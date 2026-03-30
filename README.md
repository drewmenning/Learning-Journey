# neural-networks-generative-ai-assignment

## Overview
This repository contains my Module 10 assignment on neural networks and generative AI.

## Files
- `neural_networks_generative_ai_assignment.ipynb` - main notebook for the assignment
- `requirements.txt` - Python packages needed to run the notebook

## Assignment Summary
For this assignment, I used the Fashion-MNIST dataset and built a simple convolutional neural network in TensorFlow / Keras. I first trained a baseline model and recorded its test accuracy. Then I added image augmentation using Keras preprocessing layers and retrained the model. Finally, I compared the test accuracy before and after augmentation and reflected on the impact of generative AI techniques on model performance.

## Dataset
Fashion-MNIST is a dataset of 28x28 grayscale clothing images across 10 classes.

## Model
The model is a small CNN with:
- two convolutional layers
- max pooling
- one dense hidden layer with ReLU
- dropout for regularization
- a softmax output layer for 10 classes

## Results
After running the notebook, update this section with your results:

- Baseline test accuracy: `______`
- Augmented test accuracy: `______`
- Difference: `______`

## Reflection
This assignment showed that data augmentation can help a neural network generalize better by exposing it to more variation during training. It also showed that augmentation choices matter. Realistic transformations can improve robustness, while overly aggressive transformations can reduce performance.

## How to Run
1. Open the notebook in Google Colab or Jupyter.
2. Install TensorFlow if needed:
   ```bash
   pip install tensorflow
   ```
3. Run all cells in order.
4. Copy the final accuracy values into the Results section above.
5. Push the notebook and README to GitHub.

## Repository Name
Use this exact public repository name:
`neural-networks-generative-ai-assignment`
