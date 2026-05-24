# Alfred — Local CTFd Test Instance

Everything lives in `~/Projects/alfred/`.

## One-time setup

```fish
cd ~/Projects/alfred
sudo docker compose up -d             # start CTFd
# wait ~10 seconds for boot
source venv/bin/activate.fish
python scripts/setup_demo.py          # configure instance, create challenges & token
```

Then configure Alfred:

```fish
python -m alfred config --url http://localhost:8000 --token <TOKEN FROM SETUP>
```

## Daily use

```fish
cd ~/Projects/alfred
source venv/bin/activate.fish
python -m alfred list
python -m alfred show 1
python -m alfred submit 1 'flag{s3ss10n_h4ck3d}'
python -m alfred scoreboard
python -m alfred tui
```

## Reset everything

```fish
cd ~/Projects/alfred
sudo docker compose down -v
sudo docker compose up -d
python scripts/setup_demo.py
```

## Sample challenges

| ID | Name          | Category | Points | Flag                        |
|----|---------------|----------|--------|-----------------------------|
| 1  | Admin Panel   | Web      | 500    | `flag{s3ss10n_h4ck3d}`      |
| 2  | RSA Oracle    | Crypto   | 400    | `flag{rs4_0r4cl3_br0k3n}`   |
| 3  | Buffer Overflow | Pwn    | 350    | `flag{buff3r_0v3rfl0w}`     |

## Notes

- CTFd runs in **users mode** (no teams). Login as `admin` / `admin` at http://localhost:8000
- The API token is printed by `setup_demo.py` — re-run it if you lose it
- Scoreboard shows only after at least one flag is solved
