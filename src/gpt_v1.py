"""GPT v1: bigram + token/position embeddings + ONE self-attention head."""
import json
import os

import torch
import torch.nn as nn
from torch.nn import functional as F

from data import get_batch, vocab_size, decode

torch.manual_seed(1337)

# Settings
batch_size = 32
block_size = 8        # how many characters the model can look back at
n_embd = 32           # how many numbers describe each character
max_steps = 5000
learning_rate = 1e-3
eval_interval = 500
eval_iters = 100


class Head(nn.Module):
    """One head of self-attention."""

    def __init__(self, head_size):
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)    # "what do I contain?"
        self.query = nn.Linear(n_embd, head_size, bias=False)  # "what am I looking for?"
        self.value = nn.Linear(n_embd, head_size, bias=False)  # "what do I pass on?"
        self.register_buffer("tril", torch.tril(torch.ones(block_size, block_size)))

    def forward(self, x):
        B, T, C = x.shape
        k = self.key(x)      # (B, T, head_size)
        q = self.query(x)    # (B, T, head_size)

        # How well does each query match each key? Scale to keep numbers calm.
        scores = q @ k.transpose(-2, -1) * (k.shape[-1] ** -0.5)   # (B, T, T)
        scores = scores.masked_fill(self.tril[:T, :T] == 0, float("-inf"))  # hide the future
        weights = F.softmax(scores, dim=-1)

        v = self.value(x)
        return weights @ v   # weighted mix of the values


class GPTv1(nn.Module):
    def __init__(self):
        super().__init__()
        self.token_emb = nn.Embedding(vocab_size, n_embd)    # which character is it?
        self.pos_emb = nn.Embedding(block_size, n_embd)      # which position is it in?
        self.head = Head(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)         # scores for the next character

    def forward(self, idx, targets=None):
        B, T = idx.shape
        x = self.token_emb(idx) + self.pos_emb(torch.arange(T))   # (B, T, n_embd)
        x = self.head(x)
        logits = self.lm_head(x)                                  # (B, T, vocab)

        if targets is None:
            return logits, None
        loss = F.cross_entropy(logits.view(B * T, -1), targets.view(B * T))
        return logits, loss

    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -block_size:]          # only the last block_size characters
            logits, _ = self(idx_cond)
            probs = F.softmax(logits[:, -1, :], dim=-1)
            next_id = torch.multinomial(probs, 1)
            idx = torch.cat((idx, next_id), dim=1)
        return idx


@torch.no_grad()
def estimate_loss(model):
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
    model = GPTv1()
    print("parameters:", sum(p.numel() for p in model.parameters()))
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    history = []

    for step in range(max_steps + 1):
        if step % eval_interval == 0:
            losses = estimate_loss(model)
            history.append({"step": step, "train": losses["train"], "val": losses["val"]})
            print(f"step {step}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")

        x, y = get_batch("train", batch_size, block_size)
        _, loss = model(x, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    os.makedirs("logs", exist_ok=True)
    with open("logs/gpt_v1.json", "w") as f:
        json.dump(history, f)

    start = torch.zeros((1, 1), dtype=torch.long)
    print("-" * 40)
    print(decode(model.generate(start, 400)[0].tolist()))