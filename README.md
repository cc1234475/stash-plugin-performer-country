# Stash plugin: Performer Country

This is a plugin for stash. It adds a `country performers` task. 
This task processes all preformers and replace any none standard country code provided by other services and bring them in line with what stash can display.

# How to set it up

Add the python files too your `.stash/plugins` directory

create a `virtualenv`

```bash
virtualenv -p python3 --system-site-packages ~/.stash/plugins/env
source ~/.stash/plugins/env/bin/activate
pip install ~/.stash/plugins/requirements.txt
```

# How to use

Rescan the plugins, you will find a new button in the `Tasks` sections in the settings.

