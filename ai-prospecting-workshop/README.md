# AI Prospecting Workshop Kit

Tools for coaching business development reps out of generic AI-generated outreach and into hypothesis-driven prospecting, built around the Five Questions framework, the swap test, hygiene checks, and citation tiers.

## What is in this kit

| File | What it is | Who uses it |
|---|---|---|
| `rep-simulator-prompt.md` | Paste-able claude.ai prompt. Claude plays a skeptical BDR pushing back on your coaching, then scores your talk track. | You, before the live meeting |
| `email-scorer-prompt.md` | Paste-able claude.ai prompt. Grades any draft prospecting email against the full framework, pass/fail per criterion with rewrites. | You and reps, ongoing |
| `workshop-exercise.md` | The team exercise: shared real headline scenario (AvalonBay / Equity Residential merger), rep instructions, Five Questions worksheet. | Reps, during the workshop |
| `facilitator-rubric.md` | Your run-of-show: agenda, anonymous side-by-side mechanics, discussion questions, scoring grid, objection playbook, north-star sample email. | You, during the workshop |

## How to set up the prompts in claude.ai

Option A (recommended): Claude Projects
1. In claude.ai, create a Project called "Rep Simulator".
2. Copy everything inside the copy block in `rep-simulator-prompt.md` into the Project's custom instructions.
3. Start a new chat in that Project and type `START`.
4. Repeat with a second Project called "Email Scorer" using `email-scorer-prompt.md`.

Option B: single conversation
1. Start a new chat in claude.ai.
2. Paste the entire copy block as your first message.
3. The prompt tells Claude how to begin.

## Suggested order of use

1. Rehearse with the rep simulator until you can reach a genuine (not fake-compliant) shift in at least the STANDARD and HARDER modes.
2. Run the workshop using `workshop-exercise.md` and `facilitator-rubric.md`.
3. Roll out the email scorer to the team as the standing quality gate after the workshop, not before. If they get the scorer first, they will optimize for it without understanding it.

## Standing constraints baked into every tool

- No em dashes in any output.
- All email drafts must be 75 to 100 words.
- Every claim needs source, date, and tier. Untierable claims get [VERIFY] or get cut.
