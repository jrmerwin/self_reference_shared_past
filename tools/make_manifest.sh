#!/usr/bin/env bash
# Regenerate MANIFEST.sha256.
#
# Covers every git-tracked file in the repository except the manifest itself,
# in sorted order, so the output is deterministic and diffable. Run from
# anywhere inside the working tree:
#
#     bash tools/make_manifest.sh
#
# Verify with:
#
#     sha256sum -c MANIFEST.sha256      # GNU coreutils / Git Bash
#     shasum -a 256 -c MANIFEST.sha256  # macOS
#
# Digests are taken in binary mode (-b), so they are byte-exact and independent
# of platform line-ending settings. .gitattributes sets "* -text" to stop git
# from rewriting line endings on checkout, which would otherwise invalidate
# every digest here on a Windows clone.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

git ls-files -z \
  | grep -zv '^MANIFEST\.sha256$' \
  | sort -z \
  | xargs -0 sha256sum -b \
  > MANIFEST.sha256

printf 'MANIFEST.sha256: %s files\n' "$(wc -l < MANIFEST.sha256)"
