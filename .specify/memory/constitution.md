# Physical AI & Humanoid Robotics Textbook Constitution

<!--
SYNC IMPACT REPORT
Version: 0.1.0 (initial) → 1.0.0 (full constitution)
Stage: constitution
Modified Principles: (5 core principles + 3 supporting sections added)
Added Sections: Content Standards, Technical Architecture, Governance
Removed Sections: None (first version)
Templates Updated: Pending spec/plan/tasks templates alignment
Deferred Items: None
-->

## Core Principles

### I. Technical Accuracy and Sourcing

Every claim, API reference, and technical statement must be traceable to authoritative sources:
- Official documentation: 60% of citations (ROS 2 official docs, NVIDIA docs, Gazebo, Unity)
- Peer-reviewed research: 30% of citations (IEEE, ACM, robotics journals)
- Tutorial/community resources: 10% of citations (verified, widely-used examples)
- All citations formatted in IEEE format with direct links where possible
- Code examples validated against actual runtime environments (Ubuntu 22.04, specified hardware)
- No extrapolations beyond documented behavior; gaps explicitly flagged for further research

**Rationale**: Students rely on textbook accuracy for career preparation and research. False claims or outdated references undermine learning and waste time debugging non-existent issues.

### II. Hands-On Learning Through Working Code

Every concept must be demonstrated with runnable, tested code:
- Minimum 50 working code examples across all modules
- All examples follow PEP 8 style (Python), ROS 2 functional standards
- Examples tested and verified on Ubuntu 22.04 with specified hardware (or documented cloud alternatives)
- Exercises progress: read → modify → extend → build from scratch
- Code repositories on GitHub with version control, clear documentation, and reproducibility scripts
- No pseudocode or conceptual-only examples; all instructional code is production-ready patterns

**Rationale**: Robotics and AI are practice-driven. Reading without hands-on execution leaves knowledge abstract and untested. Working code builds confidence and reveals edge cases.

### III. Spec-Driven Development and Full Documentation

All features, modules, and exercises follow spec-driven development:
- Every module has explicit learning objectives, assessment criteria, and capstone milestones
- Specifications (specs) capture scope, constraints, and success criteria before implementation
- Plans document architectural decisions, alternatives, and tradeoffs (with ADRs for significant choices)
- Tasks break plans into testable units with acceptance criteria
- All code, exercises, and examples are documented inline and in supporting READMEs
- RAG chatbot grounding: responses limited strictly to book content or user-selected text (zero hallucination tolerance)

**Rationale**: Spec-driven development ensures clarity, consistency, and testability. It prevents scope creep and makes updates/translations systematic. Documentation-first approach supports long-term maintenance and educational value.

### IV. Modular, Progressive Content Architecture

Content is organized in strict progressive difficulty to scaffold learning:
- **Module 1: ROS 2 Fundamentals** (beginner) — Nodes, topics, services, actions, launch files
- **Module 2: Gazebo/Unity Simulation** (intermediate) — Physics engines, sensor simulation, environment setup
- **Module 3: NVIDIA Isaac** (intermediate-advanced) — Real-time perception, optimization, hardware integration
- **Module 4: VLA Integration** (advanced) — Vision-Language Actions, multi-modal planning, autonomous humanoid behaviors
- **Capstone Project** (advanced) — Autonomous humanoid robot (simulation → hardware) integrating all modules
- Each module includes 4 assessments (quizzes, mini-projects, peer review); capstone is achievable within quarter
- Prerequisites and glossary support varying student backgrounds (CS, robotics, AI)

**Rationale**: Progressive scaffolding prevents overwhelm and builds competency systematically. Clear prerequisites help students self-assess readiness.

### V. Safety, Simulation-First, and Hardware Flexibility

All robotics work prioritizes safety and practical accessibility:
- Simulation-first approach: all algorithms validated in Gazebo/Isaac/Unity before hardware deployment
- Safety protocols explicitly taught for hardware operation (safe velocity limits, emergency stops, collision detection)
- Hardware requirements include alternatives: primary (RTX 4070 Ti+, Jetson Orin Nano) + cloud options (NVIDIA Isaac Cloud, AWS, GCP)
- Code includes guards, timeouts, and fallback behaviors; no infinite loops or unbounded resource allocation
- Version compatibility documented (ROS 2 Humble/Iron, Gazebo 11+, Unity 2022.3+, Isaac Sim 2023.8+)

**Rationale**: Robotics safety is non-negotiable. Simulation-first reduces hardware damage and cost. Hardware alternatives ensure accessibility for students without high-end GPUs.

## Content Standards

### Citation and Attribution
- All facts, algorithms, and APIs cite original sources in IEEE format
- Code examples reference official documentation and include version numbers
- Surveys and state-of-the-art sections explicitly acknowledge seminal papers
- No plagiarism: content written originally with citations to prevent accidental reuse
- Readability: Flesch-Kincaid grade level 12–14 (technical but accessible to CS/AI students)

