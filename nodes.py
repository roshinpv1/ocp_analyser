import os
import re
import yaml
import json
import openpyxl
from openpyxl import load_workbook
from urllib.parse import urlparse
from typing import Dict, List, Optional, Union
from core.genflow import Node, BatchNode
from utils.crawl_github_files import crawl_github_files
from utils.call_llm import call_llm
from utils.crawl_local_files import crawl_local_files
import time


# Helper to get content for specific file indices
def get_content_for_indices(files_data, indices):
    content_map = {}
    for i in indices:
        if 0 <= i < len(files_data):
            path, content = files_data[i]
            content_map[f"{i} # {path}"] = (
                content  # Use index + path as key for context
            )
    return content_map


class FetchRepo(Node):
    def prep(self, shared):
        repo_url = shared.get("repo_url")
        local_dir = shared.get("local_dir")
        project_name = shared.get("project_name")

        if not project_name:
            # Basic name derivation from URL or directory
            if repo_url:
                project_name = repo_url.split("/")[-1].replace(".git", "")
            else:
                project_name = os.path.basename(os.path.abspath(local_dir))
            shared["project_name"] = project_name

        # Get file patterns directly from shared
        include_patterns = shared["include_patterns"]
        exclude_patterns = shared["exclude_patterns"]
        max_file_size = shared["max_file_size"]

        return {
            "repo_url": repo_url,
            "local_dir": local_dir,
            "token": shared.get("github_token"),
            "include_patterns": include_patterns,
            "exclude_patterns": exclude_patterns,
            "max_file_size": max_file_size,
            "use_relative_paths": True,
            "shallow_clone": True,  # Enable shallow clone by default
            "clone_timeout": 300,   # 5 minutes timeout
            "max_depth": 1         # Only clone the latest commit
        }

    def exec(self, prep_res):
        if prep_res["repo_url"]:
            print(f"Crawling repository: {prep_res['repo_url']}...")
            max_retries = 3
            retry_delay = 5  # seconds
            
            for attempt in range(max_retries):
                try:
                    result = crawl_github_files(
                        repo_url=prep_res["repo_url"],
                        token=prep_res["token"],
                        include_patterns=prep_res["include_patterns"],
                        exclude_patterns=prep_res["exclude_patterns"],
                        max_file_size=prep_res["max_file_size"],
                        use_relative_paths=prep_res["use_relative_paths"],
                        shallow_clone=prep_res["shallow_clone"],
                        clone_timeout=prep_res["clone_timeout"],
                        max_depth=prep_res["max_depth"]
                    )
                    break  # If successful, break the retry loop
                except TimeoutError as e:
                    if attempt < max_retries - 1:
                        print(f"\nAttempt {attempt + 1} failed: {str(e)}")
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        print("\nAll retry attempts failed. Last error:")
                        raise ValueError(f"Failed to clone repository after {max_retries} attempts: {str(e)}")
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"\nAttempt {attempt + 1} failed: {str(e)}")
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        print("\nAll retry attempts failed. Last error:")
                        raise ValueError(f"Failed to clone repository after {max_retries} attempts: {str(e)}")
        else:
            print(f"Crawling directory: {prep_res['local_dir']}...")
            result = crawl_local_files(
                directory=prep_res["local_dir"],
                include_patterns=prep_res["include_patterns"],
                exclude_patterns=prep_res["exclude_patterns"],
                max_file_size=prep_res["max_file_size"],
                use_relative_paths=prep_res["use_relative_paths"]
            )

        # Convert dict to list of tuples: [(path, content), ...]
        files_list = list(result.get("files", {}).items())
        
        # Check if any files were found
        if len(files_list) == 0:
            # Get the source for better error message
            source = prep_res["repo_url"] or prep_res["local_dir"]
            include_patterns = prep_res["include_patterns"]
            exclude_patterns = prep_res["exclude_patterns"]
            
            error_msg = f"No files found in {source} matching the patterns:\n"
            error_msg += f"Include patterns: {include_patterns}\n"
            error_msg += f"Exclude patterns: {exclude_patterns}\n\n"
            error_msg += "Please check:\n"
            error_msg += "1. The repository/directory path is correct\n"
            error_msg += "2. The include/exclude patterns match your files\n"
            error_msg += "3. The repository is accessible (if using GitHub)\n"
            error_msg += "4. The file extensions in include patterns match your codebase"
            
            raise ValueError(error_msg)
            
        print(f"Fetched {len(files_list)} files.")
        return files_list

    def post(self, shared, prep_res, exec_res):
        shared["files"] = exec_res  # List of (path, content) tuples


class IdentifyAbstractions1(Node):
    def prep(self, shared):
        files_data = shared["files"]
        project_name = shared["project_name"]  # Get project name
        language = shared.get("language", "english")  # Get language
        use_cache = shared.get("use_cache", True)  # Get use_cache flag, default to True
        max_abstraction_num = shared.get("max_abstraction_num", 10)  # Get max_abstraction_num, default to 10

        # Helper to create context from files, respecting limits (basic example)
        def create_llm_context(files_data):
            context = ""
            file_info = []  # Store tuples of (index, path)
            for i, (path, content) in enumerate(files_data):
                entry = f"--- File Index {i}: {path} ---\n{content}\n\n"
                context += entry
                file_info.append((i, path))

            return context, file_info  # file_info is list of (index, path)

        context, file_info = create_llm_context(files_data)
        # Format file info for the prompt (comment is just a hint for LLM)
        file_listing_for_prompt = "\n".join(
            [f"- {idx} # {path}" for idx, path in file_info]
        )
        return (
            context,
            file_listing_for_prompt,
            len(files_data),
            project_name,
            language,
            use_cache,
            max_abstraction_num,
        )  # Return all parameters

    def exec(self, prep_res):
        (
            context,
            file_listing_for_prompt,
            file_count,
            project_name,
            language,
            use_cache,
            max_abstraction_num,
        ) = prep_res  # Unpack all parameters
        print(f"Identifying abstractions using LLM...")

        # Add language instruction and hints only if not English
        language_instruction = ""
        name_lang_hint = ""
        desc_lang_hint = ""
        if language.lower() != "english":
            language_instruction = f"IMPORTANT: Generate the `name` and `description` for each abstraction in **{language.capitalize()}** language. Do NOT use English for these fields.\n\n"
            # Keep specific hints here as name/description are primary targets
            name_lang_hint = f" (value in {language.capitalize()})"
            desc_lang_hint = f" (value in {language.capitalize()})"

        prompt = f"""
For the project `{project_name}`:

Codebase Context:
{context}

{language_instruction}Analyze the codebase context.
Identify the top 5-{max_abstraction_num} core most important abstractions to help those new to the codebase.

For each abstraction, provide:
1. A concise `name`{name_lang_hint}.
2. A beginner-friendly `description` explaining what it is with a simple analogy, in around 100 words{desc_lang_hint}.
3. A list of relevant `file_indices` (integers) using the format `idx # path/comment`.

List of file indices and paths present in the context:
{file_listing_for_prompt}

Format the output as a YAML list of dictionaries:

```yaml
- name: |
    Query Processing{name_lang_hint}
  description: |
    Explains what the abstraction does.
    It's like a central dispatcher routing requests.{desc_lang_hint}
  file_indices:
    - 0 # path/to/file1.py
    - 3 # path/to/related.py
- name: |
    Query Optimization{name_lang_hint}
  description: |
    Another core concept, similar to a blueprint for objects.{desc_lang_hint}
  file_indices:
    - 5 # path/to/another.js
# ... up to {max_abstraction_num} abstractions
```"""
        response = call_llm(prompt, use_cache=(use_cache and self.cur_retry == 0))  # Use cache only if enabled and not retrying

        # --- Validation ---
        yaml_str = response.strip().split("```yaml")[1].split("```")[0].strip()
        abstractions = yaml.safe_load(yaml_str)

        if not isinstance(abstractions, list):
            raise ValueError("LLM Output is not a list")

        validated_abstractions = []
        for item in abstractions:
            if not isinstance(item, dict) or not all(
                k in item for k in ["name", "description", "file_indices"]
            ):
                raise ValueError(f"Missing keys in abstraction item: {item}")
            if not isinstance(item["name"], str):
                raise ValueError(f"Name is not a string in item: {item}")
            if not isinstance(item["description"], str):
                raise ValueError(f"Description is not a string in item: {item}")
            if not isinstance(item["file_indices"], list):
                raise ValueError(f"file_indices is not a list in item: {item}")

            # Validate indices
            validated_indices = []
            for idx_entry in item["file_indices"]:
                try:
                    if isinstance(idx_entry, int):
                        idx = idx_entry
                    elif isinstance(idx_entry, str) and "#" in idx_entry:
                        idx = int(idx_entry.split("#")[0].strip())
                    else:
                        idx = int(str(idx_entry).strip())

                    if not (0 <= idx < file_count):
                        raise ValueError(
                            f"Invalid file index {idx} found in item {item['name']}. Max index is {file_count - 1}."
                        )
                    validated_indices.append(idx)
                except (ValueError, TypeError):
                    raise ValueError(
                        f"Could not parse index from entry: {idx_entry} in item {item['name']}"
                    )

            item["files"] = sorted(list(set(validated_indices)))
            # Store only the required fields
            validated_abstractions.append(
                {
                    "name": item["name"],  # Potentially translated name
                    "description": item[
                        "description"
                    ],  # Potentially translated description
                    "files": item["files"],
                }
            )

        print(f"Identified {len(validated_abstractions)} abstractions.")
        return validated_abstractions

    def post(self, shared, prep_res, exec_res):
        shared["abstractions"] = (
            exec_res  # List of {"name": str, "description": str, "files": [int]}
        )


