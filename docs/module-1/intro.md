# Module 1: ROS 2 Fundamentals - The Robotic Nervous System

## Module Overview

Welcome to **Module 1: ROS 2 Fundamentals**. In this module, you will learn the foundational concepts and practical skills needed to work with ROS 2 (Robot Operating System 2), the industry-standard middleware for robotics software development.

This module is designed for **students with Python and AI/ML backgrounds** who want to integrate their AI models with robotic systems. You'll move from "Hello World" examples to building real communication patterns and robot descriptions.

### What is ROS 2?

ROS 2 is a flexible framework for writing robot software. It provides:

- **Distributed communication**: Nodes running on different machines can exchange messages seamlessly
- **Hardware abstraction**: Write once, run on different robot platforms
- **Message passing**: Topics, services, and actions for flexible inter-process communication
- **Standard tools**: CLI utilities, visualization software, and debugging tools
- **Large ecosystem**: Pre-built packages for perception, control, navigation, and more

Think of ROS 2 as the "nervous system" of a robot—it enables different components (sensors, controllers, AI modules) to work together.

---

## Learning Objectives

By the end of this module, you will:

- ✅ Understand ROS 2 architecture and how nodes communicate
- ✅ Write Python ROS 2 nodes that publish and subscribe to topics
- ✅ Implement services and actions for different communication patterns
- ✅ Design custom message types for your applications
- ✅ Write URDF descriptions for humanoid robots
- ✅ Visualize robots and sensor data using RViz2
- ✅ Integrate Python AI code with ROS 2 control systems

---

## Prerequisites

Before starting this module, you should have:

- **Python 3.10+**: Comfortable with Python programming (classes, decorators, async patterns)
- **Linux basics**: Comfortable with Ubuntu terminal (apt, file paths, environment variables)
- **Git**: Basic git workflow (clone, commit, push)
- **System requirements**:
  - Ubuntu 22.04 LTS (recommended) or compatible Linux distribution
  - 4GB RAM minimum (8GB recommended for simulation)
  - 5GB disk space

---

## Module Structure

### Phase I: Foundational (Weeks 1-2)
- **Chapter 0**: Setup & Installation
- **Chapter 1**: ROS 2 Architecture (Nodes, Topics, Pub/Sub)

### Phase II: Advanced (Weeks 3-4)
- **Chapter 2**: Communication Patterns (Services, Actions, Custom Messages)
- **Chapter 3**: URDF & Robot Description

### Assessments
- **Formative Quizzes**: After each chapter to reinforce learning
- **Hands-on Exercises**: 6 exercises with automated grading
- **Capstone Project**: Integrate all concepts to build a simple humanoid controller

---

## Time Commitment

| Component | Estimated Time |
|-----------|-----------------|
| Chapter 0 (Setup) | 1-2 hours |
| Chapter 1 (Architecture) | 8-10 hours |
| Chapter 2 (Patterns) | 10-12 hours |
| Chapter 3 (URDF) | 8-10 hours |
| Exercises (6 total) | 6-8 hours |
| Capstone Project | 3-4 hours |
| **Total** | **36-46 hours** |

**Recommended pace**: 8-12 hours per week over 4-5 weeks

---

## Chapter Summary

### Chapter 0: Setup & Installation
**Goal**: Get ROS 2 running on your machine

- System requirements and preparation
- ROS 2 Humble installation on Ubuntu 22.04
- Colcon workspace creation and initialization
- Installation verification and troubleshooting
- Cloud alternatives (AWS RoboMaker, NVIDIA Isaac Cloud)

**Outcomes**: Your first ROS 2 command works → `ros2 --version`

---

### Chapter 1: ROS 2 Architecture
**Goal**: Understand how ROS 2 nodes communicate

- What is ROS 2 and why use it?
- Nodes: The computational units of ROS 2
- Topics: Asynchronous, many-to-many communication
- Publishers and subscribers: The pub/sub pattern
- Message types: Standard and custom
- ROS 2 CLI tools: Introspection and debugging
- Running and visualizing ROS 2 systems

**Outcomes**: You can write a publisher and subscriber, run them together, and inspect communication using CLI tools

---

### Chapter 2: Communication Patterns
**Goal**: Master the different ways ROS 2 nodes communicate

