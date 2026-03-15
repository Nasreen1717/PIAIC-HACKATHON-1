# Implementation Plan: Module 1 - ROS 2 Fundamentals

**Branch**: `001-ros2-fundamentals` | **Date**: 2026-01-21 | **Spec**: `specs/001-ros2-fundamentals/spec.md`
**Input**: Feature specification from `/specs/001-ros2-fundamentals/spec.md`

## Summary

Module 1 delivers a Docusaurus-based interactive textbook for teaching ROS 2 fundamentals to students with Python and AI backgrounds. The module comprises 3 comprehensive chapters covering ROS 2 architecture, communication patterns, and URDF robot description. All content is authored in Markdown with integrated code examples, exercises, and learning assessments. Implementation prioritizes hands-on learning with working code examples validated on Ubuntu 22.04 with ROS 2 Humble, progressive difficulty scaffolding (beginner → intermediate), and spec-driven content architecture following the project constitution.

## Technical Context

**Language/Version**: Python 3.10+, ROS 2 Humble (Ubuntu 22.04 LTS)
**Primary Dependencies**: Docusaurus 3.x (static site generation), MDX (interactive markdown), rclpy (ROS 2 Python client), colcon (build system), RViz2 (visualization)
**Storage**: Markdown files (.md) in `docs/` directory; code examples as separate Python/shell files
**Testing**: pytest (Python unit tests), ROS 2 built-in testing, shell script validation, automated CI/CD
**Target Platform**: Linux (Ubuntu 22.04 LTS), deployed to GitHub Pages or similar static hosting
**Project Type**: Multi-chapter educational content with integrated code examples and exercises
**Performance Goals**: Page load < 2s, code examples run in < 30s, exercises completable in 30 min each
**Constraints**: Content must be accessible offline (post-build), all code examples must run without external dependencies (beyond ROS 2 installation)
**Scale/Scope**: 80-100 pages of rendered content, 12 code examples minimum, 6 hands-on exercises, ~10k LOC (including examples and tests)

## Constitution Check

**GATE**: Must pass all checks before Phase 0 research. Re-check after Phase 1 design.

| Principle | Status | Justification |
|-----------|--------|---|
| **I. Technical Accuracy & Sourcing** | ✅ PASS | All code examples will be validated against ROS 2 official docs; citations formatted IEEE; peer-reviewed robotics literature for concepts |
| **II. Hands-On Learning** | ✅ PASS | 12+ code examples, 6 exercises with solutions, all PEP 8 compliant, tested on Ubuntu 22.04 |
| **III. Spec-Driven Development** | ✅ PASS | Specification complete; plan documents architecture; tasks will follow; ADR suggestions for significant decisions |
| **IV. Modular, Progressive Architecture** | ✅ PASS | Chapter 1 (foundational), Chapter 2 (intermediate patterns), Chapter 3 (application to robots); prerequisites explicit |
| **V. Safety, Simulation-First** | ✅ PASS | All examples use simulation-safe patterns (no hardware required); safety constraints documented in URDF chapter |