class AnalyzeRelationships1(Node):
    def prep(self, shared):
        abstractions = shared[
            "abstractions"
        ]  # Now contains 'files' list of indices, name/description potentially translated
        files_data = shared["files"]
        project_name = shared["project_name"]  # Get project name
        language = shared.get("language", "english")  # Get language
        use_cache = shared.get("use_cache", True)  # Get use_cache flag, default to True

        # Get the actual number of abstractions directly
        num_abstractions = len(abstractions)

        # Create context with abstraction names, indices, descriptions, and relevant file snippets
        context = "Identified Abstractions:\\n"
        all_relevant_indices = set()
        abstraction_info_for_prompt = []
        for i, abstr in enumerate(abstractions):
            # Use 'files' which contains indices directly
            file_indices_str = ", ".join(map(str, abstr["files"]))
            # Abstraction name and description might be translated already
            info_line = f"- Index {i}: {abstr['name']} (Relevant file indices: [{file_indices_str}])\\n  Description: {abstr['description']}"
            context += info_line + "\\n"
            abstraction_info_for_prompt.append(
                f"{i} # {abstr['name']}"
            )  # Use potentially translated name here too
            all_relevant_indices.update(abstr["files"])

        context += "\\nRelevant File Snippets (Referenced by Index and Path):\\n"
        # Get content for relevant files using helper
        relevant_files_content_map = get_content_for_indices(
            files_data, sorted(list(all_relevant_indices))
        )
        # Format file content for context
        file_context_str = "\\n\\n".join(
            f"--- File: {idx_path} ---\\n{content}"
            for idx_path, content in relevant_files_content_map.items()
        )
        context += file_context_str

        return (
            context,
            "\n".join(abstraction_info_for_prompt),
            num_abstractions, # Pass the actual count
            project_name,
            language,
            use_cache,
        )  # Return use_cache

    def exec(self, prep_res):
        (
            context,
            abstraction_listing,
            num_abstractions, # Receive the actual count
            project_name,
            language,
            use_cache,
         ) = prep_res  # Unpack use_cache
        print(f"Analyzing relationships using LLM...")

        # Add language instruction and hints only if not English
        language_instruction = ""
        lang_hint = ""
        list_lang_note = ""
        if language.lower() != "english":
            language_instruction = f"IMPORTANT: Generate the `summary` and relationship `label` fields in **{language.capitalize()}** language. Do NOT use English for these fields.\n\n"
            lang_hint = f" (in {language.capitalize()})"
            list_lang_note = f" (Names might be in {language.capitalize()})"  # Note for the input list

        prompt = f"""
Based on the following abstractions and relevant code snippets from the project `{project_name}`:

List of Abstraction Indices and Names{list_lang_note}:
{abstraction_listing}

Context (Abstractions, Descriptions, Code):
{context}

{language_instruction}Please provide:
1. A high-level `summary` of the project's main purpose and functionality in a few beginner-friendly sentences{lang_hint}. Use markdown formatting with **bold** and *italic* text to highlight important concepts.
2. A list (`relationships`) describing the key interactions between these abstractions. For each relationship, specify:
    - `from_abstraction`: Index of the source abstraction (e.g., `0 # AbstractionName1`)
    - `to_abstraction`: Index of the target abstraction (e.g., `1 # AbstractionName2`)
    - `label`: A brief label for the interaction **in just a few words**{lang_hint} (e.g., "Manages", "Inherits", "Uses").
    Ideally the relationship should be backed by one abstraction calling or passing parameters to another.
    Simplify the relationship and exclude those non-important ones.

IMPORTANT: Make sure EVERY abstraction is involved in at least ONE relationship (either as source or target). Each abstraction index must appear at least once across all relationships.

Format the output as YAML:

```yaml
summary: |
  A brief, simple explanation of the project{lang_hint}.
  Can span multiple lines with **bold** and *italic* for emphasis.
relationships:
  - from_abstraction: 0 # AbstractionName1
    to_abstraction: 1 # AbstractionName2
    label: "Manages"{lang_hint}
  - from_abstraction: 2 # AbstractionName3
    to_abstraction: 0 # AbstractionName1
    label: "Provides config"{lang_hint}
  # ... other relationships
```

Now, provide the YAML output:
"""
        response = call_llm(prompt, use_cache=(use_cache and self.cur_retry == 0)) # Use cache only if enabled and not retrying

        # --- Validation ---
        yaml_str = response.strip().split("```yaml")[1].split("```")[0].strip()
        relationships_data = yaml.safe_load(yaml_str)

        if not isinstance(relationships_data, dict) or not all(
            k in relationships_data for k in ["summary", "relationships"]
        ):
            raise ValueError(
                "LLM output is not a dict or missing keys ('summary', 'relationships')"
            )
        if not isinstance(relationships_data["summary"], str):
            raise ValueError("summary is not a string")
        if not isinstance(relationships_data["relationships"], list):
            raise ValueError("relationships is not a list")

        # Validate relationships structure
        validated_relationships = []
        for rel in relationships_data["relationships"]:
            # Check for 'label' key
            if not isinstance(rel, dict) or not all(
                k in rel for k in ["from_abstraction", "to_abstraction", "label"]
            ):
                raise ValueError(
                    f"Missing keys (expected from_abstraction, to_abstraction, label) in relationship item: {rel}"
                )
            # Validate 'label' is a string
            if not isinstance(rel["label"], str):
                raise ValueError(f"Relationship label is not a string: {rel}")

            # Validate indices
            try:
                from_idx = int(str(rel["from_abstraction"]).split("#")[0].strip())
                to_idx = int(str(rel["to_abstraction"]).split("#")[0].strip())
                if not (
                    0 <= from_idx < num_abstractions and 0 <= to_idx < num_abstractions
                ):
                    raise ValueError(
                        f"Invalid index in relationship: from={from_idx}, to={to_idx}. Max index is {num_abstractions-1}."
                    )
                validated_relationships.append(
                    {
                        "from": from_idx,
                        "to": to_idx,
                        "label": rel["label"],  # Potentially translated label
                    }
                )
            except (ValueError, TypeError):
                raise ValueError(f"Could not parse indices from relationship: {rel}")

        print("Generated project summary and relationship details.")
        return {
            "summary": relationships_data["summary"],  # Potentially translated summary
            "details": validated_relationships,  # Store validated, index-based relationships with potentially translated labels
        }

    def post(self, shared, prep_res, exec_res):
        # Structure is now {"summary": str, "details": [{"from": int, "to": int, "label": str}]}
        # Summary and label might be translated
        shared["relationships"] = exec_res


