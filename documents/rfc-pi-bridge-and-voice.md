# RFC: Pi bridge and voice I/O for the Claude Code container

- Status: draft
- Author: Claude (assistant), for Art Murashov
- Date: 2026-11-03
- Target repository: the Pi development repo (not this workspace)

## 1. Summary

Claude Code runs in a Docker container on a Raspberry Pi 5. The container has
no access to Pi hardware. This RFC describes three incremental features:

1. **Pi bridge** - a small MCP server on the Pi host, reachable only from the
   container over the Docker bridge, exposing an allowlisted set of hardware
   actions as typed tools.
2. **Text to speech** - a `speak` tool on the bridge backed by Piper TTS, plus
   an optional Claude Code Stop hook that speaks every reply automatically.
3. **Voice input** - a host-side daemon that records from a microphone,
   transcribes locally with whisper.cpp, and drives a headless Claude Code
   session with the transcript, speaking the answer back.

All audio processing stays on the device. Only Claude's own API traffic
leaves the Pi, as it does today.

## 2. Current state (measured from inside the container, 2026-11-03)

| Fact | Value |
|------|-------|
| Container network | Default Docker bridge. Container `172.17.0.2`, host gateway `172.17.0.1` |
| Hardware visible in container | None: no `/dev/snd`, `/dev/gpio*`, `/dev/i2c*`, no Docker socket |
| Privileges in container | User `claude` (uid 1000), no sudo, no apt, no systemd, no cron |
| Shared host/container paths | `/home/claude/.claude` is a bind mount from the SD card (persistent) |
| Container runtime | containerd/Docker, image is Ubuntu 26.04 aarch64 |
| Tooling in container | Python 3.14 (venv only), Node 26, git, curl, jq, ssh |
| Claude Code permission mode | Auto mode with a safety classifier. It blocked an ad-hoc TCP probe to `172.17.0.1` as a "containment escape". |

The last row matters for design: ad-hoc network calls from Bash toward the
host are discouraged by the harness, while a registered MCP server is the
intended, auditable path for tools.

## 3. Goals and non-goals

Goals

- The container never gains direct hardware or host access. All hardware
  actions go through one host process with a fixed, small API.
- Every path is on-device except Claude's API calls.
- Each step is useful on its own and can be deployed independently.
- Survives reboots: host services are systemd units, container-side
  configuration lives in the persistent `/home/claude/.claude` mount.

Non-goals

- Exposing the bridge on the LAN or the internet.
- A generic "run a shell command on the Pi" tool. This is explicitly excluded.
- Real-time, full-duplex conversation. Turn-based voice is the target.
- Cloud TTS or STT providers (may be added later as an opt-in).

## 4. Architecture overview

```
 Raspberry Pi host (trusted)                     Docker container (sandboxed)
 ┌──────────────────────────────────────┐        ┌────────────────────────────┐
 │  pi-bridge (FastMCP, systemd)        │        │  Claude Code               │
 │   bind 172.17.0.1:8765, bearer token │◄──MCP──│   MCP client "pi"          │
 │   tools: speak, gpio_*, sensor_*     │  HTTP  │   Stop hook -> speak       │
 │         └─ piper -> aplay            │        │                            │
 │                                      │        │                            │
 │  pi-voice (daemon, systemd)          │        │                            │
 │   PTT/wake word -> arecord           │        │                            │
 │   -> whisper.cpp -> text             │─docker exec─►  claude -p --resume   │
 │   <- reply text                      │        │   (headless voice session) │
 │   -> piper -> aplay                  │        │                            │
 └──────────────────────────────────────┘        └────────────────────────────┘
          │ USB mic, speaker, GPIO
```

Trust directions:

- Container -> host: only through the bridge, only the tools it exposes.
- Host -> container: `docker exec`, which the host may do anyway. The daemon
  does not require any new privilege for the container.

## 5. Step 1: Pi bridge (MCP server on the host)

### 5.1 Technology

- Python 3.11+ on the host, in a venv under `/opt/pi-bridge/venv`.
- `fastmcp` (v2.x) for the server, `uvicorn` as the ASGI server.
- Transport: MCP Streamable HTTP at `http://172.17.0.1:8765/mcp`.
- Run as a dedicated system user `pibridge` in groups `audio`, `gpio`,
  `i2c` as needed. Not root, not in the `docker` group.

