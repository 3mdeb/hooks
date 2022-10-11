# About

## Goal

The goal of this repository is to provide a common place for (pre-commit) hooks
used to verify the quality of deliverables (such as docuemntation) produced by
3mdeb.

## Usage

* You need to clone this repository to obtain a local copy of tools and
  configuration files. You can then use these tools against any other
  repository/file you need.

```bash
git clone https://github.com/3mdeb/hooks.git
```

* Refer to the section below for description of the individual tools.

## Current state

At present, this repository does not meet the above goal (yet) ;)

We need to figure out how to easily setup and maintain hooks over **multiplte**
repositories. Until then, we can simply require to run selected tools from this
repository before publishing content.

This repository does provide some configs and scripts, which can be used to
verify the basic quality of deliverables.

Please refer to the below sections to learn more about currently available
tools.

### Markdown

The goal of this tool is to verify the formatting guidelines of markdown
file, which we primarily use when creating documentation. **All** documentation
created by 3mdeb **must** adhere to these guidelines (unless there are
project-specific guidelines stating otherwise).

You can refer to the [.markdownlint.yaml](.markdownlint.yaml) for guidelines
description.

* Run markdown linter on a file `README.md`:

```bash
./markdown.sh check README.md
```

* Automatically fix some of the problems in `README.md` file:

> This can significantly speed up quality improvements of the document. But
> keep in mind that you need to review automatic fixes before publishing them,
> of course.

```bash
./markdown.sh fix README.md
```