class OrderChapters1(Node):
    def prep(self, shared):
        abstractions = shared["abstractions"]  # Name/description might be translated
        relationships = shared["relationships"]  # Summary/label might be translated
        project_name = shared["project_name"]  # Get project name
        language = shared.get("language", "english")  # Get language
        use_cache = shared.get("use_cache", True)  # Get use_cache flag, default to True

        # Prepare context for the LLM
        abstraction_info_for_prompt = []
        for i, a in enumerate(abstractions):
            abstraction_info_for_prompt.append(
                f"- {i} # {a['name']}"
            )  # Use potentially translated name
        abstraction_listing = "\n".join(abstraction_info_for_prompt)

        # Use potentially translated summary and labels
        summary_note = ""
        if language.lower() != "english":
            summary_note = (
                f" (Note: Project Summary might be in {language.capitalize()})"
            )

        context = f"Project Summary{summary_note}:\n{relationships['summary']}\n\n"
        context += "Relationships (Indices refer to abstractions above):\n"
        for rel in relationships["details"]:
            from_name = abstractions[rel["from"]]["name"]
            to_name = abstractions[rel["to"]]["name"]
            # Use potentially translated 'label'
            context += f"- From {rel['from']} ({from_name}) to {rel['to']} ({to_name}): {rel['label']}\n"  # Label might be translated

        list_lang_note = ""
        if language.lower() != "english":
            list_lang_note = f" (Names might be in {language.capitalize()})"

        return (
            abstraction_listing,
            context,
            len(abstractions),
            project_name,
            list_lang_note,
            use_cache,
        )  # Return use_cache

    def exec(self, prep_res):
        (
            abstraction_listing,
            context,
            num_abstractions,
            project_name,
            list_lang_note,
            use_cache,
        ) = prep_res  # Unpack use_cache
        print("Determining chapter order using LLM...")
        # No language variation needed here in prompt instructions, just ordering based on structure
        # The input names might be translated, hence the note.
        prompt = f"""
Given the following project abstractions and their relationships for the project ```` {project_name} ````:

Abstractions (Index # Name){list_lang_note}:
{abstraction_listing}

Context about relationships and project summary:
{context}

If you are going to make a tutorial for ```` {project_name} ````, what is the best order to explain these abstractions, from first to last?
Ideally, first explain those that are the most important or foundational, perhaps user-facing concepts or entry points. Then move to more detailed, lower-level implementation details or supporting concepts.

Output the ordered list of abstraction indices, including the name in a comment for clarity. Use the format `idx # AbstractionName`.

```yaml
- 2 # FoundationalConcept
- 0 # CoreClassA
- 1 # CoreClassB (uses CoreClassA)
- ...
```

Now, provide the YAML output:
"""
        response = call_llm(prompt, use_cache=(use_cache and self.cur_retry == 0)) # Use cache only if enabled and not retrying

        # --- Validation ---
        yaml_str = response.strip().split("```yaml")[1].split("```")[0].strip()
        ordered_indices_raw = yaml.safe_load(yaml_str)

        if not isinstance(ordered_indices_raw, list):
            raise ValueError("LLM output is not a list")

        ordered_indices = []
        seen_indices = set()
        for entry in ordered_indices_raw:
            try:
                if isinstance(entry, int):
                    idx = entry
                elif isinstance(entry, str) and "#" in entry:
                    idx = int(entry.split("#")[0].strip())
                else:
                    idx = int(str(entry).strip())

                if not (0 <= idx < num_abstractions):
                    raise ValueError(
                        f"Invalid index {idx} in ordered list. Max index is {num_abstractions-1}."
                    )
                if idx in seen_indices:
                    raise ValueError(f"Duplicate index {idx} found in ordered list.")
                ordered_indices.append(idx)
                seen_indices.add(idx)

            except (ValueError, TypeError):
                raise ValueError(
                    f"Could not parse index from ordered list entry: {entry}"
                )

        # Check if all abstractions are included
        if len(ordered_indices) != num_abstractions:
            raise ValueError(
                f"Ordered list length ({len(ordered_indices)}) does not match number of abstractions ({num_abstractions}). Missing indices: {set(range(num_abstractions)) - seen_indices}"
            )

        print(f"Determined chapter order (indices): {ordered_indices}")
        return ordered_indices  # Return the list of indices

    def post(self, shared, prep_res, exec_res):
        # exec_res is already the list of ordered indices
        shared["chapter_order"] = exec_res  # List of indices