**Gate Result**: ✅ **APPROVED** — All constitutional principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/001-ros2-fundamentals/
├── spec.md                          # Feature specification (complete)
├── plan.md                          # This file (implementation architecture)
├── research.md                      # Phase 0: dependency research & validation
├── data-model.md                    # Phase 1: content entities & structure
├── quickstart.md                    # Phase 1: setup and first-run guide
├── contracts/                       # Phase 1: API/interface contracts
│   ├── chapter-structure.json       # Chapter metadata format
│   ├── code-example-format.json     # Code example metadata
│   └── exercise-format.json         # Exercise acceptance criteria format
├── checklists/
│   └── requirements.md              # Functional requirements checklist
└── tasks.md                         # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
docs/                                 # Docusaurus content root
├── index.md                          # Module landing page
├── module-1/
│   ├── intro.md                     # Module overview, learning objectives
│   ├── chapter-1.md                 # Chapter 1: ROS 2 Architecture
│   ├── chapter-2.md                 # Chapter 2: Communication Patterns
│   ├── chapter-3.md                 # Chapter 3: URDF and Robot Description
│   ├── glossary.md                  # ROS 2 terminology reference
│   └── assessments/
│       ├── quiz-1.md                # Chapter 1 quiz (formative)
│       ├── quiz-2.md                # Chapter 2 quiz (formative)
│       ├── quiz-3.md                # Chapter 3 quiz (formative)
│       └── mini-project.md          # Module capstone (summative)
│
├── examples/                        # Code examples (referenced from chapters)
│   ├── 1-hello-world-pub.py         # Chapter 1: Publisher example
│   ├── 1-hello-world-sub.py         # Chapter 1: Subscriber example
│   ├── 1-topic-introspection.sh     # Chapter 1: ROS 2 CLI tools demo
│   ├── 2-service-server.py          # Chapter 2: Service server
│   ├── 2-service-client.py          # Chapter 2: Service client
│   ├── 2-custom-message.msg         # Chapter 2: Custom message definition
│   ├── 2-action-server.py           # Chapter 2: Action server
│   ├── 2-action-client.py           # Chapter 2: Action client
│   ├── 3-simple-humanoid.urdf       # Chapter 3: Simple humanoid URDF
│   ├── 3-humanoid-extended.urdf     # Chapter 3: Extended humanoid URDF
│   └── README.md                    # Examples index and setup instructions
│
├── exercises/                       # Hands-on exercises with solutions
│   ├── 1-1-create-publisher/
│   │   ├── README.md                # Exercise description & acceptance criteria
│   │   ├── solution.py              # Complete solution
│   │   └── test_solution.py         # Automated acceptance tests
│   ├── 1-2-modify-subscriber/
│   │   ├── README.md
│   │   ├── solution.py
│   │   └── test_solution.py
│   ├── 2-1-service-integration/
│   │   ├── README.md
│   │   ├── solution.py
│   │   └── test_solution.py
│   ├── 2-2-custom-messages/
│   │   ├── README.md
│   │   ├── solution.py
│   │   └── test_solution.py
│   ├── 3-1-basic-urdf/
│   │   ├── README.md
│   │   ├── solution.urdf
│   │   └── test_urdf.py
│   └── 3-2-humanoid-extension/
│       ├── README.md
│       ├── solution.urdf
│       └── test_urdf.py
│
├── scripts/                         # Setup and validation scripts
│   ├── install-ros2-humble.sh       # Ubuntu 22.04 installation automation
│   ├── setup-colcon-workspace.sh    # Workspace initialization
│   ├── verify-installation.sh       # Installation verification script
│   └── validate-examples.sh         # Test all examples and exercises
│
└── tests/                           # Integration and quality tests
    ├── conftest.py                  # pytest fixtures for ROS 2 testing
    ├── test_chapter_1.py            # Chapter 1 code example tests
    ├── test_chapter_2.py            # Chapter 2 code example tests
    ├── test_chapter_3.py            # Chapter 3 URDF validation tests
    └── test_content_quality.py      # Citation, spelling, structure checks
