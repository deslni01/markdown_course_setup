from __future__ import annotations  # for forward references
from dataclasses import dataclass
from pathlib import Path
import os

INDEX_PAGE = 0  # for `00-` index pages
FLASHCARDS_PAGE = 99  # for `99-` flashcard pages`

def generate_slug(title: str) -> str:
    """
    Args:
      title (str): The input string to be converted into a slug.

    Returns:
      str: The slugified version of the input string.
    """
    return (
        title.replace("(", "")
        .replace(")", "")
        .replace(" ", "_")
        .replace(":", "_-")
        .replace("/", "-")
        .replace("?", "")
        .replace("!", "")
        .replace(",", "")
        .replace("'", "")
        .lower()
    )


def _render_markdown(
    title: str, table_of_contents: str, dates: bool = True, extra: str = "## Misc."
) -> str:
    """
    Generate a markdown-file template, including YAML properties, and a table of contents.

    Args:
      title (str): The title to be used in the YAML properties and the H1 header.

      dates (bool): If the YAML properties should have a dates, adds a `dates` list to the YAML properties.

      table_of_contents (str): The supplied table of contents to render.

      extra (str): Additional markdown to add, defaults to `## Misc.`.

    Returns:
      str: A markdown template.
    """
    return (
        "---\n"
        f"title: '{title}'\n"
        "tags: []\n"
        f"{'dates: []' if dates else ''}\n"  # will this work?
        "---\n"
        f"# {title}\n"
        "## TOC\n"
        f"{table_of_contents}\n"
        "---\n"
        f"{extra}"
    )


