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

### namespell

`namespell` searches files for proper nouns, where the capitalization (or lack
thereof) of letters is important (e.g. `Zarhus` or `coreboot`) and checks if
they are spelled correctly. When the `-f/--fix` flag is passed, the tool
automatically fixes incorrectly spelled words.

There are several ways to ignore unwanted checks:

* To exclude entire files/directories from being checked specify an
[exclude](https://pre-commit.com/#config-exclude) section in
`.pre-commit-config.yaml`.

* Inline ignores are also supported

Inline ignore statements are comments in a file that tell `namespell` to ignore
specific rules/lines. They have the following structure:

```bash
<comment start> namespell:disable <rule1, rule2>
```

If no rules are specified, all of them will be ignored.

You can use inline ignores to disable checks for an entire file or specific
lines. If the statement is placed in the first line of the file, it will apply
to the whole file. If it's placed at the end of a specific line, it will only
apply to that line. The example below illustrates this.

```bash
# namespell:disable Zarhus

zarhus dasharo
zarhus dasharo Coreboot # namespell:disable Dasharo
dasharo Coreboot
```

```bash
somefile:3: 'dasharo' should be 'Dasharo'
somefile:4: 'Coreboot' should be 'coreboot'
somefile:5: 'dasharo' should be 'Dasharo'
somefile:5: 'Coreboot' should be 'coreboot'
```

As you can see, the spelling of `Zarhus` is ignored throughout the whole file
and the spelling of `Dasharo` is only ignored in line 4.

### check-upstream-status

The goal is to enforce
[these rules](https://docs.dasharo.com/dev-proc/source-code-structure/#commit-message-guidelines).
