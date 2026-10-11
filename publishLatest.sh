#!/usr/bin/env bash
set -euo pipefail

# Publish the newest built application PDFs as assets of a rolling GitHub release.
#
# Usage: ./publishLatest.sh [application-dir]
#   application-dir   directory containing Bewerbung/build (default: newest under applications/)
#
# Env:
#   RELEASE_TAG    release tag to create/update (default: latest)
#   RELEASE_REPO   repo to publish to, e.g. MBanucu/application (default: current repo)
#   DRY_RUN        set to any value to only print what would be published

releaseTag="${RELEASE_TAG:-latest}"

appDir="${1:-}"
if [ -z "$appDir" ]; then
	appDir=$(ls -1dt applications/*/ 2>/dev/null | head -1)
fi
appDir="${appDir%/}"
if [ -z "$appDir" ]; then
	echo "No application directory found" >&2
	exit 1
fi

shopt -s nullglob
pdfs=()
for dir in "$appDir"/Bewerbung/build/*/; do
	newest=$(ls -1t "$dir"*.pdf 2>/dev/null | head -1)
	if [ -n "$newest" ]; then
		pdfs+=("$newest")
	fi
done
if [ ${#pdfs[@]} -eq 0 ]; then
	echo "No built PDFs found in $appDir" >&2
	exit 1
fi

if [ -n "${DRY_RUN:-}" ]; then
	printf 'Would publish to release "%s":\n' "$releaseTag"
	printf '  %s\n' "${pdfs[@]}"
	exit 0
fi

repoArgs=()
if [ -n "${RELEASE_REPO:-}" ]; then
	repoArgs=(--repo "$RELEASE_REPO")
fi

if ! gh release view "$releaseTag" "${repoArgs[@]}" >/dev/null 2>&1; then
	gh release create "$releaseTag" "${repoArgs[@]}" \
		--title "Latest application" \
		--notes "Rolling release containing the most recently built application PDF."
fi
gh release upload "$releaseTag" "${pdfs[@]}" "${repoArgs[@]}" --clobber