class WriteChapters1(BatchNode):
    def prep(self, shared):
        chapter_order = shared["chapter_order"]  # List of indices
        abstractions = shared[
            "abstractions"
        ]  # List of {"name": str, "description": str, "files": [int]}
        files_data = shared["files"]  # List of (path, content) tuples
        project_name = shared["project_name"]
        language = shared.get("language", "english")
        use_cache = shared.get("use_cache", True)  # Get use_cache flag, default to True

        # Get already written chapters to provide context
        # We store them temporarily during the batch run, not in shared memory yet
        # The 'previous_chapters_summary' will be built progressively in the exec context
        self.chapters_written_so_far = (
            []
        )  # Use instance variable for temporary storage across exec calls

        # Create a complete list of all chapters
        all_chapters = []
        chapter_filenames = {}  # Store chapter filename mapping for linking
        for i, abstraction_index in enumerate(chapter_order):
            if 0 <= abstraction_index < len(abstractions):
                chapter_num = i + 1
                chapter_name = abstractions[abstraction_index][
                    "name"
                ]  # Potentially translated name
                # Create safe filename (from potentially translated name)
                safe_name = "".join(
                    c if c.isalnum() else "_" for c in chapter_name
                ).lower()
                filename = f"{i+1:02d}_{safe_name}.md"
                # Format with link (using potentially translated name)
                all_chapters.append(f"{chapter_num}. [{chapter_name}]({filename})")
                # Store mapping of chapter index to filename for linking
                chapter_filenames[abstraction_index] = {
                    "num": chapter_num,
                    "name": chapter_name,
                    "filename": filename,
                }

        # Create a formatted string with all chapters
        full_chapter_listing = "\n".join(all_chapters)

        items_to_process = []
        for i, abstraction_index in enumerate(chapter_order):
            if 0 <= abstraction_index < len(abstractions):
                abstraction_details = abstractions[
                    abstraction_index
                ]  # Contains potentially translated name/desc
                # Use 'files' (list of indices) directly
                related_file_indices = abstraction_details.get("files", [])
                # Get content using helper, passing indices
                related_files_content_map = get_content_for_indices(
                    files_data, related_file_indices
                )

                # Get previous chapter info for transitions (uses potentially translated name)
                prev_chapter = None
                if i > 0:
                    prev_idx = chapter_order[i - 1]
                    prev_chapter = chapter_filenames[prev_idx]

                # Get next chapter info for transitions (uses potentially translated name)
                next_chapter = None
                if i < len(chapter_order) - 1:
                    next_idx = chapter_order[i + 1]
                    next_chapter = chapter_filenames[next_idx]

                items_to_process.append(
                    {
                        "chapter_num": i + 1,
                        "abstraction_index": abstraction_index,
                        "abstraction_details": abstraction_details,  # Has potentially translated name/desc
                        "related_files_content_map": related_files_content_map,
                        "project_name": shared["project_name"],  # Add project name
                        "full_chapter_listing": full_chapter_listing,  # Add the full chapter listing (uses potentially translated names)
                        "chapter_filenames": chapter_filenames,  # Add chapter filenames mapping (uses potentially translated names)
                        "prev_chapter": prev_chapter,  # Add previous chapter info (uses potentially translated name)
                        "next_chapter": next_chapter,  # Add next chapter info (uses potentially translated name)
                        "language": language,  # Add language for multi-language support
                        "use_cache": use_cache, # Pass use_cache flag
                        # previous_chapters_summary will be added dynamically in exec
                    }
                )
            else:
                print(
                    f"Warning: Invalid abstraction index {abstraction_index} in chapter_order. Skipping."
                )

        print(f"Preparing to write {len(items_to_process)} chapters...")
        return items_to_process  # Iterable for BatchNode

    def exec(self, item):
        # This runs for each item prepared above
        abstraction_name = item["abstraction_details"][
            "name"
        ]  # Potentially translated name
        abstraction_description = item["abstraction_details"][
            "description"
        ]  # Potentially translated description
        chapter_num = item["chapter_num"]
        project_name = item.get("project_name")
        language = item.get("language", "english")
        use_cache = item.get("use_cache", True) # Read use_cache from item
        print(f"Writing chapter {chapter_num} for: {abstraction_name} using LLM...")

        # Prepare file context string from the map
        file_context_str = "\n\n".join(
            f"--- File: {idx_path.split('# ')[1] if '# ' in idx_path else idx_path} ---\n{content}"
            for idx_path, content in item["related_files_content_map"].items()
        )

        # Get summary of chapters written *before* this one
        # Use the temporary instance variable
        previous_chapters_summary = "\n---\n".join(self.chapters_written_so_far)

        # Add language instruction and context notes only if not English
        language_instruction = ""
        concept_details_note = ""
        structure_note = ""
        prev_summary_note = ""
        instruction_lang_note = ""
        mermaid_lang_note = ""
        code_comment_note = ""
        link_lang_note = ""
        tone_note = ""
        if language.lower() != "english":
            lang_cap = language.capitalize()
            language_instruction = f"IMPORTANT: Write this ENTIRE tutorial chapter in **{lang_cap}**. Some input context (like concept name, description, chapter list, previous summary) might already be in {lang_cap}, but you MUST translate ALL other generated content including explanations, examples, technical terms, and potentially code comments into {lang_cap}. DO NOT use English anywhere except in code syntax, required proper nouns, or when specified. The entire output MUST be in {lang_cap}.\n\n"
            concept_details_note = f" (Note: Provided in {lang_cap})"
            structure_note = f" (Note: Chapter names might be in {lang_cap})"
            prev_summary_note = f" (Note: This summary might be in {lang_cap})"
            instruction_lang_note = f" (in {lang_cap})"
            mermaid_lang_note = f" (Use {lang_cap} for labels/text if appropriate)"
            code_comment_note = f" (Translate to {lang_cap} if possible, otherwise keep minimal English for clarity)"
            link_lang_note = (
                f" (Use the {lang_cap} chapter title from the structure above)"
            )
            tone_note = f" (appropriate for {lang_cap} readers)"

        prompt = f"""
{language_instruction}Write a very beginner-friendly tutorial chapter (in Markdown format) for the project `{project_name}` about the concept: "{abstraction_name}". This is Chapter {chapter_num}.

Concept Details{concept_details_note}:
- Name: {abstraction_name}
- Description:
{abstraction_description}

Complete Tutorial Structure{structure_note}:
{item["full_chapter_listing"]}

Context from previous chapters{prev_summary_note}:
{previous_chapters_summary if previous_chapters_summary else "This is the first chapter."}

Relevant Code Snippets (Code itself remains unchanged):
{file_context_str if file_context_str else "No specific code snippets provided for this abstraction."}

Instructions for the chapter (Generate content in {language.capitalize()} unless specified otherwise):
- Start with a clear heading (e.g., `# Chapter {chapter_num}: {abstraction_name}`). Use the provided concept name.

- If this is not the first chapter, begin with a brief transition from the previous chapter{instruction_lang_note}, referencing it with a proper Markdown link using its name{link_lang_note}.

- Begin with a high-level motivation explaining what problem this abstraction solves{instruction_lang_note}. Start with a central use case as a concrete example. The whole chapter should guide the reader to understand how to solve this use case. Make it very minimal and friendly to beginners.

- If the abstraction is complex, break it down into key concepts. Explain each concept one-by-one in a very beginner-friendly way{instruction_lang_note}.

- Explain how to use this abstraction to solve the use case{instruction_lang_note}. Give example inputs and outputs for code snippets (if the output isn't values, describe at a high level what will happen{instruction_lang_note}).

- Each code block should be BELOW 10 lines! If longer code blocks are needed, break them down into smaller pieces and walk through them one-by-one. Aggresively simplify the code to make it minimal. Use comments{code_comment_note} to skip non-important implementation details. Each code block should have a beginner friendly explanation right after it{instruction_lang_note}.

- Describe the internal implementation to help understand what's under the hood{instruction_lang_note}. First provide a non-code or code-light walkthrough on what happens step-by-step when the abstraction is called{instruction_lang_note}. It's recommended to use a simple sequenceDiagram with a dummy example - keep it minimal with at most 5 participants to ensure clarity. If participant name has space, use: `participant QP as Query Processing`. {mermaid_lang_note}.

- Then dive deeper into code for the internal implementation with references to files. Provide example code blocks, but make them similarly simple and beginner-friendly. Explain{instruction_lang_note}.

- IMPORTANT: When you need to refer to other core abstractions covered in other chapters, ALWAYS use proper Markdown links like this: [Chapter Title](filename.md). Use the Complete Tutorial Structure above to find the correct filename and the chapter title{link_lang_note}. Translate the surrounding text.

- Use mermaid diagrams to illustrate complex concepts (```mermaid``` format). {mermaid_lang_note}.

- Heavily use analogies and examples throughout{instruction_lang_note} to help beginners understand.

- End the chapter with a brief conclusion that summarizes what was learned{instruction_lang_note} and provides a transition to the next chapter{instruction_lang_note}. If there is a next chapter, use a proper Markdown link: [Next Chapter Title](next_chapter_filename){link_lang_note}.

- Ensure the tone is welcoming and easy for a newcomer to understand{tone_note}.

- Output *only* the Markdown content for this chapter.

Now, directly provide a super beginner-friendly Markdown output (DON'T need ```markdown``` tags):
"""
        chapter_content = call_llm(prompt, use_cache=(use_cache and self.cur_retry == 0)) # Use cache only if enabled and not retrying
        # Basic validation/cleanup
        actual_heading = f"# Chapter {chapter_num}: {abstraction_name}"  # Use potentially translated name
        if not chapter_content.strip().startswith(f"# Chapter {chapter_num}"):
            # Add heading if missing or incorrect, trying to preserve content
            lines = chapter_content.strip().split("\n")
            if lines and lines[0].strip().startswith(
                "#"
            ):  # If there's some heading, replace it
                lines[0] = actual_heading
                chapter_content = "\n".join(lines)
            else:  # Otherwise, prepend it
                chapter_content = f"{actual_heading}\n\n{chapter_content}"

        # Add the generated content to our temporary list for the next iteration's context
        self.chapters_written_so_far.append(chapter_content)

        return chapter_content  # Return the Markdown string (potentially translated)

    def post(self, shared, prep_res, exec_res_list):
        # exec_res_list contains the generated Markdown for each chapter, in order
        shared["chapters"] = exec_res_list
        # Clean up the temporary instance variable
        del self.chapters_written_so_far
        print(f"Finished writing {len(exec_res_list)} chapters.")