### 5.2 Network binding and firewall

- The Pi runs several Claude Code containers. Only this one (the assistant
  workspace) may reach the bridge. The default `docker0` bridge is shared by
  all of them, so the assistant container is moved to its own Docker network
  and the bridge listens only there. See section 11 for the full isolation
  design; the short version:
  - `docker network create --subnet 172.30.0.0/24 claude-bridge`, and run the
    assistant container with `--network claude-bridge`. The host side of that
    network is `172.30.0.1` on interface `br-claude` (set with
    `-o com.docker.network.bridge.name=br-claude`).
  - Bind only to `172.30.0.1`. Never `0.0.0.0`.
  - nftables accepts the port only from that interface, so a container on
    `docker0` or any other network cannot reach it even by addressing the
    host IP directly:

```
table inet pibridge {
  chain input {
    type filter hook input priority -10;
    tcp dport 8765 iifname "br-claude" accept
    tcp dport 8765 drop
  }
}
```

- Keep the bind address in the service's env file, not in code.

### 5.3 Authentication

- A single static bearer token, generated with `openssl rand -hex 32`.
- Host side: stored in `/etc/pi-bridge/env` as `PI_BRIDGE_TOKEN=...`,
  mode 0600, owned by `pibridge`.
- Container side: the token is injected into **this container only** as an
  environment variable at `docker run` time (`--env-file
  /etc/pi-bridge/container.env`, a root-owned 0600 file on the host).
  Claude Code's MCP configuration references it as `${PI_BRIDGE_TOKEN}` and
  never contains the value (see 5.6). The other containers are started
  without that file and have no way to obtain the token.
- The server rejects any request without a matching header with 401 before
  the MCP layer sees it. A Starlette middleware around the FastMCP ASGI app is
  enough:

```python
# /opt/pi-bridge/server.py
import os, subprocess, shlex
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse
import uvicorn

TOKEN = os.environ["PI_BRIDGE_TOKEN"]
BIND = os.environ.get("PI_BRIDGE_BIND", "172.17.0.1")
PORT = int(os.environ.get("PI_BRIDGE_PORT", "8765"))

mcp = FastMCP("pi")

@mcp.tool()
def speak(text: str, voice: str = "en_US-lessac-medium") -> str:
    """Speak text aloud on the Pi speaker. Blocks until playback ends."""
    text = text.strip()
    if not text:
        return "nothing to say"
    if len(text) > 2000:
        text = text[:2000]
    # see section 6 for the piper pipeline
    subprocess.run(["/opt/pi-bridge/bin/say", voice], input=text.encode(), check=True, timeout=120)
    return f"spoke {len(text)} chars"

@mcp.tool()
def status() -> dict:
    """Basic host health: uptime, temperature, free memory."""
    temp = open("/sys/class/thermal/thermal_zone0/temp").read().strip()
    return {"cpu_temp_c": int(temp) / 1000, "uptime": open("/proc/uptime").read().split()[0]}

class BearerAuth(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.headers.get("authorization") != f"Bearer {TOKEN}":
            return PlainTextResponse("unauthorized", status_code=401)
        return await call_next(request)

app = mcp.http_app(path="/mcp")
app.add_middleware(BearerAuth)

if __name__ == "__main__":
    uvicorn.run(app, host=BIND, port=PORT)
```

### 5.4 Tool design rules

- Every tool is a fixed verb with typed, validated arguments. No tool takes
  a command string, a file path outside an allowlist, or arbitrary GPIO pin
  numbers without a whitelist.
- Tools return small JSON or short strings. No binary payloads.
- Hardware tools to add after `speak` and `status`, as needed:
  `gpio_set(pin: Literal[...], value: bool)`, `gpio_read(pin)`,
  `sensor_read(name: Literal["temp", "humidity", ...])`,
  `notify(level, text)` for an LED or buzzer.
- Long operations must have a timeout and return; the MCP client waits
  synchronously.
