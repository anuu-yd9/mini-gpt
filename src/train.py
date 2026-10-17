"""Train the GPT. Example:  python src/train.py --name small --max_steps 2000"""
import argparse
import json
import os
import time

import torch

from data import get_batch, vocab_size, decode
from model import GPT, GPTConfig

parser = argparse.ArgumentParser()
parser.add_argument("--name", default="run")
parser.add_argument("--block_size", type=int, default=32)
parser.add_argument("--n_layer", type=int, default=4)
parser.add_argument("--n_head", type=int, default=4)
parser.add_argument("--n_embd", type=int, default=64)
parser.add_argument("--dropout", type=float, default=0.1)
parser.add_argument("--batch_size", type=int, default=32)
parser.add_argument("--lr", type=float, default=1e-3)
parser.add_argument("--max_steps", type=int, default=2000)
parser.add_argument("--eval_interval", type=int, default=250)
parser.add_argument("--eval_iters", type=int, default=50)
args = parser.parse_args()

torch.manual_seed(1337)
device = "cuda" if torch.cuda.is_available() else "cpu"

cfg = GPTConfig(vocab_size=vocab_size, block_size=args.block_size, n_layer=args.n_layer,
                n_head=args.n_head, n_embd=args.n_embd, dropout=args.dropout)
model = GPT(cfg).to(device)
n_params = sum(p.numel() for p in model.parameters())
print(f"device: {device} | parameters: {n_params:,}")

optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)


def batch(split):
    x, y = get_batch(split, args.batch_size, args.block_size)
    return x.to(device), y.to(device)


@torch.no_grad()
def estimate_loss():
    model.eval()
    out = {}
    for split in ["train", "val"]:
        losses = torch.zeros(args.eval_iters)
        for k in range(args.eval_iters):
            x, y = batch(split)
            _, loss = model(x, y)
            losses[k] = loss.item()
        out[split] = losses.mean().item()
    model.train()
    return out


os.makedirs("logs", exist_ok=True)
os.makedirs("checkpoints", exist_ok=True)
ckpt_path = f"checkpoints/{args.name}.pt"

history = []
best_val, best_step = float("inf"), 0
start_time = time.time()
for step in range(args.max_steps + 1):
    if step % args.eval_interval == 0:
        losses = estimate_loss()
        elapsed = time.time() - start_time
        history.append({"step": step, "train": losses["train"], "val": losses["val"],
                        "seconds": round(elapsed, 1)})
        print(f"step {step}: train {losses['train']:.4f}, val {losses['val']:.4f}, {elapsed:.0f}s")
        if losses["val"] < best_val:   # keep the best model, not just the last one
            best_val, best_step = losses["val"], step
            torch.save({"model": model.state_dict(), "config": cfg.__dict__}, ckpt_path)
            print(f"  saved best model (val {best_val:.4f})")

    x, y = batch("train")
    _, loss = model(x, y)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

with open(f"logs/{args.name}.json", "w") as f:
    json.dump({"config": vars(args), "parameters": n_params, "history": history,
               "best_val": best_val, "best_step": best_step}, f)

# Generate the sample from the BEST model, not the last one
model.load_state_dict(torch.load(ckpt_path, map_location=device)["model"])
model.eval()
start = torch.zeros((1, 1), dtype=torch.long, device=device)
sample = decode(model.generate(start, 500)[0].tolist())
with open(f"logs/{args.name}_sample.txt", "w", encoding="utf-8") as f:
    f.write(sample)
print(f"best val {best_val:.4f} at step {best_step}")
print("-" * 40)
print(sample)
