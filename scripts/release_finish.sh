#!/bin/bash

# release 브랜치를 받아옵니다.
release_branch=$1

# release 브랜치를 finish 합니다.
git flow release finish $release_branch

# develop 브랜치로 체크아웃합니다.
git checkout develop

# 병합 직전 커밋에서 development 폴더를 복원합니다.
git checkout HEAD~1 -- development

# 복원된 폴더를 커밋합니다.
git commit -am "Restore development folder after release finish"
