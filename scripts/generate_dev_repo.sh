#!/bin/bash

echo "Enter the parent repository name:"
read parent_repo

dev_repo="${parent_repo}-dev"

gh repo create "$dev_repo" --private --description "Development repository for $parent_repo" --gitignore Python

if [ $? -eq 0 ]; then
    echo "Successfully created repository: $dev_repo"

    git clone "https://github.com/crimson206/$dev_repo.git"
else
    echo "Failed to create repository: $dev_repo"
fi