```

**Structure Decision**: A modular content-first structure (Option 1 + Documentation) where:
- **docs/** contains Docusaurus markdown chapters, assessments, and interactive content
- **examples/** contains all code examples referenced in chapters (separate files for clarity, tested independently)
- **exercises/** contains hands-on exercises with automated acceptance tests
- **scripts/** provides setup and validation automation for reproducibility
- **tests/** validates all content (code correctness, documentation quality, citations)

This separation ensures that code examples are independently testable, exercises have clear acceptance criteria, and documentation quality is enforced automatically.

## Complexity Tracking

No constitutional violations detected. All decisions align with principles:

| Decision | Justification | Alternatives Considered |
|----------|---|---|
| **Markdown-first content** | Supports semantic chunking for RAG; version-controllable; Docusaurus-native | Database-driven: higher operational cost, harder to version control |
| **Separate code examples** | Easier testing, CI/CD integration, code reuse across chapters | Embedded in markdown: hard to test, duplication |
| **pytest + ROS 2 testing** | Industry standard, integrates with CI/CD, catches Python errors early | Manual testing: unreliable, not scalable |
| **3-chapter structure** | Aligns with spec (Ch1: architecture, Ch2: patterns, Ch3: URDF); beginner-intermediate progression | 4+ chapters: scope creep; 2 chapters: insufficient depth |

## Key Architectural Decisions

### 1. Content Delivery: Markdown + Docusaurus (Decision #1)

**Choice**: Static Markdown files processed by Docusaurus 3.x with MDX support for interactive elements.

**Rationale**:
- Markdown is version-control friendly and readable in source form
- Docusaurus generates fast, static sites suitable for GitHub Pages deployment
- MDX allows inline React components for interactive visualizations (e.g., ROS 2 pub/sub diagrams)
- Semantic chunking naturally aligns with markdown structure (paragraphs, code blocks)
- No database required; content is portable and accessible offline post-build

**Alternatives Considered**:
- **Database-backed CMS** (Strapi, Contentful): Higher operational overhead, not suitable for educational version control
- **Jupyter Notebooks**: Harder to render in static site, less suitable for prose-heavy chapters
- **PDF-first**: Not web-friendly, harder to maintain versioning, poor for RAG chunking

**Risk Mitigation**: Validate markdown parsing with Docusaurus build; enforce RFC 5646 heading hierarchy for semantic chunking.

---

### 2. Code Examples: Separate Files with Test Coverage (Decision #2)

**Choice**: Each code example lives in `examples/` as independent Python or shell script with automated pytest tests.

**Rationale**:
- Allows examples to be run, tested, and validated independently during CI/CD
- Prevents duplicate code (examples referenced via `:::include` in markdown)
- PEP 8 linting and pytest coverage enforced in CI
- Exercises can extend examples without code duplication
- Clear traceability: which chapter uses which example

**Alternatives Considered**:
- **Embedded in markdown**: Simpler initially, but hard to test; duplicated if used across chapters
- **Generated from comments**: Fragile; easy to break during maintenance

**Risk Mitigation**: Document example naming convention (`<chapter>-<concept>-<type>`); maintain example index in `examples/README.md`.

---

### 3. Progressive Difficulty & Chapter Sequencing (Decision #3)

**Choice**: Strict sequential progression: Chapter 1 (foundational) → Chapter 2 (patterns) → Chapter 3 (application).

**Rationale**:
- Spec prioritizes foundational knowledge (P1 stories require Ch1 before Ch2)
- Each chapter builds on previous concepts without repetition
- Prevents cognitive overload (beginner → intermediate progression)
- Aligns with constitution's modular, progressive architecture principle

**Chapter Breakdown**:
1. **Chapter 1: ROS 2 Architecture** (Foundational, 25-30 pages)
   - Nodes, topics, pub/sub concepts
   - Installation and workspace setup
   - "Hello World" publisher/subscriber example
   - ROS 2 CLI tools (topic, node, service commands)
   - Exercises: Create publisher, modify subscriber

2. **Chapter 2: Communication Patterns** (Intermediate, 30-35 pages)
   - Topics (async, many-to-many)
   - Services (sync, request-reply)
   - Actions (goal-feedback-result)
   - Custom message types (.msg files)
   - Launch files and parameter configuration
   - Exercises: Implement service, define custom messages

3. **Chapter 3: URDF and Robot Description** (Intermediate-to-Application, 25-30 pages)
   - URDF syntax (links, joints, frames, inertia)
   - Humanoid robot structure (torso, arms, legs)
   - Collision and visual geometry
   - Visualization in RViz2
   - Exercises: Write simple URDF, extend humanoid model

**Risk Mitigation**: Cross-reference prerequisite concepts; glossary provides just-in-time explanations.

---

### 4. Testing & Validation Strategy (Decision #4)

**Choice**: Multi-level testing: code example tests (pytest), URDF validation, documentation quality checks.

**Rationale**:
- Constitution requires code examples validated on Ubuntu 22.04 with ROS 2 Humble
- Automated testing catches regressions during content updates
- Quality checks enforce citation formatting, spelling, reading level
- CI/CD integration ensures all examples run before documentation is published

**Test Levels**:
1. **Code Example Tests** (examples/): pytest validates syntax, runs on simulated ROS 2
2. **Exercise Acceptance Tests** (exercises/*/test_*.py): Automated grading against rubrics
3. **URDF Validation** (test_chapter_3.py): URDF parser validates syntax, visualization in RViz2
4. **Documentation Quality** (test_content_quality.py): IEEE citation format, reading level, no plagiarism
5. **Integration Tests** (tests/test_chapter_*.py): Full workflow validation (install → build → run)

**Risk Mitigation**: Tests run in isolated Docker environment matching student target (Ubuntu 22.04 + ROS 2 Humble).

---

### 5. Exercise Framework & Grading (Decision #5)

**Choice**: Each exercise has a README (problem description), solution code, and automated pytest tests.

**Rationale**:
- Clear problem statement prevents ambiguity
- Solution available for instructor reference and grading
- Automated tests provide consistent, objective grading (pass/fail)
- Students can self-check progress locally before submission

**Exercise Structure**:
```
exercises/<chapter>-<number>-<name>/
├── README.md                        # Problem, learning objectives, acceptance criteria
├── solution.py (or .urdf)           # Reference implementation
└── test_solution.py                 # Pytest assertions (what students must satisfy)
```

**Grading Rubric** (in README):
- **Functionality**: Code runs without errors (automated test)
- **Correctness**: Produces expected output/behavior (automated test assertions)
- **Code Quality**: Follows PEP 8, includes docstrings (linter check)
- **Documentation**: Inline comments explain non-obvious logic (manual review)

**Risk Mitigation**: Keep acceptance tests simple (< 5 assertions per exercise); provide hints in README if tests fail.

---

### 6. Citation & Attribution Strategy (Decision #6)

**Choice**: IEEE citation format, inline citations with footnote links, bibliography per chapter.

**Rationale**:
- IEEE format is standard in robotics and engineering education
- Inline citations maintain reading flow while providing attribution
- Chapter-level bibliography supports selective reading
- Enables automated checking (citations must resolve to working URLs)

**Citation Format** (IEEE style):
```markdown
ROS 2 topics enable asynchronous, publish-subscribe communication [1].

