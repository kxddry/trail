# Trail - Adultify: Production-Grade Product

## Spotlight V3: Tree-aware Navigator
- [x] Extend Spotlight contracts/results/actions for tree-aware nodes, external fallback actions, and graph preview RPC
- [x] Index pinned/current/archived tree nodes for cross-tree Spotlight search
- [x] Implement foreign-tree open flow and default-search-engine fallback actions
- [x] Fix Spotlight graph hover so transient hover never recenters and committed selection restores correctly
- [x] Add foreign-tree graph preview in Spotlight and restructure the left rail into titled sections
- [x] Run Spotlight typecheck/tests and capture follow-up notes

## Phase 1: Requirements Gathering (Agent Teams)
- [ ] **Security Architect** - Auth, session persistence, token lifecycle, vulnerabilities
- [ ] **QA Engineer** - Bug discovery, test gaps, error handling audit
- [ ] **DevOps Engineer** - CI/CD gaps, deployment hardening, monitoring
- [ ] **UX Reviewer** - UI/UX issues, error states, loading states, accessibility

## Phase 2: Backlog Creation
- [ ] Synthesize findings into prioritized backlog
- [ ] Critical bugs first (auth session expiry bug)
- [ ] CI/CD improvements
- [ ] Code quality improvements

## Phase 3: Implementation (Agent Teams)
- [ ] Fix auth session persistence bug (user-reported)
- [ ] Fix all discovered bugs
- [ ] Implement CI/CD improvements
- [ ] Code quality fixes

## Phase 4: Verification & PR
- [ ] Run all tests
- [ ] Verify auth fix works
- [ ] Create PR to main
