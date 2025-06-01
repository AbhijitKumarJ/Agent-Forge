# AgentWorkbench: Testing Enhancement Plan

## 1. Rationale and Goals
Thorough testing is crucial for ensuring the reliability, maintainability, and robustness of the AgentWorkbench platform. As the project grows in complexity and features, a comprehensive test suite will:
- Prevent regressions when new features are added or existing code is refactored.
- Provide clear documentation for how individual components (skills, tools, agents) are expected to behave.
- Facilitate easier onboarding for new developers.
- Increase overall confidence in the platform's stability.

The primary goal of this testing enhancement initiative is to systematically increase unit test coverage for all core components, starting with Skills.

## 2. Current Status (as of this plan's creation)
- **Skills with dedicated tests:** `MathSkill` (basic coverage initially, now expanded). `EchoSkill` (newly added tests).
- **Skills without dedicated tests:** `FinanceSkill`, `LLMSkill`, `NewsSkill`, `TranslationSkill`, `WeatherSkill`, `WebScrapeSkill`, `WebSearchSkill`, `WikipediaSkill`.
- **Tools:** While not the primary focus of *this initial phase*, tools like `FileTool`, `DBTool`, etc., also require testing.
- **Agents:** Basic tests exist for `SimpleAgent` and `CollaborativeAgent`.

## 3. Phase 1: Initial Skill Test Development (Completed)
This initial phase focused on establishing a testing pattern and adding tests for simple, deterministic skills:

- **`EchoSkill`**:
    - **Reasoning:** Chosen for its simplicity and lack of external dependencies. Ideal for establishing a baseline testing setup.
    - **Modifications Made:** The `execute` method was modified to return the echoed string, making it more testable (previously, it only printed the output).
    - **Tests Added:** Covered echoing various string inputs, empty strings, and no-argument calls.
- **`MathSkill`**:
    - **Reasoning:** Chosen as it had existing basic tests, providing an opportunity to demonstrate test expansion. Its `eval()` based core logic, while powerful, needs careful boundary testing.
    - **Tests Added:** Expanded to cover subtraction, multiplication, division (including division by zero), order of operations, negative numbers, and floating-point numbers.

An import issue within `AgentWorkbench/skills/__init__.py` was also identified and resolved during this phase, highlighting the immediate benefits of testing.

## 4. General Approach for Writing Unit Tests for Skills
When adding new unit tests for skills, the following general approach should be adopted:

- **Test File Location:** Tests for a skill `some_skill.py` should be placed in `AgentWorkbench/tests/test_some_skill.py`.
- **Test Class Naming:** Use `TestSomeSkillName` (e.g., `TestEchoSkill`).
- **Setup Method:** Use the `setUp` method from `unittest.TestCase` to initialize an instance of the skill.
- **Test Method Naming:** Test methods should be descriptive, e.g., `test_action_with_specific_input()` or `test_scenario_being_verified()`.
- **Assertions:** Use appropriate assertion methods from `unittest.TestCase` (e.g., `assertEqual`, `assertTrue`, `assertIsNone`, `assertRaises`).
- **Coverage:** Aim to cover:
    - **Normal operation:** Expected inputs leading to expected outputs.
    - **Edge cases:** Empty inputs, null inputs (if applicable), boundary values.
    - **Invalid inputs/Error handling:** How the skill behaves with unexpected or malformed input. If the skill is expected to handle errors gracefully (e.g., return `None`, log an error), test this behavior. If it's expected to raise an exception, use `assertRaises`.
- **Mocks for External Dependencies:** For skills that interact with external APIs (e.g., `NewsSkill`, `WeatherSkill`, `LLMSkill`) or have other external dependencies (like file system, databases if not using in-memory versions for tests):
    - Use Python's `unittest.mock` module (or a similar library) to patch out these external calls.
    - This ensures tests are deterministic, fast, and don't rely on external services being available or having specific states.
    - Test that the skill *attempts* to call the external service correctly (e.g., with the right URL or parameters) and that it handles various mocked responses (success, error) from the service appropriately.

## 5. Phase 2: Future Work - Expanding Test Coverage

The following skills (and tools/agents) are priorities for future testing efforts:

### Skills:
- **`WebScrapeSkill`**:
    - Mock HTTP requests (`requests.get`).
    - Test successful content scraping from mocked HTML.
    - Test handling of network errors or non-existent pages.
    - Test parsing of different HTML structures (if applicable).