class CombineTutorial1(Node):
    def prep(self, shared):
        project_name = shared["project_name"]
        output_base_dir = shared.get("output_dir", "output")  # Default output dir
        output_path = os.path.join(output_base_dir, project_name)
        repo_url = shared.get("repo_url")  # Get the repository URL
        # language = shared.get("language", "english") # No longer needed for fixed strings

        # Get potentially translated data
        relationships_data = shared[
            "relationships"
        ]  # {"summary": str, "details": [{"from": int, "to": int, "label": str}]} -> summary/label potentially translated
        chapter_order = shared["chapter_order"]  # indices
        abstractions = shared[
            "abstractions"
        ]  # list of dicts -> name/description potentially translated
        chapters_content = shared[
            "chapters"
        ]  # list of strings -> content potentially translated

        # --- Generate Mermaid Diagram ---
        mermaid_lines = ["flowchart TD"]
        # Add nodes for each abstraction using potentially translated names
        for i, abstr in enumerate(abstractions):
            node_id = f"A{i}"
            # Use potentially translated name, sanitize for Mermaid ID and label
            sanitized_name = abstr["name"].replace('"', "")
            node_label = sanitized_name  # Using sanitized name only
            mermaid_lines.append(
                f'    {node_id}["{node_label}"]'
            )  # Node label uses potentially translated name
        # Add edges for relationships using potentially translated labels
        for rel in relationships_data["details"]:
            from_node_id = f"A{rel['from']}"
            to_node_id = f"A{rel['to']}"
            # Use potentially translated label, sanitize
            edge_label = (
                rel["label"].replace('"', "").replace("\n", " ")
            )  # Basic sanitization
            max_label_len = 30
            if len(edge_label) > max_label_len:
                edge_label = edge_label[: max_label_len - 3] + "..."
            mermaid_lines.append(
                f'    {from_node_id} -- "{edge_label}" --> {to_node_id}'
            )  # Edge label uses potentially translated label

        mermaid_diagram = "\n".join(mermaid_lines)
        # --- End Mermaid ---

        # --- Prepare index.md content ---
        index_content = f"# Tutorial: {project_name}\n\n"
        index_content += f"{relationships_data['summary']}\n\n"  # Use the potentially translated summary directly
        # Keep fixed strings in English
        index_content += f"**Source Repository:** [{repo_url}]({repo_url})\n\n"

        # Add Mermaid diagram for relationships (diagram itself uses potentially translated names/labels)
        index_content += "```mermaid\n"
        index_content += mermaid_diagram + "\n"
        index_content += "```\n\n"

        # Keep fixed strings in English
        index_content += f"## Chapters\n\n"

        chapter_files = []
        # Generate chapter links based on the determined order, using potentially translated names
        for i, abstraction_index in enumerate(chapter_order):
            # Ensure index is valid and we have content for it
            if 0 <= abstraction_index < len(abstractions) and i < len(chapters_content):
                abstraction_name = abstractions[abstraction_index][
                    "name"
                ]  # Potentially translated name
                # Sanitize potentially translated name for filename
                safe_name = "".join(
                    c if c.isalnum() else "_" for c in abstraction_name
                ).lower()
                filename = f"{i+1:02d}_{safe_name}.md"
                index_content += f"{i+1}. [{abstraction_name}]({filename})\n"  # Use potentially translated name in link text

                # Add attribution to chapter content (using English fixed string)
                chapter_content = chapters_content[i]  # Potentially translated content
                if not chapter_content.endswith("\n\n"):
                    chapter_content += "\n\n"
                # Keep fixed strings in English
                chapter_content += f"---\n\nGenerated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)"

                # Store filename and corresponding content
                chapter_files.append({"filename": filename, "content": chapter_content})
            else:
                print(
                    f"Warning: Mismatch between chapter order, abstractions, or content at index {i} (abstraction index {abstraction_index}). Skipping file generation for this entry."
                )

        # Add attribution to index content (using English fixed string)
        index_content += f"\n\n---\n\nGenerated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)"

        return {
            "output_path": output_path,
            "index_content": index_content,
            "chapter_files": chapter_files,  # List of {"filename": str, "content": str}
        }

    def exec(self, prep_res):
        output_path = prep_res["output_path"]
        index_content = prep_res["index_content"]
        chapter_files = prep_res["chapter_files"]

        print(f"Combining tutorial into directory: {output_path}")
        # Rely on Node's built-in retry/fallback
        os.makedirs(output_path, exist_ok=True)

        # Write index.md
        index_filepath = os.path.join(output_path, "index.md")
        with open(index_filepath, "w", encoding="utf-8") as f:
            f.write(index_content)
        print(f"  - Wrote {index_filepath}")

        # Write chapter files
        for chapter_info in chapter_files:
            chapter_filepath = os.path.join(output_path, chapter_info["filename"])
            with open(chapter_filepath, "w", encoding="utf-8") as f:
                f.write(chapter_info["content"])
            print(f"  - Wrote {chapter_filepath}")

        return output_path  # Return the final path

    def post(self, shared, prep_res, exec_res):
        shared["final_output_dir"] = exec_res  # Store the output path
        print(f"\nTutorial generation complete! Files are in: {exec_res}")


