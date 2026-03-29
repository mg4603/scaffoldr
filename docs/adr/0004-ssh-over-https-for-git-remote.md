# ADR 0004: Use SSH over HTTPS for git remote

**Status: Accepted**
**Date: 29-03-2026**

## Context
After creating a GitHub repo via the API, scaffoldr needs
to set a git remote and push the initial commit.
The GitHub API returns both an SSH URL
(git@github.com:user/repo.git) and an HTTPS URL
(https://github.com/user/repo.git).

Most developers have SSH keys configured with GitHub
as it is the standard for daily git usage. HTTPS 
requires either a credential manager or embedding
the token in the url, which risks leaking it via 
.git/config if not cleaned up immediately.

## Decision
Use SSH URL by default for the git remote. Make the
protocol configurable via use_ssh in config so users 
without SSH can fall back to HTTPS. HTTPS fallback
embeds the token in the URL for the push, then
immediately resets the remote to the clean URL.

## Alternatives Considered
- HTTPS only: simple but requires either credential
  manager or token embedding, risks token exposure
- SSH only: cleaner but breaks for users without 
  SSH keys configured on GitHub
- Let users pass `--no-ssh`/`--ssh` flag only: no 
  persistent preference, user has to pass it every time 

## Consequences
- SSH is the default, works for most developers
- use_ssh = false in config enables HTTP fallback
- HTTPS fallback is safe: token removed from remote
  URL immediately after push
- users without SSH must set use_ssh = false in their 
  config


