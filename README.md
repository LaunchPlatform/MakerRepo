# MakerRepo

**MakerRepo** is an open-source Python library that brings the [Manufacturing as Code](https://docs.makerrepo.com/) concept into the [Build123D](https://github.com/gumyr/build123d) ecosystem.
It is designed to have **as little impact on your existing Build123D project as possible** — add a dependency and a few decorators; your models and workflow stay the same.

The makerrepo Python package (imported as `mr`) is a lightweight library that provides decorators such as `@artifact`, `@customizable`, and `@cached` to annotate functions that build your models.
The decorators have no effect on your existing Build123D code until it is discovered and run by tools such as [makerrepo-cli](https://github.com/LaunchPlatform/makerrepo-cli) or MakerRepo.com CI.
The goal is to enable a code-driven workflow locally (e.g. command-line tools) or in CI.
The library does not assume how it will be consumed, so annotated functions can be used with other tools and frameworks as well.
It brings Manufacturing as Code into the Build123D ecosystem.

## What is MakerRepo?

[MakerRepo](https://makerrepo.com/) is a GitHub-like platform for manufacturing as code.
You write Python code to define 3D models with Build123D, push to a Git repository on MakerRepo, and the platform builds your models and hosts the resulting CAD artifacts so you can view and share them.

This repository is the **MakerRepo Library** — the `mr` package you add to your project to expose Build123D artifacts to MakerRepo.com (e.g. via the `@artifact` decorator).
The platform’s CI then discovers, builds, and publishes those artifacts.

## Features

- **Artifacts** — Use the `@artifact` decorator to mark Build123D model functions as publishable CAD artifacts. Control options like sample/cover images and export formats (STEP, 3MF).
- **Customizables (generators)** — Use the `@customizable` decorator to define parameterized generators with a Pydantic schema for user-configurable models.
- **Cached helpers** — Use the `@cached` decorator to tag functions whose outputs can be cached to speed up builds.

## Getting started

1. Create a repository on [MakerRepo.com](https://makerrepo.com/).
2. Add `makerrepo` to your project and use the `@artifact` decorator on your Build123D model functions (see [Getting Started](https://docs.makerrepo.com/) in the docs).
3. Push your code — CI runs and publishes artifacts to the web UI.

## Documentation

- [MakerRepo Docs](https://docs.makerrepo.com/) — Full documentation, getting started, and concepts.
- [MakerRepo CLI](https://docs.makerrepo.com/makerrepo-cli/) — Use `makerrepo-cli` to build artifacts and run workflows from the command line.

## Requirements

- Python ≥ 3.11
- [Build123D](https://github.com/gumyr/build123d) ≥ 0.10.0

## License

MIT
