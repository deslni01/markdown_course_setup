# Intro

After tinkering with various note-taking systems, I've decided on an approach that I like. To facilitate easy implementation I've developed this script, as my system has a few steps that would be time-consuming to replicate on a course-by-course basis.

## Format/System

### Markdown File Structure

The system I use, as it stands now, contains a `properties` YAML section which can be used by various programs; I personally use _Obsidian_ and _Front Matter Title_.

- Properties:
  - `title` - automatically filled out for the specific markdown file, including the course short-name, as well as the section/subsection numbers, and the title.
  - `tags` - default empty array, to add tags to as needed
  - `dates` - default empty array, not included in main course index file

Below the `properties` YAML section is the _TOC - Table of Contents_.

- These are automatically filled out using the _Obsidian_ link to the file, as well as the name of the _section_/_subsection_.
- In the main _course index page_, each _section_ and its _subsections_ are present, with the _subsections_ being indented under its parent _section_.
- In the _section_ and _subsection_ files, all _section_ links are present, but only the _subsections_ of the parent _section_ are present.

Below the _TOC_ are pre-populated sections for _Key Points/Concepts_ and _Lecture_ - but this can be customized in the code using the `extra` argument in the `_render_markdown()` function.

- The _Flashcard_ files pre-populate with subsections for each of the _subsections_ present.

Example of a generated _subsection_ file:

```
---
title: BDSA 3134 - 01.03 - More Info on This Topic
tags: []
dates: []
---
# 01.03 - More Info on This Topic
## TOC
- Example Course Title
- 01.00 - Course Overview
  - 01.01 - Introduction
  - 01.02 - Foundations of This Topic
  - 01.03 - More Info on This Topic
  - 01.99 - Course Overview Flashcards
- 02.00 - Advanced Concepts
- 03.00 - Utilizing the Flamberger's Sphere
- 04.00 - More Random Section Titles Here
---
# Key Points/Concepts


# Lecture
```

### Directory Structure

My system has this general format:

- a parent folder for a specialization/related topics (e.g. a program consisting of 3 distinct parts/courses) - this is NOT generated;
  - a folder for a course, with an optional number preceding the course title for cases in which it is part of a larger specialization/program, as well as a markdown file, `00-course_name_here.md` which includes an automatically generated and filled out markdown file;
  - a folder for each defined section of the course (think chapters of a book, weeks, etc.);
    - these _section_ folders contain a `00-` _section index file_, `99-` _section flashcards file_, as well as a file for each _subsection_.

For example:

```
Parent_Specialization_Folder/
  01-course_one_folder/
    00-course_one_index_file.md
    01-section_one_folder/
      00-section_one_index_file.md
      01-subsection_one_file.md
      02-subsection_two_file.md
      ...
      99-flashcards_subsection_one.md
    02-section_two_folder/
    ...
```

## Usage

- Run `python course_setup_md.py`, or use one of the [optional arguments](#optional-arguments),
- User is prompted with a `course number` - can be left blank, otherwise will precede the _course_ directory name with the number, in 2-digit format (e.g. `1` will become `01`),
- User is prompted with `course title` - can be entered lower-case, and it will generate using _title case_ throughout the markdown files,
- User is prompted with `short-form title` - this might be a short-hand for the course, or perhaps the program code (e.g. a university might have `BTSA 5510` for the course),
  - This is _case-sensitive_ - so enter as you'd like it to appear!
  - This will be rendered in the YAML `properties` to differentiate _sections_/_subsections_,
  - For example, rather than the YAML `title` being `01.04 - Review`, it will render `BTSA 5510 - 01.04 - Review`,
    - Else there might be confusion if this is ommitted, as it isn't clear to which course `01.04 - Review` belongs,
- User is prompted for the title of the first _section_ - case insensitive and generated using _title case_,
- User is then prompted for the first _subsection_ - case insensitive and generated using _title case_,
- Subsequent _subsections_ are prompted, but `CTRL-D` will exit that _section_ and prompt the user for a new _section_ and subsequent _subsections_,
- Upon keying `CTRL-D` on a _section_ prompt, the program will then generate all directories and files.

### Optional Arguments

```
-n, --no-dirs         To create section markdown files rather than section
                      folders, indices, flashcards, and subsection files.
-t, --no-toc          To not generate a table of contents in the section files.
                      This will only work if --no-dirs is also flagged. Useful
                      to prevent large tables of contents in the section files
                      when many sections are present.
-e EXTRA, --extra EXTRA
                      Pass in a string in markdown format to over-ride the
                      additional formatting of the subsection files. When `--no-
                      dirs` also flagged, this will over-ride the additional
                      formatting of the section files. Note: best used with
                      single quotes rather than double quotes to avoid any
                      escaping issues present in the terminal.
```

- `-n`/`--no-dirs` is useful to create markdown files for a book, episodic material, etc. This generates only the main _course_ directory, _course index file_, and a formatted _section_ file for each supplied section - no _subsections_.
- `t`/`--no-toc` will only generate the _table of contents_ in the _course index file_ and **not** an expanded _TOC_ in any _section_ files - but will still create a _TOC_ with a link to the _course index file_. This is useful when the book, episodic material, etc. has many sections which would create a long _TOC_.
  - **Note:** This flag will only work when `-n`/`--no-dirs` is also flagged.
- `-e <string>`/`--extra <string>` will over-ride the markdown headers below the _table of contents_ to the supplied markdown-formatted string.
  - **Note:** Recommended to use _single quotes_ to handle terminal-related string escape issues.
  - Example: `py course_setup_md.py -nte '## Transcript\n\n## Vocabulary\n\n## Footnotes'`

```
---
title: Example 1 - Example Flag Usage
tags: []
dates: []
---
# 01 - Example Flag Usage
## TOC
- [[00-example_course|Example Course]]

---
## Transcript

## Vocabulary

## Footnotes
```
