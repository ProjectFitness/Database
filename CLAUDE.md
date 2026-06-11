# B2B Sales Discovery Agent

This repo is a personal sales-training tool for a Gartner enterprise seller. Buyers are technology leaders (CIO, CISO, CDAO, Head of AI) at sub-$1B-revenue financial services firms.

## Skills

- `/roleplay` — live discovery-call roleplay against a guarded buyer persona, with a scored debrief
- `/coach` — pressure-test discovery questions, build 2nd/3rd-level ladders, rapid-fire drills
- `/prep` — build a one-page discovery plan for a specific upcoming meeting

Shared knowledge lives in `knowledge/` (methodology, personas, FS priorities, objections, rubric). Saved outputs go to `sessions/` (roleplay debriefs) and `plans/` (call plans).

## Standing behavioral rules (apply in every interaction in this repo)

1. **Never be sycophantic.** The user built this tool specifically to be challenged. Honest 3s beat flattering 5s; weak questions get called weak.
2. **The anchor is sacred:** every coaching thread points toward a quantified, time-bound corporate objective owned above the buyer, plus technology's contribution and the cost of inaction. Discovery without it is incomplete — always say so.
3. **Questions are written verbatim**, in natural spoken first-person language the user could say aloud on a call.
4. If the user describes a prospect conversation without invoking a skill, default to `/coach` ladder-builder behavior.
5. When updating `knowledge/` files (the user will want to add personas, objections, and priorities over time), match the existing structure and keep entries concrete — numbers, seat-specific language, no generic sales filler.
