[← All question banks](../README.md) · part of [ai-interview-questions](https://github.com/landedjobs/ai-interview-questions) by [Landed](https://landed.jobs)

<div align="center">

# 📊 Data Science & Applied Science — Real AI Interview Questions

![Updated](https://img.shields.io/badge/updated-2026.07-00A86B?style=flat-square) ![Questions](https://img.shields.io/badge/66%20real%20questions-ff5b29?style=flat-square) ![Sources](https://img.shields.io/badge/every%20question-cited-6C2BD9?style=flat-square)

**ML breadth, experimentation, applied LLM and science-presentation questions from Amazon, Netflix, Stripe, Duolingo and more — reported by real candidates.**

</div>

---

**Jump to:** [ML breadth](#ml-breadth-rapid-fire-fundamentals) · [ML depth](#ml-depth-specialty-probes-and-past-project-grilling) · [Statistics & experimentation](#statistics--experimentation) · [Applied LLM](#applied-llm) · [ML coding](#ml-coding) · [Science presentation](#science-presentation) · [Product & metrics cases](#product--metrics-cases) · [Behavioral](#behavioral)

---

> **Loop intel:** Amazon's Applied Scientist loop is the highest-volume 2024-2026 source in this bank. It is consistently five rounds - Coding & Algorithms, ML Depth, ML Breadth, Business Case, Science Presentation - plus a Bar Raiser, per the official [amazon.jobs prep page](https://amazon.jobs/content/en/how-we-hire/applied-scientist-interview-prep), a full candidate debrief on [r/leetcode](https://www.reddit.com/r/leetcode/comments/1jwond7/amazon_applied_scientist_interview_experience/), and [IGotAnOffer's question bank](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview). Every question below is reproduced from a public candidate report, mock-interview writeup, or recruiting blog dated 2024-2026, with sources inline.

## ML Breadth: Rapid-Fire Fundamentals

> **Genre intel:** 2024-2026 breadth rounds are still dominated by 7 recyclable fundamentals - bias/variance, L1 vs L2, bagging/boosting/RF, class imbalance, metric selection, supervised/unsupervised/RL, and dimensionality reduction - reported at Amazon ([IGotAnOffer](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview)), Microsoft ([HireReady 2026 guide](https://www.gethireready.com/interview-guides/applied-scientist-microsoft)), Google DS prep ([r/datascience](https://www.reddit.com/r/datascience/comments/1gukca0/google_data_science_interview_prep/)), Netflix ([TryExponent](https://www.tryexponent.com/guides/netflix-data-scientist-interview)), Pinterest and Uber. Mine these first. Breadth-only preparation gets you rejected at L4, but weakness on any of these when asked live drops you out of contention.

### Bias-variance trade-off

> "Explain the bias-variance trade-off."

**Where asked:** Amazon · Applied Scientist · Science Breadth round (~2025) · [source](https://www.reddit.com/r/leetcode/comments/1jwond7/amazon_applied_scientist_interview_experience/); also in the Microsoft Applied Scientist 2026 prep guide ([HireReady](https://www.gethireready.com/interview-guides/applied-scientist-microsoft)) and corroborated on [Glassdoor](https://www.glassdoor.ca/Interview/Amazon-Applied-Scientist-Interview-Questions-EI_IE6036.0,6_KO7,24.htm)

**What they're testing:** Whether you can write down the squared-error decomposition and map it onto concrete regularization decisions (more data, stronger regularizer, smaller hypothesis class). Senior interviewers reward the math + a real example.

<details>
<summary>💡 Strong answer</summary>

Expected test error decomposes into irreducible noise plus bias-squared plus variance. High bias comes from under-fitting (too-strong prior, too few features, oversmoothed model); high variance comes from overfitting (deep nets without regularization, decision trees grown deep, k-NN with small k in high dimension). The trade-off shifts with hypothesis-class capacity, training-set size, and noise floor; resampling, regularization, ensembling, and early stopping each address one component. Cite concrete examples: "on a 50-sample fraud task a 6-depth GBM was high-variance - we switched to L2-regularized logistic with hand-crafted features and out-of-fold AUC rose 0.04".

</details>

**Follow-ups:** Bias/variance of bagging vs boosting; how cross-validation interacts with both; why ensembles roughly halve variance but not bias.

**Difficulty:** Phone-screen breadth (L4) to Bar Raiser (L7)

### L1 vs L2 regularization

> "How do L1 and L2 regularization differ in logistic regression? When do you pick each?"

**Where asked:** Amazon · Applied Scientist · Science Breadth / Science Depth loop (~2025) · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview)

**What they're testing:** Distinguish the geometry of L1 (sparse, corner-seeking) vs L2 (rotationally symmetric); connect to prior beliefs (Laplace vs Gauss); understand elastic net as a compromise.

<details>
<summary>💡 Strong answer</summary>

L2 adds the squared-weight penalty to the loss - it shrinks weights smoothly but rarely zeros them, is rotationally invariant, and has a clean Gaussian prior. L1 adds the absolute-weight penalty - the unit-ball constraint is a diamond, so the optimum hits corners, yielding sparse solutions and implicit feature selection. Use L1 when you believe most features are noise and want a parsimonious model (e.g. high-dimensional text bag-of-words); L2 when features are correlated or co-linear (L1 will arbitrarily keep one). Elastic Net mixes both when features are correlated and group sparsity matters. In practice at Amazon scale we standardize features, sweep log-spaced C values, and pick with out-of-fold AUC.

</details>

**Follow-ups:** Effect on calibration; interaction with non-convex losses (e.g. XGBoost); efficient proximal-gradient updates for L1.

**Difficulty:** Breadth round (L4-L5)

### Bagging vs boosting vs Random Forest

> "What is the difference between bagging, boosting and Random Forest?"

**Where asked:** Amazon · Applied Scientist · Science Breadth · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview); also reported on [Blind](https://www.teamblind.com/post/science-breadth-interview-amazon-hfwqznrb)

**What they're testing:** Variance reduction vs bias reduction; tree ensemble interpretations; understanding that RF is bagged trees with extra feature randomness.

<details>
<summary>💡 Strong answer</summary>

Bagging (e.g., Random Forest) trains M models on bootstrap samples and averages - it reduces variance without changing bias much, so leaves the model class unchanged. Boosting (AdaBoost, GBM, XGBoost, LightGBM) fits models sequentially, each one up-weighting previous errors, trading variance for bias and producing a strong learner from weak base learners. Random Forest = bagging + at each split a random subset of features - the feature bagging decorrelates trees and dramatically lowers variance. Use RF when you need a robust, low-tuning baseline; use gradient boosting when leaderboard performance matters but watch for overfitting on small data and the resulting need for early stopping, shrinkage, and column subsampling.

</details>

**Follow-ups:** What's the variance reduction of bagging? Why doesn't boosting help with high-noise labels? Stacking vs blending.

**Difficulty:** Breadth, mid

### Handling imbalanced data

> "How do you handle imbalanced data?"

**Where asked:** Amazon · Applied Scientist · Science Breadth round (~2025) · [source](https://www.reddit.com/r/leetcode/comments/1jwond7/amazon_applied_scientist_interview_experience/); also a recurring question in Microsoft Applied Scientist prep guides

**What they're testing:** Whether you reach for the right knob (threshold shift, not synthetic oversampling) first; awareness of leakage traps with SMOTE on time-series and CV splits.

<details>
<summary>💡 Strong answer</summary>

Imbalance isn't a modeling problem until metrics say it is: pick a metric that reflects business cost - PR-AUC, F-beta with beta tied to FN:FP cost ratio, or top-k recall. Training-side options: class weights or focal loss; SMOTE/ADASYN on features only inside CV folds to prevent leakage; balanced bagging. Inference-side: threshold calibration on a held-out set with the true operating point. Cautions: SMOTE on time-ordered data leaks future into past; up-weighting rare classes without re-tuning learning rate can hurt; for ranking problems the right fix is often a calibration layer, not retraining. Pick the cheapest fix tied to the decision boundary.

</details>

**Follow-ups:** When is PR-AUC misleading? Why focal loss works; effect on calibration.

**Difficulty:** Breadth, mid

### Metric choice for a 0.1%-positive fraud model

> "How does class imbalance interact with metrics selection? Which metric do you choose for a fraud model with 0.1% positives?"

**Where asked:** Amazon AS breadth and Microsoft AS depth (~2025-2026) · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview) · [HireReady MS-AS](https://www.gethireready.com/interview-guides/applied-scientist-microsoft)

**What they're testing:** Whether you understand ROC-AUC's optimism under heavy class skew and PR-AUC's honesty at small positive counts.

<details>
<summary>💡 Strong answer</summary>

ROC-AUC stays high because the vast negative pool gives easy true-negatives; PR-AUC punishes false-positives relative to recall of the rare class, so PR-AUC or precision@K (K = investigation capacity) tell you the operating story. Tie the metric to the decision: if you review the top 1,000 alerts/week, measure precision@1,000 and recall@1,000; report business cost via expected value per alert. Calibrate threshold on a recent window. Avoid using accuracy or "AUC-ROC" alone in stakeholder decks - pair PR-AUC with the cost-weighted loss.

</details>

**Follow-ups:** Threshold selection under shifting prevalence; calibration with Platt vs isotonic; cost-sensitive learning.

**Difficulty:** Depth (L6)

### Supervised vs unsupervised vs reinforcement learning

> "Explain the differences between supervised, unsupervised, and reinforcement learning."

**Where asked:** Amazon · Applied Scientist · Science Breadth (~2025) · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview); also covers mid-tier product DS loops

**What they're testing:** Whether you can map a business problem onto the right learning paradigm and articulate the loss signal.

<details>
<summary>💡 Strong answer</summary>

Supervised: paired (x, y) - minimize prediction loss against ground-truth labels. Unsupervised: only x - learn structure (clustering, density, representation). Reinforcement learning: agent-environment loop with reward r(s,a) - maximize expected cumulative reward with delayed labels, distributional shift, and exploration. Real Amazon systems usually sit on a continuum: representation pretraining is unsupervised, downstream ranking is supervised, marketplace bidding has RL-flavored components. Ask what signal is available before picking.

</details>

**Follow-ups:** Self-supervised vs unsupervised; offline-RL caveats for personalization.

**Difficulty:** Breadth

### Closed-form linear regression vs gradient descent

> "What is the closed-form solution of linear regression, and when is it better to use gradient descent?"

**Where asked:** Amazon · Applied Scientist · Science Breadth (~2025) · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview)

**What they're testing:** Numerical linear algebra, conditioning, scale sensitivity.

<details>
<summary>💡 Strong answer</summary>

Closed-form: beta_hat = (X^T X)^(-1) X^T y. Works when n >> p and X^T X is well-conditioned. Use gradient descent (or LBFGS) when p is large or X^T X is ill-conditioned (multicollinearity, sparse inputs, near-zero variance features). Closed-form is O(p^2 n + p^3), so quickly infeasible beyond ~10^4 features. SGD/Adam when streaming or non-convex losses. For ridge, closed-form is (X^T X + lambda I)^(-1) X^T y - still preferred when feasible.

</details>

**Follow-ups:** How to handle ill-conditioning; QR vs SVD; regularization numerical stability.

**Difficulty:** Breadth-mid

### Prove logistic loss has a global minimum

> "Write the loss function for logistic regression and prove that it has a global minimum."

**Where asked:** Amazon · Applied Scientist · Science Breadth (~2025) · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview)

**What they're testing:** Convexity argument; familiarity with MLE on a sigmoid.

<details>
<summary>💡 Strong answer</summary>

NLL with sigmoid: J(theta) = -sum [y_i log sigma(theta x_i) + (1-y_i) log (1 - sigma(theta x_i))]. Equivalent: -sum [y_i theta^T x_i - log(1 + exp(theta^T x_i))]. The term inside is the log-partition; its Hessian is X^T W X with W = diag(sigma(1-sigma)) >= 0, so the Hessian is positive semi-definite everywhere, so J is convex, so any stationary point is a global min. Strict convexity requires X to be full column rank; otherwise the minimum is a manifold.

</details>

**Follow-ups:** Why doesn't MSE work? Multinomial extension; connection to cross-entropy.

**Difficulty:** Provenance breadth (L6+)

### KL divergence vs cross-entropy

> "How is KL divergence loss different from cross-entropy loss?"

**Where asked:** Amazon · Applied Scientist · breadth (~2025) · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview)

**What they're testing:** Probabilistic framing vs loss naming confusion.

<details>
<summary>💡 Strong answer</summary>

KL(p || q) = sum p log(p/q). Cross-entropy H(p, q) = -sum p log q = H(p) + KL(p || q). For classification with one-hot p, H(p) is constant, so minimizing cross-entropy = minimizing KL(p || q). So in supervised learning the two are equivalent up to a constant; the framing matters when modeling distributions (variational inference, distillation, RL policy gradients) where you need to be careful about direction.

</details>

**Follow-ups:** Forward vs reverse KL and "mode-seeking" vs "mode-covering" behavior.

**Difficulty:** Breadth-mid

### Dimensionality reduction methods

> "What are methods for reducing dimensionality in a dataset, and how do they work?"

**Where asked:** Amazon · Applied Scientist · breadth (~2025) · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview); also Microsoft AS prep

