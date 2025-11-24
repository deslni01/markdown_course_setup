Todo:

- [x] Minor bugs/odd naming issues:

  - Roman numerals in title case (e.g. "II" becomes "Ii")
  - Conjunctions - "Children's" when entered becomes "Children'S", "Don't" becomes "Don'T", etc.
  - ALL words are currently capitalized, e.g. "The", "Of", etc.

- [ ] So... just came across an issue that could be a pain in the arse. While putting in episodes of the Norwegian for Beginners podcast, I realize I had a few typos - but I entered 56 titles, and since each file has a TOC linking to each file, that means _every file_ has typos in it - it isn't as simple as changing the singular file with the typo!

  - So.. how about a secondary script to open a dir, loop through the contents, find the supplied string to search for, and replace with the supplied swap string? Would want to maybe pass in bulk options, because there will likely be more than one typo, and I'd hate to have to run it multiple times, right?
  - And how to handle case issues? e.g. say I have "Cujisine", but obviously want it to be "Cuisine" - I'd either have to earch for "ujisine" and swap with "uisine", or figure out how to implement a way to do an insensitive "cuisine", but keep the existing capitalization...
  - Hmm.

- [ ] Similar to the one below, I suppose - what if we want to add to an existing course? Need to be able to do the following:

  - Mark if entries to an existing course,
  - Select what number to 'start' at,
  - Append new entries to existing TOCs
    - Would need to do the `00-index-file` for the course, then loop through each folder to get section `00-index-files`, `99-flashcard-files`, and all other files in the section... oofda

- [x] And in a similar fashion - what if we want to add to an existing setup? e.g. say we have 50 episodes, and tomorrow a 51st episode comes out - we'd have to manually add the new episode to all 50 existing files, plus the course index file! There has to be a better way - so we need a script to amend/edit existing TOCs...

  - Well, to that point, I'm looking at the current TOC of a 50-episode test I just did, and that's a long TOC in each file.. so maybe we completely change it to NOT add a TOC to each section file when doing `-nd` (add to the course index file, and each section would then have a singular link to that index file)? Or do we make this another optional flag to toggle this as an option?

- [ ] What about the ability to feed in a text file and process using those contents?

  - would need to figure out how to indicate section vs subsection, though...
  - indentation? if it's indented, it's subsection? then can parse the first few lines - first line if a number is the course number, then course name, then short name, then sections and indented sections?
  - I wonder about making that a 'module' and in `main` doing the arg where if it's present then it can do it? is it possible to load a module on the fly, as in make it optional? e.g. `from modulename import function if not None` or something?

- [x] Ah, what about making `extra` be an option in the `inputs` or via the command-line? e.g. I want to run this for Norsk for Beginners, but I want a specific format for this: `## Transcript\n\n## Vocabulary\n\n### Vocab Practice\n\n## Notes` - but right now there is no way to really do that unless I go into the code and swap it temporarily...
- [x] Similarly, what about a method to not make each `section` a new dir with subsections, index, and flashcards? Maybe just have each `section` just be a file? So think episodes for the podcast, right? Something small and contained, where I can put all the notes and vocab in the one doc?

- [ ] So I think we add a few optional flags using `argparse`!

  - [x]`--extra/-e <str>` to add in a string to replace the `extra` - or make this add an extra `input` rather than doing it in the command line?
  - [x]`--no-subs/-ns` to not include `subsections` or `dir` for each `section` - just have the `section` be a singular markdown file.
  - [ ] `--dry-run/-d` to not actually build the files, but output a list of formatted directories and files

- [ ] Hmmm, maybe make the TOC not include the short name?
  - e.g. instead of `CSCA 5214 - 01.03 - Ethical...`, maybe it is just
  - `01.03 - Ethical...`, but the `property title` still stays with that short name?
  - I don't quite know on this one. It looks fine in SOME instances, but in others looks weird. `NNN - 01.00` looks weird lol
  - But I suppose it'd be odd if it were just `01.01 - Introduction`, right? But that'd only be that way in the table of contents... the YAML title would have the short-key, so any external references to the file would include `NNN - 01.00` or whatever the short-form title is...
  - Well, let's just leave it for now, I guess.
