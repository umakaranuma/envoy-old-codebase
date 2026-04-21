---
trigger: always_on
---

# Development Rules

- Whenever starting development or research, the first step must always be to read the [README.md](/envoy/README.md) to understand the project context, setup, and any specific instructions.

- After completing any task or implementation, ask if you need to test in the browser and get confirmation; otherwise, do not do testing in the browser.

- After completing any task, implementation, or issue fix, update the task status in the @mentioned file. This status is located at the bottom of the file in a summary table. Once updated, move the file into a `/completed` sub-directory within the same directory as the mentioned file.

- Based on the README.md file tech stack, you must request confirmation on which directory you are going to work in when a task is assigned.

- When you are going to write code, you must first read and understand the skill for that language/framework. The skill files are located in the `.agents/skills/` folder.

- **Deployment Guidelines**: Once a task is done or implemented, if there are any deployment guidelines, they should be added to [.docs/deployment-guideline.md](/envoy/.docs/deployment-guideline.md)

- **Database Tables**: When creating tables, you must add the appropriate prefix based on the module:
  - `core_` for core module
  - `crm_` for crm module
  - `crmp_` for policy module
  - `crmf_` for finance module