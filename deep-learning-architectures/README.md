# Deep Learning Architectures in PyTorch: MLP, CNN and Character-Level LSTM

I built three small networks in PyTorch on CPU: a multilayer perceptron and a convolutional network that classify Fashion-MNIST clothing images, and a character-level LSTM that writes Shakespeare-style text. The image models trained on a 1,000-row subset of Fashion-MNIST and were scored on a separate file of 1,000 test images. I expected the CNN to win, but the MLP reached 80.7% test accuracy against 78.3% for the CNN. The LSTM, trained for 5 epochs on the first 250,000 characters of Tiny Shakespeare, finished at a validation perplexity of 4.74.

![CNN confusion matrix on the 1,000 test images](results/cnn_confusion_matrix.png)

*Read the Shirt row: the CNN got 27 of 99 shirts right and sent most of the rest to Pullover, Coat or T-shirt.*

## What I did

The MLP and the CNN share one data split and one set of optimizer settings, with the seed fixed at 42.

- **Data.** I divided pixel values by 255 and split the 1,000 training rows 800/200, stratified so all 10 classes appear in validation.
- **MLP (Part A).** Hidden layers of 256 and 128 units, ReLU, dropout of 0.2 after each, 10-way output. Adam at 1e-3, batches of 64, 15 epochs.
- **CNN (Part B).** Two convolution blocks (16 then 32 filters, 3x3 kernels, ReLU, 2x2 max pooling), then a 128-unit dense layer with dropout of 0.25. Same optimizer, 12 epochs.
- **Character LSTM (Part C).** The first 250,000 characters of Tiny Shakespeare, last 10% held out, cut into 60-character windows at a stride of 3 so every position predicts the next character. A 64-dimensional embedding, one LSTM layer of 128 hidden units and a linear output over the vocabulary. Adam at 1e-3, 5 epochs, gradients clipped at 1.0, a common guard against loss spikes in LSTMs. The writing sample starts from "ROMEO:" and draws 220 characters at temperature 0.8.

Part D, an optional DCGAN, is not included.

## Results

| Model | Scored on | Epochs | Result |
|---|---|---|---|
| MLP | 1,000 Fashion-MNIST test images | 15 | 80.7% accuracy, loss 0.5679 |
| CNN | 1,000 Fashion-MNIST test images | 12 | 78.3% accuracy, loss 0.5821 |
| Character LSTM | last 10% of the 250,000-character text | 5 | validation loss 1.56, perplexity 4.74 |

The 200-image validation split held up: final validation accuracy was 80.0% for the MLP and 78.0% for the CNN, within a point of each test score.

The MLP's 2.4-point lead on 1,000 images is small enough to be run-to-run noise at this data size, so I read it as a tie rather than a ranking. The CNN was undertrained, not overfit: its training accuracy was only 77.1% at epoch 12 and still climbing, below its validation accuracy of 78.0%. The LSTM had the opposite problem. Validation loss went flat between epochs 4 and 5 (1.5553 to 1.5555) while training loss kept falling to 1.33, so it was starting to overfit.

![CNN loss and accuracy by epoch](results/cnn_training_curves.png)

*Training accuracy (right) was still climbing at epoch 12 and still below validation accuracy, so I think the CNN needed more epochs, not a different design.*

Perplexity 4.74 means each next-character guess is about as uncertain as a fair pick among 4.74 options. The sample shows what that buys: the model learned the script's layout, a speaker's name in capitals above short lines of dialogue. Most of the words are real words, but the lines do not mean anything, and a few words are made up (prevenge, surefore). The full sample is in [results/generated_text.txt](results/generated_text.txt).

```
CORIOLANUS:
Weat's of you:
He shall be said me, and would me
If a man can prevenge is surefore.
```

## What I learned

- Data size mattered more than architecture here. I expected the CNN's edge to show on the full 60,000-image release; with 800 training images it had no room to show it.
- Fixed epoch counts cost me. I gave the CNN 12 epochs and the MLP 15, and the CNN's training accuracy was still climbing when it stopped. The MLP went the other way: validation accuracy peaked at 83.0% at epoch 14 and fell to 80.0% at epoch 15, the weights I scored on the test set. Next time I would stop on validation loss instead of a number picked ahead of time.
- The CNN's misses make sense. Shirt was the worst class by far, confused mostly with other upper-body garments that look alike at 28x28 in grayscale. Coat was also weak at 62 of 99, with 23 called Pullover, and 14 of 94 sneakers were called sandals. Bag was nearly perfect at 113 of 115. More training images are the real fix.
- The LSTM plateaued at epoch 4 with one 128-unit layer, so more epochs would not help. More text or a second layer would be the next thing to try.

## How to run

Everything the code needs is bundled in `data/`, so there is nothing to download.

```bash
pip install -r requirements.txt
jupyter notebook deep-learning-architectures-training.ipynb
```

Run all cells, or run the same code as a script:

```bash
python deep_learning_architectures_training.py
```

Either path retrains all three models (on CPU unless a CUDA GPU is available) and overwrites everything in `results/`. Run both from the repo root, since the code reads `data/` and writes `results/` by relative path.

## Files

- [deep-learning-architectures-training.ipynb](deep-learning-architectures-training.ipynb): trains and scores all three models and writes everything in `results/`.
- `deep_learning_architectures_training.py`: the same training code as a plain script.
- [deep-learning-architectures.ipynb](deep-learning-architectures.ipynb): summary notebook that reads the saved metrics, replots them and holds the written reflection.
- `data/`: `fashion_train.csv` and `fashion_test.csv` (1,000 rows each) and `tinyshakespeare.txt`.
- `results/`: `metrics.json` (scores, per-epoch histories, confusion matrix, generated text), `generated_text.txt`, the training-curve PNGs for each model, plus the CNN confusion matrix and example grids of correct and incorrect CNN predictions.
- `requirements.txt`: the Python packages used.

*Module 11 coursework for the AAS in Artificial Intelligence at DMACC, spring 2026.*
