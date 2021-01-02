# Submodules

This project contains [submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

This means that other git repos are embedded in this one, so special commands/processes must be used to work with these multiple repos.

When cloning for the first time, use `git clone --recurse-submodule` or `git clone; git submodule update --init`
to make sure submodules are cloned as well.

To pull changes to the submodule, use `cd <submodule> ; git clone`
or `git submodule update` (use the `--init` flag to be safe).

# Dev Hints

Go [here](https://discord.com/developers/applications/790129414310068224/bot) to get the bot token.
