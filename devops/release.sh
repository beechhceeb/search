#!/usr/bin/env bash

# Exit on any error
set -e

COMMITER=$(git log -1 --format='%ae')

echo "Commited by $COMMITER"

if [ "$COMMITER" = "dev-ci@mpb.com" ]; then
  echo "Skipping release due to commit from CI"
  exit 0
fi

# Check last commit message (2 commits ago because of merge commit)
LAST_COMMIT_MESSAGE=$(git log -2 --pretty=%B)

# Increase version based on commit message (version = major.minor.patch)
# Check if the last commit message contains the string "MAJOR:" or "MINOR:"
# otherwise assume this is a patch
if [[ $LAST_COMMIT_MESSAGE == *MAJOR:* ]]; then
  poetry version major
  NEW_VERSION=$(poetry version major -s)
  BUMPED="major"
elif [[ $LAST_COMMIT_MESSAGE == *MINOR:* ]]; then
  NEW_VERSION=$(poetry version minor -s)
  BUMPED="minor"
else
  NEW_VERSION=$(poetry version patch -s)
  BUMPED="patch"
fi

echo "Building the package"
poetry build

echo "Adding version change"
git add pyproject.toml

echo "Committing the package update"
git commit -m "Bump ${BUMPED} version to ${NEW_VERSION}"
git tag ${NEW_VERSION}

# Push the package update
echo "Pushing the package update"
git push
git push --tags
