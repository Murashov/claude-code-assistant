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

## To come (Art continues)

- More on worker and later stages, AI report integration, team, results.
