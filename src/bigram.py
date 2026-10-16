"""Bigram language model: predict the next character from the current one only."""
import torch
import torch.nn as nn
from torch.nn import functional as F

from data import get_batch, vocab_size, decode

torch.manual_seed(1337)

# Settings
batch_size = 32       # how many chunks of text per training step
block_size = 8        # how many characters in each chunk
max_steps = 3000      # how many training steps
learning_rate = 1e-2
eval_interval = 300   # print the loss every this many steps
eval_iters = 100      # how many batches to average when measuring loss


class BigramLanguageModel(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        # A table with one row per character. Row i holds the scores for
        # "which character comes after character i".
        self.table = nn.Embedding(vocab_size, vocab_size)

    def forward(self, idx, targets=None):
        logits = self.table(idx)  # shape (batch, time, vocab)

        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            logits = logits.view(B * T, C)
            targets = targets.view(B * T)
            loss = F.cross_entropy(logits, targets)
        return logits, loss

    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):
            logits, _ = self(idx)
            logits = logits[:, -1, :]               # scores for the last character
            probs = F.softmax(logits, dim=-1)       # turn scores into probabilities
            next_id = torch.multinomial(probs, 1)   # pick one at random by probability
            idx = torch.cat((idx, next_id), dim=1)  # add it to the text so far
        return idx


@torch.no_grad()
def estimate_loss(model):
    """Average the loss over many batches so the number is stable."""
    model.eval()
    out = {}
    for split in ["train", "val"]:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            x, y = get_batch(split, batch_size, block_size)
            _, loss = model(x, y)
            losses[k] = loss.item()
        out[split] = losses.mean().item()
    model.train()
    return out


if __name__ == "__main__":
    model = BigramLanguageModel(vocab_size)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

    # Before training: what text does it write?
    start = torch.zeros((1, 1), dtype=torch.long)
    print("BEFORE training:")
    print(decode(model.generate(start, 200)[0].tolist()))
    print("-" * 40)

    for step in range(max_steps + 1):
        if step % eval_interval == 0:
            losses = estimate_loss(model)
            print(f"step {step}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")

        x, y = get_batch("train", batch_size, block_size)
        _, loss = model(x, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print("-" * 40)
    print("AFTER training:")
    print(decode(model.generate(start, 400)[0].tolist()))