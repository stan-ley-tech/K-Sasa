import os
import math
import random
import torch
import torch.nn as nn
from torch.nn.utils.rnn import pad_sequence

print("Preparing tiny local Swahili-English dataset (no downloads)...")
pairs = [
    ("habari za asubuhi", "good morning"),
    ("jina langu ni asha", "my name is asha"),
    ("ninatoka kenya", "i am from kenya"),
    ("ninafurahi kukuona", "nice to meet you"),
    ("asante sana", "thank you very much"),
    ("samahani kwa kuchelewa", "sorry for being late"),
    ("naweza kusaidia", "can i help"),
    ("naomba maji", "i would like water"),
    ("tunaenda wapi", "where are we going"),
    ("tutaonana kesho", "see you tomorrow"),
]

def build_vocab(sentences, specials=("<pad>", "<s>", "</s>", "<unk>")):
    vocab = list(specials)
    for s in sentences:
        for tok in s.strip().split():
            if tok not in vocab:
                vocab.append(tok)
    stoi = {t: i for i, t in enumerate(vocab)}
    itos = {i: t for t, i in stoi.items()}
    return stoi, itos

src_sentences = [sw for sw, _ in pairs]
tgt_sentences = [en for _, en in pairs]
src_stoi, src_itos = build_vocab(src_sentences)
tgt_stoi, tgt_itos = build_vocab(tgt_sentences)

PAD, BOS, EOS, UNK = 0, 1, 2, 3

def encode_sentence(s, stoi, add_bos=False, add_eos=True):
    toks = [stoi.get(tok, UNK) for tok in s.strip().split()]
    if add_bos:
        toks = [BOS] + toks
    if add_eos:
        toks = toks + [EOS]
    return torch.tensor(toks, dtype=torch.long)

device = torch.device("cpu")

class Encoder(nn.Module):
    def __init__(self, vocab_size, emb_dim=64, hid_dim=128):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=PAD)
        self.gru = nn.GRU(emb_dim, hid_dim, batch_first=True)
    def forward(self, x, lengths):
        emb = self.emb(x)
        packed = nn.utils.rnn.pack_padded_sequence(emb, lengths, batch_first=True, enforce_sorted=False)
        out, h = self.gru(packed)
        return h

class Decoder(nn.Module):
    def __init__(self, vocab_size, emb_dim=64, hid_dim=128):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=PAD)
        self.gru = nn.GRU(emb_dim, hid_dim, batch_first=True)
        self.fc = nn.Linear(hid_dim, vocab_size)
    def forward(self, y_prev, h):
        emb = self.emb(y_prev)
        out, h = self.gru(emb, h)
        logits = self.fc(out)
        return logits, h

enc = Encoder(len(src_stoi), emb_dim=128, hid_dim=256).to(device)
dec = Decoder(len(tgt_stoi), emb_dim=128, hid_dim=256).to(device)
crit = nn.CrossEntropyLoss(ignore_index=PAD)
opt = torch.optim.Adam(list(enc.parameters()) + list(dec.parameters()), lr=5e-4)

def collate(batch):
    srcs = [encode_sentence(sw, src_stoi, add_bos=False, add_eos=True) for sw, _ in batch]
    tgts = [encode_sentence(en, tgt_stoi, add_bos=True, add_eos=True) for _, en in batch]
    src_lens = torch.tensor([len(x) for x in srcs])
    src_pad = pad_sequence(srcs, batch_first=True, padding_value=PAD)
    tgt_pad = pad_sequence(tgts, batch_first=True, padding_value=PAD)
    # inputs to decoder (remove last), targets (remove first)
    dec_inp = tgt_pad[:, :-1]
    dec_tgt = tgt_pad[:, 1:]
    return src_pad.to(device), src_lens.to(device), dec_inp.to(device), dec_tgt.to(device)

train_data = pairs
epochs = 20
batch_size = 2

print("Training tiny GRU seq2seq on CPU...")
for epoch in range(1, epochs + 1):
    random.shuffle(train_data)
    total_loss = 0.0
    for i in range(0, len(train_data), batch_size):
        batch = train_data[i:i+batch_size]
        src_pad, src_lens, dec_inp, dec_tgt = collate(batch)
        opt.zero_grad()
        h = enc(src_pad, src_lens)
        logits, _ = dec(dec_inp, h)
        loss = crit(logits.reshape(-1, logits.size(-1)), dec_tgt.reshape(-1))
        loss.backward()
        opt.step()
        total_loss += loss.item()
    print(f"epoch {epoch}: loss={total_loss:.4f}")

os.makedirs("./kiswahili-model-local", exist_ok=True)
torch.save({
    "enc": enc.state_dict(),
    "dec": dec.state_dict(),
    "src_stoi": src_stoi,
    "tgt_stoi": tgt_stoi,
    "src_itos": src_itos,
    "tgt_itos": tgt_itos,
}, "./kiswahili-model-local/model.pt")
print("Saved ./kiswahili-model-local/model.pt")

def greedy_translate(sentence, max_len=20):
    enc.eval(); dec.eval()
    with torch.no_grad():
        src = encode_sentence(sentence.lower(), src_stoi, add_bos=False, add_eos=True).unsqueeze(0).to(device)
        h = enc(src, torch.tensor([src.size(1)])).contiguous()
        y = torch.tensor([[BOS]], dtype=torch.long, device=device)
        out_tokens = []
        for _ in range(max_len):
            logits, h = dec(y, h)
            next_tok = logits[:, -1].argmax(-1)
            if next_tok.item() == EOS or next_tok.item() == PAD:
                break
            out_tokens.append(next_tok.item())
            y = torch.cat([y, next_tok.unsqueeze(0)], dim=1)
        return " ".join(tgt_itos[t] for t in out_tokens if t in tgt_itos)

print("Sample translations:")
for sw, _ in pairs[:3]:
    print(sw, "->", greedy_translate(sw))
print("DONE!")
