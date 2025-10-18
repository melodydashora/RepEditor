#!/usr/bin/env bash
#
# Remote Token Generation via curl
# Downloads and executes token generation script from GitHub
#

set -e

echo "Downloading token generator..."

# Download and execute the script
curl -fsSL https://raw.githubusercontent.com/melodydashora/Vecto-Pilot/main/tools/generate-tokens.sh | bash

# Or run locally if already cloned:
# bash tools/generate-tokens.sh
