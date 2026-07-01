[← All question banks](../README.md) · part of [ai-interview-questions](https://github.com/landedjobs/ai-interview-questions) by [Landed](https://landed.jobs)

<div align="center">

# 💻 Coding Exercises & ML System Design — Real AI Interview Questions

![Updated](https://img.shields.io/badge/updated-2026.07-00A86B?style=flat-square) ![Questions](https://img.shields.io/badge/23%20real%20questions-ff5b29?style=flat-square) ![Sources](https://img.shields.io/badge/every%20question-cited-6C2BD9?style=flat-square)

**Every exercise below was reported by a real candidate, with the company, stage, and source. Answers are what a strong candidate actually does.**

</div>

---

## Jump to

**Section A — Coding exercises (13):**
[Tokenization and text processing](#a1-tokenization-and-text-processing) · [Attention and transformers](#a2-attention-and-transformers) · [Sampling and decoding](#a3-sampling-and-decoding) · [Classic ML from scratch](#a4-classic-ml-from-scratch) · [Training-loop engineering](#a5-training-loop-engineering) · [AI infrastructure coding](#a6-ai-infrastructure-coding)

**Section B — ML/LLM system design (10):**
[RAG and retrieval systems](#b1-rag-and-retrieval-systems) · [LLM serving and inference](#b2-llm-serving-and-inference) · [Evaluation systems](#b3-evaluation-systems) · [Applied ML system design](#b4-applied-ml-system-design) · [Training and alignment pipelines](#b5-training-and-alignment-pipelines)

---

## Section A — Coding exercises

The pattern across labs and AI startups is consistent: less LeetCode, more "build a real ML/LLM primitive from scratch, in plain Python/NumPy/PyTorch, while talking through it." These are the exercises candidates actually report.

## A1. Tokenization and text processing

### Implement a BPE tokenizer from scratch

> Implement a Byte Pair Encoding (BPE) tokenizer. Write `train(corpus, vocab_size)` that learns the merge rules, and `encode(text)` / `decode(ids)` that apply them. No external tokenizer libraries.

**Where asked:** OpenAI — ML Engineer coding round · [PracHub (question)](https://prachub.com/interview-questions/implement-a-byte-pair-encoding-bpe-tokenizer), [PracHub (OpenAI MLE bank)](https://prachub.com/companies/openai/positions/machine-learning-engineer), [Raschka: BPE from scratch](https://sebastianraschka.com/blog/2025/bpe-from-scratch.html)

**What it tests:** Whether you actually understand how LLMs see text — greedy merge training, deterministic application of merge ranks at encode time, byte-level fallbacks — plus clean dict/counter manipulation under time pressure.

**Difficulty:** Hard (45–60 min to a working train + encode + decode)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:** Start from bytes (or characters if the interviewer allows), count adjacent-pair frequencies, repeatedly merge the most frequent pair into a new token, and record merges in order. Encoding replays merges by rank.

```python
from collections import Counter

def train(corpus: str, vocab_size: int):
    ids = list(corpus.encode("utf-8"))
    vocab = {i: bytes([i]) for i in range(256)}
    merges = {}
    next_id = 256
    while next_id < vocab_size:
        pairs = Counter(zip(ids, ids[1:]))
        if not pairs:
            break
        pair = pairs.most_common(1)[0][0]
        merges[pair] = next_id
        vocab[next_id] = vocab[pair[0]] + vocab[pair[1]]
        ids = merge(ids, pair, next_id)
        next_id += 1
    return merges, vocab

def merge(ids, pair, new_id):
    out, i = [], 0
    while i < len(ids):
        if i < len(ids) - 1 and (ids[i], ids[i + 1]) == pair:
            out.append(new_id)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return out

def encode(text, merges):
    ids = list(text.encode("utf-8"))
    while len(ids) >= 2:
        pairs = set(zip(ids, ids[1:]))
        candidates = [p for p in pairs if p in merges]
        if not candidates:
            break
        pair = min(candidates, key=lambda p: merges[p])  # lowest merge rank first
        ids = merge(ids, pair, merges[pair])
    return ids

def decode(ids, vocab):
    return b"".join(vocab[i] for i in ids).decode("utf-8", errors="replace")
```

Narrate the two things interviewers listen for: (1) encode must apply merges **in training-rank order**, not greedily by frequency in the new text; (2) byte-level start means no `<UNK>` token is ever needed.

**Follow-ups:**
- Training complexity? Naive is O(vocab_size × corpus). Speed up with a heap of pair counts + incremental updates (only pairs adjacent to a merge change).
- Why BPE over word-level or char-level vocab? (OOV handling vs sequence length tradeoff.)
- How does GPT-style pre-tokenization (regex splitting on whitespace/contractions) change training?
- What breaks with multilingual text if you train on English-heavy data? (Token fertility — same sentence costs 3–5× more tokens in low-resource languages.)

</details>

## A2. Attention and transformers

### Implement scaled dot-product self-attention

> Given matrices Q, K, V of shape `(seq_len, d_k)`, implement scaled dot-product attention in NumPy or PyTorch — no `nn.MultiheadAttention`, no `F.scaled_dot_product_attention`. Support an optional causal mask.

**Where asked:** Reported across OpenAI, Meta, and AI-lab MLE screens; now standardized as a NeetCode problem because it comes up so often · [NeetCode: Self Attention](https://neetcode.io/problems/self-attention/question), [r/MachineLearning: LC questions asked for AI/MLE roles](https://www.reddit.com/r/MachineLearning/comments/1o5zhqo/d_interview_prep_what_lc_questions_were_u_asked/), [CodeSignal lesson](https://codesignal.com/learn/courses/sequence-models-the-dawn-of-attention-1/lessons/scaled-dot-product-attention-and-masking-in-transformers-1)

**What it tests:** The single most important equation in modern ML, written correctly: scaling by √d_k, numerically stable softmax, and masking applied *before* softmax with −inf (not zero).

**Difficulty:** Medium (15–20 min; table stakes for any LLM role)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:**

```python
import numpy as np

def attention(Q, K, V, causal=False):
    d_k = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)
    if causal:
        mask = np.triu(np.ones(scores.shape, dtype=bool), k=1)
        scores = np.where(mask, -np.inf, scores)
    scores -= scores.max(axis=-1, keepdims=True)  # numerical stability
    weights = np.exp(scores)
    weights /= weights.sum(axis=-1, keepdims=True)
    return weights @ V
```

Say out loud *why* each line exists: the √d_k scaling keeps dot-product variance ~1 so softmax doesn't saturate; the max-subtraction prevents overflow; masked positions get −inf so they contribute exactly 0 probability after softmax.

**Follow-ups:**
- Extend to batched multi-head: reshape to `(batch, heads, seq, d_head)`, attend per head, concat, project. Know the einsum/transpose dance cold.
- Time and memory complexity? O(n²·d) time, O(n²) memory for the score matrix — this is the lead-in to the FlashAttention question below.
- What's the difference between padding masks and causal masks, and how do they combine?
- Why multiple heads instead of one big head? (Multiple learned similarity subspaces.)

</details>

### Implement a Transformer block from scratch

> Implement a full transformer block in PyTorch: multi-head attention, feed-forward network, residual connections, and layer norm. You may use `nn.Linear` but nothing higher-level.

**Where asked:** Reported in research-engineering onsites at frontier labs (a Pinterest→lab candidate describes "implement a transformer, layer by layer, from memory" rounds) · [Yuan Meng: MLE Interview 2.0](https://www.yuan-meng.com/posts/mle_interviews_2.0/), [Mislav Jurić: Transformer from scratch in PyTorch](https://www.mislavjuric.com/transformer-from-scratch-in-pytorch/), [HuggingFace forum walkthrough](https://discuss.huggingface.co/t/tutorial-implementing-transformer-from-scratch-a-step-by-step-guide/132158)

**What it tests:** Architecture fluency beyond the attention equation — pre-norm vs post-norm, where residuals attach, head splitting/merging shapes, and whether you can wire modules together without a reference.

**Difficulty:** Hard (30–45 min for a clean, shape-correct block)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:** Write the skeleton first, then fill in; interviewers reward structure.

```python
import torch
import torch.nn as nn

class TransformerBlock(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, dropout=0.1):
        super().__init__()
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.proj = nn.Linear(d_model, d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff), nn.GELU(), nn.Linear(d_ff, d_model)
        )
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        B, T, C = x.shape
        q, k, v = self.qkv(self.ln1(x)).chunk(3, dim=-1)
        q, k, v = (t.view(B, T, self.n_heads, self.d_head).transpose(1, 2)
                   for t in (q, k, v))
        att = (q @ k.transpose(-2, -1)) / (self.d_head ** 0.5)
        if mask is not None:
            att = att.masked_fill(mask == 0, float("-inf"))
        att = torch.softmax(att, dim=-1)
        out = (att @ v).transpose(1, 2).contiguous().view(B, T, C)
        x = x + self.drop(self.proj(out))          # residual 1 (pre-norm)
        x = x + self.drop(self.ff(self.ln2(x)))    # residual 2
        return x
```

Call out the design choices as you go: pre-norm (GPT-2 onward) trains more stably than the original post-norm; fused QKV projection is one matmul instead of three; `d_ff` is conventionally 4×`d_model`.

**Follow-ups:**
- Add positional information — compare learned embeddings, sinusoidal, and RoPE; why RoPE won for long context.
- Parameter count of one block as a function of d_model? (~12·d_model² with d_ff = 4·d_model.)
- Decoder-only vs encoder-decoder — what changes structurally and why decoder-only dominates for LLMs.
- Where does KV caching plug into your `forward` at inference time?

</details>

### Debug a broken PyTorch transformer training loop

> Here is a PyTorch training script for a small transformer language model. The loss isn't decreasing (or the model produces garbage). Find the bugs and fix them.

**Where asked:** OpenAI — ML Engineer round (debugging format is repeatedly reported for OpenAI loops) · [PracHub: Debug and fix a PyTorch Transformer training loop](https://prachub.com/interview-questions/debug-and-fix-a-pytorch-transformer-training-loop), [DarkInterview: Transformer Debug — OpenAI](https://darkinterview.com/collections/openai/questions/854ed663-de77-451d-bfe2-fdcd7287c3be)

**What it tests:** Real engineering instinct rather than recall — can you form hypotheses, instrument the loop, and spot the classic failure modes fast? Labs love this format because it can't be memorized.

**Difficulty:** Hard (bugs are planted in layers: some obvious, some subtle)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:** Don't read the code top-to-bottom hoping to spot the bug. Work a checklist out loud, ordered by frequency:

1. **`optimizer.zero_grad()` missing or misplaced** — gradients accumulate across steps and explode.
2. **Target misalignment** — for next-token prediction, inputs must be `tokens[:-1]` and targets `tokens[1:]`. Off-by-one here trains an identity function.
3. **Missing causal mask** — the model attends to the future; train loss looks amazing, generation is garbage. That symptom (great loss, terrible samples) *is* the tell.
4. **Softmax before `nn.CrossEntropyLoss`** — the loss applies log-softmax internally; feeding it probabilities silently degrades training.
5. **Missing √d_k scale in attention** — trains but poorly; softmax saturates.
6. **`model.train()` / `model.eval()` mixed up** — dropout active at eval, or BN/dropout frozen at train.
7. **Learning rate / no warmup** — transformers with Adam typically need warmup; lr=1e-2 diverges.
8. **Shape silently broadcasting** — e.g., loss over the wrong dimension, or `view` where `transpose` was needed.

Verify each fix empirically: overfit a single batch to near-zero loss first — the standard sanity test. If the interviewer lets you run code, add gradient-norm logging and a generation sample every N steps.

**Follow-ups:**
- Loss goes to NaN at step ~2k — where do you look? (LR spikes, fp16 overflow → GradScaler, bad data batch; bisect with gradient clipping and anomaly detection.)
- Train loss falls but val loss doesn't — overfitting vs data leakage vs eval-mode bug.
- How would you catch the causal-mask bug with a unit test? (Assert attention weights above the diagonal are 0.)

</details>

### Implement FlashAttention-style tiled attention

> Implement attention without ever materializing the full N×N attention matrix — process K/V in tiles and keep a running softmax, FlashAttention-style.

**Where asked:** Mistral AI — reported by a candidate describing the Mistral process ("implement flash attention") · [Candidate post (Facebook ML group)](https://www.facebook.com/groups/595424764221375/posts/2410312236065943/), [TDS: Writing FlashAttention from scratch](https://towardsdatascience.com/understanding-flash-attention-writing-the-algorithm-from-scratch-in-triton-5609f0b143ea/), [InterviewCoder: Mistral prep guide](https://www.interviewcoder.co/blog/mistral-ai-interview-questions)

**What it tests:** Whether you understand *why* attention is memory-bound and can derive the online-softmax trick — the difference between using transformers and understanding GPU-era transformers. This is a signature question for inference/training-infra roles at European labs.

**Difficulty:** Hard (the online softmax rescaling is the whole interview)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:** The key identity: softmax can be computed incrementally. For each query row, sweep K/V tiles while maintaining a running max `m`, running normalizer `l`, and running output `o`, rescaling previous partial results when a new max appears.

```python
import numpy as np

def flash_attention(Q, K, V, tile=128):
    N, d = Q.shape
    O = np.zeros((N, d))
    m = np.full(N, -np.inf)   # running row max
    l = np.zeros(N)           # running softmax denominator
    for j in range(0, N, tile):
        Kj, Vj = K[j:j + tile], V[j:j + tile]
        S = Q @ Kj.T / np.sqrt(d)              # (N, tile) — only a tile, never N×N
        m_new = np.maximum(m, S.max(axis=1))
        scale = np.exp(m - m_new)              # rescale old accumulators
        P = np.exp(S - m_new[:, None])
        l = l * scale + P.sum(axis=1)
        O = O * scale[:, None] + P @ Vj
        m = m_new
    return O / l[:, None]
```

Explain the systems framing: standard attention is O(N²) HBM traffic; tiling keeps working set in SRAM, so FlashAttention is an **IO-aware** algorithm — same FLOPs, far less memory movement, exact (not approximate) result.

**Follow-ups:**
- Also tile the queries (the real algorithm is a 2D loop) and handle the causal mask per tile.
- Why is attention memory-bound rather than compute-bound on modern GPUs? (Arithmetic intensity of the softmax stage.)
- Backward pass: why does FlashAttention recompute the attention matrix instead of storing it? (Recomputation is cheaper than N² memory.)
- How does this interact with KV caching at inference — what's different in the decode phase (one query row) vs prefill?

</details>

## A3. Sampling and decoding

### Implement temperature, top-k, and top-p sampling

> Given logits over a vocabulary, implement sampling with temperature, top-k filtering, and top-p (nucleus) filtering — composable in one function.

**Where asked:** Standard LLM-role coding screen at labs (reported in research-engineering loop write-ups; Raschka's FAQ exists because candidates keep getting asked) · [Raschka: temperature, top-k, top-p](https://sebastianraschka.com/faq/docs/temperature-topk-topp-sampling.html), [Yuan Meng: MLE Interview 2.0](https://www.yuan-meng.com/posts/mle_interviews_2.0/), [Top-p guide](https://www.shadecoder.com/topics/top-p-sampling-a-comprehensive-guide-for-2025)

**What it tests:** Do you know what the knobs you tune every day actually do — order of operations (temperature → filter → renormalize), the cumulative-sum subtlety of top-p, and clean tensor code.

**Difficulty:** Medium (20 min; the top-p boundary condition is the trap)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:**

```python
import torch

def sample(logits, temperature=1.0, top_k=0, top_p=1.0):
    logits = logits / max(temperature, 1e-8)
    if top_k > 0:
        kth = torch.topk(logits, top_k).values[..., -1, None]
        logits = logits.masked_fill(logits < kth, float("-inf"))
    if top_p < 1.0:
        sorted_logits, idx = torch.sort(logits, descending=True)
        probs = torch.softmax(sorted_logits, dim=-1)
        cum = torch.cumsum(probs, dim=-1)
        remove = cum - probs > top_p       # keep the token that crosses the threshold
        sorted_logits = sorted_logits.masked_fill(remove, float("-inf"))
        logits = torch.full_like(logits, float("-inf")).scatter(-1, idx, sorted_logits)
    probs = torch.softmax(logits, dim=-1)
    return torch.multinomial(probs, 1)
```

The two details that separate strong candidates: (1) the token that *crosses* the top-p threshold must be kept — `cum - probs > top_p`, not `cum > top_p` (otherwise top_p=0.1 with a 0.5-prob top token would remove everything); (2) renormalization happens implicitly via softmax over the filtered logits.

**Follow-ups:**
- What does temperature → 0 converge to? (Greedy argmax.) Temperature > 1? (Flatter, more diverse, more errors.)
- Why does top-p adapt better than top-k across confident vs uncertain distributions?
- Add repetition penalty and explain where it applies in the pipeline.
- Why is sampled generation non-deterministic even at temperature 0 on real serving stacks? (Batching non-determinism, floating-point reduction order.)

</details>

### Implement beam search decoding

> Implement beam search decoding for an autoregressive language model: given `model(prefix) -> log_probs`, return the highest-scoring sequence with beam width k.

**Where asked:** Perplexity AI — candidate report of the exact question · [1point3acres candidate report](https://www.1point3acres.com/interview/post/7100135), [Exponent: Perplexity question bank](https://www.tryexponent.com/questions?company=perplexity-ai)

**What it tests:** Search-over-sequences reasoning: score accumulation in log space, hypothesis bookkeeping, EOS handling, and length normalization — plus whether you can discuss when beam search is the *wrong* choice for open-ended generation.

**Difficulty:** Medium-Hard (bookkeeping-heavy; EOS handling is where candidates break)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:** Maintain k live hypotheses; each step, expand every hypothesis by the top candidates, then keep the global top k by cumulative log-prob. Move finished (EOS) hypotheses to a completed pool instead of expanding them.

```python
import heapq
import math

def beam_search(model, bos, eos, k=4, max_len=64, alpha=0.6):
    beams = [(0.0, [bos])]           # (cum_logprob, tokens)
    done = []
    for _ in range(max_len):
        candidates = []
        for score, seq in beams:
            log_probs = model(seq)   # dict/array: token -> logprob
            for tok, lp in topk(log_probs, k):
                candidates.append((score + lp, seq + [tok]))
        beams = []
        for score, seq in heapq.nlargest(2 * k, candidates):
            if seq[-1] == eos:
                done.append((score / (len(seq) ** alpha), seq))  # length norm
            else:
                beams.append((score, seq))
            if len(beams) == k:
                break
        if not beams:
            break
    done += [(s / (len(q) ** alpha), q) for s, q in beams]
    return max(done)[1]
```

Explain length normalization unprompted: raw log-prob sums penalize long sequences (every token adds negative log-prob), so you divide by `len^alpha` — otherwise beam search degenerates to short outputs.

**Follow-ups:**
- Complexity vs greedy? (k× model calls per step; batch the k hypotheses into one forward pass.)
- Why do chat LLMs use sampling instead of beam search? (Beam search finds high-likelihood but degenerate/repetitive text for open-ended generation; it wins for closed tasks like translation.)
- What is diverse beam search and when do you need it?
- How does beam search interact with a KV cache? (Cache must fork/reorder with the beams — a real serving cost.)

</details>

## A4. Classic ML from scratch

### Implement k-means clustering in NumPy

> Implement k-means from scratch in Python/NumPy: `fit(X, k)` returning centroids and assignments. No sklearn.

**Where asked:** One of the most-reported MLE coding screens across big tech and AI startups (candidate practice threads and interview recaps consistently list it) · [r/learnmachinelearning practice thread](https://www.reddit.com/r/learnmachinelearning/comments/xlrc0l/interview_practice_coding_kmeans_clustering_using/), [Medium: ML Coding Interview — K-Means](https://medium.com/nailing-the-ai-ml-interview/ml-ink-means-16d02410ac43), [r/MachineLearning: questions asked for AI/MLE roles](https://www.reddit.com/r/MachineLearning/comments/1o5zhqo/d_interview_prep_what_lc_questions_were_u_asked/)

**What it tests:** Vectorized NumPy (broadcast distance computation without loops), understanding of the EM-like alternation, and edge-case maturity (empty clusters, convergence, init sensitivity).

**Difficulty:** Medium (20–30 min; the vectorized distance matrix is the bar)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:**

```python
import numpy as np

def kmeans(X, k, max_iter=100, tol=1e-6, seed=0):
    rng = np.random.default_rng(seed)
    centroids = X[rng.choice(len(X), k, replace=False)]
    for _ in range(max_iter):
        # (n, k) distance matrix via broadcasting — no Python loops
        dists = ((X[:, None, :] - centroids[None, :, :]) ** 2).sum(-1)
        labels = dists.argmin(axis=1)
        new_centroids = np.array([
            X[labels == j].mean(axis=0) if (labels == j).any()
            else X[rng.integers(len(X))]          # re-seed empty cluster
            for j in range(k)
        ])
        if np.linalg.norm(new_centroids - centroids) < tol:
            break
        centroids = new_centroids
    return centroids, labels
```

Mention k-means++ initialization (pick each next centroid with probability proportional to squared distance from existing ones) without being asked — it's the expected "senior" flourish, and handle empty clusters explicitly; that's the planted edge case.

**Follow-ups:**
- Complexity? O(n·k·d) per iteration. How do you scale to 100M points? (Mini-batch k-means, approximate assignment via ANN.)
- How do you pick k? (Elbow/silhouette; or the honest answer — k is usually dictated by the product.)
- Where does k-means fail? (Non-spherical clusters, varying densities; contrast with DBSCAN/GMM.)
- Direct AI tie-in: k-means is exactly the coarse quantizer in IVF vector indexes — interviewers at retrieval companies love this connection.

</details>

### Implement logistic regression with gradient descent

> Implement logistic regression from scratch — sigmoid, binary cross-entropy loss, gradient computation, and a vectorized gradient-descent training loop. No ML libraries.

**Where asked:** Reported as the classic first-round MLE coding screen (a candidate's post-mortem of failing exactly this question is one of the most-read threads in r/learnmachinelearning) · [r/learnmachinelearning: Failed first coding ML interview](https://www.reddit.com/r/learnmachinelearning/comments/1gvceaj/failed_first_coding_machine_learning_interview/), [Devinterview-io: logistic regression questions](https://github.com/Devinterview-io/logistic-regression-interview-questions), [ProjectPro: LR interview questions](https://www.projectpro.io/article/logistic-regression-interview-questions-/448)

**What it tests:** Whether you can derive and implement ∂L/∂w = Xᵀ(σ(Xw) − y)/n rather than recite it — plus numerical stability (log(0), sigmoid overflow) and vectorization.

**Difficulty:** Medium (the derivation-while-coding combo is what filters people)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:**

```python
import numpy as np

def sigmoid(z):
    return np.where(z >= 0, 1 / (1 + np.exp(-z)),
                    np.exp(z) / (1 + np.exp(z)))   # stable both directions

def train(X, y, lr=0.1, epochs=1000, eps=1e-12):
    n, d = X.shape
    w, b = np.zeros(d), 0.0
    for _ in range(epochs):
        p = sigmoid(X @ w + b)
        grad_w = X.T @ (p - y) / n
        grad_b = (p - y).mean()
        w -= lr * grad_w
        b -= lr * grad_b
    return w, b

def loss(p, y, eps=1e-12):
    p = np.clip(p, eps, 1 - eps)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p)).mean()
```

Be ready to *derive* the gradient on the whiteboard: the elegance is that BCE + sigmoid gives the same `(p − y)` error-times-input form as MSE + linear — say why (the sigmoid's derivative cancels against the log-loss).

**Follow-ups:**
- Why BCE and not MSE for classification? (MSE + sigmoid is non-convex in w and has vanishing gradients when confidently wrong.)
- Add L2 regularization — which gradient term changes, and why don't we regularize the bias?
- Perfectly separable data — what happens? (Weights diverge to ∞; regularization fixes it.)
- Mini-batch vs full-batch; learning-rate scheduling; how this generalizes to softmax regression.

</details>

### Implement cosine-similarity semantic search

> Given a query embedding and a matrix of N document embeddings, return the top-k most similar documents. Implement cosine similarity yourself, vectorized — then discuss what changes at 100M documents.

**Where asked:** AI-engineer screens at RAG-focused companies (staple of the 2025–26 AI-engineer loop; appears in every serious RAG question bank and embeddings course built from real screens) · [TigerData: implementing cosine similarity](https://www.tigerdata.com/learn/implementing-cosine-similarity-in-python), [DataCamp: Top 30 RAG interview questions](https://www.datacamp.com/blog/rag-interview-questions), [CodeSignal: similarity search lesson](https://codesignal.com/learn/courses/implementing-semantic-search-with-chromadb-1/lessons/understanding-similarity-search-with-cosine-similarity)

**What it tests:** Vectorized linear algebra, argpartition vs full sort, and — the real question hiding inside — whether you know when brute force stops working and ANN indexes begin.

**Difficulty:** Easy-Medium (the code is 6 lines; the scaling discussion is the interview)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:**

```python
import numpy as np

def top_k(query, docs, k=5):
    q = query / np.linalg.norm(query)
    D = docs / np.linalg.norm(docs, axis=1, keepdims=True)
    sims = D @ q                                   # cosine == dot of unit vectors
    idx = np.argpartition(-sims, k)[:k]            # O(n), not O(n log n)
    return idx[np.argsort(-sims[idx])]
```

Two signals interviewers grade: normalizing once (cosine similarity is just a dot product of unit vectors — so you can pre-normalize the corpus at index time), and `argpartition` instead of a full sort for top-k.

Then the scaling conversation: brute force is O(N·d) per query — fine to ~1M vectors, then you move to ANN: **HNSW** (graph-based, high recall, high memory) vs **IVF-PQ** (cluster + compress, lower memory, tunable recall). Know that IVF's coarse quantizer is literally k-means.

**Follow-ups:**
- Cosine vs dot product vs Euclidean — when does the choice matter? (Un-normalized embeddings encode magnitude = popularity/confidence.)
- What recall do you lose with ANN, and how do you measure it? (recall@k vs exact brute force on a sample.)
- Hybrid search: combining BM25 + dense retrieval with reciprocal rank fusion.
- Batch 1000 queries at once — what changes? (Matrix-matrix product, GPU.)

</details>

## A5. Training-loop engineering

### Add gradient accumulation and mixed precision to a training loop

> This training loop OOMs at batch size 32 on your GPU; only batch size 8 fits. Modify it to train with an effective batch size of 32, then add mixed-precision training. Explain every change.

**Where asked:** Reported in training-infra rounds at European labs and Cohere-style MLE loops (fine-tuning efficiency is a standing theme in Mistral/Cohere interview guides) · [Cohere MLE interview guide](https://interview.norahq.com/interview-guides/cohere-machine-learning-engineer-interview-guide-2026), [Mistral prep guide](https://www.interviewcoder.co/blog/mistral-ai-interview-questions), [PyTorch: mixed precision](https://pytorch.org/blog/what-every-user-should-know-about-mixed-precision-training-in-pytorch/), [PyTorch forums: accumulating gradients](https://discuss.pytorch.org/t/accumulating-gradients/30020)

**What it tests:** Practical GPU-budget engineering — the exact skill of the fine-tuning era: loss scaling for fp16, when to step/zero the optimizer, and what actually changes statistically with accumulation.

**Difficulty:** Medium (everyone claims this skill; the loss-division detail exposes who has it)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:**

```python
import torch

accum_steps = 4                       # 8 × 4 = effective batch 32
scaler = torch.cuda.amp.GradScaler()
optimizer.zero_grad()

for step, (x, y) in enumerate(loader):          # loader yields batches of 8
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        loss = model(x, y) / accum_steps        # ← divide, or gradients are 4× too big
    scaler.scale(loss).backward()               # grads accumulate across iterations
    if (step + 1) % accum_steps == 0:
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad()
```

The three graded details: (1) **divide the loss by `accum_steps`** — otherwise you've silently multiplied your learning rate by 4; (2) `zero_grad` only after stepping, since `.backward()` accumulates by design; (3) `unscale_` before clipping so you clip true gradient norms, not scaled ones.

Explain *why* GradScaler exists: fp16 has a tiny exponent range, small gradients underflow to zero; scaling the loss up (and gradients back down before the step) preserves them. bf16 has fp32's exponent range, so on A100+/H100 you use bf16 and drop the scaler entirely.

**Follow-ups:**
- Is accumulation exactly equivalent to a bigger batch? (Almost — BatchNorm statistics differ; LayerNorm models like transformers are fine.)
- Where does the memory actually go? (Params + grads + Adam states ≈ 16 bytes/param fp32-mixed; activations scale with batch — hence activation checkpointing next.)
- When accumulation isn't enough: gradient checkpointing, LoRA/QLoRA, ZeRO/FSDP sharding — ordered by invasiveness.
- Why can bf16 skip loss scaling but fp16 can't?

</details>

## A6. AI infrastructure coding

### Implement an async task queue with a concurrency limit

> Implement an async task queue: tasks can be submitted at any time, at most N run concurrently, each submission returns a promise/future of its result. (JS/TS or Python asyncio.)

**Where asked:** Neon — a favorite interview of one of its engineers, published with real candidate/AI transcripts; the pattern is now common across AI-tooling startups precisely because it resists memorization · [David Gomes: One of my favorite programming interviews](https://davidgomes.com/async-queue-interview-ai/), [OpenAI community: AsyncOpenAI patterns](https://community.openai.com/t/using-asynchronous-client-with-asyncopenai/624114)

**What it tests:** Concurrency reasoning — the exact skill you need to call LLM APIs at scale without blowing rate limits. Ordering guarantees, backpressure, and error propagation are the layers.

**Difficulty:** Medium (easy to start, hard to finish cleanly under follow-ups)

<details><summary>💡 Strong solution approach</summary>

**Strong approach (Python asyncio):**

```python
import asyncio

class TaskQueue:
    def __init__(self, concurrency: int):
        self.sem = asyncio.Semaphore(concurrency)

    def submit(self, coro) -> asyncio.Task:
        async def _run():
            async with self.sem:
                return await coro
        return asyncio.create_task(_run())
```

**Strong approach (TypeScript, no libraries) —** the version the interviewers probe harder:

```ts
class TaskQueue {
    private running = 0;
    private waiting: Array<() => void> = [];
    constructor(private limit: number) {}

    async submit<T>(fn: () => Promise<T>): Promise<T> {
        if (this.running >= this.limit) {
            await new Promise<void>(res => this.waiting.push(res));
        }
        this.running++;
        try {
            return await fn();
        } finally {
            this.running--;
            this.waiting.shift()?.();   // wake exactly one waiter (FIFO)
        }
    }
}
```

The graded subtleties: release in `finally` so failures don't leak slots; wake exactly one waiter; preserve FIFO fairness; a rejected task must reject *its own* promise without killing the queue.

**Follow-ups:**
- Add per-task timeout and cancellation. Add `drain()` that resolves when all work finishes.
- Bounded queue: what happens when submissions outpace completion? (Backpressure — block, drop, or reject; know the tradeoffs.)
- Priorities; retries with exponential backoff + jitter (this is your OpenAI-client wrapper in real life).
- The Neon write-up's angle: interviewers now watch *how you use an AI assistant* on this problem — drive it with tests and invariants, don't paste-and-pray.

</details>

### Implement a rate limiter for an LLM API

> Implement a rate limiter for an LLM API gateway: each user gets X requests/minute and Y tokens/minute. `allow(user, tokens)` returns whether the request may proceed. Then make it work across multiple gateway instances.

**Where asked:** Reported across AI-infra SWE loops (xAI-style infra rounds; a staple wherever the product *is* an API) · [xAI SWE interview process](https://gaijineer.co/xai-software-engineer-interview-process), [Tyk: rate limiting explained](https://tyk.io/learning-center/api-rate-limiting-explained-from-basics-to-best-practices/), [Orq: API rate limits best practices](https://orq.ai/blog/api-rate-limit)

**What it tests:** The token-bucket algorithm under the twist that LLM cost is *tokens, not requests* — dual-budget limiting, lazy refill, and the single-node → distributed jump.

**Difficulty:** Medium (single node) → Hard (distributed follow-up)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:** Token bucket with lazy refill — no background timers, refill computed at check time:

```python
import time

class Bucket:
    def __init__(self, capacity, refill_per_sec):
        self.capacity = capacity
        self.tokens = capacity
        self.rate = refill_per_sec
        self.last = time.monotonic()

    def allow(self, cost=1.0):
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

class LLMRateLimiter:
    def __init__(self, rpm, tpm):
        self.make = lambda: (Bucket(rpm, rpm / 60), Bucket(tpm, tpm / 60))
        self.users = {}

    def allow(self, user, tokens):
        req, tok = self.users.setdefault(user, self.make())
        return req.allow(1) and tok.allow(tokens)   # careful: see follow-up on atomicity
    # NB: checking two buckets needs check-then-commit to avoid consuming one when the other rejects
```

Name the LLM-specific wrinkle unprompted: you don't know the *output* token count at admission time — real gateways (as OpenAI's does) reserve an estimate (prompt tokens + max_tokens) and reconcile after the response.

**Distributed version:** move bucket state to Redis, one atomic Lua script per check (read state, refill, compare, decrement). Discuss the tradeoff triangle: accuracy (central Redis) vs latency (local buckets with divided quotas) vs cost (sync intervals).

**Follow-ups:**
- Token bucket vs sliding-window-log vs fixed window — burst behavior at window boundaries.
- What do you return on rejection? (429 + `Retry-After`; well-behaved clients back off with jitter.)
- Fairness: one user's burst starving others → per-user buckets plus a global bucket.
- Priority tiers (paid vs free) and request queueing instead of hard rejection.

</details>

---

## Section B — ML/LLM system design

The design round has split in two: classic ML system design (fraud, feeds, search — still asked everywhere) and the new LLM-system round (RAG, serving, evals — now the core round at AI-native companies). Both appear below, as reported.

## B1. RAG and retrieval systems

### Design a RAG system over a private document corpus

> Design a question-answering system over a company's private documents (wikis, PDFs, contracts). Users ask natural-language questions and get accurate, cited answers. The corpus is ~10M documents and updates daily.

**Where asked:** Reported as the centerpiece of AI-engineering system design rounds (candidate report of an "AI Engineering"-focused MLSD interview; full case study write-ups exist because it's asked so often) · [r/MLQuestions: ML system design interview focused on AI engineering](https://www.reddit.com/r/MLQuestions/comments/1mjtd4j/ml_system_design_interview_focused_on_ai/), [BuildML: Design a RAG system for a private corpus](https://buildml.substack.com/p/data-science-case-study-design-a-625), [dev.to: How I aced my LLM interview — RAG chatbot](https://dev.to/mrzaizai2k/how-i-aced-my-llm-interview-building-a-rag-chatbot-2p6f)

**What it tests:** The full 2026 AI-engineer skillset in one question: chunking strategy, hybrid retrieval, reranking, grounding/citations, evals, freshness, and access control — and whether you ask about requirements before drawing boxes.

**Difficulty:** Hard (breadth question; strong candidates go deep on 2–3 components)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:** Clarify first: QPS? Latency budget? Accuracy bar and hallucination tolerance? Multilingual? Per-user permissions? (The permissions question alone signals seniority — most candidates miss that retrieval must be ACL-filtered.)

**Ingestion pipeline:** parse (PDF/HTML → text, tables handled explicitly) → chunk (structure-aware, ~300–800 tokens with overlap; chunk by headings not blind windows) → embed → index. Daily updates via incremental upserts keyed on doc hash, not full reindex.

**Retrieval:** hybrid — dense (embeddings in a vector DB) + sparse (BM25) fused with reciprocal rank fusion, because pure dense retrieval fails on exact identifiers, SKUs, and names. Retrieve ~50, then **cross-encoder rerank** to top 5–8. Apply ACL filters *at query time* in the index, never post-LLM.

**Generation:** system prompt enforcing answer-from-context-only with inline citations; refuse when retrieval confidence is low (calibrated threshold) rather than hallucinate.

**Evaluation — where strong candidates win the round:** build a golden set of (question, doc, answer) triples; measure retrieval recall@k separately from answer faithfulness (LLM-as-judge, spot-audited by humans). Retrieval failures and generation failures need different fixes; conflating them is the classic junior mistake.

**Follow-ups:**
- Answers are wrong — how do you tell whether retrieval or generation is failing? (Inspect retrieved chunks for a failure sample; recall@k vs faithfulness metrics.)
- Long documents where the answer spans chunks? (Parent-document retrieval: match on small chunks, feed the LLM the enclosing section.)
- Cost at 100k queries/day? (Cache embeddings and frequent answers, small model for rerank, big model only for generation.)
- When do you fine-tune instead of RAG? (Style/format/domain-language: fine-tune; volatile facts: RAG; usually both.)

</details>

### Design an AI tutoring platform with RAG-based Q&A

> Design an AI tutoring platform where students ask questions and get answers grounded in course materials — with follow-up conversations, per-student progress, and safeguards against just giving away homework answers.

**Where asked:** Reported on HelloInterview's community board as an asked-in-interview ML system design question · [HelloInterview: AI tutoring platform with RAG-based Q&A](https://www.hellointerview.com/community/questions/ai-tutoring-platform/cm75445ag00053b64gz80nijf)

**What it tests:** RAG plus *product* thinking: conversation state, pedagogy-driven prompting (Socratic mode vs answer mode), safety for minors, and per-course corpus isolation — a RAG question where the guardrails are the point.

**Difficulty:** Medium-Hard

<details><summary>💡 Strong solution approach</summary>

**Strong approach:** Requirements first: which subjects (math needs different handling than history — rendering, symbolic checking)? Age group (drives safety posture)? Scale (a university vs a consumer app)? Should it *teach* or *answer*? That last one shapes the whole design.

**Core architecture:** per-course ingestion of syllabi/textbooks/lecture notes into a vector index namespaced by course; conversation service holding dialogue state and a rolling summary (token budgets kill naive full-history approaches); RAG pipeline as in the corpus question above, scoped to the student's enrolled courses.

**The differentiating layers:**
- **Pedagogy policy:** a tutoring mode where the system prompt forbids final answers to graded-looking problems and instead elicits steps (detect "homework-shaped" queries with a classifier; escalate hints gradually).
- **Student model:** track per-topic mastery from interaction history; use it to adapt explanation depth and recommend review.
- **Safety:** age-appropriate content filters on both input and output, escalation path for self-harm signals, and no retention of PII in logs used for training.

**Evaluation:** grounded-accuracy on a per-course golden set, plus learning-outcome proxies (did the student answer the follow-up check correctly?) — not just answer quality.

**Follow-ups:**
- Math problems where retrieval is useless? (Route to a solver/code-execution tool; RAG for concepts, tools for computation.)
- How do you stop it doing the student's exam? (Detection + policy, but acknowledge honestly this is an arms race; discuss proctoring-adjacent signals.)
- Latency for a conversational feel? (Stream tokens; pre-fetch retrieval on question submit; target <1s to first token.)
- Cold start for a brand-new course with thin materials.

</details>

### Design a semantic search system at scale

> Design a semantic search system (text or visual): given a query, return the most relevant items from a corpus of hundreds of millions of embeddings, at <100ms latency, with items being added continuously.

**Where asked:** Core ML system design staple — ByteByteGo's visual-search chapter and HelloInterview's vector-DB deep dive exist because this round is asked across search/retrieval companies (Glean-style loops live here) · [ByteByteGo: Visual Search System](https://bytebytego.com/courses/machine-learning-system-design-interview/visual-search-system), [HelloInterview: Vector databases deep dive](https://www.hellointerview.com/learn/system-design/deep-dives/vector-databases), [Pinecone: vector similarity](https://www.pinecone.io/learn/vector-similarity/)

**What it tests:** Embedding-model training (two-tower/contrastive), ANN index internals (HNSW vs IVF-PQ — you must know how they work, not just name them), the freshness problem, and metadata filtering.

**Difficulty:** Hard

<details><summary>💡 Strong solution approach</summary>

**Strong approach:**

**Embedding side:** two-tower model trained contrastively (query tower, item tower; positives from clicks/co-engagement, in-batch negatives + hard negatives mined from the current index). Same embedding space for both towers so retrieval is a nearest-neighbor lookup.

**Index side — know the internals:**
- **HNSW:** multi-layer navigable small-world graph; log-ish search, high recall, but memory-hungry (graph + full vectors in RAM) and awkward to shard.
- **IVF-PQ:** k-means coarse quantizer partitions the space (probe top-nprobe cells); product quantization compresses vectors ~32×; less memory, tunable recall/latency, easier to shard.
- At 100M+ vectors: shard by IVF cell or random partition; fan out, gather, merge.

**Freshness:** ANN indexes hate in-place updates — run a small "fresh" brute-force/HNSW buffer for recent items alongside the big immutable index, merge results, rebuild the main index on a schedule. This tiered design is what separates candidates who've operated one.

**Serving path:** query → embed (cached for hot queries) → ANN top-200 with metadata pre-filtering → lightweight reranker → top-k. Pre-filter vs post-filter tradeoff: restrictive filters + post-filtering returns too few results; know that engines push filters into the index traversal.

**Metrics:** recall@k vs exact search (offline), click-through/engagement (online), p99 latency per stage.

**Follow-ups:**
- Embedding model update = every vector changes. How do you roll that out? (Dual-index blue/green, backfill, evaluate before cutover.)
- Multi-modal (text query → image results)? (CLIP-style joint space.)
- Why not just brute force on GPUs? (Legit to ~10M vectors — saying so shows judgment; cost curve flips after that.)
- Popularity bias in contrastive training and mitigation.

</details>

## B2. LLM serving and inference

### Design ChatGPT

> Design a ChatGPT-like conversational AI service end-to-end: streaming chat with conversation history for 100M+ users, on a fleet of GPUs, with safety filtering — walk through the request path and how you scale inference.

**Where asked:** OpenAI system design rounds (per igotanoffer's OpenAI interview breakdown) and now widely elsewhere; multiple detailed public breakdowns track the interview format · [IGotAnOffer: OpenAI system design interviews](https://igotanoffer.com/en/advice/openai-system-design-interview), [systemdesign.one: ChatGPT system design](https://newsletter.systemdesign.one/p/chatgpt-system-design), [crackingwalnuts: ChatGPT end-to-end](https://crackingwalnuts.com/post/chatgpt-system-design)

**What it tests:** Whether you understand what makes LLM serving unlike normal web serving: requests are long-lived, stateful-ish, GPU-bound, streamed, and wildly variable in cost. TTFT vs throughput tension is the heart of the round.

**Difficulty:** Hard

<details><summary>💡 Strong solution approach</summary>

**Strong approach:**

**Request path:** client → API gateway (auth, rate limiting — see the rate-limiter coding question) → chat service (loads conversation from a session store, assembles the prompt within the context budget: system prompt + rolling summary of old turns + recent turns) → safety filter on input → inference cluster → moderated, streamed response (SSE/WebSocket) → persist turn.

**Inference layer — where the round is won:**
- **Continuous batching:** requests join/leave the batch at token granularity (not static batches) — the single biggest throughput lever.
- **KV cache:** attention state per sequence; it's why long conversations cost GPU memory, why context length is capped, and what paged allocation (vLLM-style) manages.
- **Prefill vs decode:** prefill is compute-bound and parallel; decode is memory-bandwidth-bound and sequential — schedule them differently (or disaggregate onto separate pools).
- **Metrics:** TTFT (time to first token — UX) and TPOT/tokens-per-second (throughput — cost). Larger batches improve cost but hurt TTFT; state this tradeoff explicitly.

**Scale-out:** model replicas across GPU pods (tensor-parallel within a node for big models); router with session affinity so a conversation's KV cache can be reused; autoscaling on queue depth; priority classes (paid vs free) with separate queues.

**Conversation memory:** don't stuff the full history — rolling summarization plus recent-turn window; long-term user memory as a separate retrieval layer.

**Follow-ups:**
- GPU capacity math: rough tokens/sec per GPU for a given model size → GPUs for X concurrent users (interviewers want the estimation reflex, not exact numbers).
- Regional failover when a GPU cluster dies mid-conversation? (Conversations rebuild from the session store; KV cache is disposable.)
- Prompt caching for shared system-prompt prefixes.
- Where does speculative decoding fit and what breaks it? (Acceptance rate drops on unusual text.)

</details>

### Design a high-throughput LLM inference platform

> Design the model-serving platform itself: multi-tenant LLM inference for several models, maximizing GPU utilization while meeting p99 latency SLOs. Cover batching, memory management, quantization, and autoscaling.

**Where asked:** AI-infra loops at inference companies (Together AI-style SWE rounds; vLLM's architecture is effectively the reference answer the industry converged on) · [PracHub: Together AI SWE questions](https://prachub.com/companies/together-ai/positions/software-engineer), [Red Hat: why vLLM](https://developers.redhat.com/articles/2025/10/30/why-vllm-best-choice-ai-inference-today), [vLLM production stack docs](https://docs.vllm.ai/en/latest/deployment/integrations/production-stack/)

**What it tests:** One level deeper than "design ChatGPT" — PagedAttention-style memory management, quantization tradeoffs, speculative decoding, and multi-tenancy scheduling. This is the round that separates users of vLLM from people who could build it.

**Difficulty:** Hard (specialist round)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:**

**The core insight to lead with:** LLM serving is a *memory management* problem. Decode throughput is bounded by how many sequences' KV caches fit in GPU memory, and naive contiguous pre-allocation wastes 60–80% of it. **PagedAttention** fixes this: KV cache in fixed-size blocks with an indirection table (virtual memory for attention), enabling near-zero fragmentation and copy-on-write prefix sharing.

**Scheduler:** continuous batching with iteration-level scheduling; admission control based on projected KV memory (prompt length + max output); preemption policy when memory pressure hits (swap-to-CPU vs recompute — recompute usually wins).

**Model efficiency menu, with tradeoffs:** weight quantization (INT8/FP8/AWQ — ~2× memory, small quality cost; per-model eval required), KV-cache quantization, speculative decoding (draft model proposes k tokens, target verifies in one pass — exact outputs, big decode speedup when acceptance is high), prefix caching for shared system prompts.

**Multi-tenancy:** per-tenant token-budget scheduling (not request counts), SLO classes (interactive vs batch), fairness via weighted round-robin over queues. Autoscaling on queue-time and KV-utilization, not CPU.

**Observability:** TTFT/TPOT percentiles per model, KV-cache utilization, preemption rate, tokens/sec/GPU — and cost per million tokens as the north-star metric.

**Follow-ups:**
- One 70B model or one node? Tensor parallel vs pipeline parallel — communication patterns and when each wins.
- Prefill/decode disaggregation: why serve them on separate GPU pools?
- How does structured output (JSON mode / grammar-constrained decoding) affect the serving stack?
- A tenant sends 1M-token-context requests — what breaks first and what's your policy?

</details>

## B3. Evaluation systems

### Design an LLM evaluation pipeline

> Your team ships an LLM product and changes prompts/models weekly. Design the evaluation system that decides whether a change is safe to ship — offline and online.

**Where asked:** Reported as a rising staple of AI-engineer onsites ("evals and agent harnesses are what AI teams are actually building/interviewing on"); AWS ships a reference implementation because teams keep being asked to build one · [Hilary An: LLM evals and agent harnesses](https://hilaryan.substack.com/p/llm-evals-and-agent-harnesses-the), [AWS samples: automated LLM evaluation pipeline](https://github.com/aws-samples/build-an-automated-large-language-model-evaluation-pipeline-on-aws/blob/main/README.md), [HelloInterview: evaluation core concepts](https://www.hellointerview.com/learn/ml-system-design/core-concepts/evaluation), [Latitude: building LLM eval pipelines](https://latitude.so/blog/how-to-build-automated-llm-evaluation-pipelines)

**What it tests:** The judgment layer of AI engineering: golden sets, LLM-as-judge and its failure modes, CI-style regression gates, and connecting offline metrics to online outcomes. Weak candidates say "we'd use an eval framework"; strong ones design the data flywheel.

**Difficulty:** Medium-Hard

<details><summary>💡 Strong solution approach</summary>

**Strong approach:**

**Offline layer:**
- **Golden dataset:** 200–1000 curated cases sampled from real traffic (stratified by intent/difficulty), with reference answers or rubrics; versioned like code; refreshed from production failures — the flywheel.
- **Graders, in order of trust:** exact/programmatic checks where possible (format, citations present, code runs) → model-based rubric grading (LLM-as-judge) → periodic human audit of judge agreement.
- **LLM-as-judge hygiene** (this is where you win the round): pairwise comparison beats absolute scores; randomize position (position bias is real); use a judge model different from the generator (self-preference bias); calibrate against a human-labeled sample and report judge-human agreement, not just judge scores.

**CI gate:** every prompt/model change runs the eval suite; block on regression beyond a threshold with statistical significance (bootstrap over cases — 3 points on 200 cases can be noise); track per-slice results so an aggregate win can't hide a slice regression.

**Online layer:** shadow traffic first (log, don't serve) → small-% A/B on product metrics (task completion, thumbs, retention — not judge scores) → drift monitors on input distribution and output properties (length, refusal rate, sentiment) as canaries.

**Follow-ups:**
- Judge and humans disagree 30% of the time — now what? (Tighten rubrics, decompose into binary checks, more human labels on disputed slices.)
- Evals for agents/multi-turn? (Trajectory-level: task success, tool-call correctness, steps-to-completion; simulated users.)
- Contamination: your golden set leaks into a fine-tune — detection and rotation policy.
- Cost: full suite per PR is expensive — tiered evals (smoke set per commit, full set nightly).

</details>

## B4. Applied ML system design

### Design a real-time fraud detection system

> Design a system that scores every payment for fraud in real time (<100ms), at thousands of transactions per second, with a feedback loop from confirmed fraud labels — and explain how you handle extreme class imbalance.

**Where asked:** Stripe system design/ML loops (candidate write-up of the Stripe round) and a canonical MLSD case across fintech · [Medium: Every question I was asked in Stripe's system design interview](https://medium.com/@emilyhustlenyc/every-question-i-was-asked-in-stripes-system-design-interview-f6f19c2e62d6), [Manish Mazumder: real-time fraud detection MLSD](https://manishmazumder5.substack.com/p/real-time-fraud-detection-ml-system), [DataInterview: fraud detection case](https://www.datainterview.com/courses/machine-learning-system-design/case-fraud-detection)

**What it tests:** The classic MLSD trifecta — streaming feature engineering, online/offline consistency (the feature-store problem), and decision policy under asymmetric costs — plus label-delay handling that most candidates forget.

**Difficulty:** Hard

<details><summary>💡 Strong solution approach</summary>

**Strong approach:**

**Features (the substance of the round):** entity aggregates over sliding windows — card: transactions/amount in last 1m/1h/24h, distinct merchants, velocity across geographies; merchant: chargeback rate, amount distribution; pair: is this card new to this merchant; device/IP graph signals. Computed via a stream processor (Flink/KStreams) into an online feature store (Redis/DynamoDB) with the **same feature definitions** used for offline training — name the online/offline skew problem explicitly; it's the most common real-world failure.

**Model:** gradient-boosted trees (XGBoost/LightGBM) as the workhorse — tabular SOTA, fast inference, interpretable enough for disputes; optionally a deep component for sequence/graph signals. Handle imbalance (≪1% fraud) via class weighting or focal loss — and evaluate with PR-AUC / recall-at-fixed-FPR, never accuracy or plain ROC-AUC.

**Decision layer:** score → threshold bands: approve / step-up (3DS challenge) / block. Thresholds set by expected cost: false positives burn good customers and revenue, false negatives cost chargebacks — the step-up middle band is how real systems soften the tradeoff.

**Feedback loop with label delay:** chargebacks arrive 30–90 days late. Train on mature data, monitor on proxies (rule hits, customer reports), and beware feedback bias — blocked transactions never get labels (mitigate with a small exploration/holdout stream).

**Follow-ups:**
- Fraudsters adapt weekly — retraining cadence, drift detection, and why rules + model coexist (rules for instant response to new attack patterns, model for coverage).
- p99 latency budget breakdown: feature fetch vs inference vs network; graceful degradation when the feature store times out (fallback ruleset, fail-open vs fail-closed by amount).
- Explainability for declined customers and regulators (SHAP on GBDT, reason codes).
- Graph angle: fraud rings share devices/addresses — batch graph features vs online GNN, and why most shops do the former.

</details>

### Design a personalized recommendation feed

> Design the recommendation system behind a personalized feed (e.g., Instagram/Facebook feed or marketplace recs): billions of items, hundreds of millions of users, fresh content, ranked for engagement.

**Where asked:** Meta — MLE system design round (consistently reported; it's the canonical Meta MLE question) · [IGotAnOffer: Meta MLE interview](https://igotanoffer.com/blogs/tech/facebook-machine-learning-engineer-interview), [Glassdoor: Meta MLE interview questions](https://www.glassdoor.com/Interview/Meta-Machine-Learning-Engineer-Interview-Questions-EI_IE40772.0,4_KO5,30.htm), [ApplyingML: system design for discovery](https://applyingml.com/resources/discovery-system-design/)

**What it tests:** The retrieval → ranking → re-ranking funnel, two-tower retrieval, feature/training pipeline design, cold start, and metric thinking (engagement vs long-term value). At Meta this round is pass/fail on whether you volunteer the funnel structure unprompted.

**Difficulty:** Hard

<details><summary>💡 Strong solution approach</summary>

**Strong approach:** Lead with the funnel — billions of items can't be scored by a heavy model per request:

1. **Retrieval (billions → ~thousands):** multiple candidate sources merged — two-tower embedding retrieval (user tower from history/profile, item tower from content/engagement; ANN lookup), social/graph candidates, freshness pool, followed creators.
2. **Ranking (~thousands → ~hundreds):** heavy model, multi-task — predicts P(click), P(like), P(share), P(hide), dwell — combined via a tuned value formula. Architecture: large sparse-embedding + DNN (DLRM-family). Features: user, item, context, and crucially user-item interaction history sequences.
3. **Re-ranking (business layer):** diversity (don't show 10 from one creator — MMR/sliding rules), freshness boosts, integrity filters, ads slotting, exploration (small % random/UCB for new items — this is also the cold-start answer for items).

**Training pipeline:** log impressions + outcomes → point-in-time-correct feature joins (no leakage — say this phrase) → daily/continual training; monitor online/offline metric correlation.

**Cold start:** new items → content embeddings + exploration quota; new users → onboarding interests, popularity priors, contextual bandits early on.

**Metrics:** offline AUC/recall@k per task; online — the real targets — sessions, time-well-spent, retention; guardrails: hides, reports, creator diversity. Mention the engagement-vs-wellbeing tension; Meta interviewers respond well to metric skepticism.

**Follow-ups:**
- Position bias in logged data (higher slots get more clicks regardless of quality) — inverse-propensity weighting or a position feature at train + fixed at serve.
- Feedback loops: the model shapes the data it trains on — exploration and holdout slices.
- Real-time personalization: user acts on item → feed adapts within seconds (streaming user-sequence features).
- How would LLMs change this stack? (Semantic item understanding, LLM-augmented features, conversational discovery — keep it grounded.)

</details>

### Design a centralized ML training and management platform

> Design a centralized platform for your company's ML teams: training-job orchestration, experiment tracking, a feature store, a model registry, deployment, and monitoring — the internal "ML platform" round.

**Where asked:** Meta engineer mock (recorded on interviewing.io in Meta's real format); the internal-platform variant is a common senior MLE/infra round at big tech · [Interviewing.io: Meta engineer mock — centralized ML management platform](https://interviewing.io/mocks/facebook-system-design-centralized-ml-management-platform), [alirezadir: ML system design compilation](https://github.com/alirezadir/machine-learning-interviews/blob/main/src/MLSD/ml-system-design.md)

**What it tests:** Senior-level breadth — you're designing for *engineers* as users: multi-tenancy on GPUs, reproducibility, lineage, and the eternal flexibility-vs-paved-road tension. It's an org-design question wearing a systems costume.

**Difficulty:** Hard (senior/staff round)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:** Scope by user journey: an MLE goes data → features → experiment → train → evaluate → register → deploy → monitor. Design one paved road through it.

- **Data/features:** feature store with offline (warehouse, point-in-time joins for training) and online (low-latency KV for serving) planes sharing one definition — killing online/offline skew is the store's entire reason to exist.
- **Experimentation:** tracked runs (params, metrics, artifacts, code+data versions) — every result reproducible from its lineage record.
- **Training orchestration:** jobs as DAGs on a GPU cluster (Kubernetes + scheduler); quotas + preemption by priority; spot capacity with checkpointing for cost; distributed training as a library, not per-team hand-rolls.
- **Model registry:** versioned models with lineage (data, code, metrics), stage transitions (staging → prod) gated by eval suites — the CI/CD of models.
- **Serving:** standard containers for online (autoscaled, canary/shadow rollout) and batch; per-model dashboards out of the box.
- **Monitoring:** input drift, prediction drift, feature-freshness alarms, and delayed-label performance tracking; every deployed model gets these by default, not by team diligence.

The senior move: discuss *adoption* — platforms fail socially, not technically. Golden-path templates, migration support, escape hatches for research teams, and platform metrics (time-to-first-model, % models on-platform).

**Follow-ups:**
- GPU scarcity: fair-share vs priority quotas; how do you stop one team hoarding?
- One team needs a custom training loop the platform doesn't support — bend the platform or let them off-road? (Escape hatch with contract: they own their ops.)
- How does the platform change for LLM fine-tuning workloads vs classic ML? (Bigger checkpoints, shared base models, adapter/LoRA registries, eval harnesses replacing test sets.)
- Buy vs build for each layer.

</details>

## B5. Training and alignment pipelines

### Design an RLHF pipeline

> Design the post-training pipeline that aligns a base LLM with human preferences: SFT, reward modeling, and RL fine-tuning — data collection, infrastructure, and how you know it worked.

**Where asked:** Reported in research-engineering loops at frontier labs (post-training design questions feature in lab interview write-ups; the HF/AWS explainers are the canonical prep material) · [Yuan Meng: MLE Interview 2.0 — research engineering rounds](https://www.yuan-meng.com/posts/mle_interviews_2.0/), [HuggingFace: Illustrating RLHF](https://huggingface.co/blog/rlhf), [AWS: What is RLHF](https://aws.amazon.com/what-is/reinforcement-learning-from-human-feedback/), [Toloka: complete RLHF guide](https://toloka.ai/blog/what-is-rlhf/)

**What it tests:** Whether you understand alignment as a *system*: three coupled training stages, a human-data operation, reward hacking as the central failure mode, and the DPO-vs-PPO decision every lab has actually faced.

**Difficulty:** Hard (research-engineering round)

<details><summary>💡 Strong solution approach</summary>

**Strong approach:** Present the three-stage pipeline, then go deep where the interviewer steers.

**Stage 1 — SFT:** curate high-quality demonstrations (human-written + filtered synthetic); train the base model to follow instructions. Quality >> quantity; data mixture is a first-class design decision.

**Stage 2 — Reward model:** collect *pairwise preferences* (annotators pick the better of two responses — far more reliable than absolute scores); train an RM (usually the SFT model + scalar head) on Bradley-Terry loss. The data operation is the hard part: rater guidelines, inter-annotator agreement tracking, disagreement adjudication, and rater-pool diversity — say this; labs grade for it.

**Stage 3 — RL:** PPO against the RM with a **KL penalty to the SFT policy** — the KL term is what stops the policy from wandering into RM-exploiting gibberish. Infra reality: four models in memory (policy, reference, RM, value) — this is why RLHF infra is expensive and why the alternative exists:

**DPO vs PPO — the expected discussion:** DPO optimizes preferences directly with a classification-style loss (no RM at inference of the loop, no rollouts, dramatically simpler infra, more stable); PPO enables online exploration and iterated data collection and still edges it for frontier quality. Reasonable answer: DPO first for iteration speed, PPO/online methods when you have the infra and need the last few points.

**The central failure mode — reward hacking:** the policy exploits RM blind spots (length bias → verbosity, sycophancy, confident hedging). Mitigations: KL constraint, RM ensembles, iterated RM retraining on fresh policy samples, and *held-out human eval as the final arbiter* — never trust RM score alone, it's Goodhart's law in production.

**Evaluation:** win-rate vs the SFT baseline (human + LLM judge), capability regression suites (alignment tax check), safety red-teaming.

**Follow-ups:**
- RM score goes up, human eval goes down — diagnose. (Reward hacking; inspect high-RM samples, retrain RM on adversarial pairs.)
- Where do RLAIF / constitutional approaches slot in? (AI feedback replaces/augments human labels; scales the preference-data bottleneck.)
- Online (PPO/GRPO) vs offline (DPO) preference optimization — sample efficiency and distribution-shift tradeoffs.
- How does this differ for reasoning models? (Verifiable rewards — unit tests, math checkers — replace learned RMs where outputs are checkable; RLVR.)

</details>

---

<div align="center">

**Practice these out loud. [Landed](https://landed.jobs) runs voice mock interviews that grill you on exactly these questions — plus daily matched AI roles and agent-drafted application answers.**

[![Get Started](https://img.shields.io/badge/Get%20Started%20Free-→-6C2BD9?style=for-the-badge)](https://landed.jobs)

<sub>Every question traces to a public candidate report — sources inline. Asked something new recently? PRs welcome. · [All banks →](../README.md)</sub>

</div>