class FileGenerator:
    @classmethod
    def create_markdown_file(cls, markdown_page, out_dir):
        file_path = out_dir + "/" + markdown_page.filename
        output_file = Path(file_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as file:
            file.write(markdown_page.template)


@dataclass
class MarkdownPage:
    title: str
    slug: str
    template: str
    filename: str
    index: int = 0


class Section:
    def __init__(self, section_title, course):
        self.slug = generate_slug(section_title)
        self.section_title = section_title
        self.subsections = []
        self.course = course
        self.index = 0
        self.section_toc = ""

    @property
    def section_template(self):
        sec_num = f"{self.index:02d}"

        sec_title = f"{self.course.short_title} - {sec_num}.{INDEX_PAGE:02d} - {self.section_title.title()}"
        return _render_markdown(sec_title, self.section_toc)

    @property
    def flashcard_template(self):
        sec_num = f"{self.index:02d}"

        flashcards_title = f"{self.course.short_title} - {sec_num}.{FLASHCARDS_PAGE} - {self.section_title.title()} Flashcards"

        sub_sections = []

        # Adds each subsection as a header in the flashcard file
        for sub_section in self.subsections:
            sub_sections.append(f"## {sub_section.title()}\n" "\n" "\n")

        sub_section_lines = "".join(sub_sections)

        return _render_markdown(
            flashcards_title, self.section_toc, extra=sub_section_lines, dates=False
        )

    def add_subsections(self, subsection_title):
        self.subsections.append(subsection_title)

    def generate_section_toc(self, all_sections, course):
        lines = [
            f"- [[{INDEX_PAGE:02d}-{course.slug}|{course.short_title} - {course.course_title.title()}]]\n"
        ]
        for sec_idx, section in enumerate(all_sections, start=1):
            slug = generate_slug(section.section_title)
            num = f"{sec_idx:02d}"

            # Adds a link for each section
            lines.append(
                f"- [[{INDEX_PAGE:02d}-{slug}|"
                f"{course.short_title} - {num}.{INDEX_PAGE:02d} "
                f"- {section.section_title.title()}]]\n"
            )

            # Adds and indents all subsections of current section
            if section is self:
                for sub_idx, subsection in enumerate(self.subsections, start=1):
                    sub_slug = generate_slug(subsection)
                    sec_num = f"{sec_idx:02d}"
                    sub_num = f"{sub_idx:02d}"
                    lines.append(
                        f"\t- [[{sub_num}-{sub_slug}|"
                        f"{course.short_title} - {sec_num}.{sub_num} - {subsection.title()}]]\n"
                    )

                section_flashcard_file = (
                    f"\t- [[{FLASHCARDS_PAGE}-flashcards_{slug}|"
                    f"{course.short_title} - {num}.{FLASHCARDS_PAGE} "
                    f"- {self.section_title.title()} Flashcards]]\n"
                )
                lines.append(section_flashcard_file)

        return "".join(lines)

    def generate_dir_and_markdown_files(self, index, course):
        self.index = index  # store section index on the fly

        self.section_toc = self.generate_section_toc(course.sections, course)
        outdir = f"{course.output_dir}/{index:02d}-{self.slug}"

        section_index_file = MarkdownPage(
            self.section_title,
            self.slug,
            self.section_template,
            f"{INDEX_PAGE:02d}-" + self.slug + ".md",
        )

        section_flashcard_file = MarkdownPage(
            f"{self.section_title} Flashcards",
            self.slug,
            self.flashcard_template,
            f"{FLASHCARDS_PAGE}-flashcards_{self.slug}.md",
            index=FLASHCARDS_PAGE,
        )

        course_index_file = MarkdownPage(
            course.course_title,
            course.slug,
            course.course_template,
            f"{INDEX_PAGE:02d}-" + course.slug + ".md",
        )

        FileGenerator.create_markdown_file(section_index_file, outdir)
        FileGenerator.create_markdown_file(section_flashcard_file, outdir)
        FileGenerator.create_markdown_file(course_index_file, course.output_dir)

        for index, sub_section in enumerate(self.subsections, start=1):
            sub_num = f"{self.index:02d}.{index:02d}"

            sub_title = f"{self.course.short_title} - {sub_num} - {sub_section.title()}"

            sub_template = _render_markdown(sub_title, self.section_toc)

            slug = generate_slug(sub_section)
            filename = f"{index:02d}-{slug}.md"
            sub_section = MarkdownPage(sub_section, slug, sub_template, filename, index)
            FileGenerator.create_markdown_file(sub_section, outdir)


class Course:
    def __init__(self, course_title, short_title, course_number=None):
        self.course_title = course_title
        self.short_title = short_title
        self.course_number = course_number

        self.sections = []
        self.course_template = ''
        self.slug = ""

    def __str__(self):
        return (
            f"***Course Title:\n{self.course_title}\n"
            f"***Short Title:\n{self.short_title}\n"
            f"***Template:\n{self.course_template}\n"
            f"***Folder Name:{self.slug}"
        )

    def generate_course_template(self):
        title = f"{self.short_title} - {self.course_title.title()}"

        lines = [
            f"- [[{INDEX_PAGE:02d}-{self.slug}|{self.short_title} - {self.course_title.title()}]]\n"
        ]
        for sec_idx, section in enumerate(self.sections, start=1):
            sec_slug = generate_slug(section.section_title)
            sec_num = f"{sec_idx:02d}"
            lines.append(
                f"- [[{INDEX_PAGE:02d}-{sec_slug}|"
                f"{self.short_title} - {sec_num}.{INDEX_PAGE:02d} "
                f"- {section.section_title.title()}]]\n"
            )
            # indent all subsections
            for sub_idx, subsection in enumerate(section.subsections, start=1):
                sub_slug = generate_slug(subsection)
                sec_num = f"{sec_idx:02d}"
                sub_num = f"{sub_idx:02d}"
                lines.append(
                    f"\t- [[{sub_num}-{sub_slug}|"
                    f"{self.short_title} - {sec_num}.{sub_num} - {subsection.title()}]]\n"
                )

            section_flashcard_file = (
                f"\t- [[{FLASHCARDS_PAGE}-flashcards_{sec_slug}|"
                f"{self.short_title} - {sec_num}.{FLASHCARDS_PAGE} "
                f"- {section.section_title.title()} Flashcards]]\n"
            )
            lines.append(section_flashcard_file)

        table_of_contents = "".join(lines)

        return _render_markdown(title, table_of_contents, dates=False)

    @property
    def output_dir(self):
        if self.course_number:
            return os.path.join(
                os.getcwd(), f"{int(self.course_number):02d}-{self.slug}"
            )
        return os.path.join(os.getcwd(), self.slug)

    def generate_sections(self, sections) -> None:
        """
        Iterates of the course `sections`, calling `generate_dir_and_markdown_files` for each `section`.
        """
        for index, section in enumerate(self.sections, start=1):
            section.generate_dir_and_markdown_files(index, self)

    def generate_course(self) -> None:
        """
        Sets up course fields for `slug` and `course_template`, then calls `generate_sections()` to create the files.
        """
        self.slug = generate_slug(self.course_title)
        self.course_template = self.generate_course_template()
        self.generate_sections(self.sections)

def get_user_input() -> Course:
    """
    Queries the user via the command-line for the `course_number`, `course_title`, and `short_title`.
    Then for each `section`, queries the user for the `section_title` and loops over for `subsection_title` until `CTRL-D`.
    """
    course_number = input(
            "Enter the course number (leave blank if no course number): "
        )
    course_title = input("Enter the course title: ")
    short_title = input("Enter the short-form title (case-sensitive): ")
    course = Course(course_title, short_title, course_number)

    print("\nEnter the section title (or CTRL-D to finish):\n")
    try:
        while True:
            section_title = input("Section title: ")
            section = Section(section_title, course)
            try:
                while True:
                    subsection_title = input("Subsection title: ")
                    section.add_subsections(subsection_title)
            except EOFError:
                print()

            course.sections.append(section)
    except EOFError:
        print()

    return course


def main():
    course = get_user_input()
    course.generate_course()


if __name__ == "__main__":
    main()
