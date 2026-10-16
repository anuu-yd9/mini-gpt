"""Tiny demo: how a position can 'look at' the positions before it."""
import torch
import torch.nn.functional as F

torch.manual_seed(1337)
B, T, C = 1, 4, 2            # 1 sentence, 4 characters, 2 numbers per character
x = torch.randn(B, T, C)

# Version 1: for each position, average itself and everything before it (slow loop)
out1 = torch.zeros(B, T, C)
for t in range(T):
    out1[:, t] = x[:, : t + 1].mean(dim=1)

# Version 2: the same thing with one matrix multiplication
tril = torch.tril(torch.ones(T, T))          # lower-triangle of ones
weights = tril / tril.sum(dim=1, keepdim=True)
out2 = weights @ x

# Version 3: the same again, using softmax (this is what attention really does)
scores = torch.zeros(T, T)
scores = scores.masked_fill(tril == 0, float("-inf"))   # hide the future
weights3 = F.softmax(scores, dim=-1)
out3 = weights3 @ x

print("tril:\n", tril)
print("weights (each row sums to 1):\n", weights3)
print("all three give the same answer:", torch.allclose(out1, out2), torch.allclose(out1, out3))