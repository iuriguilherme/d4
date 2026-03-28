<objective>
Use the /ce:brainstorm command to conduct a thorough brainstorm for an adaptive personal planner web application.

The brainstorm must cover:
1. Personal planning methodologies (research-first)
2. Adaptive personalization strategies — how the app evolves to fit the user
3. Feature set for journaling (past) and planning (future)
4. Technical architecture for the dual FastAPI/Flask stack
5. User onboarding and profile-building approaches

The output should serve as the foundation for a product roadmap and architecture decisions.
</objective>

<context>
This system is a "planner" — a web application for human beings to:
- **Journal their routine** (documenting the past: what happened, reflections, moods, habits)
- **Plan ahead** (documenting the future: next day/week goals, tasks, intentions)

The **key differentiator** is adaptive personalization:
- The app starts simple (minimal interface, core features)
- Over time it observes how the user interacts and what they actually use
- It adapts its structure and suggestions to become the *specific kind* of planner this user needs
- Different people have fundamentally different planning styles — the system should be able to become any of them

**Tech Stack:**
- Backend API: FastAPI (handles data, logic, future mobile app support)
- Web frontend server: Flask or Quart (thin server rendering, uses FastAPI as its backend)
- Language: Python throughout
- The FastAPI layer must be designed with future mobile clients in mind (clean REST/JSON API)

**End users:** Individuals who want a personal productivity tool — not teams, not enterprises.
</context>

<brainstorm_command>
Run: /ce:brainstorm

Frame the brainstorm session around the following question:

"What should an adaptive personal planner application be, do, and become — and how do we build it well?"

Guide the brainstorm to cover these dimensions:
</brainstorm_command>

<research_areas>
1. **Planning methodology landscape**
   - Research and catalogue established personal planning systems:
     - GTD (Getting Things Done) — David Allen
     - Bullet Journal (BuJo) — Ryder Carroll
     - Time blocking / Day theming — Cal Newport
     - Pomodoro Technique — Francesco Cirillo
     - OKRs (personal scale) — John Doerr
     - Ivy Lee Method
     - Full Focus Planner — Michael Hyatt
     - Eat the Frog — Brian Tracy
     - PARA Method — Tiago Forte
     - Weekly/Daily Reviews
   - For each: core philosophy, key components, user profile it suits best, data structures it implies

2. **User archetypes**
   - What kinds of planners exist? (e.g., the list-maker, the time-blocker, the reflective journaler, the goal-tracker, the habit-builder)
   - What signals distinguish one archetype from another?
   - How does behavior (not just stated preference) reveal archetype?

3. **Adaptive personalization mechanics**
   - How can the app learn which archetype a user is, without explicit profiling questionnaires?
   - What behavioral signals matter? (frequency of use, which features they open, completion rates, time-of-day patterns)
   - How should the UI/UX evolve as the app learns? (progressive disclosure, surfacing relevant features, hiding unused ones)
   - At what point does the system "lock in" a profile vs. keep adapting?

4. **Core feature set**
   - What is the minimal viable planner (start simple)?
   - What is the full feature surface once adapted?
   - Journal/reflection features (mood, habits, daily log, weekly review)
   - Planning features (tasks, goals, time blocks, priorities, deadlines)
   - Integration points (calendar sync, reminders, tags, search)

5. **Data model considerations**
   - What entities does a universal planner need? (entries, tasks, goals, habits, time blocks, tags, moods...)
   - How do different planning methodologies map to these entities?
   - What schema flexibility is needed to support multiple paradigms?

6. **Architecture decisions**
   - FastAPI design: REST vs. GraphQL, authentication approach, versioning strategy
   - Flask/Quart web layer: server-side rendering vs. htmx/AJAX, session handling
   - How Flask talks to FastAPI (internal HTTP calls? shared DB access?)
   - Mobile readiness: what API contracts matter most for future mobile clients?

7. **Build sequence**
   - What should be built first?
   - What decisions lock in early and are hard to change?
   - What can be deferred?
</research_areas>

<output>
Save the brainstorm document to: `./docs/brainstorm/001-planner-brainstorm.md`

The document should include:
- An executive summary of the core concept
- A structured catalogue of planning methodologies with user profiles
- User archetype definitions with distinguishing signals
- Adaptive personalization strategy and mechanics
- Feature set organized by: MVP → Adapted (per archetype)
- Data model sketch (entities and relationships)
- Architecture recommendations for the FastAPI + Flask/Quart stack
- Recommended build sequence with rationale
- Open questions that need decisions before implementation
</output>

<verification>
Before completing, verify:
- All 7 research areas above are addressed in the document
- At least 8 planning methodologies are catalogued with user profiles
- The adaptive personalization section includes concrete behavioral signals (not just "observe the user")
- Architecture section addresses both the FastAPI-Flask relationship AND mobile readiness
- Build sequence is specific (what comes first, why) not generic
- Open questions section exists and contains real unresolved decisions
</verification>

<success_criteria>
The brainstorm document is comprehensive enough to:
1. Brief a developer on exactly what this product is and who it's for
2. Guide a product decision about which planning paradigm to implement first
3. Inform the initial data model design
4. Justify the FastAPI + Flask architectural split
</success_criteria>
