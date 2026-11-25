## install UV python encironment manager
https://docs.astral.sh/uv/

## creating python environment with uv
```bash
uv init --bare --python 3.13
```

### download  and sync all the python packages . 

```bash
uv sync --python 3.13
```
> this will automatically create python .venv

### run backend
```bash
uv run fastapi dev
```


### to see the api docs  

after successfull run you can find the documentations by using http://127.0.0.1:8000/docs