**What they're testing:** Linear (PCA, LDA, ICA) vs nonlinear (t-SNE, UMAP, autoencoders) trade-offs; interpretability.

<details>
<summary>💡 Strong answer</summary>

Linear methods project onto directions of maximal variance (PCA), maximal class separation (LDA), or maximal independence (ICA). For large feature spaces: PCA with randomized SVD on standardized features; truncation picked by explained-variance ratio + downstream AUC curve. Nonlinear: kernel PCA, autoencoders, contrastive embeddings. t-SNE/UMAP are visualization-only and distort distances away from neighbors. Choose by objective: feature compression -> PCA/AE; visualization -> UMAP/t-SNE with caveats; representation learning for downstream ML -> contrastive embeddings or supervised pretrained backbones.

</details>

**Follow-ups:** When does PCA fail? Why UMAP clusters aren't always meaningful; how to validate embeddings.

**Difficulty:** Breadth

### BiLSTM vs Transformer

> "How does a BiLSTM work? How does that compare to a Transformer?"

**Where asked:** Amazon · Applied Scientist · breadth (~2025) · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview); also Microsoft, Google MLE

**What they're testing:** Stateful recurrence vs attention's O(n^2) memory but parallelism.

<details>
<summary>💡 Strong answer</summary>

BiLSTM = two LSTMs run forward and backward over the same sequence; their hidden states are concatenated at each step, giving context from past and future. Good for moderate-length sequential data, small corpora, low-latency token tagging. Transformers replace recurrence with self-attention: every position attends to every other through Query/Key/Value projections, capturing long-range dependencies in O(1) sequential steps but O(n^2) memory. Trade-offs: BiLSTM trains on a single GPU-fast on long sequences, slower to parallelize; Transformer dominates when data is large enough and is the default for modern NLP/CV. Reach for BiLSTM in low-resource, latency-sensitive or streaming token-tagging applications.

</details>

**Follow-ups:** Why attention over recurrence? Complexity analyses; KV cache at inference.

**Difficulty:** Mid

### Transformer vs gradient-boosted trees on tabular data

> "How would you decide between a transformer-based neural model and a gradient-boosted tree model on a tabular task?"

