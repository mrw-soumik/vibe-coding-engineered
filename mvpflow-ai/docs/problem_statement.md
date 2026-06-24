# Problem Statement, Restaurant FAQ Assistant (worked example)

> This is the worked example used throughout the workshop. It shows what a
> *properly written* problem statement looks like, the input quality that makes
> the rest of the pipeline (research → scope → tickets) produce good output.
> Raw notes for this example live in
> [`examples/restaurant_founder_notes.txt`](../examples/restaurant_founder_notes.txt).

## 1. Summary

Small restaurant owners spend a large share of their day answering the same
customer questions, hours, menu, allergens, reservations, delivery, group
bookings, across several disconnected channels. The work is repetitive,
easy to get wrong, and pulls owners away from running the restaurant.

## 2. Who has the problem

- **Primary user:** Owners and managers of small, independent restaurants (1–3
  locations) who personally handle customer messages.
- **Secondary user:** Front-of-house staff who field the same questions by phone
  and in person.
- **Not in scope as users (yet):** Large chains with a contact-centre, and
  customers themselves (the first version is owner-facing, not a public bot).

## 3. How it is solved today

- Manually answering Instagram DMs, Facebook messages, Google review questions,
  phone calls, and texts, each in a different app.
- A static FAQ on the website or a printed menu that goes out of date.
- Ad-hoc copy/paste of stock answers, with no consistency between staff.

## 4. Why it matters (impact)

- **Time:** Repeated questions consume hours that owners would rather spend on
  service and operations.
- **Risk:** Wrong or outdated answers, especially about **allergens** and
  dietary restrictions, can harm a customer and the business.
- **Lost custom:** Missed or slow replies on social channels lose bookings and
  delivery orders.

## 5. Evidence (and how to strengthen it)

This statement is grounded in founder conversations (see the raw notes). For a
production decision it should be strengthened with:

- Number of restaurants interviewed and a short quote per pain point.
- A rough count of repeated questions per week (to size the time saved).
- Which channels actually drive the most volume (to prioritise integrations).

> Honesty note: the workshop example is illustrative. Do not present invented
> statistics as validated research, collect the numbers above before building.

## 6. Constraints and risks

- **Safety:** Allergen / dietary answers must never be guessed. Missing
  information must be flagged for owner review, not fabricated.
- **Accuracy:** Menu, hours, and delivery details change often; answers must be
  easy for the owner to keep current.
- **Trust:** Owners will not allow fully automated public replies until they
  trust the drafts, the first version must keep a human in the loop.

## 7. What a good solution must do

1. Let an owner enter restaurant information once and generate editable answers.
2. Answer common questions consistently from that information.
3. **Flag** allergen / dietary / missing-information questions for review rather
   than answering them blindly.
4. Stay simple, no POS, payments, or public auto-replies in the first version.

## 8. Success criteria

- An owner can paste their info and get useful, editable FAQ drafts in minutes.
- Common questions are answered consistently; risky ones are flagged, not
  guessed.
- The owner reports spending meaningfully less time on repeated replies.

See [`research.md`](research.md) for the domain research that informs the
solution, and [`mvp_plan.md`](mvp_plan.md) for the resulting scope and backlog.