- Log every call with timestamp, tool name and arguments to journald. This
  is the audit trail for anything the container did to the Pi.

### 5.5 systemd unit

```
# /etc/systemd/system/pi-bridge.service
[Unit]
Description=Pi bridge MCP server for the Claude container
After=network-online.target docker.service
Wants=network-online.target

[Service]
User=pibridge
Group=pibridge
SupplementaryGroups=audio gpio
EnvironmentFile=/etc/pi-bridge/env
WorkingDirectory=/opt/pi-bridge
ExecStart=/opt/pi-bridge/venv/bin/python /opt/pi-bridge/server.py
Restart=on-failure
RestartSec=3
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
ReadWritePaths=/opt/pi-bridge/cache

[Install]
WantedBy=multi-user.target
```

`docker0` only exists once the Docker daemon is up, so `After=docker.service`
is required or the bind will fail at boot.

### 5.6 Container-side registration

Claude Code reads project MCP servers from `.mcp.json` in the workspace and
expands `${VAR}` references from the environment. Commit this file to the
workspace repo (it holds no secret):

```json
{
  "mcpServers": {
    "pi": {
      "type": "http",
      "url": "http://172.30.0.1:8765/mcp",
      "headers": { "Authorization": "Bearer ${PI_BRIDGE_TOKEN}" }
    }
  }
}
```

Do not use `claude mcp add --scope user`: that writes `~/.claude.json`,
which sits outside the persistent `/home/claude/.claude` mount in this
container and would be lost on restart (verified: the file does not exist
today, only the `.claude` directory is mounted).

Then in the Claude Code permissions (user settings under the persistent
mount), allow the tools so auto mode does not prompt for each call:

```json
{
  "permissions": {
    "allow": ["mcp__pi__speak", "mcp__pi__status"]
  }
}
```

Verify with `claude mcp list` and by asking Claude to call `status`.

### 5.7 Acceptance criteria

- From the assistant container, a request without a token returns 401 and
  one with the token lists tools. From any other container and from the LAN
  the port does not answer at all (connection timeout, not refused).
- Claude lists the `pi` server as connected and `status` returns host data.
- Service restarts cleanly after `sudo reboot`.

## 6. Step 2: text to speech

### 6.1 Engine

- **Piper TTS**, on-device neural TTS. Runs faster than real time on a
  Pi 5 with "medium" voices. Install into the bridge venv:
  `pip install piper-tts`. Download a voice pair (`.onnx` + `.onnx.json`) into
  `/opt/pi-bridge/voices/`, for example `en_US-lessac-medium` and, for
  Portuguese, `pt_BR-faber-medium`.
- Fallback: `espeak-ng` (apt package, instant, robotic). Useful for error
  messages when Piper fails.
- Output device: find the card with `aplay -l`; pin it in `/etc/asound.conf`
  or pass `-D` explicitly so a hot-plugged USB device does not change the
  default.

### 6.2 The `say` helper

```sh
#!/bin/sh
# /opt/pi-bridge/bin/say  - reads text on stdin, speaks it, exits when done
VOICE="${1:-en_US-lessac-medium}"
DIR=/opt/pi-bridge/voices
exec /opt/pi-bridge/venv/bin/piper \
  --model "$DIR/$VOICE.onnx" --output-raw \
  | aplay -q -D "${PI_AUDIO_OUT:-default}" -r 22050 -f S16_LE -c 1 -t raw -
```

Notes:

- Use a lock file (`flock /run/pi-bridge/speak.lock`) inside `say` so two
  `speak` calls do not talk over each other.
- Sample rate must match the voice's `.onnx.json` (`sample_rate`), 22050 for
  medium voices.
- First synthesis after boot is slower (model load). Warm up by speaking an
  empty string at service start, or keep a persistent Piper process.

### 6.3 Explicit use by Claude

The `speak` tool from 5.3 is enough. Claude calls it when a spoken summary is
useful. Guidance for Claude lives in the workspace memories, for example
"after finishing a task started by voice, call speak with one or two
sentences".

### 6.4 Automatic use: Claude Code Stop hook