class AnalyzeCode(Node):
    def prep(self, shared):
        files_data = shared["files"]
        project_name = shared["project_name"]
        use_cache = shared.get("use_cache", True)

        def create_llm_context(files_data):
            context = ""
            file_info = []
            for i, (path, content) in enumerate(files_data):
                entry = f"--- File Index {i}: {path} ---\n{content}\n\n"
                context += entry
                file_info.append((i, path))
            return context, file_info

        context, file_info = create_llm_context(files_data)
        file_listing = "\n".join([f"- {idx} # {path}" for idx, path in file_info])
        
        # Create a mapping of file paths to their content for validation
        file_content_map = {path: content for path, content in files_data}
        
        return context, file_listing, len(files_data), project_name, use_cache, file_content_map

    def exec(self, prep_res):
        context, file_listing, file_count, project_name, use_cache, file_content_map = prep_res
        print(f"Analyzing code for comprehensive review...")

        prompt = f"""
You are a code review assistant trained to identify patterns in source code and configurations related to various aspects of code quality, security, and best practices.

Analyze the following codebase for the project `{project_name}`:

Codebase Context:
{context}

List of files:
{file_listing}

IMPORTANT: You MUST return a JSON object with TWO main sections:
1. "technology_stack": A dictionary containing all technologies found in the codebase
2. "findings": A list of issues and recommendations

For the technology stack, you MUST identify and categorize ALL technologies used in the codebase. Look for:
- Programming languages (e.g., Python, JavaScript, Java)
- Frameworks (e.g., React, Django, Spring)
- Libraries (e.g., pandas, numpy, lodash)
- Databases (e.g., PostgreSQL, MongoDB)
- Tools (e.g., Docker, Kubernetes)
- Services (e.g., AWS, Azure)

For each technology, provide:
- name: The technology name
- version: The version if found, or "unknown"
- purpose: What it's used for in this codebase
- files: List of files where it's used

Example technology stack format:
```json
{{
    "technology_stack": {{
        "programming_languages": [
            {{
                "name": "Python",
                "version": "3.8",
                "purpose": "Main application language",
                "files": ["main.py", "utils.py"]
            }}
        ],
        "frameworks": [
            {{
                "name": "Flask",
                "version": "2.0",
                "purpose": "Web framework",
                "files": ["app.py"]
            }}
        ]
    }}
}}
```

Then proceed with the existing best practice checks and return findings in the same format as before.

IMPORTANT RULES:
1. You MUST identify and return the technology stack, even if you find no issues
2. For each technology, you MUST provide at least one file where it's used
3. If you can't determine a version, use "unknown"
4. If you can't determine a purpose, provide a general description
5. The response MUST be valid JSON that can be parsed by json.loads()
6. Do not include any text before or after the JSON object
7. Do not use comments in the JSON response
8. Use double quotes for all strings in the JSON response

Now, analyze the codebase and return the complete JSON response:
"""

        response = call_llm(prompt, use_cache=(use_cache and self.cur_retry == 0))
        
        # Extract and parse JSON from response
        try:
            # Clean the response - remove any non-JSON content
            response = response.strip()
            
            # Find the first { and last }
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                print("Warning: No JSON object found in response. Returning empty findings.")
                print("Response was:", response)
                return {"technology_stack": {}, "findings": []}
                
            json_str = response[start_idx:end_idx]
            
            # Remove any comments from the JSON string
            json_str = re.sub(r'//.*?\n', '\n', json_str)
            
            # Try to parse the JSON
            try:
                analysis = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse JSON response: {str(e)}")
                print("JSON string was:", json_str)
                return {"technology_stack": {}, "findings": []}
            
            # Validate analysis structure
            if not isinstance(analysis, dict):
                print("Warning: Response is not a dictionary. Returning empty findings.")
                print("Response was:", analysis)
                return {"technology_stack": {}, "findings": []}
                
            # Ensure technology_stack exists and is a dict
            if "technology_stack" not in analysis or not isinstance(analysis["technology_stack"], dict):
                analysis["technology_stack"] = {}
                
            # Ensure findings exists and is a list
            if "findings" not in analysis or not isinstance(analysis["findings"], list):
                analysis["findings"] = []
            
            # Validate and clean up technology stack
            validated_tech_stack = {}
            for category, techs in analysis["technology_stack"].items():
                if not isinstance(techs, list):
                    continue
                    
                validated_techs = []
                for tech in techs:
                    if not isinstance(tech, dict):
                        continue
                        
                    # Ensure required fields exist
                    if "name" not in tech:
                        continue
                        
                    # Add missing fields with defaults
                    tech = {
                        "name": tech["name"],
                        "version": tech.get("version", "unknown"),
                        "purpose": tech.get("purpose", "N/A"),
                        "files": tech.get("files", [])
                    }
                    
                    # Validate files exist
                    valid_files = []
                    for file_path in tech["files"]:
                        if file_path in file_content_map:
                            valid_files.append(file_path)
                    
                    tech["files"] = valid_files
                    validated_techs.append(tech)
                
                if validated_techs:
                    validated_tech_stack[category] = validated_techs
            
            # Validate findings
            validated_findings = []
            for finding in analysis["findings"]:
                if not isinstance(finding, dict):
                    continue
                    
                # Check required fields
                if not all(k in finding for k in ["category", "severity", "description", "location", "recommendation"]):
                    continue
                    
                # Validate location
                location = finding["location"]
                if not isinstance(location, dict) or not all(k in location for k in ["file", "line", "code"]):
                    continue
                    
                # Validate types
                if not isinstance(finding["category"], str) or \
                   not isinstance(finding["severity"], str) or \
                   not isinstance(finding["description"], str) or \
                   not isinstance(finding["recommendation"], str) or \
                   not isinstance(location["file"], str) or \
                   not isinstance(location["code"], str):
                    continue
                    
                # Convert line to int if it's a string
                try:
                    location["line"] = int(location["line"])
                except (ValueError, TypeError):
                    continue
                
                # Validate file exists and line number is valid
                file_path = location["file"]
                if file_path not in file_content_map:
                    continue
                    
                file_content = file_content_map[file_path]
                file_lines = file_content.split('\n')
                
                if not (0 <= location["line"] < len(file_lines)):
                    continue
                
                # Validate code snippet matches the actual line
                actual_line = file_lines[location["line"]].strip()
                reported_snippet = location["code"].strip()
                
                if reported_snippet not in actual_line:
                    continue
                        
                validated_findings.append(finding)
            
            print(f"Found {sum(len(techs) for techs in validated_tech_stack.values())} technologies and {len(validated_findings)} findings.")
            return {
                "technology_stack": validated_tech_stack,
                "findings": validated_findings
            }
            
        except Exception as e:
            print(f"Warning: Unexpected error processing response: {str(e)}")
            print("Response was:", response)
            return {"technology_stack": {}, "findings": []}

    def post(self, shared, prep_res, exec_res):
        print("\nDEBUG: AnalyzeCode post")
        print("DEBUG: Analysis results:", exec_res)
        print("DEBUG: Technology stack found:", list(exec_res.get("technology_stack", {}).keys()))
        print("DEBUG: Number of findings:", len(exec_res.get("findings", [])))
        shared["code_analysis"] = exec_res
        print("DEBUG: Stored code_analysis in shared state")


