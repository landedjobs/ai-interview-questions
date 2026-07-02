#!/usr/bin/env python3
"""Render README.md (the index) from the bank files in banks/.
Run after adding or editing banks: python3 build_index.py
"""
import re
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = "https://landed.jobs"
ORG = "https://github.com/landedjobs"

BANKS = [
	("llm-and-ml-concepts", "🧠", "LLM & ML Concepts",
	 "Transformers, fine-tuning, RAG, agents, evals, inference, classic ML breadth — the knowledge round."),
	("coding-and-system-design", "💻", "Coding & ML System Design",
	 "Implement attention from scratch, build a RAG app, design an LLM serving stack — the hands-on rounds."),
	("frontier-ai-labs", "🚀", "Frontier AI Labs",
	 "What OpenAI, Anthropic, DeepMind, xAI, Mistral, Meta and Cohere actually ask, by lab and by round."),
	("fde-product-and-gtm", "🤝", "FDE, AI Product & GTM",
	 "Decomposition cases, customer scenarios, product sense and GTM engineering — the customer-facing loops."),
	("data-and-applied-science", "📊", "Data & Applied Science",
	 "ML breadth/depth, experimentation, applied LLM and science presentations — Amazon AS loops and beyond."),
]


# Curated marquee questions (bank slug, anchor, label, one-line hook). Anchors match the
# numbered headings the build script generates.
TOP = [
	("frontier-ai-labs", "6-the-mission-contradiction-test", "The mission-contradiction test", "Anthropic's values round — the #1 documented reason strong candidates get rejected"),
	("coding-and-system-design", "8-debug-a-transformer-with-4-failing-tests-then-train-a-classifier-openai", "Debug a transformer with 4 failing tests, then train a classifier", "OpenAI's real coding screen, not LeetCode"),
	("fde-product-and-gtm", "2-reduce-airport-security-wait-times", "Reduce airport security wait times", "The Palantir decomposition round, worked end to end"),
	("llm-and-ml-concepts", "5-what-is-kv-cache-and-how-does-it-speed-up-inference", "What is a KV cache and how does it speed up inference?", "Asked everywhere; most candidates fumble the memory math"),
	("coding-and-system-design", "5-implement-flashattention-style-tiled-attention", "Implement FlashAttention-style tiled attention", "Mistral / infra-lab favorite"),
	("frontier-ai-labs", "4-walk-me-through-your-favorite-paper", "Walk me through your favorite paper", "The research-taste round, and how it's actually graded"),
	("data-and-applied-science", "5-metric-choice-for-a-01-positive-fraud-model", "Metric choice for a 0.1%-positive fraud model", "The Amazon Applied Scientist breadth trap"),
	("llm-and-ml-concepts", "14-dpo-vs-rlhfppo-when-would-you-pick-each", "DPO vs RLHF/PPO — when would you pick each?", "Post-training's most-asked comparison"),
	("fde-product-and-gtm", "8-the-deployment-slipped-by-three-weeks-tell-the-customers-cto", "The deployment slipped three weeks — tell the customer's CTO", "The customer-scenario round FDEs live or die on"),
	("data-and-applied-science", "12-transformer-vs-gradient-boosted-trees-on-tabular-data", "Transformer vs gradient-boosted trees on tabular data", "The depth probe that separates real practitioners"),
]


def stats(slug: str):
	p = HERE / "banks" / f"{slug}.md"
	if not p.exists():
		return None
	text = p.read_text(encoding="utf-8")
	m = re.search(r"badge/(\d+)%20real%20questions", text)
	return int(m.group(1)) if m else len(re.findall(r"(?m)^### ", text))


