"""Load text, turn characters into numbers, and make training batches."""
import torch

# 1. Read the whole text file
with open("data/input.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 2. The vocabulary is every distinct character in the text
chars = sorted(set(text))
vocab_size = len(chars)

# 3. Two lookup tables: character -> number, and number -> character
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for i, ch in enumerate(chars)}

def encode(s):
    return [stoi[c] for c in s]

def decode(ids):
    return "".join(itos[i] for i in ids)

# 4. Turn the whole text into one long tensor of numbers
data = torch.tensor(encode(text), dtype=torch.long)

# 5. Split: 90% for training, 10% for checking the model
n = int(0.9 * len(data))
train_data = data[:n]
val_data = data[n:]


def get_batch(split, batch_size=4, block_size=8):
    """Pick random chunks of text. y is x shifted by one character."""
    d = train_data if split == "train" else val_data
    starts = torch.randint(len(d) - block_size, (batch_size,))
    x = torch.stack([d[i : i + block_size] for i in starts])
    y = torch.stack([d[i + 1 : i + block_size + 1] for i in starts])
    return x, y


if __name__ == "__main__":
    print("characters in text:", len(text))
    print("vocabulary size:", vocab_size)
    print("the characters:", "".join(chars))
    print("encode('hii'):", encode("hii"))
    print("decode back:", decode(encode("hii")))
    x, y = get_batch("train")
    print("x shape:", x.shape)
    print("x:\n", x)
    print("y:\n", y)