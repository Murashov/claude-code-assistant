# ChatGPT Telegram bot: context from Art (for picking CV content, not CV text)

Told by Art on 2026-11-24. Not on LinkedIn.

## What and when

- A ChatGPT wrapper for Telegram. Not a unique idea, but built when
  GPT-3.5 was released, at the very start of the AI boom.
- Built while Art was working at talabat. He would like it placed between
  talabat and Careem in the CV so parallel work raises no questions.
  (talabat ended May 2023 and Careem started May 2023, so there is no gap;
  in the CV it is a dated side project, listed between the two.)
- Why: with Russia at war and under sanctions, ChatGPT did not work there.
  Art first built it so people he knows could access the AI.

## Product and tech

- A Telegram bot talking to the OpenAI API.
- Subscriptions paid through crypto and through Robokassa, a Russian
  payment system.
- Kept track of all chats, built and managed context, managed message
  links, read media from links.
- Used the newest OpenAI API capabilities, sometimes before ChatGPT itself
  had them, including image processing.
- Seamless in Telegram: answers longer than Telegram's message limit were
  split into messages that reference each other. Replies worked as part of
  one conversation, so a single chat could hold several conversations, with
  replies building the context.
- More complicated than it sounds, and than Art expected.

## Business

- Same scaling issue as the VPN app: the API costs money, so each new user
  had to bring in more than they cost. That worked; it made a bit of money
  despite the competition.
- Art was among the first tens of such bots in Russia; later there were
  hundreds of similar ones.
- It stopped being useful when OpenAI became accessible in Russia again and
  many competing services appeared. Art decided to stop and close it.

## Takeaway

- Deep understanding of Telegram: how its apps and bots are built, the
  constraints and capabilities, and how to design an interface that works
  smoothly inside a chat. A lot of learning, not much business value.

## Open

- Tech stack.

## Dates (Art, 2026-11-24)

- Developed in 2023, launched early 2024, closed towards the end of 2025.
- On LinkedIn Art set the entry to Apr 2023 – Nov 2025 (evening of
  2026-11-24). The CV uses the same dates so the two match.

## CV decisions (Art, 2026-11-24)

- Do not mention being among the first few dozen such bots. True, but Art
  would not brag about it.