A Stop hook runs on the container side whenever Claude finishes a turn.
It receives JSON on stdin including `session_id` and `transcript_path`.
The hook extracts the final assistant text from the transcript (JSONL) and
posts it to a plain HTTP endpoint on the bridge.

Hook configuration, in the user settings under the persistent mount
(`/home/claude/.claude/settings.json`):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "python3 /workspace/scripts/speak-last-reply.py", "timeout": 60 }
        ]
      }
    ]
  }
}
```

The hook script:

```python
#!/usr/bin/env python3
# speak-last-reply.py - Stop hook: speak the last assistant message via the bridge
import json, sys, os, urllib.request

evt = json.load(sys.stdin)
if evt.get("stop_hook_active"):      # avoid loops if the hook itself ends a turn
    sys.exit(0)

text = None
with open(evt["transcript_path"]) as f:
    for line in f:
        rec = json.loads(line)
        if rec.get("type") == "assistant":
            parts = [b.get("text", "") for b in rec["message"].get("content", []) if b.get("type") == "text"]
            if parts:
                text = "\n".join(parts)
if not text:
    sys.exit(0)

token = open(os.path.expanduser("~/.claude/pi-bridge-token")).read().strip()
req = urllib.request.Request(
    "http://172.17.0.1:8765/speak",
    data=json.dumps({"text": text[:1500]}).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
)
urllib.request.urlopen(req, timeout=60)
```

Bridge side: add a plain `POST /speak` route next to the MCP app (same
middleware, same `say` helper) so the hook does not need an MCP client.

Considerations:

- Markdown in replies sounds bad. The bridge should strip code fences,
  tables and URLs before synthesis, or Claude should keep spoken text short.
  Recommended: the `/speak` route strips Markdown and truncates to roughly
  1500 characters; the first paragraph of a reply is usually the answer.
- Make the hook opt-in via a flag file (`~/.claude/speak-replies`) so it can
  be turned off from the phone by asking Claude to delete the file.
- Hooks execute outside the auto-mode classifier, so this network call is
  not blocked the way an ad-hoc Bash probe is.

### 6.5 Acceptance criteria

- `echo hello | /opt/pi-bridge/bin/say` plays audio within 1 s of warm start.
- Claude calling `speak("test")` plays audio and returns.
- With the flag file present, every reply in the session is spoken; without
  it, nothing is spoken.

## 7. Step 3: voice input

### 7.1 Why transcription is host-side

Claude Code cannot receive audio. Transcription must produce text before
Claude is involved, and doing it on the Pi keeps audio local. The daemon
below owns the entire loop; nothing inside the container listens or polls.

### 7.2 Hardware

- **Preferred: a spare Android phone as a satellite** (mic and speaker,
  streaming continuously over Wi-Fi; the Pi does wake word, VAD and whisper).
  See section 10. The rest of this step is written for Pi-attached hardware
  but applies unchanged to the satellite; only the audio source and sink
  differ.
- Pi-attached alternative: a USB microphone or USB conference speakerphone
  (has echo cancellation), a push-to-talk button on GPIO (`gpiozero.Button`),
  and the speaker from step 2. Wake word (openWakeWord with onnxruntime) is a
  later phase in either case.

### 7.3 Speech to text

- **whisper.cpp**, built on the host with cmake, model `ggml-base.en.bin`
  (English only) or `ggml-base.bin` / `ggml-small.bin` for Portuguese and
  mixed speech. On a Pi 5, `base` transcribes 10 s of audio in roughly 2-4 s;
  `small` is more accurate and 3-4x slower.
- Invocation: `whisper-cli -m models/ggml-base.en.bin -f utt.wav -nt -np -otxt`
  with 16 kHz mono 16-bit WAV input (`arecord -f S16_LE -r 16000 -c 1`).
- Python alternative: `faster-whisper` (CTranslate2) in a venv, same models,
  similar speed, easier to embed. Pick one; whisper.cpp has fewer dependencies.

### 7.4 Daemon flow (`pi-voice`)

```
loop:
  wait for button press (or wake word)
  play short "listening" chime
  arecord -> utt.wav while button held (PTT) or until 1.0 s of silence
  play "thinking" chime
  text = whisper(utt.wav)
  if text is empty or only noise: say "I did not catch that"; continue
  reply = ask_claude(text)             # section 7.5, serialized
  speak(strip_markdown(reply))         # same say helper as step 2
