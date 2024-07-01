## Python Package Setup

### Setup Base

To install required pip modules for `generate_toml.py`, run
``` bash
source scripts/setup_base.sh
```

### User Setup

- go to `generate_toml.py` file, and complete the setup in the `User Setup` session.

```python
options = Options(
    # Will you use the discussion session in your repo?
    discussion=False
)

# Define the general information of your package
kwargs = Kwargs(
    name_space="None",
    module_name="None",
    description="None",
)
```

If you wrote all the information, run
```
python generate_toml.py
```

#### Template

If you want to understand the generation process, check the `template` variable in `generate_toml.py`.

### Setup Env

#### Prerequisite

Finish [User Setup](#user-setup) first.
Of course, conda command must be available.

#### Setup Env

Run
``` bash
source scripts/setup_env.sh
```

steps
- create an conda environment named as your $MODULE_NAME
- activate the environment.
- install requirements.txt

## Workflows

Not documented yet.
