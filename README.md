# Deploy Axiom plugins for Claude Code

**Axiom Office for Claude** (In build. Not released yet.) One orchestrator, a team of specialists you can see but not talk past, and your rules enforced as code.

- Discovery decides the team.
- One front door: you talk only to the orchestrator, which alone holds sensitive data.
- Every send, refusal and run leaves a receipt.

[Talk to Deploy Axiom](https://deployaxiom.com)

## The parts it is built from

Ten plugins for Claude Code, each with a Hermes Agent original. Each one installs on its own.

Add the whole catalog once, then install any part by name:

```
claude plugin marketplace add percyhendrux123-prog/axiom-plugins
claude plugin install axiom-gatekeeper@deploy-axiom
```

Tags: **skill**: Instructions Claude loads when the task matches. No code runs. **hook**: A script Claude Code runs on an event, such as before a tool call. **mod**: JavaScript that runs inside Claude Code.

## Owner controls

### Gatekeeper (`axiom-gatekeeper`)

Checks outbound messaging calls against your own rules (STOP, consent, quiet hours, no double-texting, approved wording) before they run, and holds or denies the call when a check fails.

- Mechanism: hook
- Install from GitHub
- Hermes Agent original: [hermes-gatekeeper](https://github.com/percyhendrux123-prog/hermes-gatekeeper)
- [Repository folder](https://github.com/percyhendrux123-prog/hermes-gatekeeper/tree/main/claude-plugin/gatekeeper) · [README](https://github.com/percyhendrux123-prog/hermes-gatekeeper/blob/main/claude-plugin/gatekeeper/README.md)

```
claude plugin install axiom-gatekeeper@deploy-axiom
```

### Standing (`axiom-standing`)

Keeps a local record of checks that passed or failed, refuses to mark a task done until a check passes, and asks for approval when an agent acts above its level.

- Mechanism: mod
- Install from GitHub
- Hermes Agent original: [hermes-standing](https://github.com/percyhendrux123-prog/hermes-standing)
- [Repository folder](https://github.com/percyhendrux123-prog/hermes-standing/tree/main/claude-plugin/standing) · [README](https://github.com/percyhendrux123-prog/hermes-standing/blob/main/claude-plugin/standing/README.md)

```
claude plugin install axiom-standing@deploy-axiom
```

### Tripwire (`axiom-tripwire`)

Writes one private log line each time Claude Code refuses a tool call. It only observes: it never blocks, approves or changes a call.

- Mechanism: hook + mod
- Install from GitHub
- Hermes Agent original: [hermes-tripwire](https://github.com/percyhendrux123-prog/hermes-tripwire)
- [Repository folder](https://github.com/percyhendrux123-prog/hermes-tripwire/tree/main/claude-plugin/tripwire) · [README](https://github.com/percyhendrux123-prog/hermes-tripwire/blob/main/claude-plugin/tripwire/README.md)

```
claude plugin install axiom-tripwire@deploy-axiom
```

### Run Receipts (`axiom-run-receipts`)

Writes one private receipt per session or headless run: when it ran, how many tool calls were seen, how many were reported as failed, and how the run ended.

- Mechanism: hook
- Install from GitHub
- Hermes Agent original: [hermes-run-receipts](https://github.com/percyhendrux123-prog/hermes-run-receipts)
- [Repository folder](https://github.com/percyhendrux123-prog/hermes-run-receipts/tree/main/claude-plugin/run-receipts) · [README](https://github.com/percyhendrux123-prog/hermes-run-receipts/blob/main/claude-plugin/run-receipts/README.md)

```
claude plugin install axiom-run-receipts@deploy-axiom
```

### Declines (`axiom-declines`)

Remembers a permission request you declined and stops Claude Code asking for the same thing again.

- Mechanism: mod
- Install from GitHub
- Hermes Agent original: [hermes-declines](https://github.com/percyhendrux123-prog/hermes-declines)
- [Repository folder](https://github.com/percyhendrux123-prog/hermes-declines/tree/main/claude-plugin/declines) · [README](https://github.com/percyhendrux123-prog/hermes-declines/blob/main/claude-plugin/declines/README.md)

```
claude plugin install axiom-declines@deploy-axiom
```

## Working style

### Axioma (`axiom-axioma`)

Colors the few phrases in Claude's reply that deserve a second look, and shows an advisory card before a send, spend, spin or scrub call. Advice only, never consent.

- Mechanism: mod
- Install from GitHub
- Hermes Agent original: [hermes-axioma](https://github.com/percyhendrux123-prog/hermes-axioma)
- [Repository folder](https://github.com/percyhendrux123-prog/hermes-axioma/tree/main/claude-plugin/axioma) · [README](https://github.com/percyhendrux123-prog/hermes-axioma/blob/main/claude-plugin/axioma/README.md)

```
claude plugin install axiom-axioma@deploy-axiom
```

### Chiron (`axiom-chiron`)

Reads how much you know about a topic from your own words, with no model call, and adds one short note per turn telling Claude how to talk to you. Off until you turn it on.

- Mechanism: hook
- Install from GitHub
- Hermes Agent original: [hermes-chiron](https://github.com/percyhendrux123-prog/hermes-chiron)
- [Repository folder](https://github.com/percyhendrux123-prog/hermes-chiron/tree/main/claude-plugin/chiron) · [README](https://github.com/percyhendrux123-prog/hermes-chiron/blob/main/claude-plugin/chiron/README.md)

```
claude plugin install axiom-chiron@deploy-axiom
```

### Axiom Agent (`axiom-agent`)

The nine-article Axiom Doctrine as two skills, plus a status report of which articles have an enabled enforcer plugin. It enforces nothing itself.

- Mechanism: skill
- Install from GitHub
- Hermes Agent original: [hermes-axiom-agent](https://github.com/percyhendrux123-prog/hermes-axiom-agent)
- [Repository folder](https://github.com/percyhendrux123-prog/hermes-axiom-agent/tree/main/claude-plugin/axiom-agent) · [README](https://github.com/percyhendrux123-prog/hermes-axiom-agent/blob/main/claude-plugin/axiom-agent/README.md)

```
claude plugin install axiom-agent@deploy-axiom
```

## Fitness

### Axiom Coach (`axiom-coach`)

Skills for working a coach's desk and a self-serve plan through the open coach app's own connector, plus the three Lite calculators as written rules.

- Mechanism: skill
- Directory: in review
- Hermes Agent original: [hermes-axiom-coach](https://github.com/percyhendrux123-prog/hermes-axiom-coach)
- [Repository folder](https://github.com/percyhendrux123-prog/hermes-axiom-coach/tree/main/claude-plugin/coach) · [README](https://github.com/percyhendrux123-prog/hermes-axiom-coach/blob/main/claude-plugin/coach/README.md)

```
claude plugin install axiom-coach@deploy-axiom
```

### Axiom Coach Lite Tools (`axiom-coach-lite`)

Three local calculators: a training split, daily macro targets (five health questions first), and a cardio calorie estimate. No network, no files.

- Mechanism: mod
- Install from GitHub
- Hermes Agent original: [hermes-axiom-coach](https://github.com/percyhendrux123-prog/hermes-axiom-coach)
- [Repository folder](https://github.com/percyhendrux123-prog/hermes-axiom-coach/tree/main/claude-plugin/lite) · [README](https://github.com/percyhendrux123-prog/hermes-axiom-coach/blob/main/claude-plugin/lite/README.md)

```
claude plugin install axiom-coach-lite@deploy-axiom
```

## Before you install

- Hook and mod plugins run code with your permissions. Each README has a “Before you install” section that lists what the plugin reads, writes and calls.
- Plugins with hooks, scripts or mods are not eligible for Anthropic’s plugin directory until the publisher is verified, so they install from GitHub.
- Not affiliated with or endorsed by Anthropic.

## About this repository

This repository holds only the catalog: `.claude-plugin/marketplace.json`, which lists each plugin from its own repository (a `git-subdir` source), and the catalog page in `docs/`. The plugins live in their own repositories. To regenerate the generated files after editing `data/plugins.json`, run `python3 scripts/build.py`.

Fonts in `docs/fonts` are Geist and IBM Plex Mono, both SIL Open Font License; the licenses sit beside them.

Deploy Axiom · deployaxiom.com · MIT licensed
