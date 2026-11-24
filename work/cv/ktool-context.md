# Ktool: context from Art (for picking CV content, not CV text)

Told by Art on 2026-11-24 while drafting the Ktool position. Background so
the CV can pick the right highlights; most of this does not go in the CV.

## Starting point (joined ~Nov 2025)

- Joined about a year ago as a **founding engineer**, together with a friend.
- The product existed as a working prototype: a **desktop app for sailing
  performance analysis**, written in **PyQt**. Extremely buggy.
- It had some kind of server, but most calculations ran on the front end
  (client side).

## Founders

- One founder is a sailing coach with many accolades and a world champion.
- The other is a physicist who owns all the algorithms behind the analysis.
- Neither is a software engineer. Art and his friend joined to turn the
  prototype into a product.

## Art's primary goal

- Turn it into a modern application with a **client-server architecture**,
  server in **Python**.
- Why Python: the existing code base was PyQt and much of the code used
  NumPy, so Python was the natural trajectory.
- Planned as a staged migration.

## Team split

- Art: backend (primarily, especially early on). His friend: frontend.

## Stage 1: isolate the calculation engine (black box)

- Goal: find the code in the prototype that does the calculations and
  isolate it as much as possible into a black box (no matter how good or bad
  the code inside is) that can be plugged into the existing system.
- Done by Art on the backend, with the friend on the frontend.
- Rolled out in **about two months**.

## Stage 2: "worker", a calculation framework built from scratch

- Next step: extract the real core of the black box into a new, workable
  structure.
- That structure, called **worker**, is a framework Art designed,
  architected and built from scratch.
- Works like Gradle's dependency resolution: a **directed acyclic graph**
  where each node is a calculation step. A node is either reused and cached,
  or a pure calculation that runs on the inputs it depends on.
- Inputs are the files users upload: data from different trackers, GPS and
  position.

### Worker ingestion pipeline (step 1, produces the tier 0 parquet)

1. **Input:** one file or a set of files from a tracker. Many tracker
   brands, so many formats are supported.
2. **Format detection**, then the matching **format-specific parser**.
3. **Normalization:** the raw data frame is mapped to a predefined set of
   expected fields. **Aliases** map fields that mean the same thing but are
   named differently by different trackers. Result: a standard,
   **platform-agnostic data frame**.
4. **Enrichment:** weather data fetched from the network is added.
5. **Derivation:** fields such as speed and course are calculated from the
   data.
6. **Storage:** saved as **Parquet** to **S3**. Immutable from then on,
   except through a migration.
7. This **tier 0 parquet** is what the later parts of worker work on.

### Worker calculation graph (step 2)

- **Inputs:** the tier 0 parquet plus analysis parameters, e.g. manually
  entered wind direction, maneuver sensitivity, and others.
- The track and parameters go into a **graph**. Each node is an
  **artifact**: a piece of calculation code.
- The graph is built ahead of time: nodes fire in an order fixed at build
  time, and the build **checks for cycles**.
- The built graph is run by the worker: it reads the parquet and computes
  each node; outputs of one node feed others.
- **Caching:** each node has a **hash-based identity** made of the version
  of its code and the parameters that actually affect it. A parameter that
  never reaches a node does not change its hash, so changing that parameter
  does not force a recalculation.
- Result: only the parts of the graph affected by a parameter change or a
  code version change are recalculated.
- Nodes that are **expensive to store but cheap to compute are never
  cached**; they are always recalculated on demand.
- **Outputs** go to the frontend and to the **AI report**.

## AI report: the most important feature (Art says)

Art calls this the most important part of the whole project.

- **Problem:** the analytics interface felt overwhelming to an average
  sailor who is not into data analysis.
- **Goal:** explain what is on the screen and help users make decisions,
  e.g. adjust their training style.
- **Hosting:** Claude running on **AWS Bedrock** (heard as "BlackRock"),
  so the model can be swapped if needed.
- **Input to the AI:** a dedicated worker output (artifact) designed for AI.
  Very different from the frontend data: much smaller, leaner and more
  token-efficient.
- **Design principle:** the AI makes **no calculations and no decisions**.
  Decisions are made in code; the AI narrates and explains them and may
  highlight things, in a tightly confined way.
- **Prompt:** written by Art in close collaboration with the founder and
  head coach, who supplied the domain knowledge.
  - A **base prompt** applied to every session.
  - **Dynamic prompt construction** based on boat properties, boat class and
    the wind conditions of the session (heard as "bot" and "win").
- **Result:** dynamic prompts plus code-made decisions gave the best
  results, much better than letting the AI decide. Output quality became
  more consistent: a non-deterministic system made as deterministic as
  possible without losing the value of AI.

## Mobile app: track recorder (Kotlin Multiplatform)

- Separate from the backend work. The founder had built a prototype that
  records a track using the phone's sensors, similar to Vakaros (heard as
  "Vacaras"; Vakaros makes sailing GPS trackers).
- Art built a cross-platform, scalable app in **Kotlin Multiplatform** for
  **iOS and Android**, following **Clean Architecture** (the current standard
  approach in mobile).
- Status: a product ready to ship.
- Strategy: part of building an **ecosystem**, not only analytics software.
  Also a way to test ideas before the startup commits to building its own
  **hardware**.

## AI-assisted engineering

- Art built a set of **skills and agents** that work with the code base.
- More importantly, a set of **documentation guidelines that act as
  guardrails** for the whole AI agentic system.
- The guardrails reached the point where Art is mostly fine with the
  quality of the code the AI produces.
- Enabled the physicist co-founder (algorithm engineer) to contribute
  directly: Art showed him how to work in the system using the AI tools and
  the worker module's architecture. He has shipped multiple features this
  way, despite little experience in commercial production software.
- Now looking for the right balance between understanding the code himself
  and letting AI handle it.

## To come (Art continues)

- More on worker and later stages, AI report integration, team, results.