```

- Everything is strictly one utterance at a time. A second button press
  during processing is ignored (or cancels playback, if desired).
- Record to `/run/pi-voice/` (tmpfs) and delete the WAV after transcription.
  No audio is kept on disk.
- Run as user `pivoice` in `audio`, `gpio` and `docker` groups. The docker
  group is needed for `docker exec`; it is root-equivalent on the host, which
  is acceptable because the host is the trusted side and the daemon is small.

### 7.5 Driving Claude: headless session via `docker exec`

The daemon turns each utterance into a real user turn of a dedicated
**voice session**, separate from the interactive session used from the phone.

First run creates the session and records its id:

```
docker exec -u claude -w /workspace <container> \
  claude -p "Voice session start. Reply briefly, in plain spoken sentences." \
  --output-format json > out.json
session_id=$(jq -r .session_id out.json)   # store in /var/lib/pi-voice/session
```

Each utterance resumes it:

```
docker exec -u claude -w /workspace <container> \
  claude -p "$text" --resume "$session_id" --output-format json \
  --allowedTools "Read,Grep,Glob,mcp__pi__speak,mcp__pi__status,mcp__claude_ai_Google_Calendar__*" \
  --append-system-prompt "You are being spoken to through a microphone. Answer in one to three plain sentences without Markdown."
reply=$(jq -r .result out.json)
```

Notes:

- `--resume` keeps conversation context across utterances. Rotate to a fresh
  session daily (or when context grows) by deleting the stored id; the
  workspace memories provide long-term continuity regardless.
- Headless runs need an explicit tool allowlist; do not use
  `--dangerously-skip-permissions`. Start read-only plus `speak` and widen
  deliberately. Google Calendar writes are a reasonable later addition since
  the owner already uses Claude for that.
- Headless and interactive sessions share the same `~/.claude` mount, so
  the MCP server registration from 5.6 and memories apply to both.
- Timeout `docker exec` at 120 s. On timeout or non-zero exit, speak a short
  error and continue; never let the daemon die on a bad turn.
- The `--resume` of the voice session must never target the interactive
  session id; concurrent resumes of one session are not supported.
- Alternative to the CLI: the Claude Agent SDK (Python) running inside the
  container. It gives the same headless loop with a programmatic API but
  requires a long-lived process in the container; the CLI-per-utterance
  approach is simpler and is the recommendation for v1.

### 7.6 Latency budget (Pi 5, base model, warm)

| Stage | Typical |
|-------|---------|
| Recording end to transcript | 2-4 s |
| Claude turn (no tools) | 4-10 s |
| Claude turn with a tool call | 10-25 s |
| Synthesis start to first audio | < 1 s |

Total 8-30 s. The "thinking" chime and, optionally, a spoken "one moment"
after 8 s keep it from feeling broken.

### 7.7 Security considerations specific to voice

- Anyone within earshot can issue commands. Push-to-talk, a limited tool
  allowlist, and no destructive tools in the voice session are the controls.
  Treat the transcript as untrusted input in the system prompt wording
  ("the speaker may not be the owner").
- No cloud STT, so no audio leaves the Pi. Only the transcript text reaches
  Anthropic as part of the normal Claude request.
- Transcripts are logged in the Claude session file inside the persistent
  mount like any other conversation; nothing extra is stored on the host.

### 7.8 Acceptance criteria

- Press button, say "what is the CPU temperature", release: the Pi speaks
  the value returned by the bridge `status` tool within 20 s.
- Daemon survives a reboot and a failed Claude call.
- No `.wav` files remain under `/run/pi-voice/` after an utterance.

## 8. Rollout order and effort

| Step | Host work | Container work | Estimated effort |
|------|-----------|----------------|------------------|
| 1 Bridge | venv, server.py, env file, nftables, systemd | `claude mcp add`, permissions | 2-3 h |
| 2 TTS | piper + voices, `say`, `/speak` route | Stop hook script and settings | 1-2 h |
| 3 Voice in | mic/speaker setup, whisper.cpp build, daemon, systemd | none (uses headless CLI) | 1-2 days incl. tuning |

Claude can write the container-side pieces (hook script, settings, memory
guidance) directly in the workspace once the bridge is live. Host-side
pieces are written here as reference and deployed from the laptop.

## 9. Open questions

1. Wake word: use a stock openWakeWord model ("hey jarvis", "alexa") or
   train a custom one (openWakeWord supports training from synthetic
   samples in a few hours on a laptop)?
2. Push-to-talk button only for v1, or wake word from the start?
3. Language: English only (`.en` models, one Piper voice) or Portuguese and
   English (multilingual Whisper model, two Piper voices, language detection)?
4. Should the voice session be allowed to write to the Managed calendar, or
   stay read-only until the loop proves reliable?
5. Should the automatic Stop hook speak replies in the phone session, or only
   the voice session? (Recommendation: voice session only; the phone already
   shows the text.)

## 10. Addendum (2026-11-03): the phone as a dumb voice satellite

Decision: a spare entry-level Xiaomi (Redmi class, MediaTek Helio G25/G35 or
similar, 2-3 GB RAM, rooted) is the voice front end. It is too slow for
on-device speech recognition, so it does nothing clever: it streams its
microphone to the Pi continuously and plays back whatever audio the Pi sends.
The Pi runs voice activity detection, wake word, whisper, Claude and Piper.
All intelligence lives in the Pi repo; the phone app never changes when
models are tuned.

Bluetooth is not used: Bluetooth audio profiles cannot send a phone's own
microphone to another device, and application-level Bluetooth (RFCOMM)
gains nothing over Wi-Fi on the same LAN.

### 10.1 Pipeline on the Pi

```
phone ──PCM 16 kHz──► ring buffer ──► Silero VAD ──► openWakeWord
                                                        │ detected
                                                        ▼
                                   capture until 1 s silence (max 15 s)
                                                        ▼
                                                  whisper.cpp
                                                        ▼
                                       headless Claude session (7.5)
                                                        ▼
                                   Piper ──PCM 22.05 kHz──► phone speaker
