# Mini-GPT

A GPT-style language model built from scratch in PyTorch and trained on Shakespeare. Every part is hand-written: attention, layer norm, the feed-forward blocks and the training loop. No pretrained weights and no model libraries.

**Live demo:** https://mini-gpt1.streamlit.app/

## What it does
Predicts the next character, one at a time, and writes Shakespeare-style text from a prompt. The dashboard shows the training curves, a comparison of four models, a model that writes on request, and the architecture.

## Results
| Model | Parameters | Context | Best validation loss |
|---|---|---|---|
| Bigram (baseline) | 4,225 | 1 character | 2.48 |
| One attention head | 7,553 | 8 characters | 2.40 |
| Small GPT (4 layers, 4 heads) | 209,729 | 32 characters | 1.90 |
| **Big GPT (6 layers, 6 heads)** | **10,788,929** | **256 characters** | **1.48** |

Validation loss fell from 4.22 (random guessing) to 1.48. In effect the model went from choosing among all 65 characters to choosing among about 4 at each step.

## Overfitting
Validation loss was best at step 3,500 (1.4776). After that, train loss kept falling (1.10 to 0.95) while validation loss rose (1.48 to 1.53), a sign the model had started memorising the training text. The training script saves a checkpoint whenever validation loss improves, so the deployed model is the best one, not the last.

## Architecture
Decoder-only transformer: token and position embeddings, 6 blocks of masked multi-head self-attention (6 heads x 64 dimensions) and a feed-forward network, each with layer norm and residual connections, then a linear layer over the 65-character vocabulary. 384-dimensional embeddings, dropout 0.2.

## Training
AdamW, learning rate 3e-4, batch of 64 sequences x 256 characters, on a free Google Colab T4 GPU. About 35 minutes to the best checkpoint. Data: Tiny Shakespeare (1.1M characters, 90% train and 10% validation).

## Run it
```
pip install -r requirements.txt
python src/train.py --name small --max_steps 3000
streamlit run src/dashboard.py
```

## Limits
It is a character-level model trained on a small text, so it learns the look of Shakespeare, not meaning. Its sentences are fluent-looking nonsense.

Files: `src/model.py` (the GPT), `src/train.py` (training), `src/data.py` (tokenizer and batches), `src/dashboard.py` (the Streamlit app), `logs/` (loss histories and samples).
