# 09 — GIT POLICY

## 1. Purpose

This document defines safe Git behavior for AI-assisted work.

## 2. Before Work

Before modifying files, run:

```bash
git status --short
```

Record whether the working tree is clean.

If the working tree contains unrelated human changes, do not overwrite them.

## 3. During Work

The executor must:

- avoid broad formatting changes;
- avoid unrelated edits;
- avoid deleting files;
- avoid moving files unless task explicitly requires it;
- keep diffs small;
- check diff before reporting completion.

## 4. After Work

Run:

```bash
git diff --name-only
git diff --stat
```

If tests were required, run targeted tests.

If docs-only, report that no runtime validation was required.

## 5. Forbidden Git Operations

The AI executor must not run:

```bash
git reset --hard
git clean -fd
git push
git checkout -- .
git rebase
git merge
git commit
```

unless explicitly instructed by the human operator.

## 6. Commit Policy

The AI executor should not commit by default.

The human operator decides when to commit.

If asked to suggest commit messages, use:

```text
type(scope): concise summary
```

Examples:

```text
docs(ai): add governance control framework
test(delta): add regression coverage for gone transitions
fix(api): correct dealer stats null handling
```

## 7. Diff Review Requirement

Every task report must include:

- changed files;
- why each file changed;
- whether change was allowed;
- validation run;
- risk remaining.