def main():
	today = datetime.now(timezone.utc).strftime("%Y.%m")
	rows, total, live = [], 0, 0
	for slug, emoji, title, sub in BANKS:
		n = stats(slug)
		if n is None:
			rows.append(f"| {emoji} | **{title}** | {sub} | 🔜 |")
		else:
			rows.append(f"| {emoji} | **[{title}](banks/{slug}.md)** | {sub} | **{n}** |")
			total += n
			live += 1
	table = "| | Bank | What's inside | Questions |\n|---|---|---|---:|\n" + "\n".join(rows)

	top_rows = "\n".join(
		f"- **[{label}](banks/{slug}.md#{anchor})** — {note}"
		for slug, anchor, label, note in TOP
		if (HERE / "banks" / f"{slug}.md").exists()
	)

	readme = f"""<a name="top"></a>

<div align="center">

<a href="{SITE}"><img src="https://static.b100x.ai/email/landed-wordmark.png" alt="Landed" width="200"></a>

<img src="https://static.b100x.ai/github-repos/images/ai-interview-questions/banner.svg" alt="AI Interview Questions" width="100%">

![Questions](https://img.shields.io/badge/{total}%20real%20questions-ff5b29?style=flat-square) ![Banks](https://img.shields.io/badge/{live}%20question%20banks-6C2BD9?style=flat-square) ![Updated](https://img.shields.io/badge/updated-{today}-00A86B?style=flat-square) [![Stars](https://img.shields.io/github/stars/landedjobs/ai-interview-questions?style=social)]({ORG}/ai-interview-questions)

**{total}+ questions actually asked in AI interviews — with where they were asked, what's being tested, and the answer a strong candidate gives.**

No invented "top 50 questions" filler: every entry traces to a public candidate report, and the answers are hidden behind spoilers so you can attempt first.

</div>

---

## The banks

{table}

## ⭐ Start with these 10

The marquee questions — a mix of the most-asked and the most-distinctive. Each links straight into the bank, answer hidden behind a spoiler so you can attempt it first.

{top_rows}

## How to use this repo

1. **Pick the bank for your next round** — knowledge screen → Concepts; practical → Coding & Design; a specific lab → Frontier Labs.
2. **Attempt before opening the 💡 spoiler.** Saying an answer out loud beats reading ten of them.
3. **Chase the sources.** Each question links to the original report — the surrounding thread often has grading detail we couldn't fit.

## ➕ Add a question you were asked

Interviewed recently? The best questions come from people fresh out of the loop. [Open an "Add a question" issue →]({ORG}/ai-interview-questions/issues/new?template=add-question.yml) with the question, where it was asked, and a source if you have one — or open a PR editing the relevant bank. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Related

Part of the [Landed]({SITE}) AI-native job-search family:

- 🧭 [awesome-ai-native-jobs]({ORG}/awesome-ai-native-jobs) — the umbrella that maps the whole AI-native job landscape
- 📘 [ai-interview-guides]({ORG}/ai-interview-guides) — 33 company-by-company interview guides
- 🔥 [whos-hiring-in-ai]({ORG}/whos-hiring-in-ai) — real hiring posts from founders on X
- 💸 [recently-funded-ai-startups-hiring]({ORG}/recently-funded-ai-startups-hiring) — fresh-capital startups staffing up now
- 🚀 [ai-engineer-jobs]({ORG}/ai-engineer-jobs) — 300 live AI engineer roles, auto-updated
- 🤝 [forward-deployed-engineer-jobs]({ORG}/forward-deployed-engineer-jobs) — FDE & customer-facing engineering
- 📈 [gtm-engineer-jobs]({ORG}/gtm-engineer-jobs) — GTM engineering roles
- 🎓 [ai-fellowships-and-residencies]({ORG}/ai-fellowships-and-residencies) — 75 fellowships, residencies & programs
- 🧪 [projects-to-land-an-ai-job]({ORG}/projects-to-land-an-ai-job) — portfolio projects that actually get you hired
- 📦 [ai-engineer-portfolio-projects]({ORG}/ai-engineer-portfolio-projects) — 80+ buildable portfolio projects
- 🗺️ [ai-product-engineer-roadmap]({ORG}/ai-product-engineer-roadmap) — the AI product engineer roadmap
- 🎯 [become-a-gtm-engineer]({ORG}/become-a-gtm-engineer) — the GTM engineer roadmap

---

<div align="center">

**Practice these out loud. [Landed]({SITE}) runs voice mock interviews that grill you on exactly these questions — plus daily matched AI roles and agent-drafted application answers.**

[![Get Started](https://img.shields.io/badge/Get%20Started%20Free-→-6C2BD9?style=for-the-badge)]({SITE})

<sub>Every question traces to a public candidate report — sources inline in each bank. Asked something new recently? PRs welcome. · maintained by <a href="{SITE}">Landed</a></sub>

</div>
"""
	(HERE / "README.md").write_text(readme, encoding="utf-8")
	print(f"index: {live}/{len(BANKS)} banks, {total} questions")


if __name__ == "__main__":
	main()
