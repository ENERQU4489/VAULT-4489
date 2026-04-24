# GEMINI Context: Obsidian Second Brain (Software Engineering)

## Directory Overview
This directory is an Obsidian Vault organized for a software engineer's long-term knowledge management and daily workflow. It follows a hybrid PARA (Projects, Areas, Resources, Archive) structure with a dedicated temporal logging system.

### Folder Structure
- **`00 Daily`**: Stores daily notes and logs. This is the primary entry point for each workday.
- **`10 Inbox`**: A "capture" zone for raw thoughts, links, and snippets that haven't been processed yet.
- **`20 Projects`**: Active, goal-oriented tasks and project-specific documentation (e.g., "Feature X Implementation").
- **`30 Areas`**: Long-term responsibilities and themes that require ongoing maintenance (e.g., "Infrastructure", "Career Development", "Team Management").
- **`40 Brain`**: The "Second Brain" or Evergreen notes. High-density technical knowledge, language references, and architectural patterns.
- **`90 Meta`**: System-level content.
    - **`Templates`**: Markdown templates for standardizing note creation (Daily Notes, Project Kickoffs, etc.).
    - **`Attachments`**: Centralized storage for images, PDFs, and other non-markdown files.
- **`99 Archive`**: Completed projects or deprecated knowledge that is no longer active but worth preserving.

## Key Files
- **`.obsidian/`**: Contains vault configuration, including enabled plugins (`Templater`, `Calendar`, `Terminal`) and UI themes (Nord, Obsidianite, Wasp).
- **`90 Meta/Templates/Daily Note Template.md`**: The standard structure for daily logs, focusing on daily goals, technical discovery, and brain dumps.

## Usage & Workflow
1.  **Daily Logging**: Use the `Daily Note Template` to start every day in `00 Daily`. Document focus areas and technical hurdles.
2.  **Rapid Capture**: Save transient information in `10 Inbox` to avoid friction during deep work.
3.  **Refinement**: Periodically move notes from `Inbox` or `Daily` into `40 Brain` (for permanent knowledge) or `20 Projects` (for actionable work).
4.  **Linking**: Heavily utilize Obsidian's `[[WikiLinks]]` to connect technical concepts in `40 Brain` to specific project implementations in `20 Projects`.

## Technical Configuration
- **Primary Plugins**: `Templater` (for dynamic templates), `Calendar` (for navigating daily logs), and `Terminal` (for CLI access within Obsidian).
- **Core Plugins Enabled**: Daily Notes, Templates, Graph View, Backlinks, Canvas.