```

- Silero VAD (ONNX, ~1 MB) runs on 30 ms frames and gates openWakeWord so
  the wake word model only runs on speech. openWakeWord (ONNX, onnxruntime)
  scores 80 ms frames; both together cost a few percent of one Pi 5 core
  per stream.
- Wake word: a stock openWakeWord model to start; a custom one later (the
  project supports training from synthetic data on a laptop). A short
  acknowledgement tone is sent to the phone on detection.
- End of utterance: 1.0 s of VAD silence after speech, hard cap 15 s.
- While the Pi is speaking, incoming audio is ignored (half duplex). This
  is the only echo protection needed, and it is enough because the phone's
  mic and speaker are the same device.
- The push-to-talk button on the phone bypasses the wake word: `start` and
  `stop` messages force capture boundaries.
- Audio is held only in memory. The segment WAV lives in `/run/pi-voice/`
  (tmpfs) for the duration of the whisper call and is deleted after.
- The daemon's audio sink abstraction (used by `speak` from step 2 and by
  the Stop hook route) targets the connected phone and falls back to the
  local `aplay` path when no satellite is connected.

### 10.2 Protocol

One WebSocket per satellite, `wss://<pi>:8766/satellite`, bound to the LAN
interface only, TLS with a self-signed certificate (pinned in the app).
nftables accepts 8766 only from the LAN interface (`wlan0`/`eth0`) and drops
it from every Docker bridge, so no container can pose as a satellite or
listen to the microphone stream (section 11). Text frames are JSON; binary frames are raw
PCM.

Client to server:

| Message | Meaning |
|---------|---------|
| `{"type":"auth","token":"...","name":"redmi"}` | First message. Connection closed on mismatch. |
| `{"type":"format","sample_rate":16000,"format":"s16le","channels":1}` | Sent once after auth; stream follows. |
| binary | Continuous 20 ms PCM chunks (640 bytes). Sent for as long as the app runs. |
| `{"type":"start"}` / `{"type":"stop"}` | Optional push-to-talk override of the wake word. |
| `{"type":"cancel"}` | Stop current playback or abort the turn. |