**Where asked:** Amazon AS depth · Pinterest DS · Uber DS (cross-company reported) · [source](https://www.reddit.com/r/leetcode/comments/1jwond7/amazon_applied_scientist_interview_experience/) · [Pinterest Glassdoor](https://www.glassdoor.com/Interview/Pinterest-Data-Scientist-Interview-Questions-EI_IE503467.0%2C9_KO10%2C24.htm)

**What they're testing:** Practical model-selection judgment and "is this an ML task or an FTPM (feature-table-processing-machine) task?"

<details>
<summary>💡 Strong answer</summary>

On tabular features, default to GBM (LightGBM, XGBoost, CatBoost) - known to dominate in Kaggle and on Amazon Search/ads benchmarks. Train a small transformer only when (a) there is a sequence/embedding backbone you can fine-tune, (b) you have >>10^4 labeled rows, (c) categorical interactions are too many for hand-crafted crosses. Otherwise GBM wins on training cost, inference latency, calibration, and debuggability. A useful go-to template: GBM first; if structured-text or high-cardinality categorical embeddings matter, train FT-Transformer/SAINT as a second-tier candidate; ensemble via stacking only when leaderboard gains are material. Senior interviewers love: "start GBM, ship, then see if a NN buys 0.5% AUC worth the latency and maintenance."

</details>

**Follow-ups:** When do GBMs underfit? Calibration of NNs; cost-per-decision at serving.

**Difficulty:** Depth

---

## ML Depth: Specialty Probes and Past-Project Grilling

> **Rubric intel:** Amazon's depth round rubric is "walk through a project, follow-ups on modeling trade-offs and outcomes" ([IGotAnOffer](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview)) - it grades communication, ownership, and technical judgment, not trivia. Microsoft's Applied Scientist 2 loop is the outlier on mathematical depth: a single [r/developersIndia debrief](https://www.reddit.com/r/developersIndia/comments/1ot60wt/insane_interview_with_microsoft_applied_scientist/) enumerates 20+ questions including pure proofs, and the candidate "washed out in the ML round" on the nearest-neighbor proof. If you prep for Microsoft AS, expect a real probability of deriving a theorem on a whiteboard; if you prep for Amazon AS, expect the rubric to grade you on Communication, Bias for Action, Ownership, and Stretch Assignments.

### The project you're most proud of

> "Walk through a project you are most proud of."

**Where asked:** Amazon · Applied Scientist · Science Depth round (~2025) · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview); Yuan Meng calls this "the 45-60 min round" for research-eng MLE 2.0 ([yuan-meng.com](https://www.yuan-meng.com/posts/mle_interviews_2.0/)); Duolingo DS reports a similar prompt ([Blind](https://www.teamblind.com/post/duolingo-data-scientist-interview-bhgextxs))

**What they're testing:** Ownership, communication, depth, technical judgment and decisiveness.

<details>
<summary>💡 Strong answer</summary>

Pick one project where you made non-obvious decisions with measurable impact. Lead with the business metric you moved (e.g. "reduced chargeback rate 17% on Cross-Border Payments"). Walk through data, modeling choice (with explicit alternatives considered), evaluation methodology, and the production/operational consequences. End with what you'd do differently. Senior interviewers reward calibrated honesty: state what was lucky, what you'd keep, and what downstream system failed.

</details>

**Follow-ups:** "If you had two more weeks, what would you try?" "What would the second-best design have been?" "How did you know the uplift wasn't from another change?"

**Difficulty:** All levels

### Why that loss function?

> "Why did you pick X loss function? What would you have used if the cost were asymmetric?"

**Where asked:** Amazon · Applied Scientist · Science Depth · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview)

**What they're testing:** Cost-aware modeling, asymmetric losses, calibration.

<details>
<summary>💡 Strong answer</summary>

Connect loss to the operating decision. Default MSE under symmetric Gaussian noise; log-loss under categorical cross-entropy with calibrated outputs; pinball (quantile) loss for asymmetric intervals; focal loss when positive classes are rare and easy negatives dominate. Demonstrate practical signals: benchmarked log-loss vs hinge for a high-recall search model, picked log-loss for calibrated probabilities that downstream ranking uses for blending. If asymmetric, multiply gradients or weight samples, and validate with a confusion matrix on the cost-weighted axis.

</details>

**Follow-ups:** Why not MSE for classification; how to recover costs; threshold-free metrics.

**Difficulty:** Depth (L6+)

### Why is a GPU faster than a CPU? Why is NumPy faster than a list?

> "Why CPU is slower than GPU? Why is NumPy faster than a Python list multiplication?"

**Where asked:** Microsoft · Applied Scientist 2 · Round 2 (~2025) · [source](https://www.reddit.com/r/developersIndia/comments/1ot60wt/insane_interview_with_microsoft_applied_scientist/)

**What they're testing:** Systems literacy - interviewers gauge whether you can debug perf, converse with infra engineers and reason about data-parallel hardware.

<details>
<summary>💡 Strong answer</summary>

CPUs execute a small handful of wide threads with deep caches and branch-predict/ooo machinery - great for serial, irregular code. GPUs execute thousands of narrow SIMT threads with smaller per-thread caches - great for dense arithmetic on large tensors with high memory bandwidth and minimal branching. BLAS kernels on a GPU run at TFLOPs/W an order of magnitude beyond CPUs. NumPy beats Python lists because Python lists store pointers to boxed Python objects; arithmetic compiles to per-element Python bytecode with type dispatch overhead. NumPy stores contiguous typed buffers (C doubles) and dispatches fused SIMD kernels in C, removing the per-element interpreter overhead.

</details>

**Follow-ups:** When CPU beats GPU; why vectorize an inner loop; what cuDNN does for conv2d.

**Difficulty:** Depth (L5+)

### Prove MSE is non-convex for logistic regression

> "Prove why MSE is non-convex for logistic regression."

**Where asked:** Microsoft · Applied Scientist 2 · Round 3 (Principal Applied Scientist round, ~2025) · [source](https://www.reddit.com/r/developersIndia/comments/1ot60wt/insane_interview_with_microsoft_applied_scientist/)

**What they're testing:** Mathematical maturity; the reporting candidate "washed out" on related proofs.

<details>
<summary>💡 Strong answer</summary>

The logistic model is sigma(theta x). The MSE surrogate is J(theta) = 1/2n sum (sigma(theta x_i) - y_i)^2. J is non-convex because sigma is sigmoidal: composing a non-linear function with a squared error creates a landscape with multiple local minima at extreme theta (saturated predictions). Hessian is uninformative globally. This is exactly why cross-entropy is preferred for classification - the log sits inside the sum producing a convex objective. Equivalent sigma-in-MSE views go through X^T diag(sigma(1-sigma)) but with a (1 - 2y_i) factor that breaks sign-definiteness.

</details>

**Follow-ups:** What other surrogate losses are non-convex? When might you still use MSE?

**Difficulty:** Depth research (L7+)

### Prove 1-NN error is at most twice the Bayes error

> "Prove that 1-Nearest Neighbor has error rate at most twice the Bayes error."

**Where asked:** Microsoft · Applied Scientist 2 · Round 3 with a Principal AS (~2025) · [source](https://www.reddit.com/r/developersIndia/comments/1ot60wt/insane_interview_with_microsoft_applied_scientist/); also a classic prompt in [IGotAnOffer depth rounds](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview)

**What they're testing:** Cover's theorem literacy; asymptotic reasoning.

<details>
<summary>💡 Strong answer</summary>

Cover and Hart (1967). As n -> infinity, the nearest neighbor in metric space converges to a sample from the underlying distribution at x. So the probability 1-NN predicts y = +1 at x converges to P(y=+1 | x) under a tie-breaking convention. The conditional error 1-NN(x) = 2 P(y=+1|x) (1 - P(y=+1|x)). Compare to Bayes error B(x) = min(P, 1-P). Apply pointwise 2P(1-P) <= 2 min(P, 1-P), then take expectation. Equality only in degenerate two-point distributions; in higher dimensions get Cover's tighter bounds with the metric exponent.

</details>

**Follow-ups:** k-NN extension; curse-of-dimensionality bound; effect of label noise.

**Difficulty:** Depth research (L8)

### Code conv2d from scratch

> "Code conv2d from scratch."

**Where asked:** Microsoft · Applied Scientist 2 · Round 1 (~2025) · [source](https://www.reddit.com/r/developersIndia/comments/1ot60wt/insane_interview_with_microsoft_applied_scientist/)

**What they're testing:** Whether you can implement the operator you claim to know in deep learning interviews.

<details>
<summary>💡 Strong answer</summary>

Use a four-loop naive implementation (batch, out-channel, y, x -> sum over in_channel, k_y, k_x) and then progress to im2col + GEMM. Discuss stride, padding, dilation, groups, NCHW vs NHWC layout, memory contiguity and how PyTorch's dispatcher selects cuDNN's implicit GEMM. Be ready for the follow-up: "rewrite this in einops notation" or "make it backward pass." Senior interviewers reward: "the actual production path uses cuDNN's implicit GEMM; here's when we beat it (small batch, custom kernel)."

</details>

**Follow-ups:** Vectorize; edge cases; why im2col works.

**Difficulty:** Depth mid-to-senior

### Design and evaluate a book recommender

> "How would you design and evaluate a recommendation system that suggests books (or items) to users?"

**Where asked:** Amazon · Applied Scientist · Science Application / Business Case (~2025) · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview)

**What they're testing:** Applied ML system design; trade-offs; metrics.

<details>
<summary>💡 Strong answer</summary>

Decide the user goal: discovery vs continuation vs cold-start. Architect in two stages: candidate generation (two-tower retrieval with item embeddings trained via in-batch negatives, or a co-occurrence matrix) and re-ranking (LightGBM ranker + calibrated NN with cross-features). Define metrics: NDCG@K, recall@K for retrieval, MAP@k and uplift per session for business; add diversity, novelty, catalog-coverage slices offline; online A/B with engagement, conversion, retention. Address cold-start via content features and popularity priors; address filter-bubble via exposure-mixing and editorial seeds.

</details>

**Follow-ups:** Choice of negative sampling; debiasing; position bias.

**Difficulty:** Depth + business (L6)

### Driver fraud: SQL plus modeling pipeline

> "If you wanted to detect fraud for drivers, design the SQL and the modeling pipeline."

**Where asked:** Uber · Data Scientist · SQL round (~2025) · [source](https://igotanoffer.com/en/advice/uber-data-scientist-interview)

**What they're testing:** Domain-aware SQL, threshold rationale for streaming fraud scoring.

<details>
<summary>💡 Strong answer</summary>

SQL: window functions to score each driver's 7-day, 30-day velocity and behavior distributions; CTE chain comparing to population distributions (z-score, IQR). Modeling: gradient-boosted trees on engineered velocity, geo, payment-fingerprint features; add an isolation-forest anomaly layer; calibrate thresholds using a recent labeled window. Serving: real-time feature store with sub-second freshness; alert API. Show expected precision/recall trade-off and operational cost of false positives. Note that Uber DS loops also ask "Explain JOINs to a 10-year-old" - signaling they want communication plus SQL.

</details>

**Follow-ups:** Labeling cadence; concept drift; what guardrails matter.

**Difficulty:** Depth (L5+)

### Fine-tune a pre-trained LLM for a product feature

> "Walk through how you would fine-tune a pre-trained language model for a Microsoft product feature."

**Where asked:** Microsoft · Applied Scientist · 2026 prep guide · [source](https://www.gethireready.com/interview-guides/applied-scientist-microsoft)

**What they're testing:** Applied LLM depth; data, compute, evaluation.

<details>
<summary>💡 Strong answer</summary>

Pick base model by task: encoder (RoBERTa) for classification, encoder-decoder (T5) for span tasks, decoder-only (Phi, Llama) for generation. Fine-tune on curated product data with instruction format; freeze lower layers when data is small. Always: prepare data with human + LLM-judge labels, hold out time-based evaluation slice, report both traditional metrics (EM, F1, ROUGE) and human eval on the slices that matter. Constrain compute by LoRA/PEFT, quantize, distill.

</details>

**Follow-ups:** PEFT vs full FT; data mixtures; catastrophic forgetting.

**Difficulty:** Depth mid-to-senior

### Your favorite ML paper

> "What is your favorite ML paper? Summarize it and explain how the method could apply to our problem."

**Where asked:** Amazon · Applied Scientist · Phone Screen (~2025) · [source](https://www.reddit.com/r/leetcode/comments/1jwond7/amazon_applied_scientist_interview_experience/); also reported at Google DeepMind Research Engineer ([IGotAnOffer](https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview))

**What they're testing:** Communication, top-of-funnel curiosity, and the ability to map a research idea onto the company's domain.

<details>
<summary>💡 Strong answer</summary>

Pick a paper with a transferable method (e.g. DPO for preference optimization, LoRA for parameter-efficient tuning, Mamba for linear-time sequence modeling, FlashAttention for memory-efficient transformer training). Targeted summary in 3 minutes: motivation, method, result. Then a 30-second bridge: "here's how the same idea could shorten training of Rufus, our shopping assistant." Senior interviewers reward an honest "limitations" slide and a punchy contrast against current SOTA.

</details>

**Follow-ups:** Reproducibility, hidden gotchas, generalization.

**Difficulty:** All levels

### ML system design in the "MLE 2.0" research-eng round

> "ML system design: feature stores, distributed training, online serving."

**Where asked:** Reported as a standard round in 2026 "MLE 2.0" research-engineering loops · [Yuan Meng, Feb 1 2026](https://www.yuan-meng.com/posts/mle_interviews_2.0/)

**What they're testing:** Whether you can design the production side of ML: feature freshness, training infra, and serving, not just the model. Yuan Meng documents that she failed a backend-role onsite because they wanted a "backend engineer with ranking knowledge" rather than an ML engineer.

**Difficulty:** Senior

---

## Statistics & Experimentation

> **Genre intel:** A/B testing interviews now require estimand discipline, not just p-values. [PracHub's Apr 21, 2026 Airbnb prompt](https://prachub.com/interview-questions/design-an-a-b-test-with-causal-inference) gives all numbers and constraints in advance and asks for ITT vs TOT, design-effect-adjusted sample size, SRM checks, DiD/CUPED fall-backs, O'Brien-Fleming sequential boundaries and a ship/no-ship decision. Netflix's framework has shifted to sequential, multi-metric decisions - see the [Netflix tech blog on sequential A/B testing](https://netflixtechblog.com/sequential-a-b-testing-keeps-the-world-streaming-netflix-part-1-continuous-data-cba6c7ed49df) and [TryExponent's Netflix DS guide](https://www.tryexponent.com/guides/netflix-data-scientist-interview).

### Design and evaluate an A/B test

> "Explain how you would design and evaluate an A/B test."

**Where asked:** Amazon · Applied Scientist · breadth (~2025) · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview); the same prompt is reported at Stripe DS, Netflix DS and in Microsoft DS guides

**What they're testing:** Do you choose unit, primary metric, duration, power, and guardrails independently and explain how they interlock?

<details>
<summary>💡 Strong answer</summary>

Hypothesize: one-sentence "if-then" prediction of the treatment effect's direction. Unit: who is randomized (user, session, geo)? Treatment: what does the new feature or model do? Primary metric tied to business (engagement, conversion, retention) - one primary metric or you're chasing noise. Power: MDE, baseline, alpha = 0.05, power = 0.80 -> sample size n per arm; account for intra-cluster correlation (e.g., ICC=0.05 multiplies the design effect). Duration: cover at least one weekly cycle; prevent peeking with sequential bounds or a pre-registered stopping rule. Guardrails: latency, error rate, paid-event rate. SRM check before reading the result. Run a CUPED variance reduction if traffic is plentiful but effect is small. Ship/no-ship decision tied to confidence interval, not point estimate.

</details>

**Follow-ups:** SRM detection; when to use difference-in-differences; noncompliance handling.

**Difficulty:** All levels

### Netflix homepage experiment with conflicting metrics

> "You ran a Netflix homepage experiment testing a new row-ranking algorithm for 28 days with member-level randomization. Weekly Viewing Hours per Member +0.30% (95% CI -0.10% to +0.70%, p=0.14); Title Starts per Member +0.90% (95% CI +0.30% to +1.50%, p=0.004); Completion Rate -0.60% (95% CI -1.10% to -0.10%, p=0.02). Guardrails flat. TV is biggest share. Business goal: improve member satisfaction with what they watch to drive long-term retention. How would you advise product leadership on what to do next?"

**Where asked:** Netflix · Data Scientist · A/B framework / Translating Results into Decisions (~2025) · [source](https://www.reddit.com/r/interviewstack/comments/1q2kt1k/netflix_data_scientist_interview_framework_on/)

**What they're testing:** Whether you reconcile a statistically significant primary-secondary conflict and tie the decision to long-term retention, not point estimates.

<details>
<summary>💡 Strong answer</summary>

Primary disagreeing with secondaries (CI crosses zero, p=0.14) means we cannot rule out noise on the headline metric. Title Starts +0.90% is real; Completion Rate -0.60% signals more clicks but worse per-click satisfaction - a "clickbait" pattern. Recommend an extended ramp or a follow-up experiment which keeps the algorithm but injects a long-term-retention surrogate (30/60/90-day return rate, churn-risk model uplift), so the ship decision is tied to satisfaction, not clicks. Don't ship on Title Starts alone: the experiment is incomplete. State the decision explicitly: "extend 4 weeks with a retention-secondary; if Completion returns to baseline, ship; if not, abandon." Add a heterogeneous effects slice for TV (largest share) to ensure UI fits.

</details>

**Follow-ups:** What if sequencing shows TV-only effect? When do you promote a secondary to primary?

**Difficulty:** Depth (L6+)

### Airbnb checkout nudge: the full A/B design

> "You own experimentation for an e-commerce checkout nudge. Design a 28-day A/B test randomized at guest_id with primary metric = 7-day completed orders, guardrails = bounce rate and p95 page latency. Baseline 7-day per-guest conversion 5%; MDE 8% relative lift; two-sided alpha=0.05; power=0.80; avg 1.6 sessions/guest; ICC=0.05; 5% bot traffic; cookie resets causing cross-arm contamination."

**Where asked:** Airbnb · Data Scientist · A/B test with causal inference (PracHub prompt, Apr 21, 2026) · [source](https://prachub.com/interview-questions/design-an-a-b-test-with-causal-inference)

**What they're testing:** Estimand discipline (ITT vs TOT), clustering-aware power arithmetic, integrity-first instinct, sequential monitoring, treatment of noncompliance/contamination, and a ship decision under realistic constraints.

<details>
<summary>💡 Strong answer</summary>

Estimand: ITT as primary because the business decision is "do we ship?" TOT as secondary to describe per-user efficacy given ~70% render rate. Design effect = 1 + (m - 1) * ICC = 1 + 0.6 * 0.05 = 1.03 - tiny inflation, but address by formulating the analysis unit at the user-grain. n per arm with absolute delta 0.004, baseline 0.05, alpha 0.05, power 0.80 -> ~120k per arm (matches PracHub reference numbers). SRM check: device and geo distribution before any readout; traffic-source-mix check. Integrity: drop obvious bots, dedupe across devices, separate ITT vs exposed-population. Sequential: O'Brien-Fleming boundaries or alpha-spending with pre-specified looks; separate harm-stop from benefit-stop. Fallback plan if randomization fails: DiD with the pre/post windows, CUPAC on pre-period covariates, PSM/IPW; state parallel-trends falsification. Ship decision: compute z and 95% CI on the 5.6% vs 5.0% lift; consider practical significance over statistical with guardrails.

</details>

**Follow-ups:** "If only 60% of the required traffic arrives, what do you do?" "If contamination rises to 5%, do you trust the readout?" "If the nudge renders for only 70% of assigned-treatment guests, how do ITT and TOT diverge, and which one drives the ship decision vs the per-user efficacy story?" "Treatment is positive overall but you suspect harm on low-end devices - how do you detect a harmful subgroup without p-hacking?"

**Difficulty:** Depth (L6+)

### Randomization and p-values

> "Why is randomization important in experimental setups? What is a p-value? How would you interpret it in the context of an A/B test?"

**Where asked:** Amazon AS breadth + Senior AS screen · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview); also in the [Netflix DS TryExponent guide](https://www.tryexponent.com/guides/netflix-data-scientist-interview)

**What they're testing:** Foundational rigor - candidates who fudge p-value interpretation wash out at L5 loops.

<details>
<summary>💡 Strong answer</summary>

Randomization balances observed and unobserved confounders across arms in expectation, freeing the difference-in-means estimator from selection bias. A p-value is the probability, under the null hypothesis of no effect, of observing data at least as extreme as observed. It is *not* the probability the null is true, nor the probability the alternative is false. In an A/B test, report p-value + 95% CI; reject when p < alpha pre-registered; if you plan to peek, use sequential boundaries.

</details>

**Follow-ups:** Type I/II errors and power; why a 0.049 result doesn't replicate on re-running the experiment; multiple-testing correction.

**Difficulty:** Breadth

### Sequential tests and simultaneous experiments

> "Design sequential tests that demote underperforming variations; manage multiple simultaneous A/B tests."

**Where asked:** Netflix · Data Scientist · causal inference round · [TryExponent guide](https://www.tryexponent.com/guides/netflix-data-scientist-interview) confirms the round tests "ability to design sequential tests that demote underperforming variations"; grounded in [Netflix's own sequential-testing publication](https://netflixtechblog.com/sequential-a-b-testing-keeps-the-world-streaming-netflix-part-1-continuous-data-cba6c7ed49df)

**What they're testing:** Ability to apply always-valid inference and alpha-spending to live traffic; senior signal of production-relevant thinking.

<details>
<summary>💡 Strong answer</summary>

Use mSPRT or Always-Valid Sequential Tests for binary and continuous metrics to monitor without inflating Type I error. Treat simultaneous tests with a Bonferroni-Holm or BH-FDR correction; share traffic across experiments using layer/mutual-exclusion. The decision policy: if any variant's p-value crosses the alpha-spending threshold at a pre-specified peek, demote - don't kill - it; rotationally reallocate traffic to the highest-eCPM/eCPC variants. Netflix's published canary regression-driven experiments adapt this idea.

</details>

**Follow-ups:** Always-valid tests vs group-sequential; what do you do when guardrails trip; independence assumption under overlapping arms.

**Difficulty:** Depth (L6+)

### Compute the lift, SE and CI: ship or not?

> "Your A/B test shows control conv 5.0% (n=120,000) and treatment conv 5.6% (n=120,000). Compute the lift, its SE and 95% CI properly accounting for two-proportion comparison. Would you ship under these constraints?"

**Where asked:** Airbnb · Data Scientist · PracHub prompt · [source](https://prachub.com/interview-questions/design-an-a-b-test-with-causal-inference)

**What they're testing:** Two-proportion z-test mechanics, both statistical and practical significance.

<details>
<summary>💡 Strong answer</summary>

Lift = (0.056 - 0.05)/0.05 = +12% relative. SE_pooled = sqrt(p_pool(1-p_pool)(1/n_t + 1/n_c)) where p_pool = (0.056*120k + 0.05*120k)/240k = 0.053. z = 0.006 / SE_pooled ~ 3.7, p ~ 0.0002. CI: 0.006 +/- 1.96 * SE ~ (0.003, 0.009) absolute -> (6%, 18%) relative. Statistical significance real. Practical significance: depends on guardrails, latency, downstream margin. Ship if guardrails fine and the lower bound on lift exceeds the cost of the change - flag the CI as wide because MDE was set wider; consider extending for a tighter CI.

</details>

**Follow-ups:** Heterogeneous effects; what if SE is computed incorrectly (delta method) - what's the natural log alternative?

**Difficulty:** Depth mid-to-senior

### Statistical methods you've actually used

> "What statistical methods have you used in past projects, and why did you choose them?"

**Where asked:** Amazon · Applied Scientist · breadth/depth (~2025) · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview)

**What they're testing:** Translator between business question and statistical tool-selection.

<details>
<summary>💡 Strong answer</summary>

Walk through a representative arc - "we used mixed-effects models to capture per-SKU random effects, a Bayesian beta-binomial prior for sparse-conversions, and a bootstrap CI for feature-importance stability." Show trade-offs; cite the choice rationale, not just the method.

</details>

**Follow-ups:** When to choose Bayesian vs frequentist; what you'd do differently with more data.

**Difficulty:** Depth

### Causal inference without randomization

> "If you only have pre/post windows (no randomization), formulate a credible causal strategy (DiD with covariates/CUPED, PSM/IPW), state the identifying assumptions, write the ATE estimator, and describe how you'd test parallel trends and overlap."

**Where asked:** Airbnb · Data Scientist · PracHub prompt (Apr 21, 2026) · [source](https://prachub.com/interview-questions/design-an-a-b-test-with-causal-inference)

**What they're testing:** Causal fluency; assumption discipline; skepticism toward off-the-shelf fit.

<details>
<summary>💡 Strong answer</summary>

ATE = E[Y_post(1) - Y_post(0) | treat]. DiD: ATE = (Y_post, treat - Y_post, control) - (Y_pre, treat - Y_pre, control). Identifying assumption: parallel trends (untreated potential outcome would have evolved identically in both groups given covariates). CUPED variance-reduces using pre-period Y. PSM/IPW: estimate propensity score, weight ATE = sum(w_i * t_i * y_i) / sum(w_i * t_i). Test parallel trends with placebo leads - apply the estimator on pre-period data; reject if you see a treatment effect there. Test overlap by inspecting propensity density histograms in treatment vs control; trim/restrict to common support. Always show the sensitivity analysis.

</details>

**Follow-ups:** Synthetic control method; instrumental variables; double-ML.

**Difficulty:** Depth (L6+)

---

## Applied LLM

> **Genre intel:** Applied LLM questions now target the RAG-vs-fine-tune-vs-prompt decision tree in addition to hands-on debugging. The ["15 AI Engineer interviews" r/deeplearning debrief](https://www.reddit.com/r/deeplearning/comments/1swxb2k/i_did_15_ai_engineer_interviews_in_the_last_6/) (late 2025) confirms live coding exercises like "build a simple retriever" and "fix a hallucination"; the [aipmguru Feb 2026 mock prep](https://aipmguru.substack.com/p/what-i-learned-preparing-to-explain) reproduces the canonical RAG-vs-fine-tuning prompt verbatim.

### RAG vs fine-tuning

> "What's the difference between RAG and fine-tuning? When would you use each?"

**Where asked:** AI PM/DS interview prep (Feb 18, 2026 mock debrief) · [source](https://aipmguru.substack.com/p/what-i-learned-preparing-to-explain); also reported as the canonical screening question at Perplexity, Scale, and AI-native DS loops, and in the [15-AI-engineer debrief](https://www.reddit.com/r/deeplearning/comments/1swxb2k/i_did_15_ai_engineer_interviews_in_the_last_6/)

**What they're testing:** Decision framework; cost/accuracy reasoning; the levers of LLM-feature design.

<details>
<summary>💡 Strong answer</summary>

Fine-tuning adjusts the weights of an existing LLM on a task-specific dataset to bake in behavior - expensive (training infra, MLE weeks), better at adapting style, format and behavior, but doesn't add new knowledge reliably. RAG attaches an external retriever (BM25, dense embeddings) and injects passages into the prompt - cheap to update (just swap the corpus), gives attribution, but is bounded by context window, retrieval quality, and budget. Default to RAG when the data is large, evolving, or needs attribution (catalog QA, internal docs, support); fine-tune when the task requires consistent voice/format and the dataset is small and frozen. Combine both: fine-tune the base for tone and safety; RAG for facts. Decision tree: (1) is knowledge evolving? RAG. (2) is voice/style the bottleneck? FT. (3) compute budget? RAG cheaper; FT when you can amortize across millions of queries.

</details>

**Follow-ups:** "When would you tune the embedding model?" "How do you evaluate RAG quality?"

**Difficulty:** Mid

### Defend your RAG choice and your hallucination eval

> "Why RAG instead of fine-tuning for this product? How did you actually evaluate the hallucinations?"

**Where asked:** Reported in the AI-engineer debrief on r/deeplearning · [source](https://www.reddit.com/r/deeplearning/comments/1swxb2k/i_did_15_ai_engineer_interviews_in_the_last_6/)

**What they're testing:** Whether you evaluated hallucination with concrete metrics and slices, not vague claims.

<details>
<summary>💡 Strong answer</summary>

Explain that fine-tuning was cost-prohibitive on the dataset, so we used MiniLM for retrieval speed and a semantic-chunking strategy that dropped hallucination rate by 40%. Present the eval: an LLM-judge against a held-out gold set, paired with human spot-check on a stratified subset, plus retrieval-precision (fraction of retrieved chunks used in the final answer) and factual-accuracy pass rate. Slice by topic to surface where retrieval fails.

</details>

**Follow-ups:** What about groundedness in borderline cases; when would you switch to FT?

**Difficulty:** Mid-senior

### Prompt vs fine-tune vs RAG for a search-and-answer system

> "Design the LLM feature for a customer-facing search-and-answer system. Decide prompt vs. fine-tune vs. RAG and justify the cost."

**Where asked:** Reported across AI-native companies (Perplexity/Scale/Hugging Face) and Microsoft AS · [source](https://www.gethireready.com/interview-guides/applied-scientist-microsoft)

**What they're testing:** Producer thinking; cost-aware architecture.

<details>
<summary>💡 Strong answer</summary>

Architect the funnel: cheap embedding retrieval (top-50) -> rerank with cross-encoder -> top-5 chunks -> prompt with citations. Use a small open model for embedding/cross-encoder (~400M params) and a 7-70B LLM for answer generation behind a cache. Cache retrieved chunks by query rewrite; cache answers for high-frequency queries. Choose prompt + RAG over fine-tune because the corpus is large, evolving, and attribution is needed. Only fine-tune if user eval turns up consistent voice/format issues. Track cost: tokens/call * $/token * MAU; expose a guardrail that defaults to short answers for low confidence.

</details>

**Follow-ups:** When to switch to a smaller fine-tuned model on a slice?

**Difficulty:** Mid

### Implement a simple retriever

> "Implement a simple retriever."

**Where asked:** Live coding in AI-engineer rounds, per the r/deeplearning debrief · [source](https://www.reddit.com/r/deeplearning/comments/1swxb2k/i_did_15_ai_engineer_interviews_in_the_last_6/)

**What they're testing:** Implementation fluency - BM25/TF-IDF baseline; vector index; FAISS.

<details>
<summary>💡 Strong answer</summary>

Naive baseline: TF-IDF with cosine over tokenized docs, returning top-k. Vectorize: encode docs with sentence-transformers/MiniLM, store in a FAISS flat index, query via dot-product, return top-k by cosine. Senior signal: discuss pivot from flat to HNSW at a million vectors; ground the design with semantic chunking (200-500 tokens, 50-token overlap) so chunks stay coherent. Discuss query rewrite/expansion, hard negatives mining. Discuss evaluation: recall@10, nDCG@10 on a held-out query set.

</details>

**Follow-ups:** How would you cache this? Cross-encoder reranking; what about ingest cost?

**Difficulty:** Mid-senior

### Fix a hallucination

> "Fix a hallucination in this output."

**Where asked:** Reported live-coding exercise in the AI-engineer debrief · [source](https://www.reddit.com/r/deeplearning/comments/1swxb2k/i_did_15_ai_engineer_interviews_in_the_last_6/)

**What they're testing:** Whether you can debug the LLM call pipeline (retrieval quality, prompt grounding, model behavior).

<details>
<summary>💡 Strong answer</summary>

Diagnose in three steps: (1) is the retrieval returning the relevant chunk? Inspect top-k for query; if not, fix chunking or query rewrite, not the LLM. (2) is the chunk in context? If yes, prompt probably not grounded; reinforce "answer ONLY using the context" or use citation tokens. (3) did the model still fabricate? Constrain decoding (e.g., grammar-constrained outputs, lower temperature), or add a faithfulness classifier. Sequence = fix data, fix prompt, fix decoding, fix model. Avoid the trap of "add more knowledge" - usually the answer is observability plus prompt constraint.

</details>

**Follow-ups:** How would you monitor continuingly? How would you keep a guardrail?

**Difficulty:** Mid-senior

### Cut inference cost by 60%

> "Cut inference cost by 60% using a hybrid local/cloud setup with phi-3.5-mini and aggressive request caching."

**Where asked:** Reported AI-engineer architecture interview (no specific company tagged) in the 15-AI-engineer debrief · [source](https://www.reddit.com/r/deeplearning/comments/1swxb2k/i_did_15_ai_engineer_interviews_in_the_last_6/)

**What they're testing:** Cost reasoning at production scale.

<details>
<summary>💡 Strong answer</summary>

Architect: simple and short queries routed to phi-3.5-mini on local GPU; long-context and high-stakes queries routed to a hosted model with request-level cache + KV-cache reuse. Implement a semantic cache: embedding top-k similarity vs prior queries; on hit, return the cached answer; on miss, escalate. Budget alerts via tokens-per-minute. Surface observability so savings are visible per customer.

</details>

**Follow-ups:** When does this break? Latency budgets; cost-quality Pareto.

**Difficulty:** Mid-senior

### What LLM-native companies actually ask

> "What topics and questions are LLM/NLP-focused interviewers asking at places like Hugging Face, Scale, Perplexity?"

**Where asked:** r/MachineLearning LLM Interview Prep thread, still commonly referenced 2024-2026 · [source](https://www.reddit.com/r/MachineLearning/comments/1ein9vh/d_llm_interview_prep/); cross-company reports from [Scale AI ML Research Engineer](https://www.reddit.com/r/MachineLearning/comments/1qe1u5f/d_scale_ai_ml_research_engineer_interviews/) and [Hugging Face Paris 2024](https://www.glassdoor.com/Interview/Hugging-Face-Machine-Learning-Engineer-Interview-Questions-EI_IE6487302.0,12_KO13,38.htm)

**What they're testing:** Range and depth on transformer internals, tokenization, training stability, eval, deployment.

<details>
<summary>💡 Strong answer</summary>

Expect: tokenization & vocab choices; pretraining and continued pretraining trade-offs; instruction tuning and RLHF/DPO; attention math, KV cache, quantization; eval (BLEU/ROUGE, LLM-judges, human eval), scaling laws, MMLU/HELM-style benchmarks, retrieval-augmentation, agents. At Scale AI the coloring involves "ML concepts, LLMs, and debugging" together with PyTorch debugging (hyperparameters, transformer debugging, data pipeline preprocessing).

</details>

**Follow-ups:** Distillation; safety filtering; multi-modal.

**Difficulty:** Senior

---

## ML Coding

> **Genre intel:** Pandas transformations, SQL window functions and implement-from-scratch are table stakes across the board - but per the cross-company synthesis, coding-only preparation gets you rejected at senior levels. The 2026 "MLE 2.0" round set (per [Yuan Meng](https://www.yuan-meng.com/posts/mle_interviews_2.0/)) adds multi-level OOP toy systems and AI-assisted coding with an LLM in the loop.

### Third transaction of every user (SQL)

> "Write the third transaction of every user."

**Where asked:** Uber · Data Scientist · SQL round (~2025) · [source](https://igotanoffer.com/en/advice/uber-data-scientist-interview)

**What they're testing:** Window functions / ranking.

<details>
<summary>💡 Strong answer</summary>

`SELECT user_id, spend, transaction_date FROM (SELECT user_id, spend, transaction_date, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY transaction_date) AS rn FROM transactions) t WHERE rn = 3;` alternatively, third unique transaction date's spend summary. Discuss ties: DENSE_RANK vs ROW_NUMBER.

</details>

**Follow-ups:** Second-order follow-up on user-level history aggregation; using CTEs vs nested subqueries.

**Difficulty:** Mid

### Stadium with 3+ consecutive high-attendance days (SQL)

> "Find dates where a stadium had three or more consecutive days of attendance >=100."

**Where asked:** Netflix · Data Scientist · SQL "Transform & Analyze Data" coding (~2026) · [source](https://www.tryexponent.com/guides/netflix-data-scientist-interview)

**What they're testing:** Gaps-and-islands problem; window functions across days.

<details>
<summary>💡 Strong answer</summary>

Approach: self-join with day-1 and day-2 to find any day that is the third in a window of >=100. Or use ROW_NUMBER to assign each high-attendance day an island id, group by island, filter sum>=3. Discuss the storage and indexing assumption.

</details>

**Follow-ups:** Apply to a session-level retention problem.

**Difficulty:** Mid

### Top 3 unique salaries per department (SQL)

> "Find the top 3 unique salaries in each department and list all employees who have those salaries."

**Where asked:** Netflix · Data Scientist · SQL coding · [source](https://www.tryexponent.com/guides/netflix-data-scientist-interview)

**What they're testing:** Window functions, ranking, deduplication of salaries.

<details>
<summary>💡 Strong answer</summary>

`SELECT dept_id, emp_id, salary FROM (SELECT dept_id, emp_id, salary, DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rk FROM employees) t WHERE rk <= 3.` Discuss handling ties vs distinct salaries.

</details>

**Follow-ups:** Alternative with RANK vs DENSE_RANK; large-department scale plan.

**Difficulty:** Mid

### Push notifications before conversion

> "Write a function that returns total push notifications before user conversion from a user-event log."

**Where asked:** Uber · Data Scientist · SQL · [source](https://igotanoffer.com/en/advice/uber-data-scientist-interview)

**What they're testing:** Self-join plus aggregation; sequence ordering.

<details>
<summary>💡 Strong answer</summary>

LEFT JOIN user_events on (user_id) where event = 'notification' AND ts < convert_ts, group by user_id, count. Discuss whether push notifications before signup are eligible vs only after signup. Discuss server-time skew.

</details>

**Follow-ups:** Distribution output; cap at P95; sanity check.

**Difficulty:** Mid

### Logistic regression from scratch (Python)

> "Implement logistic regression from scratch (Python)."

**Where asked:** Common reported DS coding task across Amazon, Microsoft, Pinterest, Uber · [source](https://www.reddit.com/r/leetcode/comments/1jwond7/amazon_applied_scientist_interview_experience/)

**What they're testing:** Numerical stability, vectorization, gradient derivation.

<details>
<summary>💡 Strong answer</summary>

`def sigmoid(z): return 1/(1+np.exp(-z))`; `def loss(X,y,w): return -np.mean(y*np.log(sigmoid(X@w)+1e-9)+(1-y)*np.log(1-sigmoid(X@w)+1e-9))`; train via L-BFGS or batch GD. Discuss standardization, regularization, choice of threshold for calibration, AUC reporting.

</details>

**Follow-ups:** Add L1 regularization via proximal gradient; add class weighting; switch to mini-batch SGD.

**Difficulty:** Mid

### Cumulative weekly retention (SQL)

> "Design a SQL query to find the cumulative weekly retention of users."

**Where asked:** Pinterest · Data Scientist · first technical round · [source](https://www.reddit.com/r/DataScienceJobs/comments/1tzrc2p/pinterest_ds_interview_questions/)

**What they're testing:** Cohort analysis; lead/lag in window functions.

<details>
<summary>💡 Strong answer</summary>

GROUP BY cohort_week, then DATE_DIFF('week', cohort_week, activity_week) AS week_offset, COUNT(DISTINCT user_id) AS active_users. Compute retention = active_users / cohort_size. Discuss treating "seen within 7 days of cohort start" carefully to avoid off-by-one; discuss bots and gap-handling.

</details>

**Follow-ups:** How would you handle a stale-account segment?

**Difficulty:** Mid

### Cohort funnel in pandas

> "Implement a metric in pandas: cohort funnel from impression to click to purchase."

**Where asked:** Pinterest DS take-homes (~2024-2025) · [source](https://www.reddit.com/r/DataScienceJobs/comments/1tzrc2p/pinterest_ds_interview_questions/); also common in DS take-homes at Airbnb and Stripe

**What they're testing:** pandas fluency; groupby/pivot skills; null safety; idempotent transform.

<details>
<summary>💡 Strong answer</summary>

`def funnel(df): g = df.dropna(subset=['event']).groupby(['user_id','event']).size().unstack(fill_value=0); g['ctr'] = g.get('click',0) / g.get('impression',0); g['conv'] = g.get('purchase',0) / g.get('click',0); return g.mean()`; discuss handling de-duped sessions and the zero-impression edge case.

</details>

**Follow-ups:** Pivoting on multiple breakdowns; memory-effective groupby; using Modin/Polars for scale.

**Difficulty:** Mid

### Derive the logistic loss on a whiteboard

> "Derive logistic regression loss under a mildly constrained setting on the whiteboard."

**Where asked:** Pinterest · Data Scientist · onsite whiteboard session (reported Mar 16, 2026) · [source](https://www.glassdoor.com/Interview/Pinterest-Data-Scientist-Interview-Questions-EI_IE503467.0%2C9_KO10%2C24.htm)

**What they're testing:** End-to-end derivational fluency; connecting loss to a probability model.

<details>
<summary>💡 Strong answer</summary>

State MLE on Bernoulli given sigmoid; write NLL; show equivalence to cross-entropy; show the convexity argument (as in the MSE-non-convexity proof above). Discuss the constraint (e.g. weight budget on sum of weights) and how to Lagrange.

</details>

**Follow-ups:** Convergence guarantees under the constraint.

**Difficulty:** Senior

### Merge intervals plus ML fundamentals probe

> "A merge-interval style coding question, plus an ML fundamentals probe on Precision/Recall vs ROC-AUC and what perplexity means."

**Where asked:** Pinterest · MLE · phone screen (reported Mar 16, 2026) · [source](https://www.glassdoor.com/Interview/Pinterest-Data-Scientist-Interview-Questions-EI_IE503467.0%2C9_KO10%2C24.htm); corroborated by a [Pinterest ML phone-screen report on r/leetcode](https://www.reddit.com/r/leetcode/comments/1t51qpx/pinterest_ml_phone_interview_experience/)

**What they're testing:** LC-style coding under time pressure plus rapid-fire metric fluency in the same call.

**Difficulty:** Mid

### Two SQL plus one Python on trust & safety data

> "Trust & safety domain funnel in SQL with retention, plus a Python question on pandas dataframe transformation for CTR."

**Where asked:** Pinterest · Data Scientist · technical screen · [source](https://levelup.gitconnected.com/pinterest-interview-experience-data-scientist-3da5924f7cb6) (Level Up Coding, June 11, 2024)

**What they're testing:** Domain-flavored SQL funnels and pandas transforms in one sitting.

**Difficulty:** Mid

### Parse data and compute statistics

> "Parse data and compute statistics transformations (coding round); ML concepts, LLMs, and debugging (ML coding round)."

**Where asked:** Scale AI · ML Research Engineer · [source](https://www.reddit.com/r/MachineLearning/comments/1qe1u5f/d_scale_ai_ml_research_engineer_interviews/)

**What they're testing:** Data-wrangling fluency plus PyTorch/LLM debugging (hyperparameters, transformer debugging, data pipeline preprocessing).

**Difficulty:** Mid-senior

### OOP toy system (MLE 2.0 round)

> "Implement a toy system mimicking a database, a KV store, a chat room, a game."

**Where asked:** Reported as a 2026 "MLE 2.0" research-engineering round · [Yuan Meng, Feb 1 2026](https://www.yuan-meng.com/posts/mle_interviews_2.0/)

**What they're testing:** Multi-level OOP design under time pressure - a round that now sits alongside LC-style coding in research-eng loops.

**Difficulty:** Mid-senior

### AI-assisted coding (MLE 2.0 round)

> "Given a toy codebase plus unit tests, you are allowed to use an LLM to debug and complete the implementation."

**Where asked:** Reported as a 2026 "MLE 2.0" research-engineering round · [Yuan Meng, Feb 1 2026](https://www.yuan-meng.com/posts/mle_interviews_2.0/)

**What they're testing:** How you drive an LLM as a debugging tool - prompt hygiene, verification discipline, and knowing when the model is wrong.

**Difficulty:** Mid-senior

---

## Science Presentation

> **Rubric intel:** Amazon's "Science Presentation" / "Tech Talk" round is graded on a presentation rubric, not topic depth - the loop structure is documented on [amazon.jobs](https://amazon.jobs/content/en/how-we-hire/applied-scientist-interview-prep) and [IGotAnOffer](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview). Per the cross-company synthesis, candidates who can present a single project for 15 minutes and answer three probing follow-ups outperform candidates who ace coding rounds but can't narrate their work.

### The 15-20 minute science talk

> "Give a 15-20 minute presentation of a paper, project, or past applied work."

**Where asked:** Amazon · Applied Scientist · "Tech Talk" / Science Presentation round · [amazon.jobs](https://amazon.jobs/content/en/how-we-hire/applied-scientist-interview-prep) · [r/leetcode debrief](https://www.reddit.com/r/leetcode/comments/1jwond7/amazon_applied_scientist_interview_experience/); Duolingo DS ([Blind, Sep 2 2024](https://www.teamblind.com/post/duolingo-data-scientist-interview-bhgextxs)) and [Figma design challenges](https://www.reddit.com/r/FigmaDesign/comments/1jlg61e/figma_challenge_interview/) use similar structures

**What they're testing:** Communication to a science audience; ability to motivate, structure, and defend a contribution.

<details>
<summary>💡 Strong answer</summary>

Pick a project with measurable impact, internal or external. Structure: 1) the business/scientific motivation, 2) the gap in prior work, 3) the method in one slide (problem statement, objective, model/algorithm), 4) results with caveats and ablations, 5) operational consequences and what could break in production. Reserve 3-5 minutes for live Q&A. Anticipate the four "gotcha" questions: data leakage, generalization gap, label noise, infra cost.

</details>

**Follow-ups (actual reported):** "Why didn't you simply do X?" "What would you do next with 2 more weeks?" "How does this compare to SOTA?"

**Difficulty:** All levels - the rubric is a presentation rubric, not necessarily topic depth

### How did you debug your ML project?

> "Tell me about a past ML project deep in implementation: how did you debug it?"

**Where asked:** Amazon · Applied Scientist · Science Depth round; cross-company at Microsoft and Google · [source](https://www.reddit.com/r/leetcode/comments/1jwond7/amazon_applied_scientist_interview_experience/)

**What they're testing:** Engineering mechanics of an ML system; ability to walk through code-months of decisions in 45 minutes.

<details>
<summary>💡 Strong answer</summary>

Pick a project with a non-trivial decision timeline: a multi-month ranking model launch. Walk the listener through data assumptions, training, evaluation, and production surprises. Show how you instrumented, monitored, and pivoted when the held-out AUC didn't replicate to live, and how you connected a metric regression (e.g. SERP bounce rate) to a feature-embedding version skew.

</details>

**Follow-ups (often reported):** "How did you decide the production rollout was safe?" "What would you monitor post-launch?" "What was the biggest mistake?"

**Difficulty:** Senior

### Know your own project inside-out

> "Present a past data science project - and know your own project's technicalities in and out."

**Where asked:** Duolingo · Data Scientist · New Grad (Sep 2, 2024) · [source](https://www.teamblind.com/post/duolingo-data-scientist-interview-bhgextxs)

**What they're testing:** Depth-of-knowledge and storytelling.

<details>
<summary>💡 Strong answer</summary>

Choose a project that had technical risk and a measured outcome. Foreground the data pipeline, including how you handled missingness, drift, and backfills; the model, including what was attempted and abandoned; and the metric chain: how the model metric moved, then the business metric, then what you'd do differently. Practice with a friendly DS to time yourself - candidates commonly say the Blind readers warn "you have to know in and out of technicalities."

</details>

**Follow-ups:** "If your data shifted 5% tomorrow, what would you re-evaluate first?"

**Difficulty:** Mid

---

## Product & Metrics Cases

### Measure engagement for a productivity app

> "How would you measure engagement for a productivity app, including features or behaviors to track?"

**Where asked:** Netflix · Data Scientist · Product/Metrics case · [source](https://www.tryexponent.com/guides/netflix-data-scientist-interview)

**What they're testing:** Choice of north-star vs secondary metrics, anti-metric awareness.

<details>
<summary>💡 Strong answer</summary>

Pair a north-star with hygiene metrics. North-star: weekly active creators with one substantive artifact. Secondary: time-on-task completed without abandonment; feature-specific: list-edit rate, share frequency. Anti-metric: support tickets and privacy opt-outs - so engagement doesn't grow at the cost of trust. Decouple via dashboard slice: engagement vs retention vs satisfaction scores. Define features and behaviors to log at ingestion time so the metric isn't deadlock-locked.

</details>

**Follow-ups:** How would you avoid Goodhart's law?

**Difficulty:** Mid

### 1M users drop off at 6 months

> "Why are 1M users dropping off around 6 months after signing up, and how would you address it?"

**Where asked:** Netflix · Data Scientist · product case · [source](https://www.tryexponent.com/guides/netflix-data-scientist-interview)

**What they're testing:** Diagnose a funnel decay; frame an investigation as a series of falsifiable hypotheses.

<details>
<summary>💡 Strong answer</summary>

Hypothesis space: (1) user-mix drift (new cohorts are different), (2) experiential decay (the novelty fades), (3) hard friction at the 6-month mark (e.g. renewal/billing/algorithm getting noisier), (4) external (competitor ads). Triangulate via cohort breakdown, monthly subscription-elasticity curve, feature-use heatmap, and a counterfactual holdout where you intervene with a 6-month nudge. Pick a low-cost experiment: send a re-engagement nudge to a 5% slice; measure 30-day retention delta.

</details>

**Follow-ups:** What would you measure for retention re-engagement?

**Difficulty:** Mid

### Investigate a 15% CTR drop

> "A 15% click-through-rate decrease shows up on the new ranking. Investigate."

**Where asked:** Netflix · Data Scientist · case · [source](https://www.tryexponent.com/guides/netflix-data-scientist-interview)

**What they're testing:** Triage speed; breadth of plausible causes.

<details>
<summary>💡 Strong answer</summary>

First, instrument: did the model roll out cleanly to 100%? Did server latency shift? Second, segmentation: where is it 15%? Vertical, country, browser, time-of-day? Third, ablations: did the click position change (position bias)? Did the model prefer new content (novelty) or did personalization break (skew in feature embedding)? Fourth, ranking diagnostics: side-by-side NDCG on a recent batch; check if rankings are still differentiating or if a tie-breaking rule now dominates. Decide: ship rollback vs side-by-side test.

</details>

**Follow-ups:** How would you ship a fix without breaking trust in the experimentation platform?

**Difficulty:** Senior

### Classify products into categories

> "How would you classify products into categories and sub-categories?"

**Where asked:** Amazon · Applied Scientist · Business Case round (~2025) · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview)

**What they're testing:** Taxonomy + ML system design.

<details>
<summary>💡 Strong answer</summary>

Two-stage approach: (1) hierarchical zero-shot or few-shot LLM-based candidate category generation with retrieval over the existing taxonomy; (2) supervised classifier trained on human-labeled examples at each level, optionally using embedding features. Maintain a feedback loop for ambiguous cases routed to humans (active learning). Evaluate against held-out labeled set; A/B online against current heuristic on the share-of-misclassification metric.

</details>

**Follow-ups:** Multi-label extension; new categories that humans haven't yet labeled.

**Difficulty:** Depth (L5+)

---

## Behavioral

> **Rubric intel:** Behavioral questions in science loops are tied to Amazon's Leadership Principles. [IGotAnOffer's 2026 LP guide](https://igotanoffer.com/en/advice/amazon-leadership-principles) lists 60+ LP-tagged prompts (Ownership, Bias for Action, Customer Obsession, Dive Deep, Have Backbone / Disagree & Commit, Frugality, Earn Trust) with STAR instruction, and the [Bar Raiser round](https://igotanoffer.com/blogs/tech/amazon-behavioral-interview) is grounded in these and described as making the actual hire/no-hire call. Rehearse three STAR stories per principle.

### Outside-the-box simplification (Invent & Simplify)

> "Tell me about a time when you had to use outside-the-box thinking to simplify a task."

**Where asked:** Amazon · behavioral round · Invent & Simplify LP prompt · [source](https://www.reddit.com/r/leetcode/comments/1goesa7/need_tips_for_behavioral_part_in_amazon_sde_1/); corroborated across Amazon AS behavioral in the [LP question bank](https://igotanoffer.com/en/advice/amazon-leadership-principles)

**What they're testing:** Whether you can deliver impact without growing the system; simplicity as a first-class value.

<details>
<summary>💡 Strong answer</summary>

STAR. Situation: a 6-week-each-quarter compliance review was consuming the team. Task: cut wall-clock time. Action: I replaced a per-row manual inspection with a deterministic slice + 5-row random sample validated by an LLM with a templated prompt; refactored the report generator from 12 ad-hoc scripts into one parametrized script. Result: review time fell from 110 to 26 hours per quarter, with zero missed compliance issues.

</details>

**Follow-ups:** "What did you give up?" "What got harder?"

**Difficulty:** All levels

### Company vs client interests misaligned

> "Tell me about a time when the company's interest and the client's interest were not aligned."

**Where asked:** Amazon · Applied Scientist · Bar Raiser (~2025) · [source](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview)

**What they're testing:** Ethical judgment; Earn Trust / Customer Obsession balance.

<details>
<summary>💡 Strong answer</summary>

STAR. A vendor partner wanted to disproportionately harm a low-margin product line in a co-marketing deal; I surfaced it with a forecast of unit-economics and proposed a tiered inventory swap that preserved both the partnership and the catalog breadth we promised customers. Result: partner's adoption stayed flat and our long-tail retention improved 4%.

</details>

**Follow-ups:** How would you effect change without authority?

**Difficulty:** All levels

### Delivered something customers didn't know they needed

> "Tell me about a time you delivered something for a customer that they didn't know they needed."

**Where asked:** Amazon · Applied Scientist · Bar Raiser (~2025) · [source](https://www.reddit.com/r/leetcode/comments/1jwond7/amazon_applied_scientist_interview_experience/)

**What they're testing:** Customer Obsession LP at L6+.

<details>
<summary>💡 Strong answer</summary>

STAR. Buyer-survey data showed repeat-cart abandonment; we hypothesized that preempting address-time uncertainty would lift 7-day repurchase. Action: I built a "saved delivery addresses" feature tied to anonymized server-side geofences. Customer outcome: 7-day repurchase +6.4%; engineering outcome: dropped future re-engagement campaign need.

</details>

**Follow-ups:** How would you de-risk this in a smaller market?

**Difficulty:** Senior

### Missing a long-term commitment (Ownership)

> "Tell me about a time you realized you would not meet a long-term commitment and how you navigated it."

**Where asked:** Amazon · Applied Scientist · Bar Raiser · [LP question bank](https://igotanoffer.com/en/advice/amazon-leadership-principles) · [IGotAnOffer AS guide](https://igotanoffer.com/en/advice/amazon-applied-scientist-interview)

**What they're testing:** Ownership LP.

<details>
<summary>💡 Strong answer</summary>

STAR. I was the sole owner of an annual forecast rollout; an acquisition delayed data feeds. I communicated the shift early to stakeholders, refactored the deliverable into a phased delivery (baseline in week 6, scenarios in week 10, final in week 14), and pulled in a contractor for QA. Result: trust preserved and the final artifact landed two weeks behind, not three.

</details>

**Follow-ups:** What would you do if the new plan failed?

**Difficulty:** All levels

### Technical deep-dive on an issue (Dive Deep)

> "Tell me about a time you had to give a technical deep-dive (Dive Deep) on an issue."

**Where asked:** Amazon · Applied Scientist · Bar Raiser · [source](https://igotanoffer.com/en/advice/amazon-leadership-principles)

**What they're testing:** Dive Deep LP - the ability to go deep technically on a customer-facing issue.

<details>
<summary>💡 Strong answer</summary>

STAR. A spike in checkout error rate correlated with an ML feature-version skew. I instrumented the data pipeline, isolated the divergence to a delayed feature-cache rebuild, and crafted a one-paragraph play on cache invocation that we applied that day. Result: MTTR fell from days to hours; we added a proactive alert.

</details>

**Follow-ups:** How did you detect the issue?

**Difficulty:** Senior

### Urgent decision with incomplete information (Bias for Action)

> "Tell me about a time you had to make an urgent decision with incomplete information."

**Where asked:** Amazon · Applied Scientist · Bar Raiser · [source](https://igotanoffer.com/en/advice/amazon-leadership-principles)

**What they're testing:** Bias for Action - speed without recklessness.

<details>
<summary>💡 Strong answer</summary>

STAR. Trust & Safety spike on a category at 02:00. I convinced on-call to roll back a recent model update and run a synthetic holdout. Decision reversed vs the on-call default of waiting six hours; in the morning data confirmed the rollback was correct. The action set a new convention: any model roll-out at off-hours requires a rollback kernel ready before push.

</details>

**Follow-ups:** What would you have done if you'd been wrong?

**Difficulty:** Mid-senior

### Disagreeing with your manager

> "Tell me about a time when you disagreed with your manager's decision."

**Where asked:** Netflix · Data Scientist · behavioral · [source](https://www.tryexponent.com/guides/netflix-data-scientist-interview); Amazon Have Backbone / Disagree & Commit · [LP question bank](https://igotanoffer.com/en/advice/amazon-leadership-principles)

**What they're testing:** Direct conflict management; ability to commit after disagreement.

<details>
<summary>💡 Strong answer</summary>

STAR. Manager proposed A/B-testing a UX rework. I thought the team could learn more from a holdback. I assembled a 1-page tradeoff, the manager agreed; we did a 4-week holdback plus parallel A/B. Learning: rework had heterogeneous effects the A/B alone hid.

</details>

**Follow-ups:** What happens after disagreement if data comes back ambiguous?

**Difficulty:** All levels

### Your ML approach didn't work

> "Describe a time when your initial ML approach didn't work and you had to pivot."

**Where asked:** Microsoft · Applied Scientist · 2026 HireReady guide · [source](https://www.gethireready.com/interview-guides/applied-scientist-microsoft)

**What they're testing:** Growth mindset + accountability.

<details>
<summary>💡 Strong answer</summary>

STAR. Initial XGBoost model on a feature-table hit a plateau near AUC 0.78. I investigated and realized the bottleneck was feature freshness, not model capacity. We built an online feature store with 1-minute freshness and consolidated features; a simple linear model on the new features reached AUC 0.84 live, less than a month after the pivot.

</details>

**Follow-ups:** "How did you sell the pivot?"

**Difficulty:** Mid

---

## Which companies ask what

Compiled from the same 2024-2026 candidate reports. If a company is absent in a row, no 2024-2026 candidate report naming that genre for that company was found.

| Theme | Amazon | Microsoft | Google | Netflix | Uber | Airbnb | Pinterest | Stripe | Scale | Hugging Face |
|--|--|--|--|--|--|--|--|--|--|--|
| Bias/variance | ✅ breadth | ✅ | ✅ | ✅ | ✅ | implied | ✅ | ✅ | ✅ | - |
| L1 vs L2 | ✅ depth | ✅ | ✅ | - | - | - | - | - | - | - |
| Bagging/boosting | ✅ breadth | ✅ | - | - | - | - | - | - | - | - |
| Imbalance/metrics | ✅ breadth | ✅ | ✅ | ✅ | - | - | ✅ | ✅ | ✅ | - |
| A/B design + power | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - |
| Sequential testing | ✅ | - | - | ✅ | - | implied | - | - | - | - |
| RAG vs fine-tune | - | ✅ | ✅ | - | - | - | - | - | ✅ | ✅ |
| LLM debugging live coding | implied | - | - | - | - | - | - | - | ✅ | ✅ |
| pandas / SQL | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - |
| Implement-from-scratch | ✅ | ✅ conv2d | ✅ | - | - | - | ✅ derivation | - | - | - |
| ML system design / infra | ✅ | ✅ | ✅ | - | - | - | - | - | ✅ | - |
| Behavioral LP | 16 LPs | MSFT LP | implied | ✅ | ✅ | - | - | - | - | - |

**How to not fail this loop** (from the cross-company synthesis of all reports above):

- **Breadth-only = rejection at L4.** Amazon tests breadth across phone screen, breadth round, and Bar Raiser; weakness on bias/variance when asked live drops you out.
- **Depth-only = looks like a researcher who can't ship.** The business-case round requires end-to-end applied judgment.
- **Coding-only = rejection at senior.** Conv2d-from-scratch and pandas transforms are table stakes; they cannot carry you alone.
- **Product-metric-only = looks like an analyst who can't build models.** The full A/B prompt with clustering, SRM, sequential monitoring and a ship/no-ship call is the highest-fidelity signal of an integrated DS researcher.

---

<div align="center">

**Practice these out loud. [Landed](https://landed.jobs) runs voice mock interviews that grill you on exactly these questions — plus daily matched AI roles and agent-drafted application answers.**

[![Get Started](https://img.shields.io/badge/Get%20Started%20Free-→-6C2BD9?style=for-the-badge)](https://landed.jobs)

<sub>Every question traces to a public candidate report — sources inline. Asked something new recently? PRs welcome. · [All banks →](../README.md)</sub>

</div>