### Code Quality and Testing
- All code passes PEP 8 linting with automated checks (flake8, black)
- ROS 2 packages follow colcon build standards and pass all static analysis
- Unit tests required for every non-trivial function; integration tests for multi-module workflows
- Continuous integration (CI) verifies all examples on Ubuntu 22.04 before publication
- Documented failure modes and debugging strategies for common student errors

### Exercise and Assessment Framework
- 30+ hands-on exercises (theory → code → modification → extension)
- 4 module assessments: formative (quizzes, code reviews) + summative (mini-projects)
- Capstone project: autonomous humanoid simulation integrating all module concepts
- Grading rubrics transparent; learning outcomes measurable (knowledge, skills, competencies)
- Solutions available to instructors; student submissions support automated grading where possible

## Technical Architecture

### Deployment and Content Platform
- **Textbook**: Docusaurus-based static site deployed to GitHub Pages
- **Content Structure**: Markdown + MDX for interactivity; optimized for vector embeddings (semantic chunking)
- **RAG Chatbot**: OpenAI Agents API + ChatKit SDK, FastAPI backend, Neon Serverless Postgres, Qdrant Cloud Free Tier
- **Chatbot Constraints**: Answers only grounded in book content or explicitly selected text; no web search, no external knowledge injection
- **Authentication**: Integration with better-auth.com for user accounts (optional personalization)

### Software and Hardware Specifications
- **Operating System**: Ubuntu 22.04 LTS (primary); cloud alternatives on AWS, GCP, Azure
- **ROS 2**: Humble and Iron distributions, colcon workspace standard
- **Simulators**: Gazebo 11+, NVIDIA Isaac Sim 2023.8+, Unity 2022.3+
- **AI/ML**: PyTorch, TensorFlow 2.x for VLA models; CUDA 12.x for GPU acceleration
- **Hardware (Primary)**: RTX 4070 Ti+ (desktop development), Jetson Orin Nano (edge deployment)
- **Cloud Alternatives**: NVIDIA Isaac Cloud, AWS RoboMaker, Lambda Labs GPU cloud

### RAG Optimization
- Content chunked semantically (paragraphs/subsections, not arbitrary token windows)
- Code blocks stored separately with metadata (module, difficulty, language)
- Embedding model: OpenAI text-embedding-3-small (cost-optimized)
- Retrieval strategy: keyword + semantic hybrid search for precision
- Response template enforces citation of source sections and module context

### Source Control and Reproducibility
- All code, specs, and documentation in GitHub with Git LFS for large files
- Every example includes: requirements.txt/environment.yml, setup script, README, expected output
- Docker files for reproducible environments (Ubuntu 22.04 + ROS 2 + dependencies)
- Automated CI/CD validates all code before merge; pre-commit hooks enforce standards

## Development Workflow

### Specification and Planning
- New content follows spec → plan → tasks → implementation pipeline
- Spec captures learning objectives, acceptance criteria, content scope
- Plan documents architectural choices (tooling, sequencing, assessment methods)
- Tasks define granular, testable units with estimated complexity
- Significant technical decisions documented in Architecture Decision Records (ADRs)

### Code Review and Quality Gates
- All code changes require peer review (at least one approval)
- CI pipeline must pass: linting, tests, documentation checks
- Documentation updates must accompany code changes
- Examples tested on target hardware before merge
- Compliance checklist: adheres to constitutional principles before approval

### Release and Iteration
- Semantic versioning: MAJOR (breaking changes to curriculum), MINOR (new modules/features), PATCH (fixes, refinements)
- Releases tagged on GitHub with changelogs; Docusaurus site rebuilt automatically
- Post-publication feedback captured; errata and updates published within 2 weeks
- Annual review cycle to maintain currency with ROS 2, NVIDIA, and VLA ecosystem updates

## Governance

### Authority and Amendments
This constitution is the authoritative guide for all project decisions. Amendments require:
1. **Rationale**: Documented need for change (why current principle is insufficient)
2. **Proposal**: New or amended principle with concrete examples
3. **Review**: Approval by at least two project maintainers and one external expert (roboticist or AI researcher)
4. **Version Bump**: MAJOR for principle removals, MINOR for additions/expansions, PATCH for clarifications
5. **Migration Plan**: How existing work aligns with amended principles (one-time effort or ongoing)
6. **Announcement**: Version history in constitution header + GitHub release notes

### Compliance Verification
- Pre-merge checklist: Does this commit satisfy all applicable constitutional principles?
- Module publication: Passes content review against standards (sourcing, code quality, learning outcomes)
- Annual audit: Verify all code examples still execute on current Ubuntu/ROS 2/hardware LTS versions
- Student feedback: Track and escalate principle conflicts or unforeseen gaps

### Guidance and Operations
- Runtime guidance in `/docs/DEVELOPMENT.md` and module READMEs (not in constitution)
- Templates (spec, plan, tasks) remain the source of truth for task structure
- When operational procedures conflict with constitution, escalate to maintainers
- No unilateral exceptions to core principles; document deviations with rationale

---

**Version**: 1.0.0 | **Ratified**: 2026-01-20 | **Last Amended**: 2026-01-20
