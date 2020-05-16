#!/usr/bin/env bash
################################################################################
# sync.sh
# syncs the latest version of a file into the common branch
#
# binary files need special treatment:
#   png: unconditional checkout when changed
# wildcards are working, but need to be escaped
#
# Caveat:
# checkout --patch ignores binaries
################################################################################
set +x

files=(README.md scripts common 'common/*.png')
#files=(README.md scripts Car.ipynb BaseModel.py '*.png')
#files=('*.png')

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$SCRIPT_DIR/.."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [[ ! -d common ]]; then
  echo "-E- directory <common> does not exist."
  exit 1
fi

git show-ref --verify --quiet refs/heads/common
if [[ $? -ne 0 ]]; then
  echo "-E- branch <common> does not exist"
  exit 1
fi

pushd() {
  command pushd "$@" >/dev/null
}

popd() {
  command popd >/dev/null
}

sync_from_common() {
  echo "-M- Syncing FROM Common"
  for item in "${files[@]}"; do
    filename=$(basename -- "$item")
    extension="${filename##*.}"
    filename="$REPO/$item"
    echo "$item"
    if [[ "$extension" == 'png' ]]; then
      echo "-M- unconditional checkout of $item"
      git checkout common -- "$filename"
    else
      git checkout --patch common -- "$filename"
    fi
    echo "................................................................................"
  done
}

sync_to_common() {
  echo "-M- Syncing TO Common"
  for item in "${files[@]}"; do
    filename=$(basename -- "$item")
    extension="${filename##*.}"
    filename="$REPO/$item"
    echo "$item"
    COMMIT_HASH=$(git log -1 --date-order --all --format=format:%H -- "$filename")
    #git branch --contains "${COMMIT_HASH}"
    if [[ "$extension" == 'png' ]]; then
      echo "-M- unconditional checkout of $item"
      git checkout "${COMMIT_HASH}" -- "$filename"
    else
      git checkout --patch "${COMMIT_HASH}" -- "$filename"
    fi
    echo "................................................................................"
  done
}

############################## main ##############################
pushd "$REPO" || exit 1

if [[ $CURRENT_BRANCH == 'common' ]]; then
  sync_to_common
else
  sync_from_common
fi

popd || exit
