# VPN app: context from Art (for picking CV content, not CV text)

Told by Art on 2026-11-24, on top of the LinkedIn text.

## Idea and team

- Art and his wife (designer and product manager) decided to build an app.
  The "partner (product designer)" on LinkedIn is her.
- Art already had a VPN server set up for himself and wanted to turn it into
  a product and see how it goes.
- His first experience of building and releasing a commercial app of his own.

## What went well

- The UI looked neat, thanks to his wife's design. Art built all the small
  animations and they were smooth.
- A Docker setup for the VPN server that scaled to different countries "in
  one click": adding a new server took very little effort.

## What went wrong (Art's private context; keep the CV neutral)

- **Ad revenue:** they monetized with AdMob, which blocked them without a
  clear explanation and never paid out what was earned. Art's working
  assumption: VPN usage patterns made users look like bots. Other networks
  such as Facebook worked but paid much less.
- **Ad spend:** the account used to buy ads promoting the app was frozen
  once the war started, because they are Russian and registered on Russian
  documents. The money was never returned.
- **Payments:** some real payments came through Google Play, but many were
  stuck in a pending state, neither completing nor failing. Art still does
  not know why.
- **Traffic costs:** the cheapest server instances were enough, but VPN apps
  are very high traffic. Providers such as DigitalOcean charge per gigabyte
  above a limit, so costs grew with the number of users.

## Takeaway

- Art: a lot of good lessons.