- [x] Also, the subsections have the title, TOC, then `## Misc.` - need to change that to `## Lecture` or similar... also a `## Key Points/Concepts` at the top...

Chat GPT code suggestions:
X -> Pull all the `input()` calls into a single “driver” function (your `main` or a dedicated `from_user()` factory). Let your classes just accept data in their constructors or methods—no blocking `input()` in the middle. That way you can test `Course` and `Section` without mocking `input()`.

X -> YAML-header code is almost nearly identical in `Course.generate_course_template`, `Section.section_template`, `Section.flashcard_template` and an inline `sub_template` inside `generate_dir_and_markdown_files`.
-> Suggestion of course to factor out into a small helper, e.g. `_render_markdown(title, toc, extra)`, then each class just calls the helper with the right info, reducing copy-paste and making it obvious where to tweak formatting in one place.

    def _render_markdown(title: str, toc: str, extra: str = "") -> str:
        return (
            "---"
            f"title: {title}
            "tags: []"
            "dates: []"
            "---"
            f"{title}"
            "## TOC"
            "---"
            f"{extra}"
        )

X -> Centralize 'slugify' - the `generate_slug` logic is repeated `in Course and in inline loops` - if `course.generate_slug()` is being called everywhere, maybe make it a module-level function.

    def slugify(text: str) -> str:
        # all the replace() logic I have
        return cleaned.lower()

X -> Use data classes for simple containers - the `MarkdownPage` is a perfect candidate for a `@dataclass`, which auto-generates `__init__` and `__repr__` and makes it obvious it's just a bundle of data

    from dataclasses import dataclass

    @dataclass
    class MarkdownPage:
        title: str
        slug: str
        template: str
        filename: str
        index: int = 0

-> Naming and clarity - `generate_dir_and_markdown_files()` does a lot of work, should it maybe be split into `make_directory()` and `write_files()`?

- `course.generate_sections(self.sections)`
- passing `self.sections` to a method on the same object is redundant; you can refer to `self.sections` directly.
- Suggestions: Choose small, intention-revealing method names, and avoid passing around `self` attributes unnecessarily.

X -> Indexing and magic numbers - You hard-code "00" and "99" in lots of strings. If they're meaningful constants ("00 = index page, 99 = flashcards"), pull them out so readers immediately recognize them:
INDEX_PAGE = 0
FLASHCARDS_PAGE = 99

X -> Type annotations and docstrings - Adding signatures and return types everywhere will help readers (and tools like mypy) understand what each method does and returns.
def add_section(self, section_title: str) -> None:
""Prompt user for subsections and add a Section to self.sections""
(note: the above "" should be 3x", but that will break this whole quote block!)

-> Testability - Most logic is buried behind I/O and file writes. So for unit tests I'll want to:

- Refactor all `input()` into one place,
- Have `generate_course_template()` and `generate_section_toc()` methods return pure strings without touching the filesystem, - Test them by comparing their outputs to expected small fixtures.

-> NEXT STEPS:

- [x] Extract the shared YAML/header boilerplate
- [x] Move all console prompts into a top-level driver or `@classmethod from_user()` inside `Course`
- [x] Replace repeated `replace()` chains with one `slugify()` helper (at the top of the module or in a `utils.py` file and import it
- same with the `_render_markdown()` function)
- [x] Consider `@dataclass` for data holders (`MarkdownPage`, maybe even `Section`)
- [x] Name your constants (`00`, `99`) so their meaning is explicit
- [x] Add type hints and docstrings as you go
      -> Then it will be easier to read, test, and extend, without changing any core logic.