- Topic patterns: Filtering, QoS, adapting to bandwidth
- Services: Synchronous, request-reply communication
- Actions: Goal-based, long-running operations with feedback
- Custom message types: Defining .msg files and using them
- Launch files: Running multiple nodes with configuration
- Real-world example: Integrating AI code with joint controllers

**Outcomes**: You can implement services, actions, custom messages, and integrate Python AI code with ROS 2 control loops

---

### Chapter 3: URDF & Robot Description
**Goal**: Learn to describe robot structure and visualize it

- URDF: The Unified Robot Description Format (XML-based)
- Links: Rigid bodies with geometry, mass, and collision shapes
- Joints: Connections between links with constraints
- Humanoid robot anatomy: Torso, arms, legs, and joint types
- Visualization in RViz2: Loading and displaying robot models
- From URDF to simulation: Preparing for physics engines
- Validating and debugging URDF files

**Outcomes**: You can write URDF descriptions for humanoid robots and visualize them in RViz2

---

## Success Criteria

You've successfully completed this module when:

- ✅ You install ROS 2 Humble on Ubuntu 22.04 without errors
- ✅ All 12 code examples run successfully on your machine
- ✅ You complete all 6 exercises and pass automated tests
- ✅ You score ≥70% on formative quizzes
- ✅ You complete the capstone project (building a simple humanoid controller)
- ✅ You demonstrate understanding of pub/sub, services, actions, and URDF

---

## How to Use This Module

### For Students

1. **Start with Chapter 0**: Follow installation steps exactly; don't skip verification
2. **Read Chapter 1**: Understand the foundational concepts
3. **Run the examples**: Don't just read—run each example and modify it
4. **Do the exercises**: They have automated tests; iteration is expected
5. **Attempt the project**: Integrate what you've learned
6. **Revisit as needed**: Use the glossary and chapter refs to reinforce concepts

### For Instructors

1. **Use the quizzes**: Formative assessments after each chapter
2. **Grade exercises**: Automated tests + manual review of code quality
3. **Facilitate project**: Set office hours for capstone project support
4. **Customize examples**: Add institution-specific robots or use cases
5. **Track time**: Each student learns at different pace; adjust deadlines

---

## Technical Context

| Component | Version | Why This Choice |
|-----------|---------|-----------------|
| **ROS 2** | Humble | LTS version with Ubuntu 22.04 support; latest stable |
| **Ubuntu** | 22.04 LTS | Supported until 2032; official ROS 2 support |
| **Python** | 3.10+ | Modern Python features; rclpy stable on this version |
| **Docusaurus** | 3.x | Fast, Markdown-native, GitHub Pages friendly |
| **Test Framework** | pytest | Industry standard; great CI/CD integration |

---

## Key Terminology

Don't know what a term means? See the **Glossary** (next section) for quick definitions. The glossary includes 50+ ROS 2 terms with examples.

---

## About This Module

**Status**: Ready for Publication (v1.0.0)

**Content Volume**: 80-100 pages of rendered content

**Code Examples**: 12 working examples, tested on Ubuntu 22.04 + ROS 2 Humble

**Exercises**: 6 hands-on exercises with reference solutions and automated acceptance tests

**Author**: AI/Robotics Curriculum Team

**Citation**: If you use this module in your teaching, please cite:
> "Module 1: ROS 2 Fundamentals – The Robotic Nervous System," Hackathon Project, 2026

---

## Quick Start

Ready to dive in? Here's the fastest path:

1. **Install ROS 2**: Follow [Chapter 0: Setup & Installation](./chapter-0-setup.md)
2. **Run your first example**: Jump to [Chapter 1: Hello World](./chapter-1.md#running-hello-world)
3. **Do an exercise**: Try [Exercise 1.1: Create a Publisher](../exercises/1-1-create-publisher/README.md)
4. **Stuck?** Check the troubleshooting section in [Chapter 0](./chapter-0-setup.md#troubleshooting)

---

## Support & Resources

- **Official ROS 2 Docs**: https://docs.ros.org/en/humble/
- **ROS Answers**: https://answers.ros.org/
- **This Module's Glossary**: See [Glossary](./glossary.md)
- **Example Index**: See [Examples README](../../examples/README.md)

---

**Ready? Let's go!** Start with [Chapter 0: Setup & Installation](./chapter-0-setup.md) →

---

*Last updated: 2026-01-22*
*Version: 1.0.0 | Branch: 001-ros2-fundamentals*
