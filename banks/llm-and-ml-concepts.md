[← All question banks](../README.md) · part of [ai-interview-questions](https://github.com/landedjobs/ai-interview-questions) by [Landed](https://landed.jobs)

<div align="center">

# 🧠 LLM & ML Concepts — Real AI Interview Questions

![Updated](https://img.shields.io/badge/updated-2026.07-00A86B?style=flat-square) ![Questions](https://img.shields.io/badge/62%20real%20questions-ff5b29?style=flat-square) ![Sources](https://img.shields.io/badge/every%20question-cited-6C2BD9?style=flat-square)

**Every question below was reported by a real candidate, with the company and source. Answers are what a strong candidate actually says.**

</div>

---

**Jump to:** [Transformer & LLM fundamentals](#transformer--llm-fundamentals) · [Fine-tuning & post-training](#fine-tuning--post-training) · [RAG](#rag-retrieval-augmented-generation) · [Agents](#agents) · [Evals & observability](#evals--observability) · [Inference & serving](#inference--serving) · [Classic ML breadth](#classic-ml-breadth)

---

## Transformer & LLM Fundamentals

### 1. Why divide by sqrt(d_k) in scaled dot-product attention?

> "Walk me through why scaled dot-product attention divides by sqrt(d_k). What would happen during training if you removed that scaling factor?"

**Where asked:** OpenAI MLE (AI/MLE round) · [source](https://www.datainterview.com/blog/llms-and-transformers-interview-questions)

**What they're testing:** Whether you can derive the math and tie it back to training stability, not just recite the formula.

<details>
<summary>💡 Strong answer</summary>

Scaled dot-product attention computes Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V. As d_k grows, the dot products of unit-variance Q and K vectors grow in magnitude, pushing the softmax into regions of tiny gradient (the "softmax saturation" problem). Dividing by sqrt(d_k) keeps the input to softmax roughly unit-variance regardless of head dimension, which preserves gradient flow and helps avoid extremely peaked attention distributions during early training. Without it you'd see training instability: entropies collapse, one token dominates attention, and learning stalls. In practice, modern variants sometimes replace this with QK-norm or other normalizations for very large d_k, but the sqrt(d_k) factor remains the canonical default because it is dimension-aware without adding parameters. Senior candidates also mention that with sufficiently normalized embeddings, scaling matters less, but it is still kept for general robustness across head widths.

</details>

**Follow-ups:** Why multi-head? How does this interact with FlashAttention? Why does softmax(QK^T) without scaling still work sometimes in inference?

**Difficulty:** Mid

### 2. Why multi-head attention instead of one big head?

> "Multi-head attention splits the model dimension into h heads each of dimension d_k = d_model / h. An interviewer asks: why not just use a single attention head with the full d_model dimension?"

**Where asked:** Reported across multiple 2024-2026 AI/ML candidate guides (datainterview.com, blog.gopenai.com 2025, Medium bishalsharma 2024) · [source](https://www.datainterview.com/blog/llms-and-transformers-interview-questions)

**What they're testing:** Whether you understand representational diversity vs parameter efficiency.

<details>
<summary>💡 Strong answer</summary>

With one full-dimension head, a single softmax over the whole d_model mixes all feature subspaces into one attention distribution; in practice that distribution becomes diffuse and the model can only attend to one combined signal at a time. Multiple heads project into independent subspaces and compute separate attention patterns in parallel; outputs are concatenated and re-projected. Empirically this lets the model attend to different syntactic/semantic relations in the same layer, e.g. one head tracking syntactic dependencies, another coreference. There is a parameter-count invariance (h small heads vs 1 big head costs roughly the same FLOPs) but a representational one: more heads means more patterns per layer. The trade-off: too many heads wastes compute; too few collapses representational capacity. Modern efficient variants like GQA/MQA share KV across heads to save memory with minimal quality loss, a great senior-level gotcha to mention.

</details>

**Follow-ups:** What is Grouped Query Attention? How does MQA differ? Why not just use more layers instead?

**Difficulty:** Mid

### 3. Sinusoidal positional encodings vs RoPE

> "Compare sinusoidal positional encodings with Rotary Position Embeddings (RoPE). Which would you recommend for a modern autoregressive LLM and why?"

**Where asked:** Reported in 2026 AI engineer prep compendiums (datainterview.com, Mar 16 2026) and r/MachineLearning interview debriefs · [source](https://www.datainterview.com/blog/llms-and-transformers-interview-questions)

**What they're testing:** Understanding of relative vs absolute position and length extrapolation.

<details>
<summary>💡 Strong answer</summary>

Sinusoidal encodings from "Attention is All You Need" are absolute, fixed functions of position added to token embeddings. They generalize to moderate lengths but degrade outside training distribution and don't naturally encode relative distance in attention logits. RoPE (Su et al., 2021) rotates Q and K vectors by angle proportional to their position before the dot product, which makes the inner product encode relative position directly. This composition is what gives RoPE its length-extrapolation property via base-frequency tweaks (NTK-aware scaling, YaRN) and is what modern LLMs (LLaMA, Mistral, Qwen) all use. For a new autoregressive LLM, I'd recommend RoPE: it composes cleanly with FlashAttention, supports efficient inference, and has the best empirical track record for context extension. I'd mention ALiBi as an alternative if training-from-scratch with extreme long-context targets, but for a production system in 2026 RoPE with a tested extrapolation recipe is the safe default.

</details>

**Follow-ups:** What is YaRN? How does RoPE interact with KV cache reuse? When would you choose ALiBi?

**Difficulty:** Senior

### 4. Why do transformers need positional embeddings at all?

> "Why do transformers need positional embeddings at all? What would happen if you removed them completely? Why? Why not use simpler and more intuitive approaches like bag-of-words?"

**Where asked:** Reported at Google, Meta, OpenAI MLE interviews (r/MachineLearning, 2024) · [source](https://www.reddit.com/r/MachineLearning/comments/cttefo/d_positional_encoding_in_transformer/)

**What they're testing:** Whether you have an intuition for permutation-equivariance vs sequence modeling.

<details>
<summary>💡 Strong answer</summary>

Self-attention is permutation-equivariant: it treats the input as a set of token vectors with no built-in notion of order. Without positional information, "the dog bit the man" and "the man bit the dog" produce identical internal representations, only differing in the final projection of the [CLS]-style pooled output. Adding positional embeddings breaks that symmetry by injecting a position-dependent term into Q,K or directly into token vectors, so the model can encode word order and relative distance. Bag-of-words style approaches work for some tasks but lose the ability to model long-range order-sensitive syntax and coreference. If you removed positional embeddings entirely you'd see the model collapse to set-based reasoning: useful for retrieval-style scoring, useless for translation or code. Modern alternatives include RoPE, ALiBi, NoPE (no positional encoding at all, works for some tasks once attention sinks are learned).

</details>

**Follow-ups:** What about NoPE / attention sinks? How does this interact with relative vs absolute attention?

**Difficulty:** Mid

### 5. What is KV cache and how does it speed up inference?

> "Explain KV cache and how it speeds up autoregressive inference. Why does memory scale with sequence length?"

**Where asked:** Reported at OpenAI, Anthropic, Google MLE (Medium VectorWorks 2025; r/MachineLearning threads) · [source](https://medium.com/@VectorWorksAcademy/ace-ai-interview-series-22-understanding-kv-cache-efc418dbc0c0)

**What they're testing:** Practical inference economics and attention recomputation awareness.

<details>
<summary>💡 Strong answer</summary>

During autoregressive decoding, recomputing all key and value projections for the entire prefix at every new token is wasteful because past tokens never change. KV cache stores those K and V tensors from prior steps, so each new token only needs to compute its own Q, K, V; the attention output then concatenates to growing KV storage rather than recomputing history. The per-token compute drops from O(seq_len) to O(1), giving 10-100x decoding speedups. The cost is memory: ~2 * n_layers * n_heads * seq_len * head_dim * 2 bytes (fp16, K and V). For a 70B model with 80 layers, hidden=8192, seq=8k tokens, that's ~80 GB, often exceeding H100 memory. This is why techniques like GQA/MQA (sharing KV across heads), Multi-Head Latent Attention (low-rank KV compression), paged KV cache (vLLM style), and KV cache quantization (FP8 KV) are hot topics. Senior candidates should mention the compute-memory trade-off and FlashAttention-style recomputation as the alternative when memory is tight but FLOPs are cheap.

</details>

**Follow-ups:** How does FlashDecoding work? What is paged attention? How does GQA reduce KV cache 4-8x?

**Difficulty:** Mid - Senior

### 6. BPE vs SentencePiece vs WordPiece tokenization

> "Walk through tokenizer choices for a multilingual LLM - BPE vs WordPiece vs SentencePiece vs Unigram. Which would you pick and why?"

**Where asked:** Reported at multiple 2024-2026 sources (DataCamp RAG guide, datainterview.com Mar 2026, Medium "Ace AI Interview" series); also surfaced in many r/MachineLearning prep threads · [source](https://www.datainterview.com/blog/llms-and-transformers-interview-questions)

**What they're testing:** Knowledge of tokenization's effect on model behavior, cost, and multilingual quality.

<details>
<summary>💡 Strong answer</summary>

Tokenization splits raw text into integer IDs; it determines vocabulary size, sequence length, OOV handling, and downstream cost (more tokens = more money and latency). BPE (Byte Pair Encoding) iteratively merges the most frequent adjacent pairs, starting from bytes; it's what GPT-2/3/4 use and handles any UTF-8 cleanly. WordPiece (BERT-family) is similar but uses likelihood-based merges. SentencePiece is a system, not an algorithm: it can run BPE or Unigram language-model tokenization directly on raw text without pre-tokenization, which makes it ideal for languages without whitespace (CJK, Thai). Unigram (also via SentencePiece) starts with a large vocabulary and prunes; it allows multiple segmentations and probabilistic decoding, useful for languages with rich morphology. For a modern multilingual LLM I'd pick SentencePiece + BPE for simplicity, or Unigram if I cared about morphological precision and had the compute to tune it. Senior points: tokenization quality affects arithmetic ("3.11 vs 3.9"), code ("\n" handling), and multilingual fairness; modern models are investigating token-free approaches like ByT5 or Mamba-Bytes for low-resource languages.

</details>

**Follow-ups:** Why are some languages tokenized 5-10x less efficiently? What is the "dollar sign in code" problem (GPT-2, Llama)?

**Difficulty:** Mid

### 7. Top-k, top-p (nucleus) and temperature sampling

> "What is top-k vs top-p sampling? When do you adjust temperature vs top-p? What trade-offs do you make for code vs creative writing?"

**Where asked:** Reported at Google DeepMind, Mistral, OpenAI MLE (r/MachineLearning; huyenchip.com Jan 16 2024; sebastianraschka FAQ) · [source](https://huyenchip.com/2024/01/16/sampling.html)

**What they're testing:** Practical decoding intuition for production LLM systems.

<details>
<summary>💡 Strong answer</summary>

Greedy decoding (always pick the argmax) is deterministic but loops and boring. Sampling injects diversity by drawing from a probability distribution. Temperature scales the logits before softmax: low T sharpens the distribution toward greedy, high T flattens it. Top-k truncates to only the k highest-probability tokens before sampling, eliminating long-tail noise but capping diversity rigidly. Top-p (nucleus) samples from the smallest set of tokens whose cumulative probability mass exceeds p, which adapts to the entropy of the distribution: tight distributions yield tiny pools, flat ones larger. For code/data extraction: low temperature (0-0.2), top-p=1, often top-k off. For open-ended creative writing: temperature ~0.7-0.9, top-p ~0.9, top-k 40-100. For chat assistants: temperature 0.6-0.8, top-p ~0.9. Senior nuance: temperature and top-p are NOT redundant; they operate in different spaces (logit scale vs probability mass), and combining them lets you tune shape-of-distribution AND cut-off separately. Beam search is sometimes better for narrow NLG tasks (summarization) where argmax-quality matters.

</details>

**Follow-ups:** What is contrastive search? When does beam search beat sampling? How does min-p sampling compare?

**Difficulty:** Mid

### 8. The "lost in the middle" phenomenon

> "How does increasing the context window affect model performance? What is the 'Lost in the Middle' phenomenon and how do you mitigate it?"

**Where asked:** Reported at Anthropic (aiofferly Dec 3 2025), OpenAI (jobright Dec 24 2025), and similar at Mistral / DeepMind · [source](https://www.aiofferly.com/career-guide/anthropic-ml-interview-questions)

**What they're testing:** Production-system awareness of attention degradation and retrieval re-ranking.

<details>
<summary>💡 Strong answer</summary>

Liu et al. (2023) "Lost in the Middle" showed that even at long context lengths, LLMs reliably use information at the very beginning and end of the context but struggle to recall information in the middle: a U-shaped recall curve. This is partly because long contexts dilute attention scores (each retrieved chunk gets a smaller share of softmax mass) and partly because training data is biased toward short contexts. Mitigation strategies: (1) retrieval re-ranking to put most relevant chunks at the ends; (2) step-back prompting or chain-of-thought that re-attends to the middle; (3) prepending summaries; (4) compressing the "middle" via summarization; (5) using models trained with attention sinks or specialized long-context training (e.g., YaRN). For RAG, this is why simple top-k retrieval often under-performs hybrid + reranker pipelines. Senior caveat: the phenomenon is partially mitigated in newer models trained with long-context targets, but not eliminated.

</details>

**Follow-ups:** How do attention sinks help? What's the typical loss pattern? Does it change with instruction tuning?

**Difficulty:** Senior

### 9. Context windows and their practical limits

> "LLM context windows are increasing. They can handle millions of tokens now with smaller nimble models that run on commodity hardware. What does this mean for how we build products?"

**Where asked:** r/ExperiencedDevs (Reddit, 2025); also referenced in datainterview.com Mar 2026 · [source](https://www.reddit.com/r/ExperiencedDevs/comments/1jwhsa9/what_does_large_context_window_in_llm_mean_for/)

**What they're testing:** Understanding of where context-length marketing breaks down.

<details>
<summary>💡 Strong answer</summary>

A context window is the maximum total tokens (input + output) a model can attend to in a single forward pass. Modern frontier models advertise 128k-2M tokens but effective usable length is usually shorter because of (1) attention cost: O(n^2) memory in vanilla attention, driving per-token latency and memory; (2) the lost-in-the-middle degradation; (3) degradation when the bulk of training data was at short contexts; (4) cost: input tokens still cost real money. Practical limits: ~32k-64k tokens is the sweet spot for most RAG workloads, model "advertised" length is asymptotic, and Pinecone/Weaviate-grade retrieval plus reranking usually beats simply stuffing more context. Senior nuance: techniques like FlashAttention-2 make 100k+ feasible on a single GPU; long-context training (RoPE scaling, YaRN) and post-training specifically on long-context tasks (e.g., ANELLA, NoLiMa) materially change effective limits. Don't conflate marketing max tokens with reliable retrieval recall.

</details>

**Follow-ups:** How does FlashAttention-2 enable long context? What is ToT / attention sink? How would you test a model's effective context window?

**Difficulty:** Mid

### 10. What are embeddings, beyond similarity search?

> "What is an embedding? Why do embeddings matter in production AI systems beyond just similarity search?"

**Where asked:** Reported at OpenAI (jobright Dec 24 2025), Writer (Glassdoor), Databricks MLE (datainterview Mar 2026) · [source](https://jobright.ai/blog/openai-technical-interview-questions-2026-and-how-to-answer/)

**What they're testing:** Breadth of embedding use cases.

<details>
<summary>💡 Strong answer</summary>

An embedding is a dense vector representation of an entity (token, sentence, document, image, user, product) such that geometric similarity in vector space corresponds to semantic similarity in the source domain. They power retrieval (similarity search), clustering, recommendation, classification (via linear probe), and even features for downstream tabular ML. In modern LLM systems, embeddings are the backbone of RAG retrieval, semantic caching, agent memory stores, and reward model inputs. Senior points: (1) embedding quality depends on the model (e.g., BGE-large vs OpenAI text-embedding-3 vs Cohere embed-v3), but ALSO on chunking, prefix design (e.g., "Represent this sentence for retrieval: ..."), and finetuning for your domain. (2) They degrade under distribution shift: you MUST evaluate on your own data. (3) Matryoshka embeddings let you truncate to multiple dimensions for cost. (4) Hard negatives during training matter as much as the base model.

</details>

**Follow-ups:** How do you evaluate embedding quality? What's a good way to finetune for a vertical domain?

**Difficulty:** Junior - Mid

---

## Fine-tuning & Post-training

### 11. LoRA vs full fine-tuning

> "What is LoRA, and how is it different from full fine-tuning?"

**Where asked:** Reported at multiple 2024-2025: r/LocalLLaMA, OpenAI MLE guide (jobright Dec 24 2025), Anthropic ML guide (aiofferly Dec 3 2025) · [source](https://www.reddit.com/r/LocalLLaMA/comments/1cmlyoa/are_lora_and_qlora_still_the_goto_finetune_methods/)

**What they're testing:** Parameter-efficient fine-tuning intuition and tradeoffs.

<details>
<summary>💡 Strong answer</summary>

LoRA (Low-Rank Adaptation, Hu et al. 2021) freezes the pretrained weight matrix W and learns a low-rank update Delta W = BA, where B is d x r, A is r x k, r << min(d,k). During the forward pass, h = W x + BA x. Because BA is low-rank, the trainable parameter count drops from d*k to r*(d+k), often 100-1000x compression. Empirically this matches full fine-tuning quality on many tasks while using a fraction of GPU memory and storage (you only store the adapter, not a full model copy). Trade-offs: (1) rank r exposes a quality/capacity knob: too low underfits, too high approaches full FT; (2) merging adapters back to W at deployment is lossless; (3) LoRA assumes the task-relevant update lives in a low-rank subspace, which holds empirically but is not theoretically guaranteed; (4) compared to adapters / prompt tuning, LoRA is the sweet spot between quality and efficiency.

</details>

**Follow-ups:** What is QLoRA? How do you choose rank? Can you compose multiple LoRAs?

**Difficulty:** Mid

### 12. QLoRA vs LoRA

> "What is QLoRA and how does it differ from LoRA?"

**Where asked:** Reported at multiple companies for ML platform / applied ML roles (2025-2026) · [source](https://www.newline.co/@Dipen/qlora-vs-lora-which-finetuning-wins--683ca660)

**What they're testing:** Awareness of quantization-aware fine-tuning and serving memory math.

<details>
<summary>💡 Strong answer</summary>

QLoRA (Dettmers et al., 2023) combines 4-bit (NF4) quantization of the frozen base model with LoRA adapters trained in higher precision. The motivation is that even with LoRA the frozen model copy must reside in GPU memory during training, which dominates VRAM at 70B+ scales. By quantizing the frozen weights to 4-bit, you cut base-model memory 4x, letting you fine-tune a 65B model on a single 48GB GPU instead of an 80GB A100. Three additional tricks stabilize training: double quantization (quantize the quantization constants), paged optimizers (paged-adam to handle optimizer state spikes), and NF4 (normal-float 4) which is information-theoretically optimal for normally-distributed weights. Trade-off: a tiny quality hit (usually <1% on benchmarks) for 4x memory; some workloads show bigger regressions, especially on smaller base models. Senior caveat: an inference-time "QLoRA" model still needs to be dequantized, so don't confuse QLoRA's memory savings with decoding speed.

</details>

**Follow-ups:** When does QLoRA hurt quality? What is NF4 vs FP4? How does QLoRA compare to GPTQ-LoRA?

**Difficulty:** Senior

### 13. RLHF in plain terms: what does it solve that SFT cannot?

> "I am interviewing for a company who is heavily focused on post training processes for training an agent. They do great deal of SFT and RL with human feedback. What should I study?"

**Where asked:** Reported at multiple AI labs: Anthropic, OpenAI, Cohere, Character.ai (r/MachineLearning, Feb 2025) · [source](https://www.reddit.com/r/MachineLearning/comments/1imqlv7/d_tips_for_llm_post_training_focused_interview/)

**What they're testing:** Foundation understanding of why preference learning exists.

<details>
<summary>💡 Strong answer</summary>

SFT (supervised fine-tuning) teaches a base model to imitate demonstrations, but it can only learn what's already in the data and cannot directly optimize for "what users actually prefer" when there are many equally valid completions. RLHF adds a preference-modeling step: humans rank outputs (often pairwise), a reward model r(x, y) is trained on those preferences, and the LM is then optimized against that reward signal. Two flavors: (1) classic RLHF uses PPO with a KL penalty to the reference model; (2) Direct Preference Optimization (DPO) re-derives the same objective as a supervised loss on preference pairs: simpler, more stable, no reward model needed, dominates practical pipelines by 2025. Conclusion: RLHF/DPO is what makes ChatGPT-style assistants possible; it shapes style, refusal behaviors, helpfulness, harmlessness. Senior nuances: reward hacking, distribution shift between RM and policy, "alignment tax", and the emergence of RLHF-V, RLHF-Diffusion, online DPO, GRPO for reasoning models in 2025-2026.

</details>

**Follow-ups:** Why doesn't SFT already do this? What is reward hacking? How do you scale RLHF to 70B+?

**Difficulty:** Senior

### 14. DPO vs RLHF/PPO: when would you pick each?

> "What is DPO, and how does it differ from RLHF/PPO? When would you choose each?"

**Where asked:** Reported at Anthropic ML, OpenAI alignment, Cohere (r/MachineLearning 2025; PatSnap 60+ patent analysis Apr 2026) · [source](https://www.patsnap.com/resources/blog/articles/rlhf-vs-dpo-in-llm-fine-tuning-60-patent-analysis-2/)

**What they're testing:** Awareness of modern alignment algorithms beyond PPO.

<details>
<summary>💡 Strong answer</summary>

DPO (Rafailov et al., 2023) reformulates the RLHF objective as a closed-form supervised loss on preference pairs, eliminating the explicit reward model and the RL loop entirely. The loss is roughly -log_sigmoid(beta * [logP(y_w|x) - logP(y_l|x)] - beta_ref * [logP_ref(y_w|x) - logP_ref(y_l|x)]). Benefits: (1) simpler training pipeline, no reward-model drift; (2) more stable than PPO (no value head, no sampling during training); (3) works on smaller compute budgets. Limitations: (1) less flexible when you want multi-objective rewards or RL-with-tools; (2) offline only: cannot do online rollouts. Variants that address limits: IPO (handles noisy preferences more gracefully), KTO (single-rating instead of pairs), GRPO (group-relative policy optimization, popularized by DeepSeek-R1), online DPO. Practical rule of thumb 2025-2026: start with DPO, jump to PPO or GRPO only when online exploration or non-pairwise rewards matter.

</details>

**Follow-ups:** What is GRPO? When does online DPO beat offline DPO? Why isn't DPO universally better than PPO?

**Difficulty:** Senior

### 15. What is instruction tuning and why does it matter?

> "What is instruction tuning? How does it differ from continued pretraining?"

**Where asked:** Reported at multiple 2024-2026 sources: aiofferly Anthropic guide, OpenAI MLE interview, datainterview.com · [source](https://www.aiofferly.com/career-guide/anthropic-ml-interview-questions)

**What they're testing:** Clarity on the boundary between pretraining, SFT, and alignment.

<details>
<summary>💡 Strong answer</summary>

Instruction tuning is supervised fine-tuning on (instruction, response) pairs. The pretraining objective (next-token prediction over raw web text) gives the model world knowledge and basic language modeling, but it doesn't teach the model to follow instructions, respond helpfully, or refuse. Instruction tuning bridges that gap by teaching Q->A style with curated prompts and high-quality answers. The 2022 FLAN paper showed that mixing many task families improves zero-shot generalization; modern open-instruct datasets (OpenHermes, Alpaca, Dolly, UltraFeedback) are the substrate for both base-model fine-tunes and the SFT stage of RLHF/DPO. Key trade-offs: (1) data quality > quantity: 10k high-quality SFT examples can beat 1M noisy ones; (2) too narrow instruction data overfits; (3) the SFT-then-DPO pipeline is standard. Senior nuance: "instruction pre-training" work shows that mixing instructions into pretraining can also help generalization.

</details>

**Follow-ups:** How do you curate instruction data? What is Alpaca/Tulu/OpenHermes? Why does alignment tax exist?

**Difficulty:** Mid

### 16. Knowledge distillation for LLMs

> "Walk through knowledge distillation. How would you distill a 70B teacher into a 7B student for a domain-specific chatbot?"

**Where asked:** Reported at OpenAI MLE / Anthropic ML / Cohere MLE (Reddit, 2025) · [source](https://www.reddit.com/r/MachineLearning/comments/1imqlv7/d_tips_for_llm_post_training_focused_interview/)

**What they're testing:** Production-time awareness of model compression and dataset design.

<details>
<summary>💡 Strong answer</summary>

Distillation transfers a larger "teacher" model's behavior into a smaller "student" model. Two main modes: (1) data distillation: sample completions from the teacher on a large prompt set, then SFT the student on (prompt, teacher_response) pairs; (2) logits distillation: match the teacher's full softmax distribution (which encodes "dark knowledge" about relative confidences), typically via KL-divergence between teacher and student logits at training time. Distillation can match 80-95% of teacher quality at 5-10x smaller model size, but real-world gains depend heavily on the data distribution match to deployment. Trade-offs: synthetic-data distillation generalizes better than just SFT-imitating human answers because teacher confusion on hard examples is implicitly conveyed. Senior nuance: classic KD vs sequence-level KD vs multi-teacher ensembling; also "self-distillation" can sometimes improve a model without a smaller student. Distillation is also used in RLHF to bootstrap reward models.

</details>

**Follow-ups:** What's the role of temperature in logits distillation? When does distillation underperform naive SFT?

**Difficulty:** Senior

### 17. Catastrophic forgetting during fine-tuning

> "How do you fine-tune an LLM on a new domain without catastrophic forgetting of general capabilities?"

**Where asked:** Reported at OpenAI, Anthropic, Google DeepMind MLE (r/MachineLearning, Feb 2025) · [source](https://www.reddit.com/r/MachineLearning/comments/1imqlv7/d_tips_for_llm_post_training_focused_interview/)

**What they're testing:** Awareness of capability preservation in production fine-tuning.

<details>
<summary>💡 Strong answer</summary>

Catastrophic forgetting is the tendency of a fine-tuned model to lose previously learned capabilities (general reasoning, instruction following, language coverage) when trained on a new narrow dataset. Mitigations: (1) replay: mix in 10-30% general-domain data during fine-tuning; (2) LoRA: keeping base weights frozen means no catastrophic drift; (3) KL-regularization to the reference model (used in RLHF/PPO and applied to SFT as "anchor loss"); (4) PEFT methods like IA3, prompt tuning learn tiny parameter sets that perturb behavior minimally; (5) multi-task / instruction-mix fine-tuning (Tulu, FLAN): never single-domain SFT; (6) staged curricula: world-knowledge SFT followed by capability SFT followed by domain SFT. Senior nuance: empirical reality in 2025-2026 is that a strong SFT-then-DPO pipeline on well-curated open data is usually less destructive than narrow-domain SFT alone.

</details>

**Follow-ups:** At what data mix does this stop working? What metrics detect forgetting?

**Difficulty:** Senior

### 18. The lineage from PPO to DPO to GRPO

> "Walk through the algorithmic lineage from PPO to DPO to GRPO. What changed and why?"

**Where asked:** Reported at DeepSeek, Anthropic, OpenAI alignment, xAI (r/MachineLearning; PatSnap blog Apr 16 2026) · [source](https://www.patsnap.com/resources/blog/articles/rlhf-vs-dpo-in-llm-fine-tuning-60-patent-analysis-2/)

**What they're testing:** Currency of alignment-algorithm knowledge.

<details>
<summary>💡 Strong answer</summary>

Classic RLHF (Ouyang et al. 2022) uses PPO with reward model + KL constraint. Problems: reward hacking, instability, on-policy rollout cost. DPO (2023) closed-formed the same objective as supervised loss, eliminating the reward model and RL loop. IPO (2024) softened DPO's Bradley-Terry assumption for noisier preferences. KTO (2024) used single-rating (good/bad) instead of pairs: cheaper labeling. Online DPO (2024) iterates between sampling from current policy and updating on freshly ranked pairs. GRPO (DeepSeek-R1, early 2025) replaced the value head with group-relative advantages: sample N completions per prompt, normalize their rewards, use normalized advantages as update signal, dramatically cheaper than PPO for reasoning models. Process-reward models (PRMs) reward intermediate reasoning steps and emerged alongside GRPO. Senior view: GRPO is the dominant 2025-2026 recipe for reasoning fine-tunes; classic PPO is mostly used in safety/RLHF contexts; DPO remains default for chat-style alignment.

</details>

**Follow-ups:** How does GRPO handle reward variance? Why does DeepSeek-R1 use GRPO?

**Difficulty:** Senior

### 19. Fine-tuning vs RAG vs prompt engineering

> "How do you decide between RAG, fine-tuning, and prompt engineering for a given product feature?"

**Where asked:** Reported at Anthropic MLE (jobright Dec 18 2025), OpenAI MLE, Cohere (r/MachineLearning) · [source](https://jobright.ai/blog/anthropic-technical-interview-questions-complete-guide-2026/)

**What they're testing:** System-level thinking about cost, latency, and capability trade-offs.

<details>
<summary>💡 Strong answer</summary>

Decision heuristic 2025-2026: (1) prompt engineering first: try structures like CoT, ReAct, tool-use scaffolding with the base model. If that hits target quality, stop. (2) RAG: when the task needs fresh, document-specific, or proprietary knowledge that the base model doesn't have. RAG is preferred over fine-tuning for knowledge updates because you can swap documents without retraining, you get provenance, and it's cheaper. (3) Fine-tuning: when you need to change behavior (style, format, tool-use schema, output structure, domain jargon compression) or compress a costly prompt into learned weights. Concretely: I fine-tune when (a) I need the model to consistently do something in a specific format thousands of times per minute (latency/cost), (b) I have 10k+ high-quality supervised examples, (c) I'm online-learning from production feedback. Senior nuance: hybrid is common (RAG for grounding + light fine-tuning for persona/tool schema) and evaluation discipline separates the good practitioners from those who fine-tune prematurely.

</details>

**Follow-ups:** How do you measure fine-tuning ROI? What size of data do you need?

**Difficulty:** Senior

---

## RAG (Retrieval-Augmented Generation)

### 20. The main parts of a RAG system

> "Explain the main parts of a RAG system and how they work."

**Where asked:** Reported at OpenAI MLE (jobright Dec 24 2025), Databricks MLE, Baidu LLM Engineer (Glassdoor Nov 2025) · [source](https://www.datacamp.com/blog/rag-interview-questions)

**What they're testing:** Breadth of retrieval-pipeline knowledge.

<details>
<summary>💡 Strong answer</summary>

A RAG system has four stages. Ingestion: documents are loaded, chunked (fixed-size, semantic, or hierarchical), embedded with a model like OpenAI text-embedding-3 or BGE-large, and indexed in a vector store (Pinecone/Weaviate/Qdrant/Milvus/Chroma). Query: user query is optionally rewritten (HyDE, multi-query expansion), embedded with the same model, and used to retrieve top-k similar chunks (ANN search via HNSW or IVF); often blended with sparse retrievers (BM25) in hybrid search, then re-ranked with a cross-encoder (Cohere rerank, ColBERT). Augmentation: retrieved chunks are stuffed into the prompt as context, often with instructions to cite. Generation: an LLM produces an answer grounded in the context. Senior additions: (1) chunk metadata filters (date, source, author) can pre-narrow retrieval; (2) parent-doc retriever stores small chunks but returns larger context; (3) late interaction rerankers (ColBERT) win on quality/perf; (4) evaluators run on all four stages independently.

</details>

**Follow-ups:** Hybrid search vs pure vector? Why do pipelines deteriorate in production?

**Difficulty:** Junior - Mid

### 21. Document chunking strategies for RAG

> "I find the semantic search the greatest part of RAG. Building a good retrieval system (proper chunking, context-awareness, decent pre-retrieval)..."

**Where asked:** Reported at OpenAI, Anthropic, Writer AI (Glassdoor), Cohere MLE (r/MachineLearning, May 2024) · [source](https://www.reddit.com/r/MachineLearning/comments/1cekoc7/d_real_talk_about_rag/)

**What they're testing:** Production knowledge of pre-retrieval design.

<details>
<summary>💡 Strong answer</summary>

Chunking determines what the retriever sees, so it determines what's retrievable. Common choices: (1) fixed-size (e.g., 512 tokens): simple but breaks mid-sentence; (2) recursive character splitting (LangChain-style): respects structure; (3) semantic chunking: split on embedding-distance breakpoints; (4) document-aware splitting (markdown headers, code function defs); (5) parent-doc retriever (small chunks for retrieval, large chunks for context); (6) hierarchical / multi-granular (summaries + chunks). The tradeoff: small chunks give precise retrieval but lose context; large chunks give context but bury the answer in noise. Best practice 2025-2026: start with markdown/structural chunking at ~256-512 tokens with 10-20% overlap, then tune with retrieval metrics (Recall@k) on a labeled eval set. Senior nuance: chunking is downstream of ingestion quality; garbage docs + a perfect chunker still gives a bad RAG.

</details>

**Follow-ups:** What is parent-document retriever? How do multi-granular indexes help?

**Difficulty:** Mid

### 22. Dense vs sparse (BM25) vs hybrid retrieval

> "Dense vs sparse vs hybrid retrieval - when does each shine?"

**Where asked:** Reported at OpenAI, Anthropic, Cohere MLE (DataCamp RAG 2026 guide + r/MachineLearning) · [source](https://www.datacamp.com/blog/rag-interview-questions)

**What they're testing:** Knowledge of retrieval-system trade-offs and the "hybrid best" pattern.

<details>
<summary>💡 Strong answer</summary>

Sparse (BM25/TF-IDF): lexical overlap, fast, exact-match friendly, no model needed, hates paraphrase. Dense (DPR/contriever/BGE/OpenAI embeddings): semantic similarity in vector space, handles paraphrase and cross-lingual, but mismatches on rare entities and exact identifiers (model numbers, ticker symbols). Hybrid combines both, usually via score fusion (RRF = reciprocal rank fusion is the 2025 standard, not linear combination) or by training a reranker that sees both. Hybrid typically wins by 5-15% MRR/Recall over either alone, especially when queries are a mix of natural-language and keyword-style (e.g., "iPhone 15 specs"). Senior nuance: hybrid only helps if both signals complement each other; if your embedding model is great, hybrid is overhead; if your docs are highly technical with rare terms, BM25 alone can outperform dense. The right answer in 2026 is: hybrid with reranking.

</details>

**Follow-ups:** What is RRF? Why does hybrid help even when dense is strong alone? What about SPLADE?

**Difficulty:** Mid - Senior

### 23. Why rerank after retrieval?

> "Why do we rerank after initial retrieval in RAG? Doesn't the retriever already give good results?"

**Where asked:** Reported at OpenAI, Anthropic, Cohere (r/MachineLearning RAG threads 2024-2026) · [source](https://www.reddit.com/r/MachineLearning/comments/1cekoc7/d_real_talk_about_rag/)

**What they're testing:** Two-stage retrieval awareness and bi-encoder vs cross-encoder tradeoff.

<details>
<summary>💡 Strong answer</summary>

Cross-encoder rerankers (Cohere Rerank 3, ColBERT, monoT5) score query-document pairs jointly, with full attention over both, which is much more accurate than bi-encoder similarity but ~1000x slower. The standard pipeline (2025-2026) is bi-encoder top-100 -> cross-encoder rerank -> top-5-10 to LLM. This recovers recall lost in fast retrieval without paying the latency cost. Empirical gains on BEIR, MIRAGE, RAGAS benchmarks are typically 5-20% in nDCG@10. Senior caveat: rerank quality is bounded by retrieval recall; if the ground-truth doc isn't in the top-100, reranking won't find it. So you tune recall@k first, then reranker. Late-interaction models like ColBERT retain per-token scores and let you trade off index size vs accuracy.

</details>

**Follow-ups:** What is ColBERT? How do you train a custom reranker on domain data?

**Difficulty:** Senior

### 24. How do you evaluate a RAG system?

> "How would you evaluate the performance of a RAG system?"

**Where asked:** Reported at OpenAI MLE (jobright Dec 24 2025), Anthropic ML (aiofferly Dec 3 2025), Cohere · [source](https://www.pass4sure.com/blog/top-30-rag-interview-questions-and-answers-for-2025/)

**What they're testing:** Familiarity with RAGAS / DeepEval / bespoke evaluation discipline.

<details>
<summary>💡 Strong answer</summary>

Evaluate RAG in three layers: (1) Retrieval quality: Recall@k, MRR, nDCG@k against a held-out query set with ground-truth chunk IDs; (2) Generation quality: faithfulness (whether the answer is grounded in retrieved context, RAGAS "faithfulness"), answer-relevance (whether the answer addresses the query, RAGAS "answer_relevancy"), context-relevance (RAGAS "context_precision" / "context_recall"); (3) End-to-end: human eval via pairwise comparison, A/B testing, or LLM-as-judge. Frameworks: RAGAS, DeepEval, TruLens, Phoenix (Arize). Senior nuance: RAGAS-style metrics are useful but biased (LLM judge biases toward verbose, "confident" answers); pair them with explicit ground-truth checks and human spot-audits. Also: retrieval changes suddenly when docs change, so eval must be re-run continuously.

</details>

**Follow-ups:** How do you build a RAG eval set? What are RAGAS limitations?

**Difficulty:** Senior

### 25. Mitigating hallucinations in RAG

> "How should we evaluate hallucinations in RAG systems when semantically similar context may still be irrelevant or incorrect... and the real failure may lie in retrieval or source quality, not the model itself?"

**Where asked:** Reported at OpenAI community (Jun 26 2025), Anthropic ML (aiofferly Dec 3 2025) · [source](https://community.openai.com/t/how-should-we-evaluate-hallucinations-in-rag-systems-when-semantically-similar-context-may-still-be-irrelevant-or-incorrect-and-the-real-failure-may-lie-in-retrieval-or-source-quality-not-the-model-itself/1299514)

**What they're testing:** Diagnostic depth: separating retrieval from generation failures.

<details>
<summary>💡 Strong answer</summary>

Hallucinations in RAG have three root causes: (1) generator hallucination despite correct context: reduce via constrained decoding, low temperature, system prompts that demand citations; (2) generator hallucination due to bad retrieval: the context is wrong; (3) generator hallucination due to weak context: context is right but ambiguous, model invents to fill gaps. Mitigation: (a) cite-then-answer prompts forcing the model to ground specific claims to specific spans; (b) claim-level faithfulness scoring (split answer into atomic claims, verify each against context); (c) self-consistency / multi-sample voting; (d) re-rank with cross-encoders; (e) upstream curation: bad retrieval is more often the cause than generator bugs, so measure retrieval Recall@k separately. Senior nuance: hallucination evaluation is harder than generation quality because the truth boundary depends on doc updates; LLM-as-judge must be calibrated with a held-out human-labeled set.

</details>

**Follow-ups:** How do you detect "lost in the middle"? What is claim-level scoring?

**Difficulty:** Senior

### 26. Monitoring RAG in production

> "How do you monitor a RAG system once it goes to production? What signals tell you retrieval or generation quality is degrading?"

**Where asked:** Reported at OpenAI MLE (jobright Dec 24 2025), Databricks ML (aiofferly Jan 21 2026) · [source](https://jobright.ai/blog/openai-technical-interview-questions-2026-and-how-to-answer/)

**What they're testing:** Production observability gravity.

<details>
<summary>💡 Strong answer</summary>

Production RAG monitoring has five pillars: (1) Logs: capture (query, retrieved_chunks, generated_answer, citations_used, latency, model_version); (2) Retrieval: track Recall@k on a rolling labeled set, ANN-search-index freshness, embedding-model version drift; (3) Generation: sample 1-5% of traffic to LLM-as-judge (faithfulness, answer-relevance) and human spot-audit; (4) Cost/latency: p50/p99 by query, exploded by retrieval + LLM cost; (5) User feedback: thumbs up/down, follow-up rates. Most common regression patterns: doc corpus silently updated, embedding version pinning lost, top-k too small after a corpus growth. Senior nuance: monitor context relevance and groundedness separately; if context relevance drops first, fix retrieval; if generation drops while context relevance holds, fix prompts or model.

</details>

**Follow-ups:** How do you re-evaluate after doc changes? What is drift detection on embeddings?

**Difficulty:** Senior

### 27. RAGAS: why it's popular and where it breaks

> "How do you measure RAG quality without expensive human eval?"

**Where asked:** Reported at OpenAI MLE (jobright Dec 24 2025), Anthropic (aiofferly Dec 3 2025), Mistral · [source](https://jobright.ai/blog/openai-technical-interview-questions-2026-and-how-to-answer/)

**What they're testing:** Familiarity with industry-standard RAG eval frameworks.

<details>
<summary>💡 Strong answer</summary>

RAGAS (Reference-free Augmented Generation Assessment) is an open-source framework for RAG eval that uses LLM-as-judge in four canonical metrics: faithfulness (does the answer stay in retrieved context?), answer_relevancy (does it answer the question?), context_precision (are the retrieved chunks actually relevant?), and context_recall (does the corpus contain answers to the question?). It became popular because it works without ground-truth labels: the LLM judge derives scores from question + context + answer alone. Limits: quality depends on the LLM judge, so biases in the judge propagate; not great for very long-form or numeric answers; some metrics assume a "single right answer" when queries are open-ended. Senior nuance: pair RAGAS with a small labeled set to ground the LLM judge and detect drift. Newer tools (DeepEval, Arize Phoenix, TruLens) extend RAGAS with traces, hallucination detection, and pairwise tests.

</details>

**Follow-ups:** How do you calibrate the judge? When does RAGAS mislead?

**Difficulty:** Mid

### 28. Retrieval over structured data: tables, code, JSON

> "When you have structured knowledge (tables, code, JSON schemas, SQL), is a vanilla RAG stack with BM25 or dense retriever enough?"

**Where asked:** Reported at OpenAI (jobright Dec 24 2025), Snowflake ML (aiofferly Jan 22 2026), Databricks ML (aiofferly Jan 21 2026) · [source](https://www.aiofferly.com/career-guide/snowflake-ml-interview-questions)

**What they're testing:** Awareness of specialized retrievers and metadata filtering.

<details>
<summary>💡 Strong answer</summary>

Vanilla dense retrievers over chunked text can find conceptually similar tables or code, but they're weak on exact identifiers (column names, function signatures, JSON keys) and structural relationships. For structured data, you typically want: (1) metadata filtering: prepend chunk metadata (table name, column type, endpoint) and pre-filter with WHERE clauses before embedding search; (2) BM25 over symbol names + comments (great precision on code); (3) hybrid; (4) cross-modal encoders trained on table-text pairs; (5) structured-output retrievers that emit SQL/SPARQL directly. For tables specifically, "TableRAG" patterns (column-level chunking, schema-aware embeddings) consistently beat naive chunking. Senior nuance: real production systems usually layer these: column metadata filter -> BM25 over header text -> dense over cell text -> cross-encoder rerank. For Snowflake/Databricks stacks you often lean on Cortex Search / Databricks Vector Search which handle these for you.

</details>

**Follow-ups:** What is schema-linking in text-to-SQL?

**Difficulty:** Senior

---

## Agents

### 29. What is an AI agent vs a prompt vs a chain?

> "What is an AI agent? What is the 'Agentic Ops' problem?"

**Where asked:** Reported at Anthropic (jobright Dec 18 2025), Multi-On, LangChain (aemonline Oct 11 2025) · [source](https://pub.towardsai.net/101-ml-llm-agentic-aiops-interview-questions-31a346ac84d3)

**What they're testing:** Working definition clarity vs buzzword fluency.

<details>
<summary>💡 Strong answer</summary>

An AI agent is an LLM-driven system that can perceive, plan, and act in an environment over multiple steps, often using external tools, with persistent state. It differs from: (1) a prompt: one-shot generation with no feedback loop; (2) a chain: a static sequence of LLM calls without dynamic decision-making. The agent pattern has a planner (often the LLM itself in ReAct style), memory (short-term scratchpad + long-term store), tools (functions/APIs the agent can call), and a control loop (decide -> act -> observe -> repeat). "Agentic Ops" refers to monitoring, evaluating, and debugging agents in production, which is much harder than chat because actions can have side effects.

</details>

**Follow-ups:** What are common failure modes of agents in production?

**Difficulty:** Junior - Mid

### 30. The ReAct framework

> "What is the ReAct framework, and why is it important for Agentic AI?"

**Where asked:** Reported at Multi-On, Anthropic MLE (jobright Dec 18 2025), LangChain · [source](https://aemonline.net/blog/top-25-agentic-ai-interview-questions-with-answer-for-2026/)

**What they're testing:** Whether you understand interleaved reasoning + acting.

<details>
<summary>💡 Strong answer</summary>

ReAct (Yao et al., 2022) interleaves Thought -> Action -> Observation steps: the agent produces a reasoning trace, takes an action (tool call), observes the result, and continues until it's ready to answer. Two advantages over pure CoT prompting: (1) actions let the agent pull fresh external information (search, APIs, code exec), grounding reasoning in real data; (2) each step's observation forces the next reasoning to be re-anchored to evidence rather than wandering. In production it has been superseded by structured tool-calling: a JSON-emitting model with typed tool schemas, which is more reliable than free-text action strings but trades off ReAct's inspectability. Senior nuance: function-calling ReAct also enables parallel tool calls, conditional tool selection, and post-tool reasoning verification. Many 2025-2026 agents use ReAct for the "think loop" but with tool-calling JSON instead of free-text actions.

</details>

**Follow-ups:** ReAct vs function-calling? When does pure planning beat step-by-step?

**Difficulty:** Mid

### 31. Planning and decomposition in multi-step agent tasks

> "How do you handle planning and decomposition in multi-step tasks for an AI agent?"

**Where asked:** Reported at Anthropic (jobright Dec 18 2025), Multi-On (aemonline), DeepMind MLE · [source](https://aemonline.net/blog/top-25-agentic-ai-interview-questions-with-answer-for-2026/)

**What they're testing:** Whether you can break a vague goal into verifiable subtasks.

<details>
<summary>💡 Strong answer</summary>

Two main approaches: (1) one-shot plan: have the LLM produce a full DAG of subtasks upfront, then execute (good for known-shaped tasks, brittle if assumptions break); (2) iterative re-plan: execute one subtask, observe result, re-plan based on what you learned (more robust but slower). Common techniques: least-to-most prompting (decompose from abstract to concrete subquestions), tree-of-thoughts (branch and evaluate multiple plans), self-consistency (sample N plans, take majority), "plan-and-execute" loops where a planner LLM refines a plan as observations come in. Senior nuance: in 2026 production, isolated step-by-step monolith agents are giving way to (a) graph-of-thought DAG executors (LangGraph) and (b) constraint-checking plans: plans that include assertions ("if A fails, retry with strategy B").

</details>

**Follow-ups:** How would you evaluate plan quality? When does one-shot planning beat iterative?

**Difficulty:** Senior

### 32. Tools in agentic AI and how agents pick them

> "What are 'tools' in the context of Agentic AI? How does the agent decide which to use?"

**Where asked:** Reported at Anthropic (jobright Dec 18 2025), OpenAI MLE (jobright Dec 24 2025) · [source](https://aemonline.net/blog/top-25-agentic-ai-interview-questions-with-answer-for-2026/)

**What they're testing:** Working knowledge of tool-use interfaces and selection.

<details>
<summary>💡 Strong answer</summary>

Tools are typed functions the agent can invoke: search_web, query_database, send_email, run_code, etc., each with a JSON schema describing inputs/outputs. The agent's policy decides which tool to call: by default, the LLM itself emits a tool_call field tuned during fine-tuning or via prompt scaffolding (system prompt listing tools and rules). Better agents also use: (1) explicit selector prompts ("given the user's request and the available tools, output a JSON plan"); (2) search-style planners that retrieve tools by semantic similarity to the user's need; (3) constrained decoding (JSON-schema guided generation) to guarantee well-formed calls. Selection quality depends on (a) tool description clarity, (b) tool routing logic, (c) error feedback. Senior nuance: parallel tool calls (multiple tools in one step) are common for "gather information" substeps, but require careful deduplication.

</details>

**Follow-ups:** What is semantic tool retrieval? How do you debug wrong tool calls?

**Difficulty:** Junior - Mid

### 33. Multi-agent orchestration: when does it help?

> "Can you explain the concept of 'Multi-Agent Systems' and their advantages?"

**Where asked:** Reported at Multi-On, Anthropic MLE, AutoGen collaborators · [source](https://aemonline.net/blog/top-25-agentic-ai-interview-questions-with-answer-for-2026/)

**What they're testing:** Tradeoffs of single-agent vs multi-agent.

<details>
<summary>💡 Strong answer</summary>

Multi-agent systems split work across specialized roles (planner agent, researcher agent, coder agent, critic agent), each with its own prompt, memory, and tools, coordinated by a supervisor or message bus. Advantages: (1) separation of concerns: clearer prompts; (2) parallelism: independent subtasks run concurrently; (3) self-critique: a critic agent can review another agent's work. Disadvantages: (1) communication overhead; (2) compounded errors: if the supervisor misunderstands, all subagents suffer; (3) resource cost: 2-5x more LLM calls. Empirically (2024-2026), multi-agent helps in coding workflows (Coder + Tester + Reviewer competition) and deep research (Planner + Searcher + Synthesizer). For simple workflows it adds latency and risk without quality. Senior rule: prefer single agent with good tools; reach for multi-agent when (a) tasks need distinct role expertise, or (b) when self-critique materially improves output.

</details>

**Follow-ups:** How do you design a supervisor agent's protocol?

**Difficulty:** Senior

### 34. How do you evaluate an agent?

> "How do you evaluate an agent? What evaluation metrics make sense?"

**Where asked:** Reported at Anthropic MLE (aiofferly Dec 3 2025), OpenAI MLE (jobright Dec 24 2025), Multi-On, LangChain · [source](https://www.aiofferly.com/career-guide/anthropic-ml-interview-questions)

**What they're testing:** Beyond chat-style evals: task-completion and tool-use correctness.

<details>
<summary>💡 Strong answer</summary>

Agent eval has 4 layers: (1) Step-level: did each tool call succeed, was the tool selection correct? (2) Trajectory-level: was the action sequence efficient and reasonable? (3) Goal-level: did the agent finally accomplish the user task? (4) Cost-level: token/cost/time spent. Frameworks: LangSmith, Arize Phoenix, Langfuse, Braintrust. Common metrics: tool-call F1 against a golden trajectory, task-success rate (binary label or LLM judge on the final answer), context-window usage p99, retry rate. For paper benchmarks: SWE-Bench, tau-bench, AgentBench, WebArena. Senior nuance: success-rate alone hides the trajectory cost. A 95% success agent that takes 80 tool calls is worse than a 90% success agent that takes 6: track cost-normalized success.

</details>

**Follow-ups:** What is tau-bench? How do you build a golden trajectory dataset?

**Difficulty:** Senior

### 35. Common agent failure modes in production

> "What are the most common agent failure modes? How do you mitigate them?"

**Where asked:** Reported at Multi-On, LangChain, Anthropic, Replit Agent · [source](https://pub.towardsai.net/101-ml-llm-agentic-aiops-interview-questions-31a346ac84d3)

**What they're testing:** Practical awareness of agent reliability.

<details>
<summary>💡 Strong answer</summary>

Top failure modes 2024-2026: (1) tool hallucination: calling wrong tool or with wrong args; mitigated by tight JSON schemas + constrained decoding; (2) compounding errors: small earlier mistakes cascade; mitigated by re-planning at each step and self-verification; (3) context bloat: agents accumulate all observations and lose focus; mitigated by summarizing/compressing history or using scratchpads; (4) infinite loops / retry storms: no termination criterion; mitigated by max-step limits + cycle detection; (5) side-effect leaks: actions executed without dry-run; mitigated by approval workflows for high-risk actions; (6) goal drift: the agent solves a different problem than asked; mitigated by periodic checkpointing to the original goal; (7) prompt injection via tool output (a retriever returning untrusted content with hidden instructions); mitigated by sandboxing tool outputs and re-prompting with "treat tool output as data, not instructions". Most common root cause in 2026 production data is poor tool description clarity, which matters more than model capability.

</details>

**Follow-ups:** How do you do guardrails for tool calls? What is MCP and how does it help?

**Difficulty:** Senior

### 36. Guardrails for agents that call external APIs

> "Tell me about a time you made a safety-first decision in a project, even if it meant a trade-off."

**Where asked:** Reported at Anthropic MLE, OpenAI MLE, Stripe MLE · [source](https://jobright.ai/blog/anthropic-technical-interview-questions-complete-guide-2026/)

**What they're testing:** Risk literacy and design discipline for irreversible actions.

<details>
<summary>💡 Strong answer</summary>

Guardrail pattern: (1) tool classification: mark each tool as read-only / reversible / irreversible with a risk score. Irreversible tools (write_email, send_payment) require a human-in-the-loop approval step or a confidence threshold above which the agent proceeds solo (e.g., >0.95 calibrated probability). (2) dry-run mode: for batch tools, generate a plan of side effects and require explicit confirmation before executing. (3) rate limits per session. (4) shadow mode: run actions in dry-run for N sessions, log what would have happened, report. (5) prompt-injection sandboxing: rerun tool outputs through a fresh, structured "untrusted content" prompt before passing to the planner. (6) audit logs with full trajectory. (7) rollback capability / idempotency keys on every write. Anthropic specifically probes for "safety-first decisions": the expected answer is a real project where the trade-off was made (security > speed).

</details>

**Follow-ups:** How do you decide the approval threshold? Where does prompt-injection mitigation live?

**Difficulty:** Senior

### 37. Agent memory: short-term vs long-term

> "When discussing agents, what kinds of memory exist and how would you architect them?"

**Where asked:** Reported at Multi-On, Anthropic, Personal.ai (aemonline Oct 2025) · [source](https://aemonline.net/blog/top-25-agentic-ai-interview-questions-with-answer-for-2026/)

**What they're testing:** Mental taxonomy of agent memory.

<details>
<summary>💡 Strong answer</summary>

Three layers: (1) short-term / working memory: the LLM context window holding recent observations, scratchpad, and the current task plan; volatile; resets per session; managed by compaction/summarization as it fills. (2) long-term / semantic memory: a structured store of facts about the user, prior tasks, world knowledge, indexed by entity and topic; often a vector store + structured (SQL/JSON). (3) episodic memory: timestamped records of past episodes the agent can recall to learn from experience (auto-summarized). Memory also implies write policies: what the agent is allowed to remember about the user (privacy / consent), and conflict resolution when new info contradicts old. Senior nuance: long-term memory is the differentiator between toy demos and persistent assistants, and the architecture is typically a vector store + metadata filter + periodic compaction. MemGPT and Letta (formerly MemGPT) formalized these layers in 2024-2025.

</details>

**Follow-ups:** How do you handle stale memories? What is MemGPT?

**Difficulty:** Senior

### 38. Model Context Protocol (MCP)

> "Explain MCP and how it changes tool-use."

**Where asked:** Reported at Anthropic MLE (jobright Dec 18 2025; aiofferly Dec 3 2025), Multi-On (aemonline) · [source](https://jobright.ai/blog/anthropic-technical-interview-questions-complete-guide-2026/)

**What they're testing:** Whether you know the current state-of-the-art agent-tooling standard.

<details>
<summary>💡 Strong answer</summary>

MCP (Model Context Protocol, Anthropic 2024) is a standardized client-server protocol for exposing tools, resources, and prompts to an LLM agent. Each MCP server implements a small JSON-RPC interface: list_tools, call_tool, list_resources, read_resource. Agents that speak MCP can dynamically discover available capabilities from any MCP-compliant server (filesystem, GitHub, Postgres, Slack, etc.) without hand-coded integrations. Benefits: (1) plug-and-play tool ecosystem; (2) single security boundary (just audit your MCP servers); (3) cross-vendor: the same MCP server works against Claude, GPT, Gemini clients. Trade-offs: statelessness forces tool calls across the wire, latency-sensitive workflows may prefer in-process function calls; the spec is still evolving (e.g., sampling, elicitation). Senior view: MCP is becoming the de-facto agent integration standard by mid-2026.

</details>

**Follow-ups:** How does MCP compare to OpenAI's function-calling schema?

**Difficulty:** Mid - Senior

---

## Evals & Observability

### 39. LLM-as-judge: when it works, when it fails

> "How do you use LLMs to judge other LLMs? What are its failure modes?"

**Where asked:** Reported at Anthropic MLE (aiofferly Dec 3 2025), OpenAI MLE (jobright Dec 24 2025), Databricks ML (aiofferly Jan 21 2026) · [source](https://www.reddit.com/r/LLMDevs/comments/1kealia/llmasajudge_is_not_enough_thats_the_quiet_truth/)

**What they're testing:** Awareness of judge reliability, bias, and calibration.

<details>
<summary>💡 Strong answer</summary>

LLM-as-judge uses a (usually stronger) LLM to score, classify, or compare outputs of another LLM. Three modes: (1) pointwise: judge a single answer on a rubric; (2) pairwise: judge "A vs B" which is better; (3) reference-based: judge against a gold answer. Practical recipes: structured rubrics (CoT scoring prompts, criteria-based chains), use a stronger model than the candidate, calibrate against a human-labeled set. Failure modes: (1) position bias: "A vs B" output depends on order; mitigate by averaging both orderings; (2) length bias: longer answers judged better; (3) self-preference: judge favors its own style; (4) format bias; (5) rubric-blind evaluation: LLM judges miss domain-specific errors a human expert catches. Senior view: LLM-as-judge is reliable for ~70-85% of cases but ALWAYS needs human spot-audits for high-stakes claims. Pairwise comparison with win-rate is the most stable metric for online A/B testing.

</details>

**Follow-ups:** How do you correct for bias? When do you NEED human eval?

**Difficulty:** Senior

### 40. LLM observability vs classical ML observability

> "How do you monitor and debug an LLM system in production?"

**Where asked:** Reported at OpenAI MLE (jobright Dec 24 2025), Databricks ML (aiofferly Jan 21 2026), enterprise AI shops · [source](https://skphd.medium.com/large-language-model-operations-llmops-interview-questions-and-answers-43786c859a95)

**What they're testing:** Practical observability design ability.

<details>
<summary>💡 Strong answer</summary>

LLM observability requires: (1) full trajectory logs: prompt, retrieved context, model version, raw output, tool calls, cost, latency, user feedback; (2) eval pipelines running on sampled production data; (3) drift detection: both input drift (embedding-based topic shifts) and output drift (semantic embedding of responses, LLM-judge scores over time); (4) regression testing on a frozen task bank before every model or prompt change; (5) user feedback collection (thumbs, edits, follow-ups). Unlike classical ML observability: (a) outputs are open-ended (no fixed label schema); (b) the system is non-deterministic: sampling temperature matters; (c) prompts change frequently and silently drift; (d) "failures" are nuanced (hallucinations, factual errors, refraining too much) and not label-able as binary. Senior view: track cost-per-task not per-call, alert on both eval metric degradation and traffic shifts.

</details>

**Follow-ups:** What tools should you use? Arize Phoenix / Langfuse / Braintrust vs roll-your-own?

**Difficulty:** Senior

### 41. Regression testing before model/prompt changes ship

> "How do you make LLM/agent behavior measurable and regressions debuggable?"

**Where asked:** Reported at Databricks MLE (aiofferly Jan 21 2026), OpenAI MLE · [source](https://www.aiofferly.com/career-guide/databricks-ml-interview-questions)

**What they're testing:** CI/CD for LLM systems awareness.

<details>
<summary>💡 Strong answer</summary>

Build a frozen eval set of 200-2000 representative tasks with ground-truth labels (human or LLM-curated). Before each model/prompt/RAG corpus change ships, run all tasks through the candidate system, compute (1) automated metrics (RAGAS-style faithfulness, answer-relevance, task success rate); (2) LLM-as-judge pairwise comparison against the previous version; (3) cost/latency regression checks. Maintain a canary set: ~50 high-stakes queries you monitor even harder. Store results in CI with pass/fail thresholds per metric. Senior nuance: regression test suites must be diverse enough to catch subtle regressions: "5 hand-written queries" is worse than useless (overfits to individual prompt phrasings). Real practice: maintain a rolling 5000-query set that mixes gold labels with paired A/B trajectories.

</details>

**Follow-ups:** How big should the eval set be? What metric thresholds trigger rollback?

**Difficulty:** Senior

### 42. Designing LLM benchmarks: MMLU, GSM8K, HELM

> "What benchmarks should one use to evaluate LLMs and why?"

**Where asked:** Reported at frontier labs: Anthropic, OpenAI, DeepMind, Mistral MLE · [source](https://pub.towardsai.net/101-ml-llm-agentic-aiops-interview-questions-31a346ac84d3)

**What they're testing:** Whether you can critique and choose benchmarks, not just list them.

<details>
<summary>💡 Strong answer</summary>

MMLU: 57 multi-domain academic knowledge tests, multi-choice, measures capability breadth, but criticized for contamination, narrow formatting bias, and the "all you need is one correct answer" assumption. GSM8K: grade-school math word problems, classic reasoning benchmark, paired with chain-of-thought evaluation; complementary to MMLU because it tests coherence over knowledge. HELM (Stanford, Liang et al. 2022): holistic evaluation across many axes (accuracy, calibration, robustness, bias, fairness, efficiency), the correct citation when an interviewer wants you to argue for multi-axis measurement. Senior view: as of 2026, harder reasoning benchmarks (SWE-Bench, tau-bench, FrontierMath, GPQA Diamond) and human-preference-based ones (Chatbot Arena Elo) have eclipsed MMLU as the "real" signal. Newer "contamination-resistant" benchmarks use held-out questions, dynamical generation, or human spot-audits.

</details>

**Follow-ups:** What is contamination in benchmarks? How do you track real-world LLM quality?

**Difficulty:** Senior

### 43. Detecting distribution shift in production LLM traffic

> "How would you monitor for input distribution shift in an LLM app?"

**Where asked:** Reported at AI Ops companies, large enterprise AI shops · [source](https://pub.towardsai.net/101-ml-llm-agentic-aiops-interview-questions-31a346ac84d3)

**What they're testing:** Eyes-on production systems awareness.

<details>
<summary>💡 Strong answer</summary>

Three layers: (1) embedding-based topic shift: sample incoming queries, embed, cluster, compare cluster distribution over rolling window (e.g., 1 day vs 7 days); alert when top-K cluster centroids move > X distance. (2) lexical shift: watch token distribution, language mix, average length, special-character ratio for prompt injection markers. (3) judge metric drift: sample 1% of outputs, run LLM-as-judge, alert when judge scores fall > Y or variance grows. Tools: Arize Phoenix, whylogs, Evidently, custom Prometheus dashboards. Senior nuance: input drift often precedes model-quality degradation by days: early warning reduces incidents. Beware of false positives during scheduled feature changes (e.g., new UI fields).

</details>

**Follow-ups:** When does drift NOT indicate a real change? What is adversarial drift?

**Difficulty:** Senior

### 44. Measuring hallucination rate without expensive human eval

> "How do you measure and monitor hallucination?"

**Where asked:** Reported at OpenAI, Anthropic, Cohere · [source](https://www.pass4sure.com/blog/top-30-rag-interview-questions-and-answers-for-2025/)

**What they're testing:** Familiarity with concrete metric designs.

<details>
<summary>💡 Strong answer</summary>

Hallucination rate is the fraction of outputs that contain content not supported by ground truth (or context, in RAG). Measurement options from cheap to expensive: (1) LLM-as-judge with claim decomposition: split answer into atomic claims, judge each against context; high agreement with humans but judge-bias. (2) Self-consistency: sample N answers, measure inter-sample semantic disagreement; unreliable for factual claims. (3) Reference-based: if you have a gold answer, judge each claim against the gold. (4) Human eval: gold standard, expensive, sampled 1-5%. Tooling: DeepEval's HallucinationMetric, Patronus Lynx, Vectara HHEM leaderboard. Senior view: hallucination rate without a defined ground truth is meaningless: always pair with a labeled validation set to calibrate the metric.

</details>

**Follow-ups:** How big does your eval set need to be to trust a 1% improvement?

**Difficulty:** Senior

### 45. A/B testing LLM products

> "How would you A/B test two prompts or two models in production?"

**Where asked:** Reported at frontier labs, scale-ups, enterprises · [source](https://aemonline.net/blog/top-25-agentic-ai-interview-questions-with-answer-for-2026/)

**What they're testing:** Rigorous experimentation skill.

<details>
<summary>💡 Strong answer</summary>

Best practice 2025-2026: (1) interleaved A/B testing: randomly assign user requests to candidate A or B but interleave to control for time-of-day effects; (2) primary metric: task success rate (binary label, LLM-judge calibrated against humans) or user thumbs/retention if available; (3) guardrail metrics: latency p99, hallucination rate, refusal rate, cost-per-task. Stop after pre-set sample size (don't peek). For subjective quality without binary labels: pairwise comparison via LLM judge; measure win-rate with statistical confidence intervals. Senior view: power analysis for win-rate is tricky: small absolute differences (e.g., 51% vs 49%) require tens of thousands of comparisons to call. Always run interleaved, never switch all-at-once: you cannot disentangle "model change" from "user adaptation".

</details>

**Follow-ups:** How do you handle long-tail / power-user segments?

**Difficulty:** Senior

### 46. Evaluating reasoning models vs chat models

> "Reasoning models behave differently in eval - how do you adjust your methodology?"

**Where asked:** Reported at Anthropic MLE (aiofferly Dec 3 2025), OpenAI MLE · [source](https://www.aiofferly.com/career-guide/anthropic-ml-interview-questions)

**What they're testing:** Whether you can generalize eval methodology.

<details>
<summary>💡 Strong answer</summary>

Reasoning models (o1, o3, DeepSeek-R1) generate internal chain-of-thought tokens then a summary. Three eval differences: (1) latency/cost asymmetric: reasoning models are 10-30x more expensive and slow; normalize by "task cost" not "answer correctness". (2) Output semantics: the visible answer is much shorter than the work behind it; metrics like "verbosity" lose meaning. (3) Some metrics (exact-match GSM8K) inflate because the model has more compute to find the right answer; passive benchmarks become saturated. Senior recipe: (a) use held-out reasoning-specific benchmarks (MATH, FrontierMath, GPQA Diamond, AIME) for capability comparison; (b) re-evaluate with cost-normalized success rate; (c) add reasoning-trace analyses (model's CoT sampled and judged for logical consistency); (d) monitor for overconfidence: reasoning models fail silently when they hallucinate a wrong intermediate.

</details>

**Follow-ups:** What is the "reasoning tax"? When does CoT reasoning hurt?

**Difficulty:** Senior

---

## Inference & Serving

### 47. Speculative decoding: when it helps, when it fails

> "Explain speculative decoding. Under what conditions does it speed up inference?"

**Where asked:** Reported at frontier-lab inference teams: OpenAI, Anthropic, DeepMind, Cohere · [source](https://www.reddit.com/r/LLMDevs/comments/1r5vona/interview_experience_for_llm_inference_systems/)

**What they're testing:** Inference-system depth beyond surface-level descriptions.

<details>
<summary>💡 Strong answer</summary>

Speculative decoding uses a small "draft" model to generate K candidate tokens autoregressively, then the large "target" model scores them in a single forward pass. Tokens that match the target's argmax (or sampled with the adjusted distribution) are accepted; the first mismatch triggers a re-sample using the target's distribution. Effective when: (1) batch size is small (single or few concurrent requests): decoding is memory-bandwidth-bound and a draft model is cheaper to query; (2) draft acceptance rate is high (>60-70%): target and draft distributions must be close. Fails when: (1) batch size is large (~64+): the GPU is already compute-bound, and speculation adds overhead without throughput wins; (2) draft/target acceptance is low (e.g., domains where draft underperforms target): the wasted speculation costs more than it saves. Senior nuance: production systems using speculative decoding see small-batch latency wins of ~1.5-2.5x but large-batch throughput unchanged. This is the "Speculative Decoding Illusion" many candidates miss.

</details>

**Follow-ups:** What's a good draft model? How does Medusa / EAGLE / look-ahead decoding differ?

**Difficulty:** Senior

### 48. Dynamic batching strategies for LLM inference

> "Dynamic Batching Strategies: LLM inference is iterative and can benefit greatly from batching multiple requests together. How would you design batching policies?"

**Where asked:** Reported at multiple AI labs and inference startups (Anyscale, vLLM, OpenAI) · [source](https://www.reddit.com/r/LLMDevs/comments/1r5vona/interview_experience_for_llm_inference_systems/)

**What they're testing:** Production-serving literacy.

<details>
<summary>💡 Strong answer</summary>

LLM decoding is iterative (token-by-token) and requests share structure: they all run the same model, just with different contexts. Static batching wastes GPU on padding. Dynamic (in-flight) batching: each decode step, walk the queue of active requests, batch together the sequences that have not finished, run a GPU forward pass on the union. Continuous (in-flight) batching further refines: completed sequences can exit the batch mid-step and new ones can join. Stall-free batching (e.g., vLLM's iteration-level scheduling) avoids head-of-line blocking by separating prefill (compute-bound) and decode (memory-bound): new requests' prefill chunks can interleave with ongoing decodes. Senior nuance: prefill is latency-sensitive (TTFT: time to first token), decode needs steady TPOT (time per output token); the right scheduler balances both. FairBatching-style work prevents large requests from monopolizing the GPU.

</details>

**Follow-ups:** Explain TTFT vs TPOT tradeoff.

**Difficulty:** Senior

### 49. Quantization: INT8, INT4, FP8, AWQ, GPTQ

> "When would you pick INT8 vs GPTQ vs AWQ vs FP8 for serving an LLM?"

**Where asked:** Reported at multiple AI labs and inference startups (r/LocalLLaMA, 2025) · [source](https://www.reddit.com/r/LocalLLaMA/comments/1lq9eg5/speculative_decoding_and_quantization_im_probably/)

**What they're testing:** Awareness of quantization precision/quality/memory tradeoffs.

<details>
<summary>💡 Strong answer</summary>

PTQ (post-training quantization) trades memory and latency for some accuracy loss. Quantization levels: FP16/FP32 (training precision), INT8 weights + FP16 compute (SmoothQuant, LLM.int8()), INT4 weights + group-wise scaling (GPTQ, AWQ), FP8 weights (Hopper native FP8). Picking one: (1) AWQ / GPTQ (INT4): aggressive memory savings (~4x), small quality loss, popular for self-hosted 70B-class models. (2) INT8 (SmoothQuant, LLM.int8()): safer quality, 2x memory savings. (3) FP8: native on H100, near-zero accuracy loss, faster than INT8 on Hopper. (4) INT4 + QLoRA-style tricks: finetuning on quantized base. Memory math decides: a 70B model fp16 = 140 GB, INT8 = 70 GB, INT4 = 35 GB, FP8 = 70 GB. Senior nuance: KV cache quantization (FP8 KV) is orthogonal: 2-4x memory savings on cache without quantizing weights. Quality tests are essential at each level because outliers vary per model.

</details>

**Follow-ups:** Why do some layers resist quantization? What is QAT vs PTQ?

**Difficulty:** Senior

### 50. Paged attention (vLLM)

> "What is vLLM's paged attention, and how does it improve serving throughput?"

**Where asked:** Reported at scale-ups, AI labs MLE (r/MachineLearning inference threads) · [source](https://www.reddit.com/r/MachineLearning/comments/1r5vncj/d_interview_experience_for_llm_inference_systems/)

**What they're testing:** Production-serving depth.

<details>
<summary>💡 Strong answer</summary>

Paged attention (Kwon et al., SOSP 2023) borrows virtual-memory paging for KV cache. Traditional KV cache allocates one contiguous block per sequence: heavy fragmentation wastes memory. Paged attention stores the KV cache in fixed-size "pages" (e.g., 16 tokens per page), indexed by a per-sequence page table. Memory is allocated only as needed and pages are reused across sequences when possible. Empirically this gives 2-4x throughput over naive static allocation (HuggingFace transformers) and 14-24x over FasterTransformer in multi-tenant serving. vLLM is the open-source implementation. Senior nuance: paged attention unlocks continuous batching, prefix-sharing across requests, beam-search efficient caching, and serves as the foundation for modern LLM serving alongside SGLang, TGI, TensorRT-LLM.

</details>

**Follow-ups:** What is prefix sharing? How do beam search and paged attention interact?

**Difficulty:** Senior

### 51. Latency vs throughput vs cost: choosing batch sizes

> "How would you evaluate the latency-throughput sweet spot and adjust the system as load patterns change?"

**Where asked:** Reported at frontier labs, inference startups (Anyscale, vLLM, Together) · [source](https://www.reddit.com/r/LLMDevs/comments/1r5vona/interview_experience_for_llm_inference_systems/)

**What they're testing:** Real-world serving economics reasoning.

<details>
<summary>💡 Strong answer</summary>

Three objectives are typically in tension: (1) p50/p99 latency (TTFT + TPOT) for user-facing apps; (2) throughput (tokens/sec across all users); (3) cost ($/M tokens served). As batch size increases, throughput rises (better GPU utilization), but per-request latency also rises (each step takes longer for everyone). The right batch is where the marginal latency cost equals the marginal throughput benefit: typically mid-load for chat apps, maxed-out for batch processing. For the LLM-specific tradeoff: chat has strict TTFT (<300ms ideal) and TPOT (<50ms ideal); one can saturate decode memory bandwidth at batch >= 8 typically. Cost models: input tokens are 5-10x cheaper than output tokens (because prefill is amortized), so prompt caching is huge. Senior nuance: continuous batching + speculative decoding + quantization is the modern serving stack: each gives ~2x wins and the combination is ~5-10x.

</details>

**Follow-ups:** When do you prioritize latency over throughput? How does prompt caching factor in?

**Difficulty:** Senior

### 52. Scaling LLM inference for traffic spikes

> "How do you provision LLM serving infrastructure for variable demand?"

**Where asked:** Reported at frontier labs, scale-ups · [source](https://aemonline.net/blog/top-25-agentic-ai-interview-questions-with-answer-for-2026/)

**What they're testing:** Operational excellence awareness.

<details>
<summary>💡 Strong answer</summary>

Strategy stack 2025-2026: (1) autoscaling GPU pools (Kubernetes + custom metrics); (2) request batching and queueing: absorb spikes with throttle/defer queues; (3) prompt caching: identical system prompts become one cached prefix, massive TTFT and cost wins; (4) tiered model routing: small/cheap model for easy queries, large model only when the small one is uncertain; (5) KV cache reuse across turns of the same conversation; (6) speculative prefill: start generating the next response while the model still finishes the previous one (pipelining). Senior nuance: smooth overload via graceful degradation is better than sharp 503s: cap concurrent decodes per user, prioritize short responses when latency budget is tight.

</details>

**Follow-ups:** How do you measure SLI / SLO for an LLM app?

**Difficulty:** Senior

### 53. FlashAttention and why it matters

> "Explain FlashAttention. Why is it the backbone of modern LLM training and serving?"

**Where asked:** Reported at frontier labs, PhD-level MLE, and inference systems roles (datainterview 2026; r/MachineLearning inference threads) · [source](https://www.datainterview.com/blog/llms-and-transformers-interview-questions)

**What they're testing:** Memory-compute tradeoff literacy.

<details>
<summary>💡 Strong answer</summary>

FlashAttention (Dao et al., 2022; v2 in 2023; v3 in 2024) is an IO-aware exact attention algorithm that reorders the attention computation to operate on tiles of Q,K,V that fit in on-chip SRAM, then accumulates softmax statistics without materializing the full N x N attention matrix in HBM. Two big wins: (1) memory drops from O(N^2) to O(N), enabling 100k+ context windows; (2) speedups of 2-4x because HBM bandwidth is the dominant cost in attention. FlashAttention-2 improves parallelism and work partitioning; FlashAttention-3 (Hopper) uses async warp-specialization and FP8 to reach ~2x v2. Senior nuance: FlashAttention enabled practical long-context training but it is an "exact" implementation: approximate attention (Sparse, Linear) sometimes beats it for million-token contexts.

</details>

**Follow-ups:** What is FlashDecoding? How does paged attention compose with FlashAttention?

**Difficulty:** Senior

### 54. Prompt caching and KV cache prefix sharing

> "How do you cut prompt-token cost in production?"

**Where asked:** Reported at frontier labs and scale-ups (jobright OpenAI; r/MachineLearning) · [source](https://jobright.ai/blog/openai-technical-interview-questions-2026-and-how-to-answer/)

**What they're testing:** Cost optimization intuition.

<details>
<summary>💡 Strong answer</summary>

Many production prompts have large static prefixes (system prompt, tool definitions, retrieved context, persona instructions). If two requests share the first N tokens of the prompt, KV computations for those tokens are identical and need to be done only once. Prompt caching stores the KV cache of a prefix so subsequent matching requests reuse it. Implementations: OpenAI prompt caching (auto-prefix-match), vLLM automatic prefix caching (APC), SGLang RadixAttention (more aggressive). Cost math: a 5000-token system prompt at $1/1M input tokens = $0.005 per request if uncached, vs ~$0 reused if cached. For an app with stable system prompts, this is a 50-90% cost reduction. Senior nuance: only prefix-EXACT matches cache; usually resolve this by routing same system-prompt apps through the same instance and standardizing prompt format.

</details>

**Follow-ups:** How does it interact with retrieval updates? What about RadixAttention?

**Difficulty:** Senior

---

## Classic ML Breadth

### 55. Bias-variance tradeoff: practical rules of thumb

> "Summarize practical rules of thumb an ML engineer can follow when deciding whether an observed generalization gap is primarily due to model bias or model variance. Include specific metric thresholds, experiment types, and quick tests that can be run under time pressure."

**Where asked:** Reported at multiple FAANG / Google / Meta / Amazon ML Engineer (r/FAANGinterviewprep, Nov 2025) · [source](https://www.reddit.com/r/FAANGinterviewprep/comments/1q752rn/faang_machine_learning_engineer_interview/)

**What they're testing:** Diagnostic depth, not just textbook definition.

<details>
<summary>💡 Strong answer</summary>

Bias is error from wrong assumptions (underfitting); variance is sensitivity to training-data fluctuations (overfitting). Total expected error = bias^2 + variance + irreducible noise. Practical rules of thumb: train-eval gap <1% = high bias; >5% = high variance. If high bias: bigger model, better features, more layers, longer training, less regularization. If high variance: more data, stronger regularization, dropout, shorter training, ensemble (bagging), data augmentation. Senior nuance on real production models: deep nets without enough data exhibit high variance; classical models (linear, GBMs) exhibit high bias. Quick diagnostic: train on 10% of data; if train error spikes, the model is probably data-limited (variance); if it stays low, you have capacity but bad features (bias). Ensemble methods like bagging reduce variance; boosting reduces bias.

</details>

**Follow-ups:** How does ensemble learning relate? Why does early stopping reduce variance?

**Difficulty:** Mid - Senior

### 56. L1 vs L2 regularization

> "When should you use L1 vs L2 regularization? Walk through Ridge vs Lasso."

**Where asked:** Reported at FAANG and AI companies 2024-2026 (r/FAANGinterviewprep; Medium adilshamim 65 ML; Towards AI Dec 28 2025) · [source](https://pub.towardsai.net/top-20-regularization-interview-questions-and-answers-e3ad61560d94)

**What they're testing:** Geometric / sparsity intuition.

<details>
<summary>💡 Strong answer</summary>

L2 (weight decay) adds a quadratic penalty on weights: lambda * sum(w^2). It shrinks weights smoothly toward zero, encouraging small-but-nonzero values. L1 adds an absolute-value penalty: lambda * sum(|w|). Because the L1 constraint region is a diamond (corners on axes), the optimum hits corners more often, shrinking some weights to exactly zero, producing sparsity, i.e., feature selection. Elastic Net combines both. When to pick: L2 if all features likely useful (deep nets, dense tabular); L1 if you want built-in feature selection (high-dim, low-signal feature spaces like text bag-of-words, genetics); ElasticNet when you want both shrinkage and selection. Senior nuance: modern deep net regularization (dropout, weight decay, label smoothing, MixUp) often outperforms strict L1/L2 in practice.

</details>

**Follow-ups:** What is weight decay vs L2 reg in Adam? Why doesn't L1 work well in NN training?

**Difficulty:** Junior - Mid

### 57. Precision vs recall vs F1 vs AUC

> "Distinguish precision, recall, F1, ROC-AUC, PR-AUC. When does each shape a decision?"

**Where asked:** Reported at FAANG, AI startups (r/MachineLearning prep threads; Towards AI; Medium adilshamim 65 ML Qs 2025) · [source](https://adilshamim8.medium.com/65-machine-learning-interview-questions-2025-2fde3a358dc9)

**What they're testing:** Choice of metric vs cost asymmetry.

<details>
<summary>💡 Strong answer</summary>

Precision = TP/(TP+FP): "of what I predicted positive, how many are right". Recall = TP/(TP+FN): "of all positives, how many did I find". F1 = harmonic mean of precision/recall; balances when classes are roughly balanced. ROC-AUC = area under TPR vs FPR curve: threshold-invariant, works well at balanced classes. PR-AUC = area under precision vs recall curve: MUCH better at imbalanced classes. Decision rule: pick metric by the cost asymmetry. Search for cancer: high recall, accept low precision. Spam filter with user friction cost: high precision, accept missing some spam. Ranker / retrieval: NDCG@k with graded relevance. Senior nuance: F1 is a single-threshold summary; pick continuous metrics when you sweep thresholds. For imbalanced data, PR-AUC is the right answer. Production: track calibration (Brier, ECE) for probabilistic predictions.

</details>

**Follow-ups:** What is calibration? Why is ROC-AUC misleading on imbalanced data?

**Difficulty:** Junior - Mid

### 58. Handling severe class imbalance in production

> "How would you handle imbalanced classes during model training?"

**Where asked:** Reported at FAANG, AI startups ML Engineer 2024-2026 · [source](https://adilshamim8.medium.com/65-machine-learning-interview-questions-2025-2fde3a358dc9)

**What they're testing:** Practical recipe awareness and trade-off understanding.

<details>
<summary>💡 Strong answer</summary>

Layered approach: (1) data-level: resampling (oversample minority via SMOTE/ADASYN, undersample majority), class-balanced mini-batches; (2) loss-level: class-weighted loss, focal loss for hard examples, label smoothing; (3) metric-level: favor PR-AUC, F-beta (F2 if recall matters), not accuracy; (4) model-level: calibration (Platt, isotonic), probability thresholds tuned on validation; (5) deployment-level: two-stage cascade (cheap filter -> expensive model). Senior nuance: oversampling can leak duplicates into validation; use stratified splits. SMOTE assumes feature-space density assumptions that don't always hold. Class weighting is usually the cleanest lever. Threshold-tuning at deployment is often more impactful than any training change.

</details>

**Follow-ups:** Why does accuracy break? How does threshold-tuning compare to cost-sensitive learning?

**Difficulty:** Mid

### 59. Word embeddings, from classic to modern retrieval

> "What are the most common word embedding methods?"

**Where asked:** Reported at AI / FAANG ML Engineer (Medium adilshamim 65 ML 2025; r/MachineLearning prep) · [source](https://adilshamim8.medium.com/65-machine-learning-interview-questions-2025-2fde3a358dc9)

**What they're testing:** Breadth from classical embeddings to dense modern ones.

<details>
<summary>💡 Strong answer</summary>

Embeddings are dense vectors representing items (words, sentences, users, products). Classical options: count-based: bag-of-words, TF-IDF (sparse, high-dim, no semantic info). Distributed/static: Word2Vec (CBOW/Skip-gram), GloVe (global co-occurrence matrix factorization): 2013-2014 era, captures semantic relations ("king - man + woman = queen"). Contextual: ELMo, BERT-family, OpenAI text-embedding-3: same word gets different vector by context. These power retrieval-augmented generation, recommendation, classification with linear probes, clustering. Senior nuance: modern dense embedders (BGE, E5, Cohere embed-v3, OpenAI text-embedding-3-large) are almost always the right answer for production retrieval. Sparse lexical (BM25) and dense are usually complementary (hybrid wins). Embedding quality degrades under domain shift, so finetune on your data with hard negatives for production.

</details>

**Follow-ups:** What are hard negatives? Why does contrastive learning help embedders?

**Difficulty:** Mid

### 60. Overfitting: detection and prevention

> "How do you detect and prevent overfitting in production ML systems?"

**Where asked:** Reported at FAANG ML Engineer, AI startups · [source](https://medium.com/@aakash.gupta_19288/machine-learning-model-optimization-interview-questions-you-should-master-3d36d82a0733)

**What they're testing:** Diagnostic and mitigation depth.

<details>
<summary>💡 Strong answer</summary>

Overfitting = model captures noise/idiosyncrasies in training data, fails to generalize. Detected by: gap between training and validation/test error that grows over training; poor performance on holdout set. Prevention layers: (1) data: more data, better data quality, data augmentation; (2) model: simpler architecture, fewer features; (3) regularization: L1/L2, dropout, early stopping, weight decay; (4) ensemble: bagging (random forests) reduces variance; (5) cross-validation: k-fold for robust estimate of generalization error. Senior nuance: in deep learning the "double descent" phenomenon complicates the overfitting story: some overparameterized models generalize better than smaller ones (interpolation regime). Production-specific: monitoring the train-val gap over time catches overfitting retraining pipelines. Don't conflate train-test gap with real-world shift.

</details>

**Follow-ups:** What is double descent? How does dropout regularize?

**Difficulty:** Junior - Mid

### 61. Diagnosing bias vs variance by experiment

> "You are given a tabular dataset where the model underperforms. Walk through diagnosing bias vs variance by training at multiple data sizes."

**Where asked:** Reported at FAANG ML Engineer (r/FAANGinterviewprep Nov 2025; r/MachineLearning prep) · [source](https://www.reddit.com/r/FAANGinterviewprep/comments/1q752rn/faang_machine_learning_engineer_interview/)

**What they're testing:** Diagnostic-by-experiment ability.

<details>
<summary>💡 Strong answer</summary>

Workflow: (1) Plot learning curves: train and validation error vs training set size at multiple N (e.g., 0.1K, 1K, 10K, 100K). (2) Patterns: high bias: both curves plateau at high error with small gap (model underfits data); high variance: train error low, validation error much higher, gap shrinks with more data. (3) Concrete example: say training error = 5%, validation error = 25% at small data. As data doubles 8x, validation drops to 10%. High variance; solution: more data, simpler model, regularization, ensembling. If instead train error rises (5% -> 12%) with more data: high bias; bigger model, better features, longer training. Senior view: this diagnostic is cheap, often >3 effective experiments return a clear story, and it's the first thing to run before throwing compute at a complex model.

</details>

**Follow-ups:** What is ensemble learning vs stacking? Why does boosting reduce bias and bagging reduce variance?

**Difficulty:** Mid - Senior

### 62. Grid search vs random search vs Bayesian optimization

> "Compare hyperparameter search strategies."

**Where asked:** Reported at FAANG, AI startups ML Engineer · [source](https://adilshamim8.medium.com/65-machine-learning-interview-questions-2025-2fde3a358dc9)

**What they're testing:** Awareness of search-space economics.

<details>
<summary>💡 Strong answer</summary>

Grid search enumerates all combinations over a Cartesian grid: wasteful when most hyperparameters don't matter. Random search samples uniformly: Bergstra & Bengio 2012 showed it matches/exceeds grid in high-dim spaces because not all hyperparameters matter equally. Bayesian optimization (Gaussian processes, TPE, Optuna) builds a surrogate model of validation-loss-as-a-function-of-hparams, picks the next trial by expected improvement: converges to good configs in far fewer trials. Hyperband, ASHA, BOHB combine BO with early stopping for cheap parallelism. Senior recipe 2025-2026: start with random search 20-50 trials to map the landscape, then switch to Optuna/TPE for fine-tuning; warm-start from past experiments. Always tune on a frozen eval set; never tune on test.

</details>

**Follow-ups:** What is warm-starting? Why does BO assume smoothness?

**Difficulty:** Mid

---

<div align="center">

**Practice these out loud. [Landed](https://landed.jobs) runs voice mock interviews that grill you on exactly these questions — plus daily matched AI roles and agent-drafted application answers.**

[![Get Started](https://img.shields.io/badge/Get%20Started%20Free-→-6C2BD9?style=for-the-badge)](https://landed.jobs)

<sub>Every question traces to a public candidate report — sources inline. Asked something new recently? PRs welcome. · [All banks →](../README.md)</sub>

</div>
