# Development Guidelines

## Core Principles

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

### 2. Decision Documentation
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

#### Recent Examples:

**1. Web Interface Architecture**
- **Option A**: Full template system everywhere (too complex)
- **Option B**: Hybrid approach (chosen - simple + structured where needed)
- **Option C**: Pure inline HTML everywhere (too limited for meeting data)

**2. Real-time Transcript Display** 
- **Option A**: Polling every second (inefficient)
- **Option B**: WebSocket with SocketIO (chosen - efficient real-time updates)
- **Option C**: Server-sent events (good but less interactive)

**3. Copy Functionality**
- **Option A**: Manual text selection (user friction)
- **Option B**: One-click copy buttons (chosen - efficient workflow)
- **Option C**: Multiple export formats upfront (over-engineering)

## Implementation Standards

### Code Quality
- **Readability First**: Code should be self-documenting
- **Minimal Dependencies**: Only add libraries that solve real problems
- **Error Handling**: Graceful degradation, not silent failures
- **Testing**: Mock components for development, real components for production

### Architecture Decisions
- **Start Simple**: Begin with the most basic working solution
- **Iterate Purposefully**: Add complexity only when justified
- **Hybrid Approaches**: Mix simple and complex as needed
- **User Experience**: Optimize for the primary use case first

### Documentation Requirements
- **Decision Rationale**: Why this approach over alternatives
- **Trade-offs**: What we gained and what we sacrificed
- **Future Considerations**: How decisions impact future development
- **Examples**: Show the decision in action

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

## Success Examples

### ✅ Meeting Agent Web Interface
**Problem**: Need meeting management with copy functionality
**Options Considered**: 
- Full SPA framework (too complex)
- Pure server-side rendering (too limited)  
- Hybrid approach (chosen)

**Why Hybrid**: Simple dashboard for basic controls, rich templates for meeting data, perfect balance of simplicity and functionality.

### ✅ Configuration Management
**Problem**: Need secrets and settings management
**Options Considered**:
- All in config files (insecure)
- All in environment variables (hard to manage)
- Hybrid approach (chosen)

**Why Hybrid**: Secrets in environment (secure), settings in YAML (manageable), best of both approaches.

This approach ensures every solution is well-reasoned, documented, and optimized for both simplicity and effectiveness.