# Before you start

Ensure we read again the RALPH.md file (this file) when we start a new iteration to ensure that we are updated on the general instructions. This file may change between iterations and it's the very first document we shall read.  

Read the file RALPH.local.md and add the instructions to the context if they aren't in the context yet. The RALPH.md (this file) has general instructions for any and all task. The RALPH.local.md has specific instructions to the current task.  

Read the files compound-engineering.local.md, AGENTS.md and the related files in the docs/ folder, specially in the subfolders docs/architecture and docs/solutions for old documentation, as a means to ensure you don't break decisions that were made before.  

# During work

We use the Compound Engineering method. Follow these steps in this order:  

1. Use the ce-brainstorm skill from the "compound-engineering" plugin before starting anything. This will generate a brainstorm document in docs/brainstorms/. Use that document for the next step;  
2. Use the ce-plan skill from the "compound-engineering" plugin using the brainstorm document as argument. This will generate a plan document in docs/plans/. Use that document for the next step, but before going to the next step, run the skill deepen-plan to update the document;  
3. Use the ce-work skill from the "compound-engineering" plugin using the plan document as argument. Use the same command more times until the plan document is implemented;  
4. Use the ce-review skill from the "compound-engineering" plugin after the work session. Use the same command more times until all work has been reviewed and problems identified;  
5. Use the ce-compound skill from the "compound-engineering" plugin after the review is finished. Ensure all knowledge is documented, files README.md, AGENTS.md and RALPH.md are all updated during this step.  

*Important*: Before compacting the context, use the ce-compound skill to ensure outstanding changes have been documented.   

## What to update in markdown files

### README.md

The file README.md is for humans and should describe the project we are working on in general. If the current session made changes and this document needs updating, update only the needed portions.  

### AGENTS.md

The file AGENTS.md has information for AI agents and should be updated with knowledge about this project in general that is relevant to any agent.  

### RALPH.md

The file RALPH.md (this file) is related to the "ralph-loop" plugin which we are using and should be updated with knowledge that is not just relevant to our current loop, but for Ralph in general.  

# Known Limitations

- **Subagent rate limits**: Spawning many parallel subagents (e.g., 13 for ce-review) can exhaust the API rate limit immediately. When this happens, fall back to inline review from direct codebase reads — the main conversation context has no rate limit issue, only the spawned sub-agents do.
- **Subagent plugin file access**: Subagents spawned via the Agent tool cannot read files under `~/.claude/plugins/cache/`. If a skill instructs subagents to read plugin references (e.g., `references/schema.yaml`), the main conversation should read those files and pass the content directly in the subagent prompt, or do that work inline.

# When you finish

After each iteration, update the knowledge about what was tried and didn't work to the RALPH.local.md file so the next iteration doesn't try the same things that won't work again.  

Ensure you update information in the RALPH.local.md that will allow the next iteration to figure out what has been done, what is actually working and what needs to be redone. That document should be the single source of truth about the task and the progress on how much we accomplished the task. We are not in a hurry and the other iterations can improve our work. It's a collective effort across time.  

If there's knowledge that exceeds the scope of the current task and it's useful for Ralph in general, update RALPH.md file (this file) as well.  
