# ADR 0005: XDG-Compliant Config Path via platformdirs

**Status: Accepted**   
**Date: 24-04-2026**   

## Context
v0.1.0 stores config at `~/.scaffoldr/config.toml` and user issue
templates at `~/.scaffoldr/issues.toml`.
The `~/.scaffoldr/` convention clutters the home directory and 
ignores the XDG Base Directory Specification, which defines 
`$XDG_CONFIG_HOME` (defaulting to `~/.config/`) as the correct 
location for user config files on linux.
macOS and Windows have their own conventions.

Hardcoding `~/.scaffoldr/` also means that `scaffoldr` behaves
differently from the rest of the CLI tool ecosystem..

## Decision
Use the `platformdirs` library to resolve the config directory at 
runtime via `user_config_dir("scaffoldr")`.
This yields:
  Linux:   `~/.config/scaffoldr/`       (or `$XDG_CONFIG_HOME`)
  macOS:   `~/Library/Application Support/scaffoldr/`
  Windows: `C:\Users\<user>\AppData\Local\scaffoldr`

All config-path references in the codebase will use a single
`CONFIG_DIR` constant derived from `platformdirs`. 
The old `~/.scaffoldr/` path will be detected on startup; if 
present and the new path is absent, a deprecation warning is 
printed to stderr. A `scaffoldr config migrate` command will move 
files to the new location.

## Alternatives Considered
- Hardcode `~/.config/scaffoldr/`: correct on Linux but wrong on 
  macOS and windows. Rejected.
- Use the `appdirs` library: predecessor to `platformdirs`, 
  unmaintained since 2021. Rejected.
- Keep `~/.scaffoldr`: non-standard, clutters home dir, 
  inconsistent with ecosystem. Rejected

## Consequences
### Positives
- Follows platform conventions on all OSes
- Single config directory footprint for all future scaffoldr
  config files (templates dir, etc.)

### Negatives
- Breaking changes for v0.1.0 users - mitigated by automatic
  detection and migrate command
- New dependency: `platformdirs>=4.0.0`
