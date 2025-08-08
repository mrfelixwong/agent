# CLAUDE.md - Project Instructions

## Project Overview
This is a Meeting Agent that records, transcribes, and summarizes meetings with cost tracking and a web interface.

## Core Development Principles

### 1. Simplest and Most Efficient Approach
**Always generate solutions and code with the simplest and most efficient approach**

- **Simplest**: Prefer straightforward, readable solutions over complex architectures
- **Most Efficient**: Optimize for performance, maintainability, and user experience
- **Balance**: Simple deployment with rich functionality where needed

#### Examples:
- ✅ **Hybrid UI**: Simple inline HTML for basic pages, templates for complex data
- ✅ **Mock Components**: Use mocks for testing, real components for production
- ✅ **Configuration**: Secrets in environment variables, settings in YAML files
- ❌ **Over-engineering**: Full microservices for a single-user meeting agent
- ❌ **Complexity**: Complex ORM when simple database operations suffice

### 2. Decision Documentation Requirement
**For each request, tell me what alternatives you considered, and why you pick the current one**

Every implementation decision must include:

#### Format:
```
## 🎯 Implementation Options

### Option A: [Approach Name]
**Pros:** [Benefits]  
**Cons:** [Drawbacks]  
**Complexity:** [Low/Medium/High]

### Option B: [Approach Name] (Recommended)
**Pros:** [Benefits]  
**Cons:** [Drawbacks]  
**Complexity:** [Low/Medium/High]

## ✅ Decision: Why Option B
- **Simplicity**: [How it's simpler]
- **Efficiency**: [How it's more efficient]  
- **Use Case Fit**: [How it matches requirements]
```

## Key Architecture Decisions

### Configuration System (Hybrid Approach)
- **Secrets** (API keys, passwords) → Environment variables in `~/.zshrc`
- **Settings** (ports, models, paths) → Config file `config/settings.yml` 
- **Never** create `.env` files - always use shell profile for secrets

### Web Interface Architecture (Hybrid)
- **Dashboard**: Simple inline HTML for basic meeting controls
- **Meeting Pages**: Proper templates for structured data display
- **Copy Functionality**: One-click ChatGPT-ready formatting
- **Real-time Features**: WebSocket for live transcript updates

### File Structure
- `src/` - Main application code
- `src/web/templates/` - HTML templates for meeting pages
- `production_cli.py` - Primary entry point
- `start_web.py` - Web interface launcher
- `tests/` - Unit tests (keep these)
- `test_*.py` - Integration tests (keep these)

## Implementation Standards

### Code Quality Requirements
1. **Security First**
   - Never commit API keys or secrets
   - Always use environment variables for sensitive data
   - Keep non-sensitive settings in YAML config files

2. **Simplicity First**
   - Remove unnecessary debug/demo files
   - Keep the codebase clean and focused
   - Maintain proper separation of concerns
   - Choose simple solutions over complex architectures

3. **Environment Variables**
   - Only for secrets: `OPENAI_API_KEY`, `EMAIL_ADDRESS`, `EMAIL_PASSWORD`
   - Users should add these to `~/.zshrc`, not `.env` files
   - Validate secrets only for real components, skip for mock components

4. **Cost Tracking**
   - Track transcription costs ($0.006/minute default)
   - Store in database and display in UI
   - Make cost per minute configurable in settings.yml

5. **Testing Strategy**
   - Use mock components for testing (`use_mock_components=True`)
   - Keep integration tests for real API validation
   - Always test web interface functionality

## Decision Examples

### Recent Implementation Decisions:

**1. Web Interface Architecture**
- **Option A**: Full template system everywhere (too complex)
- **Option B**: Hybrid approach (chosen - simple + structured where needed)
- **Option C**: Pure inline HTML everywhere (too limited for meeting data)

**Why Hybrid**: Simple dashboard for basic controls, rich templates for meeting data, perfect balance of simplicity and functionality.

**2. Real-time Transcript Display** 
- **Option A**: Polling every second (inefficient)
- **Option B**: WebSocket with SocketIO (chosen - efficient real-time updates)
- **Option C**: Server-sent events (good but less interactive)

**Why WebSocket**: Most efficient for real-time bidirectional communication with graceful fallback.

**3. Copy Functionality**
- **Option A**: Manual text selection (user friction)
- **Option B**: One-click copy buttons (chosen - efficient workflow)
- **Option C**: Multiple export formats upfront (over-engineering)

**Why One-click**: Optimizes for primary use case (ChatGPT discussion) with minimal complexity.

## Review Checklist

Before implementing any solution, ask:

1. **Is this the simplest approach that meets requirements?**
2. **What alternatives did I consider?**
3. **Can I explain why this is most efficient?** 
4. **Does this optimize for the primary use case?**
5. **Will this be easy to maintain and extend?**

## Anti-Patterns to Avoid

### ❌ Over-Engineering
- Complex abstractions for simple problems
- Full frameworks for basic functionality
- Premature optimization without measurement

### ❌ Under-Engineering  
- No error handling or edge case consideration
- Hardcoded values instead of configuration
- No separation of concerns

### ❌ Poor Decision Documentation
- "Because it's better" without explanation
- No consideration of alternatives
- Missing trade-off analysis

## Development Guidelines

- Use the hybrid configuration system (secrets in env, settings in YAML)
- Maintain cost tracking for all transcription operations
- Keep the web interface simple and functional
- Follow the existing code patterns and structure
- Always validate configuration but skip validation for mocks
- Document alternatives considered for each implementation decision

## Files to Never Recreate
- setup_env.py (removed - use ~/.zshrc instead)
- .env files (use environment variables)
- Debug/demo files (keep codebase clean)
- Empty placeholder directories

## When Making Changes
1. **Document Alternatives**: List options considered and reasoning
2. **Test with Mock Components**: `python test_web.py`
3. **Ensure Secrets Work**: Test with real API keys if available
4. **Maintain Hybrid Config**: Secrets in env, settings in YAML
5. **Keep Cost Tracking**: All transcription operations must track costs
6. **Update Documentation**: If architecture changes, update this file
7. **Push to GitHub**: Commit changes after each significant update

## Success Criteria
- **Simplicity**: New developers can understand the codebase quickly
- **Efficiency**: System performs well with minimal resource usage
- **Maintainability**: Changes are easy to make without breaking existing functionality
- **User Experience**: Primary workflows (record, review, copy to ChatGPT) are seamless