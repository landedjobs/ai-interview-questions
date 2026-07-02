# Contributing

Every question here was reported by a real candidate, with a source. Help us keep it that way.

## 1. Suggest a question (easiest)

[Open an "Add a question" issue →](https://github.com/landedjobs/ai-interview-questions/issues/new?template=add-question.yml) with:
- the **question** (as close to verbatim as you can),
- **where** it was asked (company, role, round),
- a **source** if there is one (Glassdoor/Blind/Reddit/blog) — first-hand ("I was asked this in my Aug 2026 loop") is great too.

## 2. Open a PR

Pick the right bank in `banks/`:
- `llm-and-ml-concepts.md` — knowledge/theory
- `coding-and-system-design.md` — hands-on exercises + ML system design
- `frontier-ai-labs.md` — OpenAI/Anthropic/DeepMind/etc.
- `fde-product-and-gtm.md` — forward-deployed, product, GTM
- `data-and-applied-science.md` — DS / applied-scientist / MLE

Follow the existing question format: a numbered `### N. Title`, the question as a blockquote, **Where asked** with a source link, **What they're testing**, the answer inside `<details><summary>💡 Strong answer</summary>…</details>`, then **Follow-ups** and **Difficulty**.

The numbering and per-bank counts are regenerated — after adding questions, run `python3 build_index.py` to refresh the index totals. You don't need to renumber by hand (a maintainer runs the numbering pass).

## What we won't merge

Invented "top interview questions" with no source, textbook definitions dressed up as interview questions, or anything you can't tie to a real loop. The whole point of this repo is that it's real.

Thanks. 🙏