[1] Open Robotics, "Understanding ROS 2 Topics," ROS 2 Documentation, 2025.
    [Online]. Available: https://docs.ros.org/en/humble/Concepts/Intermediate/About-Topic.html.
    [Accessed: Jan. 21, 2026].
```

**Risk Mitigation**: Validate all citation URLs in CI; maintain citation metadata in frontmatter (YAML) for semantic chunking.

---

## Design Phases

### Phase 0: Research & Validation (Output: `research.md`)

Research tasks to resolve technical unknowns:

1. **ROS 2 Humble installation on Ubuntu 22.04**: Verify official documentation, test installation script
2. **colcon workspace structure**: Validate directory layout, build artifacts
3. **rclpy API stability**: Confirm Python 3.10+ compatibility, no breaking changes in recent releases
4. **URDF parser capabilities**: Test XML parsing, joint type validation, RViz2 visualization
5. **Docusaurus 3.x MDX support**: Test interactive code examples, embedded visualizations
6. **IEEE citation standards**: Verify format for textbooks, online sources (DOI vs URL)
7. **ROS 2 testing best practices**: Research rclpy testing patterns, mock/fixture approaches
8. **Semantic chunking for RAG**: Determine optimal markdown structure for vector embeddings

**Deliverable**: `research.md` with findings, rationale, and any required adjustments to technical context.

### Phase 1: Design & Content Structure (Output: `data-model.md`, `contracts/`, `quickstart.md`)

Design tasks:

1. **Content Entity Model** (`data-model.md`):
   - Chapter entity: title, learning objectives, prerequisites, estimated time
   - Code example entity: name, concept, language, tested-on (ROS 2 version), dependencies
   - Exercise entity: description, learning objectives, acceptance criteria, estimated time
   - Assessment entity: type (quiz/mini-project), questions/rubric, expected completion time

2. **Content Contracts** (`contracts/`):
   - `chapter-structure.json`: Chapter metadata schema (title, objectives, prerequisites, sections)
   - `code-example-format.json`: Example metadata (name, concept, language, tested-version, dependencies, citation)
   - `exercise-format.json`: Exercise metadata (description, acceptance-criteria list, estimated-time-min)

3. **Quick-Start Guide** (`quickstart.md`):
   - Installation verification on Ubuntu 22.04
   - First example walkthrough (Chapter 1 "Hello World")
   - Debugging tips for common setup issues

4. **Agent Context Update**:
   - Run `.specify/scripts/bash/update-agent-context.ps1` (fallback: manual update)
   - Add Docusaurus, ROS 2, URDF, rclpy to tech stack documentation

**Deliverable**: Complete data model, JSON contracts, quickstart guide; agent context updated.

### Phase 2: Task Generation (Output: `/sp.tasks` command)

Task generation (deferred to `/sp.tasks` command) will produce `tasks.md` with:
- Granular writing tasks (outline chapter, write theory section, code examples, exercises)
- Code development tasks (implement example, write tests, validate on CI)
- Quality assurance tasks (review citations, verify formatting, spell check)
- Integration tasks (Docusaurus build, deploy to GitHub Pages)

**Deliverable**: `tasks.md` with dependency graph and estimated complexity.

---

## Technology Stack Decisions

| Technology | Version | Decision | Justification |
|-----------|---------|----------|---|
| **Docusaurus** | 3.x | ✅ Chosen | Fast, static site generation; native Markdown support; GitHub Pages deployment; MDX for interactivity |
| **ROS 2** | Humble | ✅ Chosen | LTS version, Ubuntu 22.04 official support; latest stable at time of spec |
| **Python** | 3.10+ | ✅ Chosen | Students assumed to have Python knowledge; rclpy stable on 3.10+ |
| **Testing** | pytest | ✅ Chosen | Industry standard; integrates with CI/CD; works with ROS 2 testing patterns |
| **URDF** | Standard | ✅ Chosen | ROS 2 standard format; supported by RViz2, Gazebo, Isaac Sim |
| **VCS** | Git + GitHub | ✅ Chosen | Spec prerequisite; enables CI/CD; standard for educational content |

---

## Success Metrics (from Spec)

| Metric | Target | Validation Method |
|--------|--------|---|
| Installation success rate | 100% on first attempt | CI/CD on Ubuntu 22.04 docker image |
| Code example pass rate | 100% (12 examples) | pytest on each example |
| Exercise completion rate | 80% of students | Student survey post-module |
| Content volume | 80-100 pages | Docusaurus build output |
| Citations | IEEE format, 100% working | URL validation in CI |
| Reading level | Flesch-Kincaid 12-14 | Automated readability check |
| Code quality | PEP 8 compliant | flake8 linter in CI |

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|---|
| ROS 2 version mismatch | Code examples won't run | Pin Humble version in CI; test on official docker image |
| URDF visualization failure | Students can't verify exercises | Provide RViz2 screenshot validation; fallback to XML parsing check |
| Docusaurus build failures | Content unreleased | Test build locally before push; use pre-commit hooks |
| Citation link rot | Outdated references | Automated URL check in CI; manual audit quarterly |
| Student environment variance | Examples fail on some systems | Provide Docker environment for reproducibility; troubleshooting guide |
| Scope creep (more chapters) | Timeline delays | Spec defines 3 chapters only; defer advanced topics to Module 2-4 |

---

## Next Steps

1. **Phase 0**: Run research tasks, resolve unknowns in `research.md`
2. **Phase 1**: Generate data model, content contracts, quickstart guide
3. **Phase 2**: Execute `/sp.tasks` to generate granular implementation tasks
4. **Implementation**: Execute tasks as defined in `/sp.tasks` output
5. **Review & Merge**: PR review, CI/CD validation, merge to main branch

---

**Version**: 1.0.0 | **Status**: Ready for Phase 0 Research | **Branch**: `001-ros2-fundamentals`