class GenerateReport(Node):
    def prep(self, shared):
        print("\nDEBUG: Starting GenerateReport prep")
        print("DEBUG: Keys in shared:", list(shared.keys()))
        
        analysis = shared.get("code_analysis", {})
        print("DEBUG: Code analysis data:", analysis)
        
        findings = analysis.get("findings", [])
        print("DEBUG: Number of findings:", len(findings))
        
        # Support both old and new technology formats
        if "technology_stack" in analysis:
            technology_stack = analysis["technology_stack"]
        else:
            technology_stack = analysis.get("technologies", {})
        print("DEBUG: Technology stack:", technology_stack)
        
        project_name = shared.get("project_name", "Unknown Project")
        output_dir = shared.get("output_dir", "analysis_output")
        
        print("DEBUG: Project name:", project_name)
        print("DEBUG: Output directory:", output_dir)
        
        return findings, technology_stack, project_name, output_dir

    def exec(self, prep_res):
        findings, technology_stack, project_name, output_dir = prep_res
        print("\nDEBUG: Starting GenerateReport exec")
        print("DEBUG: Number of findings:", len(findings))
        print("DEBUG: Technology stack categories:", list(technology_stack.keys()))
        
        # Group findings by category
        categories = {}
        for finding in findings:
            category = finding.get("category", "Uncategorized")
            if category not in categories:
                categories[category] = []
            categories[category].append(finding)
        
        print("DEBUG: Categories found:", list(categories.keys()))
        
        # Generate markdown report
        report = f"# Code Analysis Report for {project_name}\n\n"
        
        # Technology Stack section
        report += "## Technology Stack\n\n"
        if not technology_stack:
            report += "No technologies identified in the codebase.\n\n"
        else:
            for category, techs in technology_stack.items():
                if not techs:
                    continue
                # Format category name nicely
                pretty_category = category.replace('_', ' ').title()
                report += f"### {pretty_category}\n\n"
                for tech in techs:
                    # Use 'name' instead of 'technology' for new format
                    tech_name = tech.get('name') or tech.get('technology', 'Unknown')
                    report += f"- **{tech_name}**"
                    if 'version' in tech and tech['version'] and tech['version'] != 'unknown':
                        report += f" (v{tech['version']})"
                    report += f"\n  - Purpose: {tech.get('purpose', 'N/A')}\n"
                    if 'files' in tech and tech['files']:
                        report += f"  - Files: {', '.join(tech['files'])}\n\n"
                    else:
                        report += f"  - Files: N/A\n\n"
        
        # Summary section
        report += "## Summary\n\n"
        report += f"Total findings: {len(findings)}\n\n"
        
        if findings:
            report += "Findings by category:\n"
            for category, category_findings in categories.items():
                report += f"- {category}: {len(category_findings)} findings\n"
            report += "\n"
            
            # Add severity distribution
            severity_counts = {"High": 0, "Medium": 0, "Low": 0}
            for finding in findings:
                severity = finding.get("severity", "Low")
                if severity in severity_counts:
                    severity_counts[severity] += 1
            
            report += "### Severity Distribution\n\n"
            report += f"- High Priority: {severity_counts['High']} findings\n"
            report += f"- Medium Priority: {severity_counts['Medium']} findings\n"
            report += f"- Low Priority: {severity_counts['Low']} findings\n\n"
            
            # Add key recommendations section
            report += "### Key Recommendations\n\n"
            high_priority_findings = [f for f in findings if f.get("severity") == "High"]
            medium_priority_findings = [f for f in findings if f.get("severity") == "Medium"]
            
            if high_priority_findings:
                report += "1. **High Priority Issues**:\n"
                for finding in high_priority_findings[:3]:  # Show top 3 high priority findings
                    report += f"   - {finding['description']}\n"
                report += "\n"
            
            if medium_priority_findings:
                report += "2. **Medium Priority Issues**:\n"
                for finding in medium_priority_findings[:3]:  # Show top 3 medium priority findings
                    report += f"   - {finding['description']}\n"
                report += "\n"
            
            # Detailed findings by category
            for category, category_findings in categories.items():
                report += f"## {category}\n\n"
                
                # Sort findings by severity
                def get_severity(finding):
                    severity_order = {"High": 0, "Medium": 1, "Low": 2}
                    return severity_order.get(finding.get("severity", "Low"), 2)
                
                sorted_findings = sorted(category_findings, key=get_severity)
                
                for finding in sorted_findings:
                    severity = finding.get("severity", "Low")
                    location = finding.get("location", {})
                    
                    report += f"### {location.get('file', 'Unknown File')} (Line {location.get('line', 'N/A')}) - {severity} Priority\n\n"
                    report += f"**Problem:** {finding['description']}\n\n"
                    report += f"**Recommendation:** {finding['recommendation']}\n\n"
                    
                    if 'code' in location:
                        report += "**Code Snippet:**\n```\n"
                        report += f"{location['code']}\n"
                        report += "```\n\n"
        
        # Add conclusion
        report += "## Conclusion\n\n"
        if findings:
            report += "This analysis highlights several areas for improvement in the codebase:\n\n"
            if severity_counts['High'] > 0:
                report += "1. **Security**: Address high-priority security findings\n"
            if severity_counts['Medium'] > 0:
                report += "2. **Reliability**: Improve error handling and system stability\n"
            if severity_counts['Low'] > 0:
                report += "3. **Code Quality**: Enhance code maintainability and documentation\n\n"
            report += "Addressing these findings will improve the overall quality, security, and maintainability of the codebase.\n"
        else:
            report += "No significant issues were found in the codebase. The code appears to follow good practices in terms of security, reliability, and maintainability.\n"

        # Generate HTML with styling
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Code Analysis Report - {project_name}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    line-height: 1.4;
                    margin: 0;
                    padding: 15px;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                h1 {{ font-size: 1.5em; margin: 0 0 15px 0; padding-bottom: 5px; border-bottom: 2px solid #eee; }}
                h2 {{ font-size: 1.2em; margin: 15px 0 10px 0; color: #444; }}
                h3 {{ font-size: 1.1em; margin: 10px 0 5px 0; color: #555; }}
                .section {{
                    margin: 10px 0;
                    padding: 10px;
                    background: #f8f9fa;
                    border-radius: 4px;
                }}
                .tech-list {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 10px;
                    margin: 10px 0;
                }}
                .tech-item {{
                    background: white;
                    padding: 8px;
                    border-radius: 4px;
                    border: 1px solid #eee;
                }}
                .finding-list {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
                    gap: 10px;
                    margin: 10px 0;
                }}
                .finding {{
                    background: white;
                    padding: 10px;
                    border-radius: 4px;
                    border: 1px solid #eee;
                }}
                .severity-high {{ color: #dc3545; }}
                .severity-medium {{ color: #fd7e14; }}
                .severity-low {{ color: #28a745; }}
                .severity-badge {{
                    display: inline-block;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: 0.9em;
                    font-weight: 500;
                    margin-right: 8px;
                }}
                .severity-high .severity-badge {{ background: #dc3545; color: white; }}
                .severity-medium .severity-badge {{ background: #fd7e14; color: white; }}
                .severity-low .severity-badge {{ background: #28a745; color: white; }}
                pre, code {{
                    background: #f8f9fa;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: monospace;
                    font-size: 0.9em;
                }}
                .summary {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 10px;
                    margin: 10px 0;
                }}
                .summary-item {{
                    background: white;
                    padding: 10px;
                    border-radius: 4px;
                    border: 1px solid #eee;
                }}
                ul, ol {{ margin: 5px 0; padding-left: 20px; }}
                li {{ margin: 3px 0; }}
                @media print {{
                    body {{ padding: 10px; }}
                    .section {{ break-inside: avoid; }}
                }}
            </style>
        </head>
        <body>
            <h1>Code Analysis Report for {project_name}</h1>
            
            <div class="section">
                <h2>Summary</h2>
                <div class="summary">
                    <div class="summary-item">
                        <strong>Total Findings:</strong> """ + str(len(findings)) + """
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Technology Stack</h2>
                <div class="tech-list">
        """
        
        if not technology_stack:
            html_content += "<p>No technologies identified in the codebase.</p>"
        else:
            for category, techs in technology_stack.items():
                if not techs:
                    continue
                for tech in techs:
                    tech_name = tech.get('name') or tech.get('technology', 'Unknown')
                    html_content += f"""
                    <div class="tech-item">
                        <h3>{tech_name}{f" (v{tech['version']})" if 'version' in tech and tech['version'] and tech['version'] != 'unknown' else ""}</h3>
                        <p><strong>Category:</strong> {category.replace('_', ' ').title()}</p>
                        <p><strong>Purpose:</strong> {tech.get('purpose', 'N/A')}</p>
                        <p><strong>Files:</strong> {', '.join(tech.get('files', ['N/A']))}</p>
                    </div>
                    """
        
        html_content += """
                </div>
            </div>
        """
        
        if findings:
            html_content += """
            <div class="section">
                <h2>Findings</h2>
                <div class="finding-list">
            """
            
            for category, category_findings in categories.items():
                for finding in category_findings:
                    severity = finding.get("severity", "Low")
                    location = finding.get("location", {})
                    
                    html_content += f"""
                    <div class="finding severity-{severity.lower()}">
                        <h3>
                            <span class="severity-badge">{severity}</span>
                            {location.get('file', 'Unknown File')} (Line {location.get('line', 'N/A')})
                        </h3>
                        <p><strong>Category:</strong> {category}</p>
                        <p><strong>Problem:</strong> {finding['description']}</p>
                        <p><strong>Recommendation:</strong> {finding['recommendation']}</p>
                    """
                    
                    if 'code' in location:
                        html_content += f"""
                        <p><strong>Code Snippet:</strong></p>
                        <pre><code>{location['code']}</code></pre>
                        """
                    
                    html_content += "</div>"
            
            html_content += """
                </div>
            </div>
            """
        
        html_content += """
            <div class="section">
                <h2>Conclusion</h2>
        """
        
        if findings:
            html_content += """
                <p>This analysis highlights several areas for improvement in the codebase:</p>
                <ul>
            """
            
            severity_counts = {"High": 0, "Medium": 0, "Low": 0}
            for finding in findings:
                severity = finding.get("severity", "Low")
                if severity in severity_counts:
                    severity_counts[severity] += 1
            
            if severity_counts['High'] > 0:
                html_content += f"<li><strong>Security</strong>: Address {severity_counts['High']} high-priority security findings</li>"
            if severity_counts['Medium'] > 0:
                html_content += f"<li><strong>Reliability</strong>: Improve {severity_counts['Medium']} medium-priority issues</li>"
            if severity_counts['Low'] > 0:
                html_content += f"<li><strong>Code Quality</strong>: Enhance {severity_counts['Low']} low-priority items</li>"
            
            html_content += """
                </ul>
                <p>Addressing these findings will improve the overall quality, security, and maintainability of the codebase.</p>
            """
        else:
            html_content += """
                <p>No significant issues were found in the codebase. The code appears to follow good practices in terms of security, reliability, and maintainability.</p>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """

        # Save both Markdown and HTML
        os.makedirs(output_dir, exist_ok=True)
        
        # Save Markdown
        md_path = os.path.join(output_dir, "analysis_report.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(report)
            
        # Save HTML
        html_path = os.path.join(output_dir, "analysis_report.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Generate PDF
        pdf_path = None
        try:
            from weasyprint import HTML
            pdf_path = os.path.join(output_dir, "analysis_report.pdf")
            HTML(string=html_content).write_pdf(pdf_path)
            print(f"Generated PDF report: {pdf_path}")
        except Exception as e:
            print(f"Warning: Could not generate PDF: {str(e)}")
            print("Please ensure WeasyPrint is installed correctly.")
        
        return {
            "markdown": md_path,
            "html": html_path,
            "pdf": pdf_path
        }

    def post(self, shared, prep_res, exec_res):
        # Store the report paths in shared state
        shared["analysis_report"] = exec_res
        
        # Print the report paths
        print(f"\nAnalysis reports generated:")
        print(f"- Markdown: {exec_res['markdown']}")
        print(f"- HTML: {exec_res['html']}")
        if exec_res['pdf']:
            print(f"- PDF: {exec_res['pdf']}")


class ProcessExcel(Node):
    def prep(self, shared):
        """Prepare input by checking Excel file and sheet name."""
        excel_file = shared.get("excel_file")
        if not excel_file:
            raise ValueError("Excel file path not provided in shared state")
            
        if not os.path.exists(excel_file):
            raise ValueError(f"Excel file not found: {excel_file}")
            
        sheet_name = shared.get("sheet_name")
        output_dir = shared.get("output_dir", ".")
        return excel_file, sheet_name, output_dir

    def exec(self, inputs):
        """Execute Excel processing logic."""
        excel_file, sheet_name, output_dir = inputs
        
        def is_valid_git_repo(url):
            """Check if the URL is a valid Git repository."""
            if not url:
                return False
            # Common Git URL patterns
            patterns = [
                r'^https?://(?:[\w-]+@)?(?:github\.com|gitlab\.com|bitbucket\.org)/[\w-]+/[\w-]+(?:\.git)?$',
                r'^git@(?:github\.com|gitlab\.com|bitbucket\.org):[\w-]+/[\w-]+(?:\.git)?$'
            ]
            return any(re.match(pattern, url.strip()) for pattern in patterns)

        def find_component_and_repo(sheet):
            """Find component name and Git repository URL in the sheet."""
            component_name = None
            repo_url = None
            
            for row in sheet.iter_rows(min_row=1, max_row=sheet.max_row):
                # Check if this row has the component name
                if any(cell.value and "component name" in str(cell.value).lower() for cell in row):
                    # The component name should be in the next column
                    for i, cell in enumerate(row):
                        if cell.value and "component name" in str(cell.value).lower():
                            if i + 1 < len(row) and row[i + 1].value:
                                component_name = str(row[i + 1].value).strip()
                                break
                
                # Check if this row has the Git repo URL
                if any(cell.value and "git repo link" in str(cell.value).lower() for cell in row):
                    # The URL should be in the next column
                    for i, cell in enumerate(row):
                        if cell.value and "git repo link" in str(cell.value).lower():
                            if i + 1 < len(row) and row[i + 1].value:
                                repo_url = str(row[i + 1].value).strip()
                                break
                
                if component_name and repo_url:
                    break
            
            return component_name, repo_url

        def validate_sheet(sheet):
            """Process the sheet and validate its contents."""
            mandatory_count = 0
            valid_git_urls = 0
            total_rows = 0
            
            for row in sheet.iter_rows(min_row=1, max_row=sheet.max_row):
                total_rows += 1
                # Check if this is a mandatory field (has 'M' in third column)
                if len(row) > 2 and row[2].value and str(row[2].value).strip().upper() == 'M':
                    mandatory_count += 1
                    
                    # If this is a Git repo URL field, validate it
                    if any(cell.value and "git repo link" in str(cell.value).lower() for cell in row):
                        for i, cell in enumerate(row):
                            if cell.value and "git repo link" in str(cell.value).lower():
                                if i + 1 < len(row) and row[i + 1].value:
                                    url = str(row[i + 1].value).strip()
                                    if is_valid_git_repo(url):
                                        valid_git_urls += 1
                                    break
            
            return {
                "total_rows": total_rows,
                "mandatory_fields": mandatory_count,
                "valid_git_urls": valid_git_urls,
                "is_valid": mandatory_count > 0 and valid_git_urls > 0
            }

        try:
            # Load the Excel file
            wb = load_workbook(excel_file, read_only=True)
            
            # Get the specified sheet or first sheet
            sheet = wb[sheet_name] if sheet_name else wb.active
            
            # Find component name and repo URL
            component_name, repo_url = find_component_and_repo(sheet)
            
            # Validate the sheet
            validation_results = validate_sheet(sheet)
            
            # Save validation results to JSON
            os.makedirs(output_dir, exist_ok=True)
            validation_file = os.path.join(output_dir, "excel_validation.json")
            
            with open(validation_file, "w") as f:
                json.dump({
                    "component_name": component_name,
                    "repo_url": repo_url,
                    "validation": validation_results
                }, f, indent=2)
            
            return {
                "component_name": component_name,
                "repo_url": repo_url,
                "validation": validation_results
            }
            
        except Exception as e:
            raise ValueError(f"Error processing Excel file: {str(e)}")

    def post(self, shared, prep_res, exec_res):
        """Store results in shared state."""
        if not exec_res["validation"]["is_valid"]:
            raise ValueError("Excel validation failed. Please check the excel_validation.json file for details.")
            
        # Store the Git repo URL in shared state
        shared["repo_url"] = exec_res["repo_url"]
        
        # Store the component name as project name
        shared["project_name"] = exec_res["component_name"]
        
        # Store validation results
        shared["excel_validation"] = exec_res["validation"]
        
        return "default"
