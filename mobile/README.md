# Filing Analyst — mobile (Expo)

A React Native client for the Filing Analyst backend, runnable on your phone with
[Expo Go](https://expo.dev/go). Pick a 10-K, watch the analysis run, and read the
trade score, metrics, red flags, and AI summary — the same workup the web UI shows.

## Run it

You need the backend running and your phone on the **same Wi-Fi** as your computer.

**1. Start the backend so the phone can reach it** (note `--host 0.0.0.0`):

```bash
cd ../backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**2. Start Expo:**

```bash
cd mobile
npm install
npx expo start
```

**3. Open it on your phone:** scan the QR code with **Expo Go** (Android) or the
Camera app (iOS). If you're signed into the same Expo account in the CLI and in
Expo Go, the project also appears under your projects automatically.

The app auto-detects the backend at `http://<your-computer>:8000` from the Expo dev
host, so on the same network there's nothing to configure.

## Reaching the app over cellular (optional)

Same-Wi-Fi is the simplest path. To use the app off your network, run Expo with a
tunnel **and** point it at a publicly reachable backend:

```bash
npx expo start --tunnel
```

Expose the backend with a tunnel of your choice (e.g. `cloudflared tunnel --url
http://localhost:8000`) and set its URL in `mobile/.env`:

```
EXPO_PUBLIC_API_URL=https://your-subdomain.trycloudflare.com
```

See `.env.example`. Only `EXPO_PUBLIC_*` variables are exposed to the app.

## Notes

- Requires the [Anthropic API key](../README.md#configuration) configured on the
  backend; the phone app only talks to your backend, never to Anthropic directly.
- Built with Expo SDK 56 (React Native 0.85). `npx tsc --noEmit` type-checks the app.
