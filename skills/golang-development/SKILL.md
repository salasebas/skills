---
name: golang-development
description: "Use whenever you write or change Go code: conventions and testing."
---

# Go

- Use latest Go version (verify, don't assume). Build with `-ldflags="-s -w"`
- Check modernity: `go run golang.org/x/tools/gopls/internal/analysis/modernize/cmd/modernize@latest -fix -test ./...`
- Idiomatic Go: explicit error handling, early returns, small interfaces, composition, defer for cleanup, table-driven tests

## Go Testing

- When working with tests in Go, read in `references/go-testing.md` for actionable testing guidelines.
