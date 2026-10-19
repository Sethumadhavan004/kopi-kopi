# Contributing

Thanks for wanting to help. kopi-kopi is small on purpose, so the best contributions keep it simple.

## Set up

```
git clone https://github.com/Sethumadhavan004/kopi-kopi
cd kopi-kopi
pip install -e ".[dev]"
```

`-e` installs it "editable": your changes take effect without reinstalling.

## Before you open a pull request

```
ruff check .          # style and common mistakes
python -m pytest      # all tests
```

Both also run automatically on every push (GitHub Actions, on Windows and Linux).

Changed the cursor art or colours? Render a preview and look at it:

```
python tools/preview.py cursors.gif --ibeam
```

## Where things live

Start with [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In short:

- behaviour (what a tap means): `kopi_kopi/core.py`, with tests in `tests/test_core.py`
- anything OS-specific: `kopi_kopi/platforms/`
- the cursor look: `kopi_kopi/cursor_art.py` and `kopi_kopi/config.py`

**Adding macOS or Linux:** write `kopi_kopi/platforms/<os>.py` with the functions listed in
`kopi_kopi/platforms/__init__.py`, and pick it in `load()`. The state machine stays as it is.

## Making a release (maintainers)

1. Update the version in `kopi_kopi/__init__.py` and add an entry to `CHANGELOG.md`, through a PR.
2. Try the build first: Actions → **Release** → *Run workflow* on `main`, then download and run the artifacts.
3. Tag `main`: `git tag v1.0.0 && git push origin v1.0.0`. The tag must match the version, or the release stops.
4. GitHub Actions tests the built app, creates the GitHub Release (Windows zip + Python package)
   and publishes to PyPI.
