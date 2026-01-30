from course_setup_md import handle_title, get_user_input, parse_args, parse_terminal_text, generate_slug, render_markdown, Course, Section


# Test cases for handle_title function
def test_handle_title_valid():
  assert handle_title("course title") == "Course Title"

def test_handle_title_roman_numerals():
  assert handle_title("course title ii") == "Course Title II"
  assert handle_title("course title ix") == "Course Title IX"

def test_handle_title_lower_case_words():
  assert handle_title("title of the course") == "Title of the Course"
  assert handle_title("the course is important") == "The Course Is Important"

# Test cases for get_user_input function
# function to mock inputs
def mock_inputs(course_seq):
  course_sequence = course_seq.copy()

  def _mock(_prompt=""):
    if not course_sequence:
      raise EOFError
    next_input = course_sequence.pop(0)
    if next_input is None:
      raise EOFError
    return next_input
  return _mock

def test_get_user_input_with_dirs(monkeypatch):
  # `write_dirs=True` contains subsections
  monkeypatch.setattr('builtins.input', mock_inputs(["1", "example course", "EC 1", "Section 1", "Subsection 1-1", "Subsection 1-2", None, "Section 2", "Subsection 2-1", "Subsection 2-2", None]))
  course = get_user_input(write_dirs=True)
  assert isinstance(course, Course)
  assert course.course_title == "example course"
  assert isinstance(course.sections[0], Section)
  assert course.sections[1].section_title == "Section 2"
  assert course.sections[1].subsections[0] == "Subsection 2-1"

def test_get_user_input_without_dirs(monkeypatch):
  # `write_dirs=False` does not contain subsections
  monkeypatch.setattr('builtins.input', mock_inputs(["", "example course", "EC 1", "Section 1", "Section 2", "Section 3", None]))
  course = get_user_input(write_dirs=False)
  assert isinstance(course, Course)
  assert isinstance(course.sections[0], Section)
  assert course.sections[1].section_title == "Section 2"
  assert course.sections[2].section_title == "Section 3"
  assert course.sections[0].subsections == []

def test_get_user_input_formatting(monkeypatch):
  # test empty string for course title
  monkeypatch.setattr('builtins.input', mock_inputs(["", "", "", "example course", "EC 1", "Section 1", None]))
  course = get_user_input(write_dirs=True)
  assert isinstance(course, Course)
  assert course.course_title == "example course"

  # empty string with whitespace "    "
  monkeypatch.setattr('builtins.input', mock_inputs(["", "   ", "   ", "  example course  ", "EC 1", "Section 1", None]))
  course = get_user_input(write_dirs=True)
  assert isinstance(course, Course)
  assert course.course_title == "example course"

def test_get_user_input_course_number(monkeypatch):
  monkeypatch.setattr('builtins.input', mock_inputs(["", "example course", "EC 1", "Section 1", None, None]))
  course = get_user_input(write_dirs=True)
  assert isinstance(course, Course)
  assert course.course_number is None

  monkeypatch.setattr('builtins.input', mock_inputs(["1", "example course", "EC 1", "Section 1", None, None]))
  course = get_user_input(write_dirs=True)
  assert isinstance(course, Course)
  assert course.course_number == 1

def test_get_user_input_course_number_invalid(monkeypatch):
  monkeypatch.setattr('builtins.input', mock_inputs(["a", "1", "example course", "ec 1", None]))
  course = get_user_input(write_dirs=True)
  assert isinstance(course, Course)
  assert course.course_number == 1



# parse args function test cases
# parse_terminal_text function test cases
# generate_slug function test cases
# render_markdown function test cases