Server to client:

| Message | Meaning |
|---------|---------|
| `{"type":"state","value":"idle|listening|thinking|speaking"}` | Drives the UI and the status LED colour. |
| `{"type":"transcript","text":"..."}` | What whisper heard. |
| `{"type":"reply","text":"..."}` | Claude's reply text. |
| `{"type":"audio_start","sample_rate":22050,"format":"s16le","channels":1}` | Followed by binary PCM chunks (Piper output streamed as produced), then `{"type":"audio_end"}`. |
| `{"type":"tone","name":"wake|error"}` | Short built-in sounds the app plays itself. |
| `{"type":"error","text":"..."}` | Shown on screen. |

Bandwidth is about 256 kbit/s upstream, continuous. Raw PCM is fine on a
home LAN; Opus (24 kbit/s) is a later option if the phone's 2.4 GHz Wi-Fi
proves unreliable.

### 10.3 The Android app

A small native app (Kotlin). It has to be native: a web page cannot keep the
microphone open in the background.

- Foreground service with `foregroundServiceType="microphone"` and a
  persistent notification; a partial wake lock and a Wi-Fi lock
  (`WIFI_MODE_FULL_HIGH_PERF`) so MIUI does not sleep the radio.
- `AudioRecord`, 16 kHz mono 16-bit, `VOICE_RECOGNITION` source (disables
  the phone's own AGC and noise suppression, which otherwise mangle quiet
  speech for whisper). 20 ms reads posted to the WebSocket.
- `AudioTrack` at 22.05 kHz for playback of the streamed reply.
- Reconnect loop with exponential backoff (1 s to 30 s). The Pi restarts
  and Wi-Fi drops; the app must never need a tap to recover.
- UI: large hold-to-talk button, state colour, last transcript and reply.
  Keep the screen on only while the app is in front; the service runs
  without it.
- Settings: Pi host, token, satellite name. Token stored in app private
  storage, entered once.
- No models, no inference, no root required. Target the Android version the
  phone actually runs (entry-level Xiaomi ships Android 10-13 / MIUI 12-14).

### 10.4 MIUI specifics (entry-level Xiaomi)

MIUI is aggressive about killing background apps. All of these are needed
or the service will silently die within minutes:

- Settings > Apps > the app > Battery saver: **No restrictions**.
- Settings > Apps > Permissions > **Autostart** enabled for the app.
- Recent apps: lock the app (pull down on its card, tap the lock).
- Settings > Battery > disable "Battery saver" and MIUI optimisation if
  present under Developer options (`Turn on MIUI optimization` off).
- Developer options: keep "Stay awake while charging" on.
- Wi-Fi: Advanced settings, "Keep Wi-Fi on during sleep: Always".
- Phone stays on the charger. Entry-level Xiaomis run cool at this load.
- With root, `pm set-app-links`/`dumpsys deviceidle whitelist +<package>`
  adds the app to the Doze allowlist, which removes the last source of
  radio sleep. Not required if the settings above are applied.

Microphone quality on this class of phone is adequate for near-field speech
(within roughly two metres in a quiet room). Place the phone where it is
spoken to, not across the room; whisper on the Pi handles the rest.

### 10.5 Effect on earlier sections

- Step 2 local speaker becomes optional. Piper and the `say` helper remain;
  the output target is chosen at runtime (satellite if connected, else
  local).
- Step 3 section 7.2 is superseded. Whisper settings (7.3), the headless
  Claude session (7.5), latency (7.6) and the voice security notes (7.7)
  apply unchanged. Add roughly 0.5 s for wake word confirmation to the
  latency budget.
- The daemon from 7.4 gains the WebSocket listener, the VAD and wake word
  stages, and the audio sink abstraction; it loses `arecord` and the GPIO
  button except as a fallback.
- Acceptance for step 3 becomes: with the app running in the background and
  the phone screen off, say the wake word and ask for the CPU temperature;
  the phone plays the wake tone and speaks the answer within 20 s, and the
  transcript appears on screen when the app is opened.

## 11. Addendum (2026-11-03): only the assistant container may talk to the Pi

