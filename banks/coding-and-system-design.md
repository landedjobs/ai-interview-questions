[← All question banks](../README.md) · part of [ai-interview-questions](https://github.com/landedjobs/ai-interview-questions) by [Landed](https://landed.jobs)

<div align="center">

# 💻 Coding Exercises & ML System Design — Real AI Interview Questions

![Updated](https://img.shields.io/badge/updated-2026.07-00A86B?style=flat-square) ![Questions](https://img.shields.io/badge/64%20real%20questions-ff5b29?style=flat-square) ![Sources](https://img.shields.io/badge/every%20question-cited-6C2BD9?style=flat-square)

**Every exercise below was reported by a real candidate, with the company, stage, and source. Answers are what a strong candidate actually does.**

</div>

---

## Jump to

**Section A — Coding exercises (37):**
[A1. Tokenization, attention and transformers](#a1-tokenization-attention-and-transformers) · [A2. Sampling and decoding](#a2-sampling-and-decoding) · [A3. Debugging ML systems](#a3-debugging-ml-systems) · [A4. Classic ML from scratch](#a4-classic-ml-from-scratch) · [A5. Training-loop engineering](#a5-training-loop-engineering) · [A6. Retrieval and RAG coding](#a6-retrieval-and-rag-coding) · [A7. Agents, LLM APIs and production plumbing](#a7-agents-llm-apis-and-production-plumbing) · [A8. Systems, performance and take-homes](#a8-systems-performance-and-take-homes)

**Section B — ML/LLM system design (27):**
[B1. LLM serving and inference](#b1-llm-serving-and-inference) · [B2. RAG, search and retrieval](#b2-rag-search-and-retrieval) · [B3. Training, fine-tuning and alignment](#b3-training-fine-tuning-and-alignment) · [B4. Evaluation and safe deployment](#b4-evaluation-and-safe-deployment) · [B5. Agents and AI products](#b5-agents-and-ai-products) · [B6. Applied ML systems](#b6-applied-ml-systems)

---

## Section A — Coding exercises

The pattern across 2024–2026 loops is consistent: less LeetCode, more "build or debug a real ML/LLM primitive from scratch, in plain Python/NumPy/PyTorch, while talking through it." A strong 2026 candidate is expected to **debug ML systems end-to-end**, not just implement fresh components — and the "transport plumbing" (rate limiting, retries, streaming, batching) now eats at least one prompt per loop.

## A1. Tokenization, attention and transformers

### Implement a BPE tokenizer from scratch

> Implement a Byte Pair Encoding (BPE) tokenizer. Write `train(corpus, vocab_size)` that learns the merge rules, and `encode(text)` / `decode(ids)` that apply them. No external tokenizer libraries.

**Where asked:** OpenAI — ML Engineer coding round; also reported as a take-home at Anthropic for ML Engineer candidates · [PracHub (question)](https://prachub.com/interview-questions/implement-a-byte-pair-encoding-bpe-tokenizer) · [PracHub (OpenAI MLE bank)](https://prachub.com/companies/openai/positions/machine-learning-engineer) · [Raschka: BPE from scratch (Jan 17 2025)](https://sebastianraschka.com/blog/2025/bpe-from-scratch.html)

**What it tests:** Understanding that BPE is *deterministic given merges*; keeping the merge table as an ordered priority structure, not a list; round-trip stability across non-ASCII bytes; handling of GPT-2/GPT-4 whitespace pre-tokenization patterns.

**Time expected:** 60–90 minutes.

**Difficulty:** Medium-Hard.

<details><summary>💡 Strong solution approach</summary>

Start from a 256-byte base vocab, count adjacent-pair frequencies, repeatedly merge the most frequent pair into a new token, and record merges in order. Encoding replays merges by rank.

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

**Gotchas that sink candidates:** O(N²) per merge if you rescan the whole corpus (use a heap of pair counts + incremental updates); using a Python set instead of a dict for merges; forgetting that merges are *ordered*; losing byte-level determinism on UTF-8 boundaries. Strong candidates account for GPT-2-style regex pre-tokenization (`'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+`) and call out that this is what makes subword tokenization non-trivial.

**Follow-ups:** Why BPE over word-level or char-level vocab? (OOV handling vs sequence length.) What breaks with multilingual text if you train on English-heavy data? (Token fertility — the same sentence costs 3–5× more tokens in low-resource languages.)

</details>

### Implement scaled dot-product self-attention

> Given matrices Q, K, V of shape `(seq_len, d_k)`, implement scaled dot-product attention in NumPy or PyTorch — no `nn.MultiheadAttention`, no `F.scaled_dot_product_attention`. Support an optional causal mask.

**Where asked:** Reported across OpenAI, Meta, and AI-lab MLE screens; now standardized as a NeetCode problem because it comes up so often · [NeetCode: Self Attention](https://neetcode.io/problems/self-attention/question) · [r/MachineLearning: LC questions asked for AI/MLE roles](https://www.reddit.com/r/MachineLearning/comments/1o5zhqo/d_interview_prep_what_lc_questions_were_u_asked/) · [CodeSignal lesson](https://codesignal.com/learn/courses/sequence-models-the-dawn-of-attention-1/lessons/scaled-dot-product-attention-and-masking-in-transformers-1)

**What it tests:** The single most important equation in modern ML, written correctly: scaling by √d_k, numerically stable softmax, and masking applied *before* softmax with −inf (not zero).

**Time expected:** 15–20 minutes — table stakes for any LLM role.

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

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

**Follow-ups:** Extend to batched multi-head (see the next question). Time and memory complexity? O(n²·d) time, O(n²) memory for the score matrix — this is the lead-in to the FlashAttention question below. What's the difference between padding masks and causal masks, and how do they combine? Why multiple heads instead of one big head? (Multiple learned similarity subspaces.)

</details>

### Implement multi-head self-attention correctly

> "Implement a multi-head self-attention layer (forward pass) using PyTorch or NumPy that: Projects inputs into queries (Q), keys (K), and values (V)…" — PracHub records that this evaluates "practical implementation skills and conceptual understanding of multi-head self-attention, including query/key/value projections, head-wise tensor reshaping, masking behavior, and considerations for numerical stability and computational complexity."

**Where asked:** Apple — ML Engineer, technical screen (and multiple ML interview trackers) · [PracHub (Mar 29 2026)](https://prachub.com/interview-questions/implement-multi-head-self-attention-correctly) · Also listed by Voker under Google NumPy coding: "Implement multi-head attention in NumPy: scaled dot-product for batched Q,K,V. Do per-head projections, reshape, apply mask, and return attention weights." · [Voker (2026)](https://voker.io/explore/interview/question/google-ml-coding-hand-code-multi-head-attention-in-numpy)

**What it tests:** Tensor shape discipline; understanding that multi-head attention computes attention in parallel across subspaces, not sequentially; mask semantics (additive vs multiplicative, padding vs causal); numerical stability via softmax over scaled logits.

**Time expected:** 45–60 minutes.

**Difficulty:** Hard.

<details><summary>💡 Strong solution approach</summary>

Accept `x` of shape `(B, T, D)`. Project once into `Q, K, V` of `(B, T, H*D_head)`; then `reshape` to `(B, H, T, D_head)` to keep heads independent.

```python
scores = (Q @ K.transpose(-2, -1)) / sqrt(D_head)          # (B, H, T, T)
scores = scores.masked_fill(mask == 0, float("-inf"))      # mask BEFORE softmax
attn = softmax(scores, dim=-1)
out = (attn @ V)                                           # reshape back to (B, T, D)
```

Gotchas separating strong from weak: (1) failing to scale by `1/sqrt(D_head)` causes softmax saturation and zero-grad on first/last tokens; (2) applying softmax before the mask silently masks the wrong positions; (3) collapsing H into the batch dim instead of reshaping loses parallelism semantics; (4) PyTorch's `softmax` is numerically stable only along the right axis. Mention causal mask efficiency with `torch.triu(torch.ones(T, T), diagonal=1)` if time allows.

</details>

### Implement a Transformer block from scratch

> Implement a full transformer block in PyTorch: multi-head attention, feed-forward network, residual connections, and layer norm. You may use `nn.Linear` but nothing higher-level.

**Where asked:** Reported in research-engineering onsites at frontier labs (a Pinterest→lab candidate describes "implement a transformer, layer by layer, from memory" rounds) · [Yuan Meng: MLE Interview 2.0](https://www.yuan-meng.com/posts/mle_interviews_2.0/) · [Mislav Jurić: Transformer from scratch in PyTorch](https://www.mislavjuric.com/transformer-from-scratch-in-pytorch/) · [HuggingFace forum walkthrough](https://discuss.huggingface.co/t/tutorial-implementing-transformer-from-scratch-a-step-by-step-guide/132158)

**What it tests:** Architecture fluency beyond the attention equation — pre-norm vs post-norm, where residuals attach, head splitting/merging shapes, and whether you can wire modules together without a reference.

**Time expected:** 30–45 minutes for a clean, shape-correct block.

**Difficulty:** Hard.

<details><summary>💡 Strong solution approach</summary>

Write the skeleton first, then fill in; interviewers reward structure.

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

**Follow-ups:** Add positional information — compare learned embeddings, sinusoidal, and RoPE; why RoPE won for long context. Parameter count of one block as a function of d_model? (~12·d_model² with d_ff = 4·d_model.) Decoder-only vs encoder-decoder — what changes structurally? Where does KV caching plug into your `forward` at inference time?

</details>

### Implement FlashAttention-style tiled attention

> Implement attention without ever materializing the full N×N attention matrix — process K/V in tiles and keep a running softmax, FlashAttention-style.

**Where asked:** Mistral AI — reported by a candidate describing the Mistral process ("implement flash attention") · [Candidate post (Facebook ML group)](https://www.facebook.com/groups/595424764221375/posts/2410312236065943/) · [TDS: Writing FlashAttention from scratch](https://towardsdatascience.com/understanding-flash-attention-writing-the-algorithm-from-scratch-in-triton-5609f0b143ea/) · [InterviewCoder: Mistral prep guide](https://www.interviewcoder.co/blog/mistral-ai-interview-questions)

**What it tests:** Whether you understand *why* attention is memory-bound and can derive the online-softmax trick — the difference between using transformers and understanding GPU-era transformers. A signature question for inference/training-infra roles at European labs.

**Time expected:** ~45–60 minutes (the online softmax rescaling is the whole interview).

**Difficulty:** Hard.

<details><summary>💡 Strong solution approach</summary>

The key identity: softmax can be computed incrementally. For each query row, sweep K/V tiles while maintaining a running max `m`, running normalizer `l`, and running output `o`, rescaling previous partial results when a new max appears.

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

Explain the systems framing: standard attention is O(N²) HBM traffic; tiling keeps the working set in SRAM, so FlashAttention is an **IO-aware** algorithm — same FLOPs, far less memory movement, exact (not approximate) result.

**Follow-ups:** Also tile the queries (the real algorithm is a 2D loop) and handle the causal mask per tile. Why is attention memory-bound rather than compute-bound on modern GPUs? Backward pass: why does FlashAttention recompute the attention matrix instead of storing it? How does this interact with KV caching at inference — what's different in decode (one query row) vs prefill?

</details>

## A2. Sampling and decoding

### Implement temperature, top-k, and top-p sampling

> "Implement a sampling routine that supports temperature, top-k, and top-p (nucleus) filtering."

**Where asked:** AI Engineer / ML Engineer take-homes at OpenAI, Anthropic, Cohere, Mistral, and AI-native startups; reported on AI Engineer prep lists 2024–2026 as a paid take-home or 60-min live coding · [Raschka: LLM sampling series](https://sebastianraschka.com/faq/docs/temperature-topk-topp-sampling.html) · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** NumPy/PyTorch fluency; understanding that top-p is *cumulative* over sorted probabilities; edge cases when the distribution is small; order of operations (temperature → filter → renormalize).

**Time expected:** 45–60 minutes.

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

Sort logits descending, compute softmax, cumsum, mask tokens past the smallest prefix whose cumulative ≥ p, renormalize.

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

Gotchas: forgetting to apply temperature *before* top-k/p; masking tokens to 0 instead of −inf (lets them survive softmax on tie scores); not seeding the RNG and getting flaky tests; off-by-one in the cumulative cutoff ("strictly greater" vs "≥") — the token that *crosses* the top-p threshold must be kept, otherwise top_p=0.1 with a 0.5-prob top token would remove everything.

**Follow-ups:** What does temperature → 0 converge to? (Greedy argmax.) Why does top-p adapt better than top-k across confident vs uncertain distributions? Why is generation non-deterministic even at temperature 0 on real serving stacks? (Batching non-determinism, floating-point reduction order.)

</details>

### Implement beam search decoding

> Implement beam search decoding for an autoregressive language model: given `model(prefix) -> log_probs`, return the highest-scoring sequence with beam width k.

**Where asked:** Perplexity AI — candidate report of the exact question · [1point3acres candidate report](https://www.1point3acres.com/interview/post/7100135) · [Exponent: Perplexity question bank](https://www.tryexponent.com/questions?company=perplexity-ai) — also appears combined with sampling prompts at Mistral, Cohere, and AI startups.

**What it tests:** Search-over-sequences reasoning: score accumulation in log space, hypothesis bookkeeping, EOS handling, and length normalization (score with `log P(seq) / len(seq)^alpha` to avoid the naive length-bias bug) — plus whether you can discuss when beam search is the *wrong* choice for open-ended generation.

**Time expected:** ~30–45 minutes.

**Difficulty:** Medium-Hard (EOS handling is where candidates break).

<details><summary>💡 Strong solution approach</summary>

Maintain k live hypotheses; each step, expand every hypothesis by the top candidates, then keep the global top k by cumulative log-prob. Move finished (EOS) hypotheses to a completed pool instead of expanding them.

```python
import heapq

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

**Follow-ups:** Complexity vs greedy? (k× model calls per step; batch the k hypotheses into one forward pass.) Why do chat LLMs use sampling instead of beam search? (Beam search finds high-likelihood but degenerate/repetitive text for open-ended generation; it wins for closed tasks like translation.) How does beam search interact with a KV cache? (Cache must fork/reorder with the beams — a real serving cost.)

</details>

## A3. Debugging ML systems

### Debug a transformer with 4 failing tests, then train a classifier (OpenAI)

> "You are given a transformer-based ML model with four failing unit tests — two bugs are known, two are novel. Identify, debug, and fix each bug so the model trains and evaluates correctly. Given a labeled dataset, write code to train a classifier, analyze the dataset (class balance, feature distributions), and report key performance metrics."

**Where asked:** OpenAI — Machine Learning Engineer, technical screen · [PracHub (Apr 20 2026; first published Aug 4 2025)](https://prachub.com/interview-questions/debug-transformer-and-train-classifier) — reported alongside related OpenAI prompts "Implement 1NN with NumPy", "Compute entropy and implement 1-NN", "Implement Backprop for a Tiny Network", and "Debug MiniGPT and Backpropagate Matmul".

**What it tests:** Triage discipline; whether you read the existing encoder-head contract before "fixing" anything; whether you map each failing test to a class of failure (loss-mismatch, label-mismatch, leakage in split, encoder not wired) before reaching for code.

**Time expected:** 75–90 minutes (60 min coding + 15–30 min EDA/metrics).

**Difficulty:** Hard.

<details><summary>💡 Strong solution approach</summary>

**Part A — Debug.** The strong move is the order of operations:

1. Reproduce each failing test in isolation and capture its actual vs expected output.
2. Classify each failure as loss-mismatch, label-mismatch, encoder-head wiring bug, or split/leakage bug.
3. For the "known" bugs, look at the docstring / git history first.
4. For "novel" bugs, write a minimal failing example before editing the model.
5. Add a regression assertion per fix that genuinely distinguishes the bug from the fix (e.g., a test that asserts the label encoder returns `long` not `int`).

Gotchas that sink candidates: chasing the "novel" frame and missing that a known bug is misdescribed; rewriting the encoder instead of testing whether the head consumes `[CLS]` vs pooled mean; failing to run *all* tests after each fix.

**Part B — Train/evaluate.** Show EDA that drives a decision: class counts, untruncated length histogram, truncation rate, duplicate rate. Pick a leakage-free split (stratified K-fold if K is small); compute class weights from train only; use linear warmup + cosine decay; gradient-clip at 1.0; dynamic padding; select on macro-F1 (resists imbalance) with a confusion matrix; report ROC-AUC when K=2. Pin seeds and `torch.use_deterministic_algorithms(True)` for reproducibility — and call out the run-time trade-off.

</details>

### Debug an actual LLM inference step in a 20–30 line Colab skeleton (Anthropic)

> "The weirdest part was the final round: they dropped me into a Google Colab notebook with maybe 20 to 30 lines of skeleton Python and asked me to debug an actual LLM inference step" — and was "explicitly told not to use an LLM." Preceded by a 15-minute "open-ended alignment brainstorm". Other rounds: "database-style CodeSignal rounds designed to test raw coding implementation speed."

**Where asked:** Anthropic — AI Safety Fellow (MLE track), final onsite round · [Exponent candidate report (2026)](https://www.tryexponent.com/experiences/anthropic-machine-learning-engineer-interview-8c0afd)

**What it tests:** Faithful step-through of a forward pass without leaning on an LLM for hints; identifying numeric/tensor-shape mismatches in a tiny inference skeleton; comfort reasoning about KV-cache, sampling temperature, and logits manipulation.

**Time expected:** 55 minutes for the Colab round (per Exponent); 15 minutes alignment brainstorm.

**Difficulty:** Hard.

<details><summary>💡 Strong solution approach</summary>

Treat the skeleton as a black box you cannot search-engine. Narrate your read of each line — what tensor comes in, what tensor goes out — and trace one prompt end-to-end on paper before touching code.

Build a checklist of likely defect classes: shape mismatch between hidden states and `lm_head`; off-by-one in position IDs; softmax temperature missing or applied twice; top-k applied before vs after temperature; masking on the wrong axis; NaN from log(0) in cross-entropy; jinja templating eating whitespace in chat templates. Diagnose via print-shape checkpoints inserted at module boundaries.

Stretch-time signal: notice when an apparent bug is actually a *correct* numerical-noise tolerance and skip chasing it. Crucial etiquette: stay narrative ("I'm scanning for shape errors first, then for sampling bugs"), never paste an external snippet, never silently invoke an LLM.

</details>

### Implement backprop for a tiny network (OpenAI)

> "Implement Backprop for a Tiny Network" (rated hard, 137 candidate reports) and the sibling prompt "Debug MiniGPT and Backpropagate Matmul" (rated medium, 58 candidate reports).

**Where asked:** OpenAI — ML Engineer, technical screen (live coding); PracHub reports the same category at Anthropic and other AI-native employers · [PracHub (Apr 20 2026)](https://prachub.com/interview-questions/debug-transformer-and-train-classifier) · [PracHub OpenAI bank — "240+ real OpenAI interview questions"](https://prachub.com/companies/openai)

**What it tests:** Differentiating through a matmul; whether you can hand-roll a backward kernel and match a numerical gradient check; chain rule under non-linearities.

**Time expected:** 60–90 minutes.

**Difficulty:** Hard.

<details><summary>💡 Strong solution approach</summary>

Define the forward pass as a list of `{'x':, 'w':, 'b':, 'act':}` records, then run reverse-mode:

```python
dy = 1.0
for layer in reversed(layers):
    dx, dW, db = local_grad(layer, dy)
    dy = dx
```

Gotchas: forgetting a transposed weight during matmul backward; using `.T` on a non-2D tensor; a numerical gradient check tolerance (1e-5) silently passing because both directions go to NaN; mixing `torch.no_grad` and autograd and getting surprising gradients; not handling broadcasting in the bias backward.

</details>

## A4. Classic ML from scratch

### Implement k-means from scratch

> "ML Coding Interview: K-Means — K-Means is an unsupervised learning algorithm used for clustering data points into groups based on similarity."

**Where asked:** Anthropic and OpenAI phone screens (algorithmic / "code it in plain Python"), plus AI-native startups; reported on multiple PracHub tracks · [Medium: Nailing the AI/ML Interview — K-Means](https://medium.com/nailing-the-ai-ml-interview/ml-ink-means-16d02410ac43) · [r/learnmachinelearning practice thread](https://www.reddit.com/r/learnmachinelearning/comments/xlrc0l/interview_practice_coding_kmeans_clustering_using/)

**What it tests:** Convexity/initialization sensitivity, vectorized NumPy, and the conceptual distinction between Lloyd's algorithm and accelerated variants.

**Time expected:** 30–45 minutes (NumPy), 60 minutes with k-means++ and an inertia curve.

**Difficulty:** Easy-Medium.

<details><summary>💡 Strong solution approach</summary>

Initialize by k-means++ (probability proportional to `||x − nearest centroid||²`), then iterate Lloyd's algorithm.

```python
import numpy as np

def kmeans(X, k, max_iter=100, tol=1e-6, seed=0):
    rng = np.random.default_rng(seed)
    centroids = X[rng.choice(len(X), k, replace=False)]   # or kmeans++ init
    for _ in range(max_iter):
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

Gotchas: empty cluster after an update (re-seed from the farthest point); label drift from lazily using assignments inside `mean()`; broadcasting mistakes in `||X − c||²`; float32 overflow for >1M points. Mention k-means++ without being asked — it's the expected "senior" flourish. Direct AI tie-in: k-means is exactly the coarse quantizer in IVF vector indexes — retrieval companies love this connection.

</details>

### Implement logistic regression from scratch

> "Implementation of Logistic Regression from Scratch using Python" — the classic implementation request: sigmoid, binary cross-entropy loss, gradient computation, and a vectorized gradient-descent training loop. No ML libraries.

**Where asked:** Applied ML / ML Engineer loops at Anthropic, OpenAI, and AI-native startups as a warm-up or screening prompt · [GeeksforGeeks (Aug 5 2025)](https://www.geeksforgeeks.org/machine-learning/implementation-of-logistic-regression-from-scratch-using-python/) · [r/learnmachinelearning: Failed first coding ML interview](https://www.reddit.com/r/learnmachinelearning/comments/1gvceaj/failed_first_coding_machine_learning_interview/)

**What it tests:** Cross-entropy vs softmax+log-sum-exp stability; gradient derivation (∂L/∂w = Xᵀ(σ(Xw) − y)/n) rather than recitation; weight initialization; regularization.

**Time expected:** 30–45 minutes.

**Difficulty:** Easy-Medium.

<details><summary>💡 Strong solution approach</summary>

```python
import numpy as np

def sigmoid(z):
    return np.where(z >= 0, 1 / (1 + np.exp(-z)),
                    np.exp(z) / (1 + np.exp(z)))   # stable both directions

def train(X, y, lr=0.1, epochs=1000):
    n, d = X.shape
    w, b = np.zeros(d), 0.0
    for _ in range(epochs):
        p = sigmoid(X @ w + b)
        w -= lr * (X.T @ (p - y) / n)
        b -= lr * (p - y).mean()
    return w, b
```

Gotchas: log(0) in cross-entropy without `eps`; not clipping logits, causing NaN from `sigmoid` overflow; forgetting to add L2 regularization to the loss; mixing learning-rate scaling with batch scaling under mini-batches; failing the conceptual argument for why cross-entropy (not MSE) is the right objective — MSE + sigmoid is non-convex in w and has vanishing gradients when confidently wrong.

</details>

### Compute entropy and implement 1-NN (OpenAI)

> "Compute entropy and implement 1-NN" (rated medium, 62 candidate reports) and "Implement 1NN with NumPy" (rated medium, 204 candidate reports).

**Where asked:** OpenAI — ML Engineer, technical screen · [PracHub (Apr 20 2026)](https://prachub.com/interview-questions/debug-transformer-and-train-classifier) · [PracHub OpenAI bank](https://prachub.com/companies/openai)

**What it tests:** Whether you use `log2` vs `ln` correctly, handle zero-probability, vectorize the 1-NN with `argmin` rather than a loop, and validate.

**Time expected:** 30 minutes.

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

```python
H = -np.sum(p * np.log2(p + eps))                              # entropy

dists = ((X[:, None, :] - Q[None, :, :]) ** 2).sum(-1)         # 1-NN
preds = y[dists.argmin(axis=1)]
```

Gotchas: applying `log2` to `p=0` without `eps`; storing the full `n×m×d` distance tensor for large datasets (use FAISS or blockwise computation instead); using label-encoded classes without preserving the order.

</details>

## A5. Training-loop engineering

### Write a training loop with gradient accumulation and mixed precision

> "Implement a training loop that supports mixed-precision, gradient accumulation, gradient clipping, cosine LR schedule with warmup, and deterministic reproducibility." A common live variant: "This training loop OOMs at batch size 32; only batch size 8 fits. Modify it to train with an effective batch size of 32, then add mixed precision. Explain every change."

**Where asked:** ML Engineer / AI Engineer / Applied ML roles — reported at OpenAI, Anthropic, Mistral, Cohere take-homes · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions) · [Cohere MLE interview guide](https://interview.norahq.com/interview-guides/cohere-machine-learning-engineer-interview-guide-2026) · [PyTorch: mixed precision](https://pytorch.org/blog/what-every-user-should-know-about-mixed-precision-training-in-pytorch/)

**What it tests:** Discipline around `.zero_grad()` placement, `.backward()` vs `.step()` ordering, `set_to_none=True` for memory, calling `scaler.update()` once per *effective* step (not per micro-batch), and `model.eval()` vs `train()` for dropout/BatchNorm.

**Time expected:** 60 minutes.

**Difficulty:** Medium-Hard.

<details><summary>💡 Strong solution approach</summary>

```python
scaler = torch.amp.GradScaler('cuda')
opt.zero_grad()

for step, batch in enumerate(loader):
    with torch.autocast('cuda'):
        loss = model(batch) / accum_steps       # divide, or gradients are 4x too big
    scaler.scale(loss).backward()               # grads accumulate across iterations
    if (step + 1) % accum_steps == 0:
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt)
        scaler.update()
        opt.zero_grad(set_to_none=True)
```

The graded details: (1) **divide the loss by `accum_steps`** — the dreaded trap where the per-step LR effectively multiplies by `accum_steps`; (2) `zero_grad` only after stepping, since `.backward()` accumulates by design; (3) `scaler.unscale_` before clipping so you clip true gradient norms — otherwise clip happens on scaled grads and you get tiny clipped values; (4) don't call `loss.backward()` outside autocast on a mixed-precision model; (5) don't recompute the warmup target after each `zero_grad`.

Explain *why* GradScaler exists: fp16 has a tiny exponent range, so small gradients underflow to zero; scaling the loss up (and gradients back down before the step) preserves them. bf16 has fp32's exponent range, so on A100+/H100 you use bf16 and drop the scaler entirely.

**Follow-ups:** Is accumulation exactly equivalent to a bigger batch? (Almost — BatchNorm statistics differ; LayerNorm models like transformers are fine.) Where does the memory actually go? (Params + grads + Adam states ≈ 16 bytes/param; activations scale with batch — hence gradient checkpointing.) When accumulation isn't enough: gradient checkpointing, LoRA/QLoRA, ZeRO/FSDP sharding — ordered by invasiveness.

</details>

## A6. Retrieval and RAG coding

### Implement cosine-similarity search from scratch

> "Implement cosine similarity, dot product, and Euclidean distance functions from scratch" and "Build a simple vector similarity search from scratch."

**Where asked:** Reported across multiple AI engineering banks; often appears at AI-native startups as a 30–60 min pair-coding exercise for AI Engineer / Forward Deployed Engineer / AI Solutions Engineer roles · [amitshekhariitbhu/ai-engineering-interview-questions (2k+ stars, updated through 2026)](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Numerical stability under large embedding vectors; awareness that pure Python loops will not pass for N>10k; ability to add a top-k ANN shortcut without prompting.

**Time expected:** 30–45 minutes (basic), 90 minutes with the ANN extension.

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

Use NumPy for the dense baseline and torch for GPU. Normalize once — cosine similarity then reduces to a dot product.

```python
import numpy as np

def cosine_search(q, M, k=10):
    q = q / (np.linalg.norm(q) + 1e-12)
    M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
    sims = M @ q
    idx = np.argpartition(-sims, k)[:k]        # O(n), not O(n log n)
    return idx[np.argsort(-sims[idx])]
```

Gotchas: forgetting `eps` in the denominator; using 32-bit float for 1024-d embeddings; recomputing norms inside the inner loop. Strong candidates add a "scale to 1M vectors" hook — block-wise matmul + IVF-PQ or FAISS — and call out the latency ceiling (~10 ms for 1M vectors on CPU). Cosine vs dot product vs Euclidean: un-normalized embeddings encode magnitude (popularity/confidence), so the choice matters.

</details>

### Implement semantic search using embeddings

> "Implement semantic search using embeddings and cosine similarity."

**Where asked:** AI Engineer roles at multiple AI-native startups, especially search-adjacent companies (Perplexity, Cohere, Glean, You.com) and applied ML roles · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Indexing design; understanding of vector vs lexical trade-offs; whether you reach for hybrid retrieval. (This is the from-scratch cosine search above delivered as a *product feature*, not an optimization exercise.)

**Time expected:** 60–90 minutes.

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

Build on the cosine-search primitive, but the differentiating move is calling out that pure semantic search goes off-piste for "exact term" queries (IDs, SKUs, names) and proposing a hybrid score:

```python
score = alpha * bm25(q, d) + (1 - alpha) * cosine(embed(q), embed(d))
```

Learn `alpha` per domain offline. Pre-normalize the corpus at index time; use `argpartition` for top-k; measure recall@k against exact brute force on a sample when you introduce an ANN index.

</details>

### Build a small RAG app (chunking, embedding, retrieval, answer)

> "Implement a basic RAG pipeline using an embedding model and a vector database", "Build a basic document parser that extracts text from PDFs and splits it into chunks", and "Implement a simple re-ranker for search results."

**Where asked:** AI Engineer / Forward Deployed Engineer / AI Solutions Architect roles across AI-native startups; reported as a ~4-hour take-home at multiple AI employers in 2025–2026 (Cursor, OpenAI solutions-style, Anthropic sales-engineering adjacent) · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** End-to-end ownership; understanding of chunk overlap, hybrid BM25+embedding retrieval, rerankers, citations; graceful handling of retrieval failure (out-of-corpus queries).

**Time expected:** 4–6 hours.

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

1. **Loader:** `pypdf` for PDFs, recursive character splitter with overlap 100–200 tokens.
2. **Embedder:** sentence-transformers `all-MiniLM-L6-v2` baseline; swap to OpenAI/Cohere embeddings.
3. **Index:** Qdrant/FAISS.
4. **Retriever:** top-20 hybrid (dense + BM25).
5. **Rerank:** cross-encoder or LLM yes/no rerank.
6. **Generation:** prompt template with citations.
7. **Fallback:** when context is empty, refuse gracefully.

Gotchas: no overlap means lost context across chunk boundaries; ignoring chunk metadata; no max-marginal-relevance so results all say the same thing; no citation trace.

</details>

### Write a chunking strategy module (fixed-size / recursive / semantic)

> "Write code for different text chunking strategies (fixed-size, recursive, semantic)."

**Where asked:** AI Engineer / RAG Engineer roles across vendors 2025–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Awareness that chunking is the largest hidden lever in RAG quality; whether you compare strategies empirically rather than hand-waving.

**Time expected:** 60 minutes.

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

Implement three strategies behind one interface `chunk(text, strategy) -> List[str]`. Strong candidates include overlap, embed-and-sentence-cluster for the semantic path, and a `length_callback` that respects the embedder's max tokens.

Gotchas: ignoring whitespace; a recursive splitter that doesn't respect Markdown headings; a semantic splitter producing chunks > 512 tokens.

</details>

### Implement a simple re-ranker for search results

> "Implement a simple re-ranker for search results."

**Where asked:** AI Engineer / RAG Engineer roles; especially at Perplexity, Glean, Cohere 2025–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Cross-encoder vs LLM rerank vs reciprocal-rank fusion; awareness that reranking is often the single biggest retrieval quality lift.

**Time expected:** 45–60 minutes.

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

Reciprocal Rank Fusion is the simplest baseline:

```python
score(d) = sum(1 / (k + rank_i(d)) for each ranking i)
```

For a cross-encoder, score `(query, doc)` pairs directly. Gotchas: not handling ties; not caching scores; evaluating with recall only — use `nDCG@10` as well.

</details>

## A7. Agents, LLM APIs and production plumbing

### Build a simple AI agent with tool use

> "Build a simple AI agent with tool use (e.g., calculator, web search)" and "Write a function calling (tool use) handler for an LLM API."

**Where asked:** AI Engineer / Agent Engineer / Forward Deployed Engineer roles at Cursor, Anthropic, OpenAI, and LangChain-adjacent startups 2025–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Tool schema design; response parsing; loop termination; rate limits; surfacing errors back to the model.

**Time expected:** 90–120 minutes.

**Difficulty:** Medium-Hard.

<details><summary>💡 Strong solution approach</summary>

Define tools as JSON Schema. The agent loop:

```python
while steps < MAX and not done:
    tool_calls = model.respond(messages)
    for tc in tool_calls:
        messages.append(tool_result(tc, run(tc)))
    done = not tool_calls
```

Gotchas: infinite loops ("never reaches done" — need a max-step cap, a "final answer" sentinel, or a stop token); not surfacing tool errors and letting the model hallucinate; using a string parser instead of structured outputs (OpenAI/Cohere/Anthropic all expose this directly now); context-window blow-up after 10 retries.

</details>

### Build a sliding-window + summary conversation memory

> "Implement a conversation memory system for a chatbot (sliding window, summary, buffer)."

**Where asked:** AI Engineer / Agent Engineer roles; especially agent-platform vendors (Cursor, Replit, Cognition) · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Context-window budget management; the trade-off between fidelity, latency, and cost.

**Time expected:** 60–90 minutes.

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

Three memory classes, all exposing `update(messages) -> List[Message]` and `context() -> List[Message]`. Sliding-window keeps the last `k` turns verbatim; the summary class rolls older turns through an LLM with a fixed token budget; buffer is raw.

Gotchas: the summary hallucinating facts; mixing buffered and summarized messages without preserving ordering; skipping cost estimation.

</details>

### Implement a streaming response handler for an LLM API

> "Implement streaming responses for an LLM API."

**Where asked:** AI-native employer coding screens; especially Cursor (interactive streaming UX) and OpenAI/Anthropic SDK-adjacent roles 2025–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Async generator handling; SSE parsing; partial-JSON chunks.

**Time expected:** 45–60 minutes.

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

```python
async for chunk in sse_client(url):
    data = json.loads(chunk.data)
    yield data["delta"]
```

Use `httpx.AsyncClient` with `timeout=httpx.Timeout(connect=5, read=60)`. Gotchas: buffering all chunks to get "complete JSON" (kills the streaming UX); ignoring backpressure; not handling `data: [DONE]`; partial tool-call JSON parsing.

</details>

### Implement retry with exponential backoff for LLM API calls

> "Implement a retry mechanism with exponential backoff for LLM API calls."

**Where asked:** AI Engineer and SWE new-grad loops at Cohere, Anthropic, Mistral 2024–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Respect for `Retry-After`, jitter, idempotency keys on POST, and distinguishing retriable (5xx, 429) from non-retriable (400, 401) errors.

**Time expected:** 30–45 minutes.

**Difficulty:** Easy-Medium.

<details><summary>💡 Strong solution approach</summary>

```python
for attempt in range(max_attempts):
    try:
        r = post(..., timeout=...)
        break
    except Retryable:
        sleep(jitter * 2 ** attempt)
```

Gotchas: retrying on 401 (the token is dead); using a sleep that doesn't compose with async; missing idempotency keys on POST (causing duplicate "create" calls in tools/agents); reading `Retry-After` as int seconds only (it can also be a date).

</details>

### Build a rate-limited async LLM API client

> "Day 1-2: Pick your language and write five infrastructure utilities from scratch. Rate limiter, LRU cache with TTL, batch aggregator, retry-with-backoff…"

**Where asked:** Cohere — Software Engineer, Day 1–2 technical round; the pattern is shared by Anthropic's "database-style CodeSignal rounds" and SWE-track AI employers generally 2024–2026 · [InterviewCoder: Cohere SWE interview (May 26 2026)](https://www.interviewcoder.co/blog/cohere-software-engineer-interview)

**What it tests:** Token-bucket vs leaky-bucket choice; asyncio ordering; respect for HTTP `Retry-After`; idempotency keys; circuit breaking.

**Time expected:** 60–90 minutes (full polished version).

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

Token bucket per route, in-memory or Redis-backed if multi-instance.

```python
bucket = TokenBucket(rate=10, capacity=20)

async def call(req):
    while not bucket.consume():
        await asyncio.sleep(backoff)
    return await retry_with_expo(req, max_tries=5, respect_retry_after=True)
```

Gotchas: ignoring 429 silently; firing concurrent requests past the limit (a lock must serialize — use an asyncio Lock per key); not handling streaming backpressure; not honoring `Retry-After`; opening unbounded connections; missing idempotency keys on retries (duplicate "create" calls in tools/agents).

</details>

### Implement an async task queue with a concurrency limit

> Implement an async task queue: tasks can be submitted at any time, at most N run concurrently, each submission returns a promise/future of its result. (JS/TS or Python asyncio.)

**Where asked:** Neon — a favorite interview of one of its engineers, published with real candidate/AI transcripts; the pattern is now common across AI-tooling startups precisely because it resists memorization · [David Gomes: One of my favorite programming interviews](https://davidgomes.com/async-queue-interview-ai/) · [OpenAI community: AsyncOpenAI patterns](https://community.openai.com/t/using-asynchronous-client-with-asyncopenai/624114)

**What it tests:** Concurrency reasoning — the exact skill you need to call LLM APIs at scale without blowing rate limits. Ordering guarantees, backpressure, and error propagation are the layers.

**Time expected:** ~45 minutes (easy to start, hard to finish cleanly under follow-ups).

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

Python asyncio version:

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

TypeScript version (no libraries) — the one interviewers probe harder:

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

**Follow-ups:** Add per-task timeout and cancellation; add `drain()`. Bounded queue — what happens when submissions outpace completion? (Backpressure: block, drop, or reject.) Priorities; retries with exponential backoff + jitter. The Neon write-up's angle: interviewers now watch *how you use an AI assistant* on this problem — drive it with tests and invariants, don't paste-and-pray.

</details>

### Implement a rate limiter for an LLM API gateway

> Implement a rate limiter for an LLM API gateway: each user gets X requests/minute and Y tokens/minute. `allow(user, tokens)` returns whether the request may proceed. Then make it work across multiple gateway instances.

**Where asked:** Reported across AI-infra SWE loops (xAI-style infra rounds; a staple wherever the product *is* an API) · [xAI SWE interview process](https://gaijineer.co/xai-software-engineer-interview-process) · [Tyk: rate limiting explained](https://tyk.io/learning-center/api-rate-limiting-explained-from-basics-to-best-practices/) · [Orq: API rate limits best practices](https://orq.ai/blog/api-rate-limit)

**What it tests:** The token-bucket algorithm under the twist that LLM cost is *tokens, not requests* — dual-budget limiting, lazy refill, and the single-node → distributed jump.

**Time expected:** ~45–60 minutes.

**Difficulty:** Medium (single node) → Hard (distributed follow-up).

<details><summary>💡 Strong solution approach</summary>

Token bucket with lazy refill — no background timers, refill computed at check time:

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
        return req.allow(1) and tok.allow(tokens)
        # NB: checking two buckets needs check-then-commit to avoid
        # consuming one when the other rejects
```

Name the LLM-specific wrinkle unprompted: you don't know the *output* token count at admission time — real gateways reserve an estimate (prompt tokens + max_tokens) and reconcile after the response.

**Distributed version:** move bucket state to Redis, one atomic Lua script per check (read state, refill, compare, decrement). Discuss the tradeoff triangle: accuracy (central Redis) vs latency (local buckets with divided quotas) vs cost (sync intervals).

**Follow-ups:** Token bucket vs sliding-window-log vs fixed window — burst behavior at window boundaries. What do you return on rejection? (429 + `Retry-After`.) Fairness: per-user buckets plus a global bucket. Priority tiers (paid vs free) and queueing instead of hard rejection.

</details>

### Implement token counting and context window management

> "Write code to implement token counting and context window management."

**Where asked:** AI Engineer roles at any vendor with multi-tenant LLM serving; common at Mistral, OpenAI applied, Anthropic 2025–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Awareness that budgeting is per-model; truncation strategy; what overflow looks like (mid-token splits).

**Time expected:** 30–45 minutes.

**Difficulty:** Easy-Medium.

<details><summary>💡 Strong solution approach</summary>

Use the model's actual tokenizer (`tiktoken` for the OpenAI family). Truncate from the middle to preserve both the system prompt and the most recent context.

Gotchas: counting characters not tokens; using `len(text.split())`; off-by-one for `BOS`/`EOS` tokens.

</details>

### Build a prompt template system with variable substitution

> "Implement a prompt template system with variable substitution."

**Where asked:** AI Engineer / Prompt Engineer roles; especially at vendors implementing their own SDK layer — a common 2025–2026 pattern · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Templating hygiene (Jinja vs f-strings vs Mustache); chat vs completion messages; multi-message templates with role-tagged blocks.

**Time expected:** 30–45 minutes.

**Difficulty:** Easy-Medium.

<details><summary>💡 Strong solution approach</summary>

Use Jinja2 with a chat-aware delimiters block:

```jinja
{% for m in messages %}<|{{ m.role }}|>{{ m.content }}{% endfor %}
```

Add strict-undefined mode in production and protection against prompt injection. Gotchas: string-formatting user input as code; no escape on `}}`; merging context into the system prompt via `format` and accidentally leaking template internals.

</details>

### Implement an eval pipeline with LLM-as-a-judge

> "Build an evaluation pipeline for LLM outputs using LLM-as-a-judge."

**Where asked:** AI Engineer / ML Eval Engineer roles; especially at OpenAI, Anthropic, Scale AI 2025–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Calibration of the judge prompt; bias mitigation (position bias, verbosity bias); structured-output parsing; cost ceilings.

**Time expected:** 90 minutes.

**Difficulty:** Medium-Hard.

<details><summary>💡 Strong solution approach</summary>

Build a service that takes `(prompt, response, rubric)` → `(score, rationale)`. Strong candidates randomize response order; use chain-of-thought before scoring; align the judge to humans on a calibration set; report inter-rater agreement.

Gotchas: a judge prompt with no rubric; non-blind comparison; a single judge.

</details>

### Detect and handle hallucinations in LLM outputs

> "Write code to detect and handle hallucinations in LLM outputs."

**Where asked:** AI Engineer / Eval roles; especially at Perplexity, Glean, and ChatGPT Enterprise-adjacent teams 2025–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Whether you conceive of "hallucination" as a multi-symptom concept (intrinsic vs extrinsic, factuality vs faithfulness) and can apply check-worthy span detection.

**Time expected:** 60 minutes.

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

Layered approach: (1) self-consistency across samples; (2) RAG-grounding check (does each claim have a citation?); (3) NLI model scoring; (4) a classifier trained on a labeled "factual error" corpus.

Gotchas: a single threshold collapses all failure modes; "asking the LLM if it's hallucinating" is circular; no labeled eval set.

</details>

## A8. Systems, performance and take-homes

### Optimize a Python-simulated TPU kernel to beat 1487 cycles (Anthropic performance take-home)

> "This repo contains a version of Anthropic's original performance take-home, before Claude Opus 4.5 started doing better than humans given only 2 hours." The README adds: "If you optimize below 1487 cycles, beating Claude Opus 4.5's best performance at launch, email us at performance-recruiting@anthropic.com with your code (and ideally a resume) so we can be appropriately impressed and perhaps discuss interviewing." A previous iteration provided starter code that achieved "18532 cycles (7.97x faster than this repo starts you)" and warned "Multicore is disabled intentionally in this version."

**Where asked:** Anthropic — Performance Engineering / any technical role, 2-hour take-home (publicly open-sourced) · [github.com/anthropics/original_performance_takehome](https://github.com/anthropics/original_performance_takehome) · [Hacker News discussion (Jan 2026)](https://news.ycombinator.com/item?id=46700594) · [Anthropic engineering blog: AI-resistant technical evaluations (Jan 21 2026)](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

**What it tests:** VLIW instruction packing, SIMD-style vectorization, dependency analysis, and the ability to write your own debugging tooling inside a custom VM with no visualization. Anthropic describes the evolution from "serial → VLIW + SIMD + multicore" to a "tiny, heavily constrained instruction set" precisely to "resist" frontier models.

**Time expected:** 2 hours (shortened from 4 hours in v2 → v3).

**Difficulty:** Hard (HN comments framed the task as exposing the gap even for senior engineers).

<details><summary>💡 Strong solution approach</summary>

1. Read the simulator README + `Machine.py` and the example kernels in `tests/` before touching code.
2. Write your own cycle-accurate trace visualizer — Anthropic intentionally ships none.
3. Optimize one axis at a time: first dependency analysis to pack independent slots into the same VLIW bundle, then loop unrolling and SIMD-style "load 4 elements per cycle" patterns, finally allocating multicore carefully (when re-enabled).
4. Regression-check via `python tests/submission_tests.py` against fixed thresholds.
5. Never touch `tests/` — Anthropic explicitly invalidates solutions that modify the test folder.

The hardest-signal move: notice the competing metric — instruction count vs wall-clock cycles — and pick the one whose bottleneck is binding, rather than chasing the wrong one.

</details>

### Generate outputs for images and pipelines (Anthropic)

> "This question evaluates algorithmic and systems engineering skills related to batch image processing, parallelization, I/O versus CPU trade-offs, and deterministic output association within the Coding & Algorithms domain."

**Where asked:** Anthropic — Software Engineer, Coding & Algorithms round (live coding or take-home style) · [PracHub (Nov 9 2025)](https://prachub.com/coding-questions/generate-outputs-for-images-and-pipelines)

**What it tests:** Designing a batch job that processes a directory of images through a model pipeline, associates outputs back to inputs deterministically, and parallelizes without breaking I/O ordering. Probes streaming vs batch trade-offs and backpressure.

**Time expected:** 45–60 minutes (live) or 4–6 hours (take-home).

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

Enumerate constraints first: input format (jpg, png, multi-page tiff), model I/O (CPU vs GPU), expected cardinality (100k images), target SLA. Standard skeleton:

1. A globbing iterator that yields `(path, stable_id)` to preserve deterministic ordering even after sort.
2. A thread or process pool sized to `min(cpu_count, model_concurrency)`.
3. A producer-consumer queue decoupling disk I/O from inference.
4. An output writer that flushes per shard to avoid data loss on crash.
5. An optional retry queue keyed by `stable_id`, not path (filenames can collide).

```python
paths = sorted(glob("*.jpg"))
pool = ThreadPoolExecutor(max_workers=GPU_CONCURRENCY)
for path, result in zip(paths, pool.map(run_pipeline, paths)):
    write(stable_id(path), result)
```

Gotchas that separate strong from weak: blocking the event loop on numpy decode; hashing by path when timestamps change; holding the entire batch in memory; not handling intermittent CUDA OOM.

</details>

### LRU cache implementation (OpenAI onsite)

> The "classic LRU Cache implementation question", reported at OpenAI's platform SWE onsite.

**Where asked:** OpenAI — Software Engineer (Platform), onsite coding · [Medium: How I prepared for my OpenAI interview (Nov 11 2025)](https://medium.com/@tomzat/how-i-prepared-for-my-openai-interview-and-what-actually-helped-a185eefbafe6)

**What it tests:** `OrderedDict` vs doubly-linked-list + dict; O(1) get/set/evict; thread safety; serialization.

**Time expected:** 20–30 minutes.

**Difficulty:** Easy-Medium.

<details><summary>💡 Strong solution approach</summary>

`OrderedDict` (move_to_end on access, popitem last on eviction) covers it in 12 lines. For "no library" interviewers: a doubly linked list with `(key, value, prev, next)` nodes plus a hashmap.

Gotchas: forgetting move-to-end on *update*, not just on *get*; off-by-one on capacity (evict when len==cap, not after); thread-safety invariants under concurrent get/put.

</details>

### In-memory file system coding challenge (Perplexity)

> "Perplexity Interview Experience: In-Memory File System Coding Challenge. Verified candidate reports — coding."

**Where asked:** Perplexity AI — Software Engineer, take-home or technical screen; the pattern also matches Anthropic "Coding & Algorithms" prompts that involve "build a small data structure and operations on it" · [1point3acres Perplexity interview bank (2026)](https://www.1point3acres.com/interview/company/perplexity)

**What it tests:** Tree data structure design; command parsing (mkdir, cd, ls, touch, rm, cat); path normalization; error handling for invalid paths.

**Time expected:** 60–90 minutes.

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

Build a `Node(name, is_dir, children, parent)`. Parse commands with `split()`. On every `cd`, traverse parent links and reject upward escapes from the working dir.

```python
root = Node("/", True, {}, None)
cwd = root
for cmd in commands:
    parts = cmd.split()
    if parts[0] == "cd":
        cwd = resolve(cwd, parts[1])
```

Gotchas: not handling `..` from root; case sensitivity (decide the policy upfront); paths containing spaces; not clamping recursion depth on deeply nested mkdir.

</details>

### Cohere infrastructure utilities (5-in-1 take-home)

> "Day 1-2: Pick your language and write five infrastructure utilities from scratch. Rate limiter, LRU cache with TTL, batch aggregator, retry-with-backoff…"

**Where asked:** Cohere — Software Engineer, Day 1–2 of a 4–6 week loop ("recruiter screen, two technical rounds in production-quality Python") · [InterviewCoder: Cohere SWE interview (May 26 2026)](https://www.interviewcoder.co/blog/cohere-software-engineer-interview)

**What it tests:** Production hygiene: TLS retries, jittered backoff, monotonic clocks, idempotency, instrumentation hooks.

**Time expected:** 4–6 hours for the full set.

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

Deliver each utility with a small unit test suite and a single shared `now()` abstraction so retries are deterministic. Use `asyncio` for the rate limiter; `functools.lru_cache` is acceptable but you lose credit for TTL unless you wrap it.

Gotchas: timeouts that don't compose; mixing `time.sleep` and `asyncio.sleep`; `except Exception` swallowing retryable errors silently; not surfacing metrics.

</details>

### Cursor 8-hour paid take-home build session

> Cursor candidate report: "They basically gave me access to part of their codebase and were like, 'Figure it out, see anything you want to build, and just build it.' For eight hours I worked out of a Sl…" Cursor's loop: "four stages: a 30-minute recruiter screen, two 60-minute technical phone screens, and an 8-hour paid [onsite build]."

**Where asked:** Cursor (Anysphere) — Software Engineer L3 / new grad, final onsite · [Exponent candidate report (May 8 2026)](https://www.tryexponent.com/experiences/cursor-software-engineer-interview-a9c32f) · [InterviewCoder: Cursor SWE interview (May 30 2026)](https://www.interviewcoder.co/blog/cursor-software-engineer-interview)

**What it tests:** Speed of orientation in a real codebase, scoping skills, push-vs-pull instincts, shipping a small feature end-to-end in hours.

**Time expected:** 8 hours (paid).

**Difficulty:** Medium (the signals are scoping + shipping).

<details><summary>💡 Strong solution approach</summary>

Spend the first 30 minutes reading `README`, `CONTRIBUTING`, top-of-stack entry points, and recent PR titles. Pick a small, contained, user-visible win that exercises a real subsystem (a new keyboard shortcut, a code-action, a tree-sitter query update). Write tests if a test runner exists; otherwise write a script that demonstrates the feature.

Gotchas: getting stuck on a sprawling subsystem; over-engineering; shipping without a clear demo path.

</details>

### Mistral 60-minute live coding (algorithm + practical AI utility)

> "Coding & Algorithms: A 60-minute live coding session" within a 6-round loop — ML-flavored algorithmic coding plus practical AI utilities (tokenizer, streaming HTTP client, eval harness glue).

**Where asked:** Mistral AI — Engineer loop · [DataInterview: Mistral AI Engineer guide (Mar 16 2026)](https://www.datainterview.com/blog/mistral-ai-engineer-interview)

**What it tests:** Production Python; time-pressure problem decomposition; edge-case handling.

**Time expected:** 60 minutes.

**Difficulty:** Medium.

<details><summary>💡 Strong solution approach</summary>

Open with constraints and an example. State what the test suite will exercise. Use type hints; keep corner cases on a separate list; do not introduce third-party libs unless approved.

Gotchas: edge cases (empty input, Unicode, overflow); missing docstring on the public surface; relying on global state in async code.

</details>

### Coding exercises reported by multiple employers (cross-reference)

| Exercise | Companies confirmed | Difficulty | Typical time |
| --- | --- | --- | --- |
| Multi-head attention from scratch | Apple, Google (Voker), OpenAI, Anthropic tracks | Hard | 45–60 min |
| Transformer debug + train classifier | OpenAI (PracHub) | Hard | 75–90 min |
| BPE tokenization from scratch | OpenAI, Anthropic (Raschka reference) | Medium-Hard | 60–90 min |
| K-means from scratch | OpenAI, Anthropic, AI startups | Easy-Medium | 30–45 min |
| Logistic regression from scratch | OpenAI, AI startups | Easy-Medium | 30–45 min |
| Top-p sampling / beam search | Mistral, Cohere, AI startups | Medium | 45–60 min |
| Rate-limited async LLM client | Cohere, Anthropic, OpenAI | Medium | 60–90 min |
| LRU cache implementation | OpenAI (Nov 2025) | Easy-Medium | 20–30 min |
| Backprop for a tiny network | OpenAI (PracHub), Anthropic | Hard | 60–90 min |
| RAG app build (chunk + embed + retrieve) | Cursor, OpenAI, Anthropic solutions | Medium | 4–6 hours |
| Agent with tool use | Cursor, Anthropic, AI startups | Medium-Hard | 90–120 min |
| Performance kernel take-home | Anthropic | Hard | 2 hours (paid) |
| LLM inference debug in Colab | Anthropic AI Safety Fellow | Hard | 55 min |
| In-memory file system | Perplexity, Anthropic | Medium | 60–90 min |
| Streaming response handler | OpenAI, Anthropic, Cursor | Medium | 45–60 min |
| Retry with exponential backoff | Anthropic, Cohere, Mistral | Easy-Medium | 30–45 min |

---

## Section B — ML/LLM system design

In 2026, system-design prompts at AI employers orbit a small number of archetypes: ChatGPT-style serving, RAG with eval, evaluation platforms, inference platforms, agent platforms, and content/fraud moderation. The strongest candidates identify the archetype in the first 3 minutes, lock in the scaling assumptions, then drive the remaining time on the one or two subsystems where depth matters most to that specific company.

## B1. LLM serving and inference

### Design ChatGPT to handle 100 million users

> "How would you design ChatGPT to handle 100 million users?" — paired with "system reliability and fault tolerance" and "how to scale machine learning workloads."

**Where asked:** OpenAI — Software Engineer (Platform), onsite system design; the same prompt family has been reported at multiple AI employers for both platform SWE and ML serving roles · [Medium: How I prepared for my OpenAI interview (Nov 11 2025)](https://medium.com/@tomzat/how-i-prepared-for-my-openai-interview-and-what-actually-helped-a185eefbafe6) · [IGotAnOffer: OpenAI system design interviews](https://igotanoffer.com/en/advice/openai-system-design-interview)

**What it tests:** Whether you understand what makes LLM serving unlike normal web serving: requests are long-lived, GPU-bound, streamed, and wildly variable in cost. The TTFT-vs-throughput tension is the heart of the round.

**Time expected:** 45–55 minutes.

**Difficulty:** Hard (Senior / Staff SWE / MLE).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** 100M DAU, prompt + 50-turn chat history, median first-token latency <500ms, p99 <2s, a token-throughput target, and a target cost per 1M tokens.

**Architecture:** clients → CDN + edge WAF → API gateway (auth, rate-limit, abuse) → request router → inference fleet of H100/A100 pods with continuous batching (vLLM-style), paged KV cache, and prefix sharing for system prompts.

**State:** stateless inference pods; persistent Redis session store (chat turn IDs) and Postgres for user/org metadata; object store for attachments; vector store for retrieval-augmented memory if applicable.

**Data flow:** gateway → LLM-serving fleet with a load balancer using "least loaded by KV occupancy", *not* "least loaded by request count"; stream SSE back.

**Evaluation:** weekly load test at 5× median; shadow new model routes on 1% traffic; canary on cost/latency deltas; rolling deploy with auto-rollback at +5% p99 regression.

**Monitoring:** golden-signal dashboards (latency, traffic, errors, saturation) plus AI-specific metrics — TTFT, ITL, GPU SM occupancy, KV-cache hit ratio, drift in token throughput.

**Cost/latency:** prefix caching moves ~30% of repeat prompts onto cheap shared prefixes; speculative decoding cuts p50 for short prompts.

**Depth signals interviewers probe for:** continuous batching and paged KV; KV occupancy as the load-balance signal; tenant-aware fairness when one customer saturates the fleet.

**Follow-up probes:** How do you contain a single tenant consuming >5% of GPU-hours? Model-weight rollout — blue/green vs in-place re-shard? How do you detect a silent regression in *quality*, not just latency? How do you handle a 10× burst from a launch event?

</details>

### Design an LLM inference platform (vLLM-as-a-Service)

> "Design an LLM Inference Platform (vLLM-as-a-Service)."

**Where asked:** AI Platform Engineer / Inference Engineer roles; reported at Anthropic, OpenAI, Together, Anyscale, Modal 2024–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions) · [PracHub: Together AI SWE questions](https://prachub.com/companies/together-ai/positions/software-engineer)

**What it tests:** One level deeper than "design ChatGPT" — memory management, batching math, quantization tradeoffs, speculative decoding, and multi-tenancy scheduling. The round that separates users of vLLM from people who could build it.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Staff/Senior MLE).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** serve 100B+ models at <500ms TTFT, 80+ tok/s/user, with multi-tenant isolation and cost controls.

**Architecture:** model registry (S3/GCS); bootstrap pod pulls weights into NVMe; vLLM serving with continuous batching + paged KV + chunked prefill; multi-LoRA hot-swap; prefix cache; speculative decoding; HTTP/SSE gateway.

**Placement:** bin-packing on GPU SKUs (H100, A100, L40S) with a scheduler that treats KV occupancy as the load signal. Admission control based on projected KV memory (prompt length + max output); preemption policy under memory pressure (swap-to-CPU vs recompute — recompute usually wins).

**Eval:** golden prompts replayed nightly; quality parity vs upstream; a regression suite gates deploys.

**Monitoring:** TTFT, ITL, GPU SM occupancy, KV-cache hit ratio, queue depth, request admission rate — and cost per million tokens as the north-star metric.

**Cost:** spot when tolerable; the autoscaler scales on token throughput, not request count (target tokens/s-per-GPU).

**Depth signals:** continuous vs static batching math; prefix-cache amortization; speculative decoding heads; "why vLLM over TGI / TensorRT-LLM" — pick one and explain the trade.

**Follow-up probes:** How do you hot-swap a model without dropping traffic? How do you ensure fairness across tenants? How do you autoscale on bursty traffic without cold-start penalties? Prefill/decode disaggregation — why serve them on separate GPU pools?

</details>

### Design an on-device AI assistant

> "Design an On-Device AI Assistant."

**Where asked:** Apple, Google (Pixel/Gemini Nano), Qualcomm AI Hub; AI-native startups building on-device features; also reported at Microsoft (Copilot+ PC) and Samsung Galaxy AI 2024–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Small-model serving under hardware constraints; quantization quality trade-offs; escalation policy design.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** <50ms first token; <2GB memory; works offline; secure against model extraction.

**Architecture:** small SLM (3–8B) quantized int4/int8; ONNX Runtime / Core ML / TFLite; tool-call policy constrained to device-only actions; local vector store of user content; sync with cloud for escalation.

**Eval:** per-task quality vs the cloud baseline; latency; battery cost; cold-start.

**Depth signals:** token streaming cadence design; quantization's effect on quality for dialog tasks; a tier-based escalation policy.

**Follow-up probes:** How do you decide what stays on device vs escalates? How do you update the model?

</details>

## B2. RAG, search and retrieval

### Design a RAG system with evaluation

> "You are asked to design a Retrieval-Augmented Generation (RAG) system that answers user questions using a private corpus (e.g., internal docs…)" — PracHub: "This question evaluates expertise in designing RAG systems, covering end-to-end architecture, document ingestion and preprocessing, embedding and indexing strategies, retrieval and reranking, prompt/context assembly, safety/fallbacks, and per-component evaluation."

**Where asked:** OpenAI — ML System Design; the same prompt family is reported at Anthropic, Glean, Perplexity, Cohere, Cursor 2024–2026 · [PracHub (Jun 24 2026)](https://prachub.com/interview-questions/design-a-rag-system-with-evaluation) · [r/MLQuestions: MLSD interview focused on AI engineering](https://www.reddit.com/r/MLQuestions/comments/1mjtd4j/ml_system_design_interview_focused_on_ai/)

**What it tests:** The full 2026 AI-engineer skillset in one question: chunking strategy, hybrid retrieval, reranking, grounding/citations, per-component evals, freshness, and access control.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** 1M docs; private corpus (PII/redaction concerns); sub-3s p95 latency; refusal when context is empty is acceptable.

**Architecture:** ingestion (loader → parser → chunker — recursive/structural → embedder → vector index) + serving (query embed → hybrid retriever top-50 → reranker top-5 → prompt assembler → LLM → streamed answer with citations).

**Data:** chunk overlap 100–200 tokens; preserve section/heading metadata; embed with a domain-tuned model or fine-tune on contrastive pairs from the corpus.

**Index:** Qdrant/FAISS/pgvector + BM25 with reciprocal-rank fusion; rerank via cross-encoder or LLM yes/no. Apply ACL filters *at query time* in the index, never post-LLM.

**Eval:** offline — nDCG@10 against human-labeled Q-A pairs, retrieval recall@k, generation groundedness via NLI or LLM judge, answer-F1 against labeled spans; online — thumbs, follow-up rate. Measure retrieval and generation *separately*: they need different fixes, and conflating them is the classic junior mistake.

**Monitoring:** retrieval recall over time, drift in chunk-length distribution, judge-vs-human agreement, latency p50/p95 by component.

**Cost/latency:** prefix caching across system prompts; reranker only on the head, not the tail; dynamic embedding batches; on empty context — refuse rather than hallucinate.

**Depth signals:** reranking lifts nDCG by 5–15 points and is the "second-best lever" after chunking; refusal + citations are the safety cornerstone.

**Follow-up probes:** How do you keep the index fresh when docs change hourly? What happens when the embedder is replaced? Multi-tenant isolation? How do you evaluate *groundedness* reliably?

</details>

### Design a semantic search system at scale

> "Design semantic search for [a domain]: blends vector + lexical, low-latency under a billion docs."

**Where asked:** AI Engineer / Search Engineer / Applied ML roles — reported at OpenAI, Anthropic, Glean, Perplexity, Elastic, Pinecone 2024–2026 · [ByteByteGo: Visual Search System](https://bytebytego.com/courses/machine-learning-system-design-interview/visual-search-system) · [HelloInterview: Vector databases deep dive](https://www.hellointerview.com/learn/system-design/deep-dives/vector-databases)

**What it tests:** Embedding-model training (two-tower/contrastive), ANN index internals (HNSW vs IVF-PQ — how they work, not just their names), the freshness problem, and metadata filtering.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior / Staff).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** 1B docs, 100k+ QPS, p95 <100ms, recall@10 >0.9 on labeled queries.

**Architecture:** ingest (chunk → embed → vector store + BM25 inverted index) → hybrid retriever (weighted sum or reciprocal-rank fusion) → optional reranker → client.

**Index internals — know them:** HNSW (multi-layer navigable small-world graph; log-ish search, high recall, memory-hungry, awkward to shard) vs IVF-PQ (k-means coarse quantizer + product quantization compressing ~32×; less memory, tunable recall/latency, easier to shard). At 100M+ vectors: shard by IVF cell or random partition; fan out, gather, merge.

**Freshness:** ANN indexes hate in-place updates — run a small "fresh" brute-force/HNSW buffer for recent items alongside the big immutable index, merge results, rebuild on a schedule.

**Eval:** nDCG@10 against human-labeled queries; offline recall@k vs latency curve; recall@k vs exact brute force on a sample.

**Monitoring:** index health (orphan vectors, stale fields), recall trend by query class, drift in embedding distribution (cosine to an anchor set).

**Cost/latency:** quantize embeddings (int8) for memory; cache popular queries; offload reranking to a smaller model.

**Follow-up probes:** How do you re-index without downtime? (Dual-index blue/green, backfill, evaluate before cutover.) Multi-lingual? What happens when the embedder changes? Why not brute force on GPUs? (Legit to ~10M vectors — saying so shows judgment.)

</details>

### Design a multimodal search system (text + image + video)

> "Design a Multimodal Search System (Text, Image, Video)."

**Where asked:** Pinterest, Google, Meta, Adobe, Shutterstock, Runway, ElevenLabs 2025–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Cross-modal embedding spaces, contrastive training, fusion weighting, and identity resolution across modalities.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** text or image or audio query, mixed-modality results; p95 <500ms; 100M+ items.

**Architecture:** per-modality encoders (CLIP for image/text, CLAP for audio, video-frame + CLIP pooling for video) → unified embedding space → ANN over a multimodal index; a cross-modal query encoder maps any input into that space.

**Data:** pairwise contrastive training; modality-specific fine-tuning.

**Eval:** per-modality and cross-modal recall@k; human A/B on relevance.

**Depth signals:** handling the "same item, different modalities" identity problem; how to weight modalities during fusion.

**Follow-up probes:** How do you handle an item that has 10+ image variants?

</details>

### Design an AI search engine for an e-commerce platform

> "Design an AI-powered search engine for an e-commerce platform."

**Where asked:** Amazon, Shopify, eBay, Etsy, Instacart, Wayfair 2024–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Blending lexical, semantic, and personalized signals under a latency budget; multi-locale; cold-start for new sellers.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE).

<details><summary>💡 Strong solution approach</summary>

**Architecture:** query understanding (spell + intent + filters) → candidate generation (BM25 + ANN) → reranker (cross-encoder or DCN) → personalization layer (user history).

**Eval:** nDCG@10 + purchase rate.

**Depth signals:** the recall point where personalization wins is where you "spend" the latency budget; a cold-start path; A/B calibration across catalog velocity.

**Follow-up probes:** How do you A/B test without losing new-seller visibility?

</details>

### Design an AI tutoring platform with RAG-based Q&A

> Design an AI tutoring platform where students ask questions and get answers grounded in course materials — with follow-up conversations, per-student progress, and safeguards against just giving away homework answers.

**Where asked:** Reported on HelloInterview's community board as an asked-in-interview ML system design question · [HelloInterview: AI tutoring platform with RAG-based Q&A](https://www.hellointerview.com/community/questions/ai-tutoring-platform/cm75445ag00053b64gz80nijf)

**What it tests:** RAG plus *product* thinking: conversation state, pedagogy-driven prompting (Socratic mode vs answer mode), safety for minors, and per-course corpus isolation — a RAG question where the guardrails are the point.

**Time expected:** 45–60 min design round.

**Difficulty:** Medium-Hard.

<details><summary>💡 Strong solution approach</summary>

Requirements first: which subjects (math needs different handling than history — rendering, symbolic checking)? Age group (drives safety posture)? Scale? Should it *teach* or *answer*? That last one shapes the whole design.

**Core architecture:** per-course ingestion of syllabi/textbooks/lecture notes into a vector index namespaced by course; a conversation service holding dialogue state and a rolling summary (token budgets kill naive full-history approaches); a RAG pipeline scoped to the student's enrolled courses.

**The differentiating layers:**
- **Pedagogy policy:** a tutoring mode where the system prompt forbids final answers to graded-looking problems and instead elicits steps (detect "homework-shaped" queries with a classifier; escalate hints gradually).
- **Student model:** track per-topic mastery from interaction history; adapt explanation depth and recommend review.
- **Safety:** age-appropriate content filters on both input and output, an escalation path for self-harm signals, and no PII retention in logs used for training.

**Evaluation:** grounded accuracy on a per-course golden set, plus learning-outcome proxies (did the student answer the follow-up check correctly?) — not just answer quality.

**Follow-up probes:** Math problems where retrieval is useless? (Route to a solver/code-execution tool.) How do you stop it doing the student's exam? (Detection + policy — acknowledge it's an arms race.) Latency for a conversational feel? (Stream tokens; pre-fetch retrieval; <1s to first token.) Cold start for a brand-new course with thin materials.

</details>

## B3. Training, fine-tuning and alignment

### Design a distributed training pipeline for an LLM with fault tolerance

> "Design a distributed training pipeline for a large language model. How would you handle fault tolerance?"

**Where asked:** Anthropic — ML / Infra Engineer; confirmed as a 2026 Anthropic MLE question by multiple guides · [Jobright: Anthropic technical interview guide (Dec 18 2025)](https://jobright.ai/blog/anthropic-technical-interview-questions-complete-guide-2026/) · [System Design Handbook: Anthropic guide](https://www.systemdesignhandbook.com/guides/anthropic-system-design-interview/) · [Exponent: Anthropic system design (Mar 2026)](https://www.tryexponent.com/blog/anthropic-system-design-interview)

**What it tests:** 3D parallelism, checkpoint/restart economics, data-pipeline determinism, and whether you can reason about failure as the *normal* case at cluster scale.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE / Infra Engineer; Exponent rates Anthropic system design 4.5/5 difficulty).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** train a 70B–700B model on a multi-trillion-token corpus across N nodes × M GPUs (e.g., N=128, M=8 H100); MFU >50%.

**Architecture:** 3D parallelism (TP=8 within node, PP across nodes, DP across replicas); ZeRO-3/FSDP for optimizer-state sharding; activation recomputation or selective offload; gradient-accumulation microbatching.

**Data pipeline:** parquet shards, webdataset-style shuffle, deterministic sampler with epoch seeding, dataloader prefetch; nearline deduplication with MinHash/SimHash; quality filtering via heuristics + a small classifier.

**Fault tolerance:** spot-instance preemption handling; periodic checkpoint every k steps to S3 with parity; resume via FSDP `load_state_dict` and step-state restore; an elastic agent that drains a failed node, re-buckets the data, and rejoins.

**Eval:** held-out validation perplexity + capability-specific evals (MMLU, HumanEval); periodic regression suites gated on PRs.

**Monitoring:** loss curves per shard, gradient norms, NCCL all-reduce latency, GPU memory headroom, step-time variance.

**Cost:** spot at ~70% of on-demand; checkpoint frequency tuned against cost-of-restart; preemption rate is a primary SLO.

**Depth signals:** how do you re-bucket mid-training? How do you recover optimizer state? Where do you put telemetry when the trainer is the bottleneck?

**Follow-up probes:** How do you handle a NaN gradient? What if a node's NCCL hangs? How do you keep eval from blocking training on a shared cluster? How do you checkpoint without stalling?

</details>

### Design a fine-tuning platform (instruction / PEFT / RLHF)

> "Design a fine-tuning platform for a large language model." Variant: "How would you design an end-to-end fine-tuning system for [domain] with quality evaluation?"

**Where asked:** OpenAI (Principal PM, Fine-Tuning), Anthropic MLE, Mistral MLE; AI startups building PEFT/LoRA products 2024–2026. The Exponent PM report captured the theme: "we have this magical technology, help us figure out what to do with it." · [Exponent: OpenAI Principal PM Fine-Tuning experience (May 12 2026)](https://www.tryexponent.com/experiences/openai-principal-product-manager-interview-b44ff6)

**What it tests:** Multi-tenant training infrastructure; data-quality discipline; eval-gated rollout; safety guardrails on customer fine-tunes.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE / PM-T).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** thousands of customers fine-tuning; mid-training safety; per-tenant isolation; a cost target per training run.

**Architecture:** dataset ingress (curate, PII-strip, license-flag) → LoRA/full-finetune trainer on shared or dedicated GPUs (QLoRA reduces memory ~4× for 70B) → eval pipeline (capability regression + targeted metric) → model registry + serving (multi-LoRA hot-swap or per-tenant).

**Data:** a rubric for "good" data; few-shot priming; toxicity screening.

**Eval:** canary tasks to detect catastrophic forgetting; A/B on production traffic for new variants.

**Monitoring:** loss curves, eval deltas, GPU memory per shard, throughput in tok/s.

**Cost/latency:** spot for training; LoRA merge so serving is cheap; never re-train from base.

**Depth signals:** data quality is the dominant lever; "the hardest part is not training — it is producing high-quality eval golden sets"; versioning per (model, dataset, recipe, eval).

**Follow-up probes:** How do you prevent a customer from breaking the model on safety? How do you scale to 10K concurrent training jobs?

</details>

### Design an RLHF pipeline

> Design the post-training pipeline that aligns a base LLM with human preferences: SFT, reward modeling, and RL fine-tuning — data collection, infrastructure, and how you know it worked.

**Where asked:** Reported in research-engineering loops at frontier labs (post-training design questions feature in lab interview write-ups; the HF/AWS explainers are the canonical prep material) · [Yuan Meng: MLE Interview 2.0 — research engineering rounds](https://www.yuan-meng.com/posts/mle_interviews_2.0/) · [HuggingFace: Illustrating RLHF](https://huggingface.co/blog/rlhf) · [AWS: What is RLHF](https://aws.amazon.com/what-is/reinforcement-learning-from-human-feedback/)

**What it tests:** Whether you understand alignment as a *system*: three coupled training stages, a human-data operation, reward hacking as the central failure mode, and the DPO-vs-PPO decision every lab has actually faced.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (research-engineering round).

<details><summary>💡 Strong solution approach</summary>

Present the three-stage pipeline, then go deep where the interviewer steers.

**Stage 1 — SFT:** curate high-quality demonstrations (human-written + filtered synthetic); train the base model to follow instructions. Quality >> quantity; the data mixture is a first-class design decision.

**Stage 2 — Reward model:** collect *pairwise preferences* (annotators pick the better of two responses — far more reliable than absolute scores); train an RM (usually the SFT model + scalar head) on Bradley-Terry loss. The data operation is the hard part: rater guidelines, inter-annotator agreement tracking, disagreement adjudication, rater-pool diversity — say this; labs grade for it.

**Stage 3 — RL:** PPO against the RM with a **KL penalty to the SFT policy** — the KL term is what stops the policy from wandering into RM-exploiting gibberish. Infra reality: four models in memory (policy, reference, RM, value) — this is why RLHF infra is expensive and why the alternative exists.

**DPO vs PPO — the expected discussion:** DPO optimizes preferences directly with a classification-style loss (no rollouts, dramatically simpler infra, more stable); PPO enables online exploration and iterated data collection and still edges it for frontier quality. Reasonable answer: DPO first for iteration speed, PPO/online methods when you have the infra and need the last few points.

**The central failure mode — reward hacking:** the policy exploits RM blind spots (length bias → verbosity, sycophancy, confident hedging). Mitigations: KL constraint, RM ensembles, iterated RM retraining on fresh policy samples, and *held-out human eval as the final arbiter* — never trust RM score alone; it's Goodhart's law in production.

**Evaluation:** win-rate vs the SFT baseline (human + LLM judge), capability regression suites (alignment-tax check), safety red-teaming.

**Follow-up probes:** RM score goes up, human eval goes down — diagnose. (Reward hacking; inspect high-RM samples, retrain the RM on adversarial pairs.) Where do RLAIF / constitutional approaches slot in? Online (PPO/GRPO) vs offline (DPO) preference optimization — sample efficiency and distribution-shift tradeoffs. How does this differ for reasoning models? (Verifiable rewards — unit tests, math checkers — replace learned RMs where outputs are checkable; RLVR.)

</details>

## B4. Evaluation and safe deployment

### Design an LLM evaluation platform

> "Design an LLM Evaluation Platform." Live variant: "Your team ships an LLM product and changes prompts/models weekly. Design the evaluation system that decides whether a change is safe to ship — offline and online."

**Where asked:** Eval Engineer / MLE roles; especially at Scale AI, OpenAI Evals, Anthropic, Hugging Face, Artificial Analysis 2025–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions) · [AWS samples: automated LLM evaluation pipeline](https://github.com/aws-samples/build-an-automated-large-language-model-evaluation-pipeline-on-aws/blob/main/README.md)

**What it tests:** The judgment layer of AI engineering: golden sets, LLM-as-judge and its failure modes, CI-style regression gates, and connecting offline metrics to online outcomes.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE / Eval Engineer).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** support multi-model A/B, multi-judge (human + LM + heuristic), 10K-prompt test suites at <10% of model-serving cost, reproducibility under model change.

**Architecture:** dataset registry (huggingface-hub style), task runner (Ray/K8s), judge service returning `(score, rationale)`, results store (ClickHouse), dashboards (nDCG, accuracy, calibration, drift).

**Judges, in order of trust:** exact/programmatic checks where possible (format, citations present, code runs) → model-based rubric grading with chain-of-thought → periodic human audit of judge agreement. LLM-as-judge hygiene: pairwise beats absolute scores; randomize position (position bias is real); use a judge model different from the generator (self-preference bias); calibrate against human labels and report judge-human agreement, not just judge scores.

**CI gate:** every prompt/model change runs the suite; block on regression beyond a threshold with statistical significance (bootstrap CIs — 3 points on 200 cases can be noise); track per-slice results so an aggregate win can't hide a slice regression. Example ship rule: "release iff judge score does not regress by >0.5% AND human spot-check matches 95%."

**Monitoring:** per-prompt drift, per-task score drift, calibration drift.

**Cost:** batch judge calls; cache by `(prompt_hash, model_id)`; tier "release gate" (fast) vs "audit" (slow) suites.

**Follow-up probes:** How do you avoid the judge being gamed by the model it scores? How do you detect data leakage between training and eval? How do you handle multi-criteria trade-offs (latency vs quality)? Evals for agents/multi-turn? (Trajectory-level: task success, tool-call correctness, steps-to-completion.)

</details>

### Design a system for safe deployment of AI models in production

> "How would you approach designing a system to ensure the safe deployment of AI models in production?"

**Where asked:** Anthropic — Machine Learning Engineer (reported Nov 24 2024); the same theme appears at OpenAI and Google DeepMind 2024–2026 · [AMA Interview: MLE at Anthropic](https://www.amainterview.ai/interview-questions/machine-learning-engineer-at-anthropic)

**What it tests:** Whether you can operationalize "safety" — pre-deploy evaluation, staged rollout, incident taxonomy, and launch gating — rather than hand-wave about alignment.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** pre-deploy evaluation (capabilities + red-team); a rollout policy (shadow → 1% → 10% → 100%); monitoring of safety incidents by severity (P0 jailbreak, P1 hallucination, …); abuse and policy enforcement.

**Architecture:** pre-prod eval harness → deploy gate (must-pass criteria per incident category) → production canary with synthetic adversarial probes → incident-response runbook.

**Evals:** red-team coverage by capability class; calibration of automated red-teaming against human experts.

**Monitoring:** production drift detectors on classifier outputs; a jailbreak-rate proxy metric.

**Depth signals:** distinguishing a *safety regression* from a *quality regression*; tying safety to launch gating.

**Follow-up probes:** How do you define "safe" in your reward model vs your policy? How do you test for emergent capabilities?

</details>

### Design a content moderation system using AI

> "Design a content moderation system using AI."

**Where asked:** OpenAI policy, Anthropic policy, Reddit, Discord, Meta, Roblox, Character.AI, Replika 2024–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Multi-modal classification at scale; the false-positive vs false-negative policy tension; human-review escalation design.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE / ML Platform).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** classify text/image/video at <500ms with high recall on policy violations (P0/P1) and a low false-positive rate to avoid user harm.

**Architecture:** ingest → multi-modal classifier (toxicity, NSFW, CSAM, PII, hate) → escalation queue for human reviewers → enforcement layer (warn, restrict, suspend).

**Data/models:** classifier trained on policy-tagged data; rule-based + ML ensemble; banned-entity regex; embedding similarity to known-violation clusters.

**Eval:** per-policy F1, latency p95, appeals overturn rate.

**Monitoring:** drift per category (jailbreaks, slang); appeal rate as a calibration signal.

**Cost/latency:** GPU-light classifiers (distilled BERT) for the first pass; route to larger models only when confidence is low.

**Depth signals:** addressing the "false-positive harms users, false-negative harms platform" tension; jurisdictional policy differences; moderator-tool UX as a quality-loop input.

**Follow-up probes:** How do you keep up with new slang or jailbreaks? What happens when a borderline case gets promoted to human review? How do you handle appeals?

</details>

## B5. Agents and AI products

### Design a Deep Research agent

> "Design a Deep Research Agent." (Reference implementations: OpenAI Deep Research, Anthropic Research, Perplexity Deep Research — the question has been reported at all three.)

**Where asked:** AI Engineer / Agent Engineer / Forward Deployed roles at OpenAI, Anthropic, Perplexity, Cognition, Sierra, Decagon 2025–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions) · [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)

**What it tests:** Planner/executor decomposition, tool reliability, citation verification, loop guardrails, and cost ceilings.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** 5–30 minute multi-step research tasks; high citation accuracy; graceful tooling failures.

**Architecture:** planner (decompose query) → executor (browser + search + code + file I/O tools with retries + citations) → critic (verify claims) → synthesizer (final report with tracked sources).

**Data:** shared scratchpad; explicit "what do I know vs need" state; a persistent plan.

**Tools:** web search with cheap browsers, code-interpreter shell, fetch+parse, vector search.

**Evals:** rubric on "is this claim sourced and accurate"; LLM judge with human calibration; a cost ceiling per task.

**Monitoring:** tool-call counts, retries, "stuck" detection (loop guardrails).

**Cost/latency:** parallelize independent sub-plan branches; cap agentic loops.

**Depth signals:** distinguishing planner vs executor; "every research step is a write-then-verify cycle"; the trend toward a *critic* agent vs a single-writer pattern.

**Follow-up probes:** How do you prevent infinite loops? How do you choose when to trust a source?

</details>

### Design a multi-agent customer support system

> "Design a Multi-Agent Customer Support System."

**Where asked:** Sierra, Decagon, Ada, Intercom, Salesforce Einstein, Atlassian, Moveworks 2025–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Orchestration and handoff between specialized agents; bounding hallucination via tools; escalation design.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE / Senior PM).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** resolve 70%+ of tickets without a human; escalate the rest cleanly; bound hallucination via tools.

**Architecture:** triage agent → researcher (RAG over the knowledge base) → action agent (refund API, ticket update, email send) → human handoff. The orchestrator hands off via structured state; each agent has its own tools and prompt.

**Evals:** resolution rate, escalation rate, CSAT, hallucination rate.

**Monitoring:** per-agent tool-call counts; the deflection funnel.

**Cost/latency:** short agent chains for simple tickets; escalate when confidence is low.

**Depth signals:** "an agent that performs a side-effect must require explicit human confirmation above a threshold."

**Follow-up probes:** How do you prevent agents from taking irreversible actions without confirmation?

</details>

### Design an AI coding agent (Cursor / Copilot / Claude Code style)

> "Design an AI Coding Agent."

**Where asked:** Cursor, Anthropic, Cognition, Replit, GitHub Copilot team 2024–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions) · Closely related to Anthropic's published engineering write-up: [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)

**What it tests:** Tool-use loop design, repository-scale context assembly, sandboxing, and permission models.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** multi-turn chat in an IDE; tool use (read_file, edit_file, run_cmd, search); repository-scale context (10K+ files); <2s first-token latency.

**Architecture:** frontier chat model; tool-use loop; context assembler (file pickers + embeddings + repo summary); local sandbox for code execution; permission model (allow / ask / deny) per tool.

**Context:** ranked file snippets plus symbol resolution from tree-sitter/AST.

**Eval:** SWE-bench-style multi-file PR quality; code-review-grade quality on internal goldens; "does this match the user's intent."

**Cost/latency:** stream tokens; lazy repo map; cache embeddings; sub-agents for parallel reads.

**Depth signals:** how you keep the agent from making large undos; how you implement the sandbox; how rights-scoped tools work in a corporate IDE.

**Follow-up probes:** How do you prevent the agent from introducing a security bug? How do you handle long-running commands?

</details>

### Design memory for a personal AI assistant

> "Design Memory for a Personal AI Assistant."

**Where asked:** OpenAI (Memory feature), Replika, Inflection Pi, Rabbit, Rewind AI and others 2024–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Memory schema design (episodic vs semantic vs procedural), privacy and consent, selective recall, bounded growth.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** lifetime memory across sessions; privacy consent; selective recall; bounded growth.

**Architecture:** episodic memory (event stream) + semantic memory (entities and facts) + procedural memory (preferences); retrieval merges them with recency weighting; explicit "remember this" operations.

**Data:** vector store + structured knowledge graph; per-user encryption at rest; opt-in.

**Eval:** longitudinal helpfulness (does the assistant get better over a week?); leakage rate (does it surface private info inappropriately?).

**Depth signals:** a memory schema that survives user deletion; conflict resolution when two memories contradict.

**Follow-up probes:** How do you handle memory-poisoning attacks? How do you let the user edit/delete memory?

</details>

### Design an AI gateway/proxy for org-wide LLM access

> "Design an AI gateway/proxy for managing LLM access across an organization."

**Where asked:** AI Platform / MLOps roles; reported at multiple AI-native B2B startups and internal-platform teams at OpenAI/Anthropic customers 2025–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Central auth/RBAC, budget enforcement, PII redaction, compliance logging, and cost-aware model routing.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE).

<details><summary>💡 Strong solution approach</summary>

**Architecture:** client SDK or proxy → gateway (auth, rate-limit, PII redaction) → router (model selector on cost, latency, capability) → provider adapters (OpenAI, Anthropic, Mistral) → log sink.

**Evals:** latency p95 vs direct calls, cost per request, audit correctness.

**Cost/latency:** prefix caching across users; route cheap prompts to small models; opt-in tags forcing high-stakes prompts to frontier-class models only.

**Depth signals:** prompt-injection defense at the gateway (system-prompt isolation, output scrubbing); per-tenant cost dashboards.

**Follow-up probes:** How do you handle the prompt-injection / data-leakage threat model? How do you keep PII redaction from breaking valid prompts?

</details>

### Design an AI-powered email assistant

> "Design an AI-powered email assistant."

**Where asked:** Google (Smart Compose / Gemini for Workspace), Microsoft (Copilot for Outlook), Superhuman, Grammarly and others 2024–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Privacy partitioning, on-device vs cloud split, OAuth-constrained side effects, and draft-quality evaluation.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** draft, summarize, schedule, prioritize; respects user privacy; works offline for drafts.

**Architecture:** client-only flow for drafting (small LM on device) → cloud for heavy tasks (summarize inbox) → sends via OAuth-constrained Gmail/MS Graph API.

**Eval:** ROUGE for summaries; user acceptance rate of drafts.

**Depth signals:** draft-replay A/B at scale; privacy partitioning of training data.

**Follow-up probes:** How do you avoid sending a draft that includes private PII to a model trainer?

</details>

### Design a multi-tenant AI chatbot platform

> "Design a multi-tenant AI chatbot platform where each business gets a custom chatbot."

**Where asked:** Intercom, Ada, Drift, Sierra, Yellow.ai, Cognigy, ChatBotKit 2025–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Per-tenant data isolation, per-tenant fine-tune or RAG, and multi-tenant cost controls.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE).

<details><summary>💡 Strong solution approach</summary>

**Architecture:** tenant boundary at the document store; a per-tenant RAG index; a shared base model with optional per-tenant LoRA.

**Eval:** tenant-specific resolution + safety metrics.

**Depth signals:** per-tenant rate limiting; cost dashboards; incident isolation.

**Follow-up probes:** How do you prevent a noisy tenant from starving others?

</details>

### Design a medical diagnosis assistant using AI

> "Design a medical diagnosis assistant using AI."

**Where asked:** Hippocratic AI, Glass Health, OpenAI Health, Google Med-PaLM, Tempus 2024–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Regulated-domain design: HIPAA/GDPR-class compliance, clinician-in-the-loop, calibration, and bias/fairness testing across populations.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE / Healthcare MLE).

<details><summary>💡 Strong solution approach</summary>

**Architecture:** calibrated probability model → LLM explanation → decision support → clinician review.

**Eval:** per-condition sensitivity/specificity, stratified across demographics; calibration curves.

**Depth signals:** any production deployment requires a human-in-the-loop; bias mitigation through stratified training data.

**Follow-up probes:** How do you measure calibration? How do you audit for bias after deployment?

</details>

## B6. Applied ML systems

### Design a real-time recommendation system

> "Design a real-time AI recommendation system."

**Where asked:** TikTok, Meta, X, Pinterest, Spotify, Netflix, YouTube; conversational recommendation at Replika/Character.AI 2024–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions)

**What it tests:** Two-tower retrieval, ANN serving, cold-start handling, and online-exploration design under a strict latency budget.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE / Recommender Systems).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** 100M users, 1M items, real-time updates (within seconds of new behavior), p95 <200ms retrieval, engagement-quality targets (watch time, dwell).

**Architecture:** two-tower DNN → ANN index + side features (popularity, recency) → reranker / LLM re-ranker → serving within the latency budget.

**Data:** embeddings trained with in-batch negatives or sampled softmax; user/item features (popularity, freshness, embeddings, taxonomy).

**Eval:** offline — nDCG, MAP, recall@k on a holdout; online — A/B on long-term engagement, dwell, churn.

**Monitoring:** per-segment CTR drift, embedding freshness, calibration.

**Cost/latency:** precompute user embeddings; quantize item embeddings; cap LLM re-ranking to the top-200.

**Depth signals:** two-tower vs end-to-end transformer; bandits vs supervised for online exploration; mitigating the popularity-bias feedback loop.

**Follow-up probes:** How do you handle an item with no history (cold-start)? How do you run A/B without harming newly onboarded users?

</details>

### Design a feed-ranking system

> "Design the ranking pipeline for a social feed at [company] scale."

**Where asked:** Meta, TikTok, X, Snap, Pinterest 2024–2026; also in Reddit candidate reports for ML roles (2025) · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions) · [IGotAnOffer: Meta MLE interview](https://igotanoffer.com/blogs/tech/facebook-machine-learning-engineer-interview)

**What it tests:** The multi-stage funnel (candidate gen → light ranker → heavy ranker → blending) and whether you volunteer it unprompted.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** real-time <100ms with a deep ranking model; multi-stage design.

**Architecture:** candidate generation (two-tower or behavioral embedding) → light ranker (small MLP) → heavy ranker (DCN/DIN/transformer) → blending (business rules, diversity, freshness).

**Data:** actions, impressions, dwell, hides, explicit negatives.

**Eval:** offline delta on engagement rate; online A/B on retention; interleaving for fast feedback.

**Monitoring:** per-segment model performance; bias toward active users.

**Depth signals:** the home feed's biggest lever is candidate-generation recall, not the ranker; blending is where most of the engineering lives.

**Follow-up probes:** How do you handle the cold-start user? How do you prevent an echo chamber without hurting engagement? Position bias in logged data — inverse-propensity weighting or a position feature at train, fixed at serve.

</details>

### Design a real-time fraud / abuse-detection ML system

> "Design a fraud detection system powered by LLMs" / "Design a real-time fraud detection system."

**Where asked:** Stripe, Adyen, Coinbase, Block, Riskified, Sift; AI startups building LLM-driven risk ops 2025–2026 · [amitshekhariitbhu/ai-engineering-interview-questions](https://github.com/amitshekhariitbhu/ai-engineering-interview-questions) · [Medium: Every question I was asked in Stripe's system design interview](https://medium.com/@emilyhustlenyc/every-question-i-was-asked-in-stripes-system-design-interview-f6f19c2e62d6)

**What it tests:** Streaming feature engineering, online/offline consistency, decision policy under asymmetric costs, label delay, and explainability.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE / Risk ML).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** <100ms decision at line rate; very high recall on fraud, very low false-positive rate; audit trail and explainability.

**Architecture:** features (velocity, device, IP, graph) → gradient-boosted model + neural sequence embedding → LLM as a *second opinion* on surfaced cases → action (allow, challenge/3DS step-up, decline, manual review).

**Data:** labeled transactions (chargebacks, disputes), device-fingerprint graph, behavioral features — computed via a stream processor into an online feature store with the **same definitions** used offline (name the online/offline skew problem explicitly).

**Eval:** PR-AUC, F1 at a chosen recall target, "loss saved" vs false-positive cost; offline replay + online shadow. Handle extreme imbalance (≪1% fraud) via class weighting; never evaluate with accuracy.

**Label delay:** chargebacks arrive 30–90 days late — train on mature data, monitor on proxies, and beware feedback bias (blocked transactions never get labels; keep a small exploration/holdout stream).

**Monitoring:** per-population drift; adversarial patterns; chargeback-rate slope.

**Depth signals:** how you label fraud after the fact without biasing toward known patterns; "LLM as second opinion" is the most 2026-flavored signal — it only works with calibrated policy prompts and structured outputs.

**Follow-up probes:** How do you A/B test changes without bleeding risk? How do you react to a sudden model-degradation incident? Explainability for declined customers and regulators (SHAP on GBDT, reason codes)?

</details>

### Design an ML feature store

> "Design an ML feature store and online/offline serving."

**Where asked:** Senior ML Platform / Senior MLE roles at Stripe, Airbnb, Uber, Meta, Doordash and AI-infrastructure startups 2024–2026 (multiple Jobright/Voker entries 2025–2026)

**What it tests:** Point-in-time correctness, train/serve parity, freshness SLOs, and backfill strategy.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (Senior MLE / Platform).

<details><summary>💡 Strong solution approach</summary>

**Requirements:** features computed once, served online and offline with parity, sub-ms p95 online; freshness tracking; ACLs across teams.

**Architecture:** ingestion (Kafka-style stream) → materialization (Flink/Spark) → online store (Redis/DynamoDB) + offline store (parquet/Iceberg).

**Data model:** timestamp keying for point-in-time correctness; feature definitions in a registry with owner and version.

**Pitfalls:** train/serve skew when the online path uses a different computation; leakage when offline joins include future rows.

**Eval:** PSI / KL drift between online and offline feature distributions.

**Monitoring:** freshness SLO per feature; staleness alerts; per-feature skew alarms.

**Depth signals:** point-in-time-correct join keys; backfill strategy; "feature freshness as a first-class contract."

**Follow-up probes:** How do you ensure online/offline parity? How do you backfill a feature without downtime?

</details>

### Design a centralized ML training and management platform

> Design a centralized platform for your company's ML teams: training-job orchestration, experiment tracking, a feature store, a model registry, deployment, and monitoring — the internal "ML platform" round.

**Where asked:** Meta engineer mock (recorded on interviewing.io in Meta's real format); the internal-platform variant is a common senior MLE/infra round at big tech · [Interviewing.io: Meta engineer mock — centralized ML management platform](https://interviewing.io/mocks/facebook-system-design-centralized-ml-management-platform) · [alirezadir: ML system design compilation](https://github.com/alirezadir/machine-learning-interviews/blob/main/src/MLSD/ml-system-design.md)

**What it tests:** Senior-level breadth — you're designing for *engineers* as users: multi-tenancy on GPUs, reproducibility, lineage, and the eternal flexibility-vs-paved-road tension. It's an org-design question wearing a systems costume.

**Time expected:** 45–60 min design round.

**Difficulty:** Hard (senior/staff round).

<details><summary>💡 Strong solution approach</summary>

Scope by user journey: an MLE goes data → features → experiment → train → evaluate → register → deploy → monitor. Design one paved road through it.

- **Data/features:** feature store with offline (warehouse, point-in-time joins) and online (low-latency KV) planes sharing one definition — killing online/offline skew is the store's entire reason to exist.
- **Experimentation:** tracked runs (params, metrics, artifacts, code+data versions) — every result reproducible from its lineage record.
- **Training orchestration:** jobs as DAGs on a GPU cluster (Kubernetes + scheduler); quotas + preemption by priority; spot capacity with checkpointing; distributed training as a library, not per-team hand-rolls.
- **Model registry:** versioned models with lineage, stage transitions (staging → prod) gated by eval suites — the CI/CD of models.
- **Serving:** standard containers for online (autoscaled, canary/shadow rollout) and batch; per-model dashboards out of the box.
- **Monitoring:** input drift, prediction drift, feature-freshness alarms, delayed-label performance tracking — by default, not by team diligence.

The senior move: discuss *adoption* — platforms fail socially, not technically. Golden-path templates, migration support, escape hatches for research teams, and platform metrics (time-to-first-model, % models on-platform).

**Follow-up probes:** GPU scarcity — fair-share vs priority quotas? A team needs a custom training loop the platform doesn't support — bend the platform or let them off-road? How does the platform change for LLM fine-tuning vs classic ML? (Bigger checkpoints, shared base models, adapter/LoRA registries, eval harnesses replacing test sets.) Buy vs build for each layer.

</details>

### System design prompts reported by multiple employers (cross-reference)

| Question | Top employers confirmed | Common depth signal |
| --- | --- | --- |
| Design ChatGPT @ 100M users | OpenAI | continuous batching + paged KV |
| Distributed training with fault tolerance | Anthropic, OpenAI, Mistral | spot-aware checkpoint restart loop |
| RAG with evaluation | OpenAI, Anthropic, Glean, Perplexity | reranker nDCG lift |
| LLM inference platform | Anthropic, OpenAI, Together | prefix-cache amortization |
| LLM evaluation platform | OpenAI, Anthropic, Scale AI | human + LM judge calibration |
| Semantic search at scale | OpenAI, Glean, Perplexity | hybrid retriever recall |
| Content moderation | OpenAI, Anthropic, Meta, Roblox | false-positive vs false-negative policy |
| Real-time recommendation system | TikTok, Meta, Replika | two-tower + cold-start |
| Fraud/abuse detection | Stripe, Coinbase, Adyen | LLM-as-second-opinion architecture |
| Feature store | Stripe, Airbnb, Uber | train/serve parity + freshness |
| Fine-tuning platform | OpenAI, Anthropic, Mistral | eval-gated rollout |
| Deep research agent | OpenAI, Anthropic, Perplexity | critic + scratchpad |
| AI coding agent | Cursor, Anthropic, GitHub | tool-use permission policy |
| Safe deployment of AI models | Anthropic, OpenAI, GDM | launch gating policy |

---

<div align="center">

**Practice these out loud. [Landed](https://landed.jobs) runs voice mock interviews that grill you on exactly these questions — plus daily matched AI roles and agent-drafted application answers.**

[![Get Started](https://img.shields.io/badge/Get%20Started%20Free-→-6C2BD9?style=for-the-badge)](https://landed.jobs)

<sub>Every question traces to a public candidate report — sources inline. Asked something new recently? PRs welcome. · [All banks →](../README.md)</sub>

</div>
