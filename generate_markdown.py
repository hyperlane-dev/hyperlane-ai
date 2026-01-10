import os
import mimetypes
from datetime import datetime
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import re


class ThreadSafeFileProcessor:

    def __init__(self, source_dir="source", output_file="dataset.md", max_workers=None):
        self.source_dir = source_dir
        self.output_file = output_file
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.dataset = []
        self.dataset_lock = threading.Lock()
        self.progress_lock = threading.Lock()
        self.processed_count = 0
        self.total_files = 0
        self.start_time = None
        self.text_extensions = {
            ".txt",
            ".md",
            ".py",
            ".js",
            ".html",
            ".css",
            ".json",
            ".xml",
            ".csv",
            ".sql",
            ".yml",
            ".yaml",
            ".ini",
            ".cfg",
            ".conf",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".php",
            ".rb",
            ".go",
            ".rs",
            ".sh",
            ".bat",
            ".ps1",
            ".dockerfile",
            ".gitignore",
            ".env",
            ".log",
            ".readme",
            ".license",
            ".makefile",
            ".cmake",
        }
        self.extension_to_lang = {
            ".py": "python",
            ".js": "javascript",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".xml": "xml",
            ".csv": "csv",
            ".sql": "sql",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".ini": "ini",
            ".cfg": "cfg",
            ".conf": "bash",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".php": "php",
            ".rb": "ruby",
            ".go": "go",
            ".rs": "rust",
            ".sh": "bash",
            ".bat": "batch",
            ".ps1": "powershell",
            ".dockerfile": "dockerfile",
            ".gitignore": "gitignore",
            ".env": "env",
            ".log": "log",
            ".makefile": "makefile",
            ".cmake": "cmake",
            ".md": "markdown",
            ".txt": "text",
        }
        self.stats = {
            "files_per_second": 0,
            "total_processing_time": 0,
            "thread_stats": {},
        }
        # Language-specific comment patterns
        self.comment_patterns = {
            "python": [r"#.*$"],
            "javascript": [r"//.*$", r"/\*"],
            "typescript": [r"//.*$", r"/\*"],
            "java": [r"//.*$", r"/\*"],
            "cpp": [r"//.*$", r"/\*"],
            "c": [r"//.*$", r"/\*"],
            "rust": [r"//.*$"],
            "go": [r"//.*$", r"/\*"],
            "php": [r"//.*$", r"#.*$", r"/\*.*?\*/"],
            "ruby": [r"#.*$"],
            "bash": [r"#.*$"],
            "shell": [r"#.*$"],
            "sql": [r"--.*$", r"/\*.*?\*/"],
            "css": [r"/\*.*?\*/"],
            "scss": [r"/\*.*?\*/", r"//.*$"],
            "less": [r"/\*.*?\*/", r"//.*$"],
            "html": [r"<!--.*?-->"],
            "xml": [r"<!--.*?-->"],
            "yaml": [r"#.*$"],
            "yml": [r"#.*$"],
            "dockerfile": [r"#.*$"],
            "makefile": [r"#.*$"],
            "cmake": [r"#.*$"],
            "powershell": [r"#.*$"],
            "ps1": [r"#.*$"],
            "r": [r"#.*$"],
            "perl": [r"#.*$"],
            "lua": [r"--.*$", r"--\[\[.*?\]\]"],
            "haskell": [r"--.*$", r"\{.*?\}"],
            "erlang": [r"%.*$"],
            "elixir": [r"#.*$"],
            "swift": [r"//.*$", r"/\*.*?\*/"],
            "kotlin": [r"//.*$", r"/\*.*?\*/"],
            "scala": [r"//.*$", r"/\*.*?\*/"],
            "dart": [r"//.*$", r"/\*.*?\*/"],
            "objective-c": [r"//.*$", r"/\*.*?\*/"],
        }

    def filter_content(self, content):
        lines = content.split("\n")
        filtered_lines = []
        in_yaml_frontmatter = False
        in_license_section = False
        in_contributing_section = False
        in_contact_section = False
        for line in lines:
            if line.strip().startswith("<img") or line.strip().startswith("!["):
                continue

            # Remove specific HTML tags (self-closing and with attributes)
            tags_to_remove = [
                "Catalog",
                "Appreciate",
                "CratesDownloads",
                "GitHubMetrics",
                "Bottom",
                "Share",
            ]

            for tag in tags_to_remove:
                # Remove self-closing tags like <Catalog /> or <Catalog attribute="value" />
                line = re.sub(rf"<{tag}\s*[^>]*/>", "", line, flags=re.IGNORECASE)
                # Remove opening and closing tags like <Catalog>content</Catalog>
                line = re.sub(
                    rf"<{tag}\s*[^>]*>.*?</{tag}>",
                    "",
                    line,
                    flags=re.IGNORECASE | re.DOTALL,
                )
                # Remove opening tags like <Catalog attribute="value">
                line = re.sub(rf"<{tag}\s*[^>]*>", "", line, flags=re.IGNORECASE)
            if (
                "shields.io" in line
                or "img.shields.io" in line
                or ("docs.rs" in line and "badge.svg" in line)
            ):
                continue
            if "[!tip]" in line:
                continue
            if "github.com" in line and "badge.svg" in line:
                continue
            if line.strip() == "---":
                in_yaml_frontmatter = not in_yaml_frontmatter
                continue
            if in_yaml_frontmatter:
                continue
            line_lower = line.lower()
            if any(
                (
                    keyword in line_lower
                    for keyword in [
                        "# 许可证",
                        "## 许可证",
                        "本项",
                        "mit 许可证",
                        "## license",
                        "# license",
                    ]
                )
            ):
                in_license_section = True
                continue
            if any(
                (
                    keyword in line_lower
                    for keyword in [
                        "# 贡献指南",
                        "## 贡献指南",
                        "## 贡献",
                        "# 贡献",
                        "欢迎贡献",
                        "issue",
                        "pull request",
                        "## contributing",
                        "# contributing",
                    ]
                )
            ):
                in_contributing_section = True
                continue
            if any(
                (
                    keyword in line_lower
                    for keyword in [
                        "# 联系方式",
                        "## 联系方式",
                        "## 联系",
                        "# 联系",
                        "邮箱",
                        "@",
                        "mailto",
                    ]
                )
            ):
                in_contact_section = True
                continue
            if (
                in_license_section or in_contributing_section or in_contact_section
            ) and line.strip().startswith("#"):
                in_license_section = False
                in_contributing_section = False
                in_contact_section = False
            if in_license_section or in_contributing_section or in_contact_section:
                continue
            line = line.replace("<center>", "").replace("</center>", "")
            if "<Bottom" in line:
                continue
            if "<Share" in line:
                continue
            if line.strip() == ">":
                continue
            filtered_lines.append(line)
        result_lines = []
        prev_empty = False
        for line in filtered_lines:
            is_empty = not line.strip()
            if is_empty and prev_empty:
                continue
            result_lines.append(line)
            prev_empty = is_empty
        return "\n".join(result_lines)

    def remove_code_comments(self, content, language):
        """
        Remove comments from code content based on the specified language.
        This method is careful to preserve content inside string literals.

        Arguments:
        - `content`: The code content to process
        - `language`: The programming language of the content

        Returns:
        - Content with comments removed
        """
        if not content or not language:
            return content

        patterns = self.comment_patterns.get(language.lower(), [])
        if not patterns:
            return content

        # Process line by line to handle string literals properly
        lines = content.split("\n")
        result_lines = []

        in_multiline_comment = False
        in_multiline_string = False
        string_delimiter = None

        for line in lines:
            if not line.strip():
                result_lines.append(line)
                continue

            processed_line = line
            i = 0
            new_line = ""
            in_string = False
            string_char = None
            escaped = False

            # Process character by character to handle strings and comments properly
            while i < len(processed_line):
                char = processed_line[i]
                next_char = processed_line[i + 1] if i + 1 < len(processed_line) else ""

                # Handle escape sequences
                if escaped:
                    new_line += char
                    escaped = False
                    i += 1
                    continue

                if char == "\\":
                    escaped = True
                    new_line += char
                    i += 1
                    continue

                # Handle string literals
                if not in_string and char in ['"', "'"]:
                    in_string = True
                    string_char = char
                    new_line += char
                elif in_string and char == string_char:
                    in_string = False
                    string_char = None
                    new_line += char
                elif in_string:
                    new_line += char
                else:
                    # Check for comments only when not in string
                    comment_found = False

                    for pattern in patterns:
                        if (
                            pattern.startswith("//")
                            and char == "/"
                            and next_char == "/"
                        ):
                            # Single-line comment, skip rest of line
                            comment_found = True
                            break
                        elif pattern.startswith("#") and char == "#":
                            # Hash comment, skip rest of line
                            comment_found = True
                            break
                        elif (
                            pattern.startswith("--")
                            and char == "-"
                            and next_char == "-"
                        ):
                            # SQL-style comment, skip rest of line
                            comment_found = True
                            break

                    if comment_found:
                        break  # Skip the rest of the line
                    else:
                        new_line += char

                i += 1

            result_lines.append(new_line)

        # Handle multi-line comments (/* */ style)
        content_with_single_line_comments_removed = "\n".join(result_lines)
        result = content_with_single_line_comments_removed

        # Remove multi-line comments carefully
        for pattern in patterns:
            if pattern == r"/\*":
                try:
                    # Process multi-line comments line by line to handle strings properly
                    lines = result.split("\n")
                    result_lines = []
                    in_multiline_comment = False

                    for line in lines:
                        if not in_multiline_comment:
                            # Look for /* in this line
                            if "/*" in line:
                                # Check if /* is inside a string
                                in_string = False
                                string_char = None
                                i = 0
                                while i < len(line):
                                    char = line[i]
                                    if not in_string and char in ['"', "'"]:
                                        in_string = True
                                        string_char = char
                                    elif in_string and char == string_char:
                                        in_string = False
                                        string_char = None
                                    elif (
                                        not in_string
                                        and i < len(line) - 1
                                        and char == "/"
                                        and line[i + 1] == "*"
                                    ):
                                        # Found /* not in string, start of multi-line comment
                                        in_multiline_comment = True
                                        # Add content before /*
                                        line = line[:i]
                                        break
                                    i += 1

                        if in_multiline_comment:
                            # Look for */ in this line
                            if "*/" in line:
                                in_multiline_comment = False
                                # Remove content up to and including */
                                line = line.split("*/", 1)[1]
                            else:
                                # Skip this entire line as it's inside a multi-line comment
                                line = ""

                        if line.strip() or not in_multiline_comment:
                            result_lines.append(line)

                    result = "\n".join(result_lines)
                except Exception:
                    # If anything goes wrong, skip this pattern
                    continue

        return result

    def read_text_file(self, file_path):
        encodings = ["utf-8", "gbk", "gb2312", "latin1"]
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding, buffering=8192) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                return f"Read error: {str(e)}"
        return "Unable to decode file content"

    def get_file_info(self, file_path):
        try:
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "mime_type": mimetypes.guess_type(file_path)[0] or "unknown",
            }
        except Exception as e:
            return {"size": 0, "error": str(e)}

    def process_single_file(self, file_path, file_id):
        thread_id = threading.current_thread().ident
        if thread_id not in self.stats["thread_stats"]:
            self.stats["thread_stats"][thread_id] = {"processed": 0, "errors": 0}
        try:
            file_path = Path(file_path)
            relative_path = file_path.relative_to(self.source_dir)
            extension = file_path.suffix.lower()
            file_info = self.get_file_info(file_path)
            file_data = {
                "id": file_id,
                "filename": file_path.name,
                "path": str(relative_path),
                "full_path": str(file_path),
                "extension": extension,
                "file_info": file_info,
                "processed_time": datetime.now().isoformat(),
                "thread_id": thread_id,
            }
            if extension in self.text_extensions:
                file_data["type"] = "text"
                content = self.read_text_file(file_path)
                file_data["content"] = content
                file_data["encoding"] = "utf-8"
            self.stats["thread_stats"][thread_id]["processed"] += 1
            return file_data
        except Exception as e:
            self.stats["thread_stats"][thread_id]["errors"] += 1
            return {
                "id": file_id,
                "filename": (
                    file_path.name if hasattr(file_path, "name") else str(file_path)
                ),
                "path": str(file_path),
                "error": str(e),
                "processed_time": datetime.now().isoformat(),
                "thread_id": thread_id,
            }

    def update_progress(self):
        with self.progress_lock:
            self.processed_count += 1
            if (
                self.processed_count % 10 == 0
                or self.processed_count == self.total_files
            ):
                elapsed = time.time() - self.start_time
                fps = self.processed_count / elapsed if elapsed > 0 else 0
                progress = self.processed_count / self.total_files * 100
                print(
                    f"\rProgress: {self.processed_count}/{self.total_files} ({progress:.1f}%) - {fps:.1f} files/s - Time elapsed: {elapsed:.1f}s",
                    end="",
                    flush=True,
                )

    def collect_all_files(self):
        all_files = []
        if not os.path.exists(self.source_dir):
            print(f"Error: Source directory '{self.source_dir}' does not exist")
            return all_files
        print(f"Scanning directory: {self.source_dir}")
        for root, dirs, files in os.walk(self.source_dir):
            if ".git" in dirs:
                dirs.remove(".git")
            for file in files:
                file_path = os.path.join(root, file)
                if (
                    file.upper() == "LICENSE"
                    or file == "Cargo.toml"
                    or file == ".gitignore"
                    or (file.lower() == "license.md")
                    or file.endswith(".yml")
                    or file.endswith(".yaml")
                ):
                    continue
                all_files.append(file_path)
        self.total_files = len(all_files)
        print(f"Found {self.total_files} files")
        return all_files

    def process_directory_multithread(self):
        all_files = self.collect_all_files()
        if not all_files:
            return False
        print(f"Starting multithreaded processing (worker threads: {self.max_workers})")
        print("-" * 60)
        self.start_time = time.time()
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.process_single_file, file_path, idx + 1): file_path
                for idx, file_path in enumerate(all_files)
            }
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    with self.dataset_lock:
                        self.dataset.append(result)
                    self.update_progress()
                except Exception as e:
                    print(f"\nFailed to process file {file_path}: {e}")
        print("\n" + "=" * 60)
        total_time = time.time() - self.start_time
        self.stats["total_processing_time"] = total_time
        self.stats["files_per_second"] = (
            self.total_files / total_time if total_time > 0 else 0
        )
        print(f"Processing completed!")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Processing speed: {self.stats['files_per_second']:.2f} files/second")
        print(f"Active threads: {len(self.stats['thread_stats'])}")
        return True

    def generate_markdown_report(self):
        output_path = Path(self.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        current_file_handle = open(self.output_file, "w", encoding="utf-8")
        current_file_size = 0
        print(f"Creating output file: {self.output_file}")
        current_time = datetime.now()
        time_header = f"<!--{current_time.strftime('%Y-%m-%d %H:%M:%S')}-->\n"
        current_file_handle.write(time_header)
        try:
            for item in sorted(self.dataset, key=lambda x: x.get("id", 0)):
                if "error" in item:
                    continue
                extension = item["extension"]
                lang = self.extension_to_lang.get(extension, "")
                content_lines = []
                content_lines.append(f"# Path: {item['path']}\n\n")
                file_content = item.get("content", "")
                filtered_content = self.filter_content(file_content)
                if not filtered_content.strip():
                    continue
                if lang and filtered_content:
                    if lang == "markdown":
                        content_lines.append(filtered_content)
                        content_lines.append("\n\n")
                    else:
                        # Remove comments from code content before adding to markdown
                        code_without_comments = self.remove_code_comments(
                            filtered_content, lang
                        )
                        content_lines.append(f"```{lang}\n")
                        content_lines.append(code_without_comments)
                        content_lines.append("\n```\n\n")
                else:
                    content_lines.append(filtered_content)
                    content_lines.append("\n\n")
                entry_content = "".join(content_lines)
                entry_content = re.sub(r"\n\s*\n", "\n", entry_content)
                current_file_handle.write(entry_content)
                current_file_size += len(entry_content.encode("utf-8"))
            print(f"\n✅ Markdown report generated: {self.output_file}")
        finally:
            if current_file_handle:
                current_file_handle.close()

    def run(self):
        if self.process_directory_multithread():
            self.generate_markdown_report()
            return True
        return False


def main():
    source_directory = "./source"
    output_md = "./dataset/dataset.md"
    max_workers = None
    processor = ThreadSafeFileProcessor(
        source_dir=source_directory, output_file=output_md, max_workers=max_workers
    )
    print("=== 📝 Multithreaded AIMarkdown Generator (Markdown Output Version) ===")
    print(f"Source directory: {source_directory}")
    print(f"Output file: {output_md}")
    print(f"Max worker threads: {processor.max_workers}")
    print(f"CPU cores: {os.cpu_count()}")
    print("=" * 60)
    success = processor.run()
    if success:
        print("\n🎉 Markdown report successfully generated as Markdown file!")
    else:
        print("\n❌ Processing failed, please check if source directory exists.")


if __name__ == "__main__":
    main()