Requirement: the Pi runs three or four other Claude Code containers. None of
them may reach the bridge, the voice daemon, or the phone's audio stream.
Only the assistant container (the one with this workspace mounted) is
trusted to call Pi tools, and the credential that proves it must exist only
inside that container.

### 11.1 Threat model

- Another container is compromised or simply misbehaves and tries to call
  `speak`, read sensors, or connect to the satellite socket.
- Another container tries to sniff the token from a shared location.
- The assistant container is restarted or rebuilt; nothing should need to
  be re-entered by hand, and nothing should leak into a git repository.

### 11.2 Layer 1: network placement

- The assistant container runs on a dedicated user-defined network
  `claude-bridge` (172.30.0.0/24, host side `172.30.0.1`, bridge interface
  named `br-claude`). The other containers stay on `docker0` or on their own
  networks. Docker's default inter-network isolation stops container-to-
  container traffic across bridges.
- The bridge binds to `172.30.0.1` only. The satellite socket binds to the
  LAN address only.
- nftables (priority -10, so it runs before Docker's own rules) enforces the
  interface a packet arrived on. Binding alone is not enough: a container on
  `docker0` can address `172.30.0.1` because it is a host address, and only
  the `iifname` rule stops it.

```
table inet pibridge {
  chain input {
    type filter hook input priority -10;
    # bridge: only from the assistant container's network
    tcp dport 8765 iifname "br-claude" accept
    tcp dport 8765 drop
    # satellite socket: only from the LAN, never from any container
    tcp dport 8766 iifname { "wlan0", "eth0" } accept
    tcp dport 8766 drop
  }
}
```

- Optional: give the assistant container a fixed address
  (`--ip 172.30.0.10`) and add `ip saddr 172.30.0.10` to the accept rule.
  This only matters if a second container is ever attached to
  `claude-bridge`; keep the network single-tenant instead.

### 11.3 Layer 2: a credential that lives only in this container

- Token generated once on the host: `openssl rand -hex 32`.
- Host copy: `/etc/pi-bridge/env` (read by the bridge service).
- Container copy: `/etc/pi-bridge/container.env` containing
  `PI_BRIDGE_TOKEN=<token>`, root-owned, mode 0600, passed with
  `--env-file` only in the assistant container's `docker run` (or compose
  service). It is never written into `/workspace`, never into the shared
  `.claude` mount, and the other containers are started without it.
- Claude Code reads the MCP server definition from the committed
  `/workspace/.mcp.json`, which contains `${PI_BRIDGE_TOKEN}` and expands it
  at startup. The Stop hook script (6.4) reads the same variable instead of
  a token file.
- The auto-mode permission classifier already blocks Claude from dumping
  environment variables, so the token is not casually visible in the
  session either; it is used by the MCP client process, not by the model.
- Rotation: change the value in both files, restart the bridge, restart the
  container.

### 11.4 Why not other mechanisms

- Mutual TLS: stronger in theory, but Claude Code's MCP client configuration
  carries headers, not client certificates, so it would need a local proxy
  inside the container. Not worth it on a single-host LAN.
- A Unix socket bind-mounted only into this container: equivalent isolation,
  but it needs a stdio shim inside the container because the MCP client
  speaks HTTP. Keep as a fallback if Docker networking ever gets in the way.
- Source IP filtering alone: container addresses on `docker0` are dynamic,
  so the dedicated network is required anyway.

### 11.5 Direction host to container

The voice daemon reaches Claude with `docker exec <assistant-container>`
(section 7.5). It names this container explicitly; nothing in that path
touches the other containers. The daemon user needs the `docker` group on
the host, which is root-equivalent there; that is accepted because the host
is the trusted side.

### 11.6 Acceptance criteria

- From the assistant container: MCP tools listed and callable.
- From another container: a request to `172.30.0.1:8765` times out.
- From a laptop on the LAN: `8765` times out; `8766` completes a TLS
  handshake and the satellite protocol works.
- `docker inspect` of the other containers shows no `PI_BRIDGE_TOKEN`.
- After `docker restart` of the assistant container, the `pi` server is
  listed without any manual step.
