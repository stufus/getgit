# Summary
This is a quick script which uses Gitlab APIs to list every project that a low privilege user has access to and either clone the repo or pull (to update changes). It has the effect of allowing you to easily keep a local copy up to date of every repo in an organisatoin.

If any project has a wiki, it will clone that too.

# Setup
To get an API token, you need to:
1. Log into gitlab.
2. Go to User Settings/Access Tokens (```/-/user_settings/personal_access_tokens```)
3. Create an access token which needs ```read_api```

# Bugs
Probably, and you'll need to customise the code if you want to do anything different.

# Examples

Checkout everything I have access to on https://git.boat.internal and store it in /usr/home/stuart/git-org (API token: glpat-ssHXnCabQjFhQier_A4)

```$ ./getgit.py -t glpat-ssHXnCabQjFhQier_A4 -u https://git.boat.internal -d /usr/home/stuart/git-org```

Checkout everything I have access to on https://git.boat.internal and store it in /usr/home/stuart/git-org and suppress SSH banner (API token: glpat-ssHXnCabQjFhQier_A4)

```$ GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=error" ./getgit.py -t glpat-ssHXnCabQjFhQier_A4 -u https://git.boat.internal -d /usr/home/stuart/git-org```

Further help

```./getgit.py -h```