- **`WikipediaSkill`**:
    - Mock the Wikipedia API library calls.
    - Test successful data retrieval.
    - Test handling of disambiguation pages or pages not found.
- **`WebSearchSkill`**:
    - Mock the search API calls (e.g., Google Search API via a library).
    - Test query formation and response parsing.
- **`NewsSkill`**, **`FinanceSkill`**, **`LLMSkill`**, **`TranslationSkill`**, **`WeatherSkill`**:
    - These often rely on external APIs and will require API key management for live testing (which should be separate from unit tests).
    - Unit tests should heavily mock the API interaction layer.
    - Test parameter passing to the API and parsing of expected responses (success/error).
- **Consider parameterization for skills like `MathSkill`** to easily test many input-output pairs without writing a new method for each.

### Tools:
- **`FileTool` (Completed):**
    - **Location:** `AgentWorkbench/tools/file_tool.py`
    - **Tests Added:** `AgentWorkbench/tests/test_file_tool.py`
    - **Coverage:**
        - Successful file reading (`mode='r'`).
        - Successful file writing (`mode='w'`).
        - Handling of missing content when `mode='w'`.
        - Handling of invalid mode argument.
        - Error handling for `FileNotFoundError` on read.
        - Error handling for `IOError` (e.g., permission issues) on write.
        - Reading from an empty file.
    - **Mocking:** Utilized `unittest.mock` to simulate `builtins.open` and `builtins.print` for isolated and deterministic tests.
- **`PrintTool` (Completed):**
    - **Location:** `AgentWorkbench/tools/print_tool.py`
    - **Tests Added:** `AgentWorkbench/tests/test_print_tool.py`
    - **Coverage:**
        - Printing single string arguments.
        - Behavior with multiple arguments (only the first is printed).
        - Behavior with no arguments.
        - Printing empty strings and strings with special characters.
    - **Mocking/Capture:** Utilized `unittest.mock.patch` with `io.StringIO` to capture and verify output sent to `sys.stdout`.
- **`ReverseTool` (Completed):**
    - **Location:** `AgentWorkbench/tools/reverse_tool.py`
    - **Tests Added:** `AgentWorkbench/tests/test_reverse_tool.py`
    - **Coverage:**
        - Reversing various string types (simple, spaces, numbers/specials, empty, palindrome).
        - Handling of no arguments (defaults to empty string).
        - Behavior with multiple arguments (only first is used).
        - Behavior with non-string inputs (e.g., integers causing `TypeError`, lists being reversed).
    - **Mocking/Capture:** Utilized `unittest.mock.patch` with `io.StringIO` to capture and verify output sent to `sys.stdout`.
- **`SQLiteTool` (Completed):**
    - **Location:** `AgentWorkbench/tools/db_tool.py` (defines `SQLiteTool`)
    - **Tests Added:** `AgentWorkbench/tests/test_sqlite_tool.py`
    - **Coverage:**
        - Database initialization (`_ensure_db`): table creation if DB file doesn't exist, no action if DB file exists.
        - Storing key-value pairs using `REPLACE INTO`.
        - Retrieving existing values.
        - Attempting to retrieve non-existent keys (returns `None`).
        - Error handling for `sqlite3.connect` failures.
        - Error handling for `conn.execute` failures.
    - **Mocking:** Utilized `unittest.mock.patch` to simulate `sqlite3.connect` (and its context manager behavior), `sqlite3.Connection`, `sqlite3.Cursor` objects, and `os.path.exists`. Also captured `builtins.print`.
- **`KnowledgeBaseTool`**: Similar to `SQLiteTool` (previously `DBTool`), depends on its underlying storage. (Further testing needed for `KnowledgeBaseTool` itself)

### Agents:
- Expand tests for `SimpleAgent` and `CollaborativeAgent` to cover more complex interactions, different skill combinations, and error states.

## 6. Running Tests
Tests should be runnable individually and as a suite. Standard Python `unittest` discovery can be used:
```bash
# From the repository root or AgentWorkbench directory
python -m unittest discover tests
# or for individual files
python -m unittest tests.test_some_skill
```
Integration with CI/CD pipelines should be set up to run tests automatically on each commit/PR.

This plan provides a roadmap for systematically improving the test coverage of the AgentWorkbench project, leading to a more stable and reliable platform.
