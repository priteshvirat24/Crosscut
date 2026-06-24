<p align="center">
  <img src="docs/screenshots/logo.png" alt="Crosscut" width="120" />
</p>

<h1 align="center">Crosscut</h1>

<p align="center">
  <strong>A GitLab Duo Agent Platform Flow powered by GitLab Orbit. Run only the tests that matter.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" />
  <img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python" />
  <img src="https://img.shields.io/badge/next.js-15-black.svg" alt="Next.js" />
  <img src="https://img.shields.io/badge/GitLab-Orbit-orange.svg" alt="GitLab Orbit" />
  <img src="https://img.shields.io/badge/Duo_Agent-Platform-green.svg" alt="Duo Agent Platform" />
</p>

---

## 📖 The Story

**The Developer Pain Point**  
Organizations run hundreds or thousands of tests for every merge request because they simply do not know which tests are actually affected by a change. Small code changes trigger massive CI workloads. Shared libraries multiply this cost exponentially across repositories. Developers wait longer for feedback, companies spend millions on unnecessary compute, and CI infrastructure scales inefficiently.

**How Crosscut Fixes It**  
Crosscut is a **GitLab Duo Agent Platform Flow** that acts as an autonomous CI optimizer. When a developer opens a Merge Request, the Crosscut Agent analyzes the diff and extracts the changed symbols. It then queries the **GitLab Orbit Knowledge Graph** (via `glab orbit remote`) to traverse incoming call relationships across all repositories. Crosscut discovers the exact transitive impact of the change, selects only the relevant test files, and dynamically generates a targeted child pipeline.

**What Changes for the Developer?**  
Developers no longer wait 45 minutes for a massive mono-repo or cross-repo test suite to run just to merge a 5-line change. Crosscut instantly reduces the CI payload (often by 90%+), executing only what matters. Feedback loops become instant. 

---

## 🚀 Features & Functionality

Crosscut operates completely natively within the GitLab ecosystem:
1. **Event Triggered**: Listens for GitLab Merge Request events.
2. **Diff Analysis**: An agent identifies changed symbols (e.g., `validate_payment()`).
3. **Orbit Traversal**: Issues precise Query DSL to the Orbit graph to find cross-repo dependents.
4. **Test Selection**: Cross-references Orbit nodes with known test files.
5. **Automated Action**: Triggers a targeted CI pipeline and posts the compute savings as a comment directly on the MR.

## 🛠️ Architecture

Crosscut is built as a highly visual, living demonstration of the Duo Agent Platform:
- **Backend**: Python 3.12, LangGraph (Agent workflows), and a dedicated `OrbitClient` subsystem for DSL generation.
- **Frontend**: A stunning Next.js 15 cinematic dashboard featuring real-time React Flow graphs, 3D interactive Orbit Reactors, and deep visualization of the Agent's decision cycle.

## 🏃 Quick Start

```bash
git clone https://gitlab.com/your-org/crosscut.git
cd crosscut
make install
cp .env.example .env
make dev
```

Visit `http://localhost:3000` to see the live dashboard, explore the **Orbit Query Viewer**, and watch the **Platform Integration Ecosystem** in action.

## 🎥 Hackathon Demo Scenario

**Trigger:** MR `!342` modifies `validate_payment()` in `payment-library`.  
**Orbit Discovery:** Orbit Remote traverses incoming calls, crossing into 4 other repositories (`checkout-service`, `billing-service`, etc.).  
**Agent Decision:** The Duo Agent identifies that out of 418 total tests across the ecosystem, only 12 are transitively impacted.  
**Action:** A pipeline runs 12 tests.  
**Result:** 97% compute reduction. Execution drops from 38 minutes to 2 minutes.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
