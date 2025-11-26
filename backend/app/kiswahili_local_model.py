import os
import torch
import torch.nn as nn
from torch.nn.utils.rnn import pad_sequence

# Token IDs must match training script
PAD, BOS, EOS, UNK = 0, 1, 2, 3


class Encoder(nn.Module):
    def __init__(self, vocab_size, emb_dim=128, hid_dim=256):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=PAD)
        self.gru = nn.GRU(emb_dim, hid_dim, batch_first=True)

    def forward(self, x, lengths):
        emb = self.emb(x)
        packed = nn.utils.rnn.pack_padded_sequence(
            emb, lengths, batch_first=True, enforce_sorted=False
        )
        _, h = self.gru(packed)
        return h


class Decoder(nn.Module):
    def __init__(self, vocab_size, emb_dim=128, hid_dim=256):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=PAD)
        self.gru = nn.GRU(emb_dim, hid_dim, batch_first=True)
        self.fc = nn.Linear(hid_dim, vocab_size)

    def forward(self, y_prev, h):
        emb = self.emb(y_prev)
        out, h = self.gru(emb, h)
        logits = self.fc(out)
        return logits, h


def _encode_sentence(s, stoi, add_bos=False, add_eos=True):
    toks = [stoi.get(tok, UNK) for tok in s.strip().split()]
    if add_bos:
        toks = [BOS] + toks
    if add_eos:
        toks = toks + [EOS]
    return torch.tensor(toks, dtype=torch.long)


_model_loaded = False
_enc = None
_dec = None
_src_stoi = None
_tgt_itos = None
_device = torch.device("cpu")


def _load_model():
    global _model_loaded, _enc, _dec, _src_stoi, _tgt_itos
    if _model_loaded:
        return
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ckpt_path = os.path.normpath(os.path.join(base_dir, "..", "kiswahili-model-local", "model.pt"))
    if not os.path.exists(ckpt_path):
        raise RuntimeError(f"Kiswahili model checkpoint not found at {ckpt_path}")
    ckpt = torch.load(ckpt_path, map_location=_device)
    _src_stoi = ckpt["src_stoi"]
    tgt_stoi = ckpt["tgt_stoi"]
    _tgt_itos = ckpt["tgt_itos"]
    _enc = Encoder(len(_src_stoi)).to(_device)
    _dec = Decoder(len(tgt_stoi)).to(_device)
    _enc.load_state_dict(ckpt["enc"])
    _dec.load_state_dict(ckpt["dec"])
    _enc.eval()
    _dec.eval()
    _model_loaded = True


def translate(text: str, max_len: int = 20) -> str:
    """Translate a Swahili sentence to English using the tiny local GRU model."""
    _load_model()
    with torch.no_grad():
        src = _encode_sentence(text.lower(), _src_stoi, add_bos=False, add_eos=True).unsqueeze(0).to(_device)
        lengths = torch.tensor([src.size(1)], device=_device)
        h = _enc(src, lengths).contiguous()
        y = torch.tensor([[BOS]], dtype=torch.long, device=_device)
        out_tokens = []
        for _ in range(max_len):
            logits, h = _dec(y, h)
            next_tok = logits[:, -1].argmax(-1)
            if next_tok.item() in (EOS, PAD):
                break
            out_tokens.append(next_tok.item())
            y = torch.cat([y, next_tok.unsqueeze(0)], dim=1)
        return " ".join(_tgt_itos.get(t, "") for t in out_tokens if t in _tgt_itos)
