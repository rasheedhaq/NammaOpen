# NammaOpen API

## Public web routes
- `GET /` mobile-first search app
- `GET /s/{identifier}` public shop page using UPI ID or owner phone
- `GET /manifest.webmanifest` PWA manifest
- `GET /service-worker.js` service worker

## Shop APIs
- `POST /v1/shops`
  - create a shop and auto-seed category services
- `GET /v1/shops/{shop_id}`
  - full detail including services, payment plan, and fallback shops
- `GET /v1/shops/public/{identifier}`
  - fetch shop by UPI handle or owner phone
- `PATCH /v1/shops/{shop_id}`
  - update shop metadata

## Status APIs
- `PATCH /v1/shops/{shop_id}/status`
  - set `open`, `closed`, `paused`, or `likely_closed`
- `GET /v1/shops/{shop_id}/status`
  - latest non-expired status event

## Discovery APIs
- `GET /v1/shops/search?q&pin&lat&lng`
  - fuzzy shop/category search
  - ranks open shops first
  - uses optional live location for nearby fallback ordering

## Notification APIs
- `POST /v1/notifications/reopen/{shop_id}`
  - persist a reopen subscription for web or chat contacts

## Payment APIs
- `POST /v1/payments/initiate/{shop_id}`
  - generate or refresh the shop plan payment link

## Bot APIs
- `POST /v1/bots/whatsapp/webhook`
- `POST /v1/bots/telegram/webhook`

Payload shape:

```json
{
  "contact": "+919876543210",
  "text": "1",
  "channel": "whatsapp",
  "profile_name": "Raju"
}
```

Supported commands:
- `hi` starts onboarding
- `1` marks shop open
- `2` marks shop closed
- `3 21:00` marks shop open until a time
- `catalog` lists active services
- `pay` returns plan link
- `help` shows the command summary
