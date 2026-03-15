---
id: 001
title: Establish Textbook Constitution
stage: constitution
date: 2026-01-20
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: master
user: architext
command: /sp.constitution
labels: ["governance","spec-driven","robotics","education","standards"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - Constitution compliance checklist
  - No unresolved placeholders
---

## Prompt

Core principles:
- Technical accuracy from official documentation and peer-reviewed sources
- Educational clarity for students with programming/AI background
- Hands-on practicality with tested code examples
- Industry-standard tools (ROS 2, NVIDIA Isaac, Gazebo, Unity)
- Spec-driven development with full documentation

Key standards:
- Citations: IEEE format, traceable to official docs (60%), peer-reviewed papers (30%), tutorials (10%)
- Code: PEP 8 compliant Python, functional ROS 2 packages, tested on Ubuntu 22.04
- Structure: Learning objectives per module, theory-example-exercise-assessment flow
- Quality: Zero plagiarism, Flesch-Kincaid grade 12-14
- Documentation: Runnable, well-documented code with GitHub version control

Content requirements:
- 4 Modules: (1) ROS 2 Fundamentals, (2) Gazebo/Unity Simulation, (3) NVIDIA Isaac, (4) VLA Integration
- 300-400 pages total
- Minimum 50 working code examples, 30 hands-on exercises
- 4 module assessments + 1 capstone project (autonomous humanoid)
- Progressive difficulty: beginner → intermediate → advanced

Technical constraints:
- Platform: Docusaurus, deployed to GitHub Pages
- RAG chatbot: OpenAI Agents/ChatKit SDK, FastAPI, Neon Serverless Postgres, Qdrant Cloud Free Tier
- Chatbot grounding: Only book content or user-selected text (no hallucinations)
- Hardware specs: RTX 4070 Ti+, Jetson Orin Nano (include cloud alternatives)
- Software: ROS 2 Humble/Iron, Gazebo, Unity, Isaac Sim/ROS
- RAG optimization: Content structured for vector embedding and retrieval
- Source control: GitHub-based with all specs via Spec-Kit Plus
- Code repository: GitHub-ready examples with comprehensive documentation

Success criteria:
- Live book deployed on GitHub Pages
- Fully functional embedded RAG chatbot answering book-specific queries
- All code executes error-free on specified hardware
- Measurable learning outcomes through exercises
- Technical review passed by robotics/AI experts
- End-to-end reproducibility of all examples
- Content supports personalization (user background) and Urdu translation
- Capstone achievable within quarter timeframe
- Safety protocols and simulation-first approach included

Special features support:
- Authentication integration (better-auth.com compatible)
- Personalization based on user software/hardware background
- Translation-ready structure for Urdu
- Glossary and prerequisites for varying student backgrounds

## Response snapshot

✅ **Constitution created at `.specify/memory/constitution.md` (v1.0.0)**

Created a comprehensive project constitution establishing governance for the Physical AI & Humanoid Robotics Textbook project. The constitution includes:

**5 Core Principles:**
1. Technical Accuracy and Sourcing (60% official docs, 30% peer-reviewed, 10% tutorials)
2. Hands-On Learning Through Working Code (50+ examples, all tested, PEP 8 compliant)
3. Spec-Driven Development and Full Documentation (specs → plans → tasks pipeline)
4. Modular, Progressive Content Architecture (4 modules, capstone, scaffolded difficulty)
5. Safety, Simulation-First, and Hardware Flexibility (Gazebo/Isaac/Unity validated, cloud alternatives)

**3 Supporting Sections:**
- Content Standards (citations, code quality, assessments)
- Technical Architecture (Docusaurus + Qdrant RAG, Ubuntu 22.04, ROS 2 Humble/Iron)
- Development Workflow (spec-driven pipeline, CI/CD, semantic versioning)

**Governance Framework:**
- Amendment procedure (rationale → proposal → review → version bump → migration plan)
- Compliance verification (pre-merge checks, annual audits, student feedback loops)
- Authority and escalation paths for operational conflicts

## Outcome

- ✅ Impact: Foundation established for 300–400 page robotics textbook with 50+ code examples, 30+ exercises, capstone project, and RAG chatbot
- 🧪 Tests: Constitution validated against no-placeholder and spec-alignment checks
- 📁 Files: `.specify/memory/constitution.md` (177 lines, v1.0.0)
- 🔁 Next prompts: Create spec for Module 1 (ROS 2 Fundamentals); design RAG chatbot grounding strategy; establish CI/CD for code validation
- 🧠 Reflection: Constitution successfully encodes project values (accuracy, hands-on learning, safety, spec-driven discipline) into enforceable governance. Ready to proceed with feature specifications and planning.

## Evaluation notes (flywheel)

- Failure modes observed: None in this stage
- Graders run and results (PASS/FAIL): ✅ PASS — No unresolved placeholders, version coherence, governance clarity
- Prompt variant (if applicable): Single-pass constitution generation with full principle integration
- Next experiment: Apply constitution checklist retroactively to existing content (if any); validate template alignment with spec/plan/tasks templates
