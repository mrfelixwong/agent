# CLAUDE.md - AI Assistant Instructions

## Project Overview
Meeting Agent that records, transcribes, and summarizes meetings with cost tracking and web interface.

## Core Requirements

### 1. Always Use Simplest & Most Efficient Approach
- Prefer straightforward solutions over complex architectures
- Optimize for performance, maintainability, and user experience
- Balance simple deployment with rich functionality where needed

### 2. Document All Decisions
For each request, tell me:
- What alternatives you considered
- Why you picked the current approach
- Trade-offs made

**Format:**
```
## Options Considered:
- Option A: [Approach] - Pros/Cons
- Option B: [Approach] - Pros/Cons (Recommended)

## Decision: Why Option B
- Simpler because: [reason]
- More efficient because: [reason]
- Better fits use case: [reason]
```

## Key Architecture Rules

**Configuration (Hybrid):**
- Secrets → Environment variables in `~/.zshrc` (never `.env` files)
- Settings → `config/settings.yml`

**Web Interface (Hybrid):**
- Dashboard: Simple inline HTML
- Meeting pages: Proper templates for structured data
- Copy functionality: One-click ChatGPT-ready format

**Testing:**
- Development: `use_mock_components=True` (no API keys needed)
- Production: Real components with environment variables

## Implementation Standards

1. **Security**: Never commit secrets, use environment variables
2. **Simplicity**: Remove unnecessary files, choose simple solutions
3. **Cost Tracking**: All transcription operations must track costs
4. **Error Handling**: Graceful degradation, not silent failures

## Anti-Patterns to Avoid
- ❌ Over-engineering: Complex abstractions for simple problems
- ❌ Under-engineering: No error handling, hardcoded values
- ❌ Poor documentation: "Because it's better" without reasoning

## Files to Never Create
- `.env` files (use ~/.zshrc)
- `setup_env.py` files (removed)
- Debug/demo files (keep codebase clean)

## Workflow
1. Document alternatives and reasoning for each decision
2. Test with mock components first
3. Maintain hybrid config approach (secrets in env, settings in YAML)
4. Keep cost tracking intact
5. Push to GitHub after significant changes

## Success Criteria
- New developers understand codebase quickly
- System performs well with minimal resources  
- Changes don't break existing functionality
- Primary workflows (record → review → copy to ChatGPT) are seamless