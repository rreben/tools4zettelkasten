"""MCP Server for Zettelkasten management.

This server provides tools for managing a Zettelkasten through the MCP protocol.
It is part of the tools4zettelkasten package and uses the same settings and
core modules as the CLI and Flask interfaces.
"""

import re
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import handle_filenames as hf
from .persistency import PersistencyManager
from . import reorganize as ro
from . import analyse
from . import settings as st

# Initialize MCP server
mcp = FastMCP("zettelkasten")


def get_zettelkasten_manager() -> PersistencyManager:
    """Get PersistencyManager for the main Zettelkasten."""
    return PersistencyManager(st.ZETTELKASTEN)


def get_input_manager() -> PersistencyManager:
    """Get PersistencyManager for the input folder."""
    return PersistencyManager(st.ZETTELKASTEN_INPUT)


# =============================================================================
# Input Management Tools
# =============================================================================

@mcp.tool()
def list_input_files() -> list[dict[str, Any]]:
    """List all files in the input folder.

    Returns information about each file including whether it has
    a valid ID and ordering.
    """
    manager = get_input_manager()
    files = manager.get_list_of_filenames()

    result = []
    for filename in files:
        if manager.is_markdown_file(filename) or manager.is_text_file(filename):
            note = hf.create_Note(filename)
            has_id = hf.is_valid_id(note.id)
            has_ordering = hf.is_valid_ordering(note.ordering) if note.ordering else False

            # Try to get title from file content
            title = note.base_filename.replace("_", " ")
            try:
                content = manager.get_file_content(filename)
                if content and content[0].startswith("#"):
                    title = content[0].lstrip("#").strip()
            except Exception:
                pass

            result.append({
                "filename": filename,
                "title": title,
                "has_id": has_id,
                "has_ordering": has_ordering,
                "ordering": note.ordering,
                "id": note.id
            })

    return result


@mcp.tool()
def preview_staging() -> list[dict[str, str]]:
    """Preview what staging would do without making changes.

    Shows the planned rename operations for files in the input folder.
    """
    manager = get_input_manager()
    files = manager.get_list_of_filenames()

    changes = []
    for filename in files:
        if manager.is_markdown_file(filename) or manager.is_text_file(filename):
            try:
                content = manager.get_file_content(filename)
                if content and content[0].startswith("#"):
                    new_base = hf.create_base_filename_from_title(content[0][2:])
                    note = hf.create_Note(filename)
                    ordering = note.ordering
                    file_id = note.id

                    new_filename = hf.create_filename(ordering, new_base, file_id)

                    if new_filename != filename:
                        changes.append({
                            "old_name": filename,
                            "new_name": new_filename
                        })
            except Exception as e:
                changes.append({
                    "old_name": filename,
                    "error": str(e)
                })

    return changes


@mcp.tool()
def stage_file(filename: str) -> dict[str, Any]:
    """Stage a single file from the input folder.

    This renames the file to have a proper base filename derived from its title.
    Does NOT add ID or ordering - those should be added manually or through reorganize.

    Args:
        filename: Name of the file in the input folder
    """
    manager = get_input_manager()

    if not manager.is_file_existing(filename):
        return {"success": False, "error": f"File not found: {filename}"}

    try:
        content = manager.get_file_content(filename)
        if not content or not content[0].startswith("#"):
            return {"success": False, "error": "File has no valid markdown header"}

        new_base = hf.create_base_filename_from_title(content[0][2:])
        note = hf.create_Note(filename)
        new_filename = hf.create_filename(note.ordering, new_base, note.id)

        if new_filename != filename:
            manager.rename_file(filename, new_filename)
            return {
                "success": True,
                "old_name": filename,
                "new_name": new_filename
            }
        else:
            return {
                "success": True,
                "old_name": filename,
                "new_name": filename,
                "message": "No rename needed"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# Zettelkasten Query Tools
# =============================================================================

@mcp.tool()
def get_zettel(identifier: str) -> dict[str, Any]:
    """Get a single Zettel by ID or filename.

    Args:
        identifier: Either the 9-character ID or the full filename
    """
    manager = get_zettelkasten_manager()
    files = manager.get_list_of_filenames()

    # Find the file
    target_file = None
    if identifier.endswith(".md"):
        # It's a filename
        if manager.is_file_existing(identifier):
            target_file = identifier
    else:
        # It's an ID - search for it
        for filename in files:
            note = hf.create_Note(filename)
            if note.id == identifier:
                target_file = filename
                break

    if not target_file:
        return {"error": f"Zettel not found: {identifier}"}

    note = hf.create_Note(target_file)
    content = manager.get_string_from_file_content(target_file)

    # Extract title from content
    lines = content.split("\n")
    title = note.base_filename.replace("_", " ")
    if lines and lines[0].startswith("#"):
        title = lines[0].lstrip("#").strip()

    # Find links in the file
    links = []
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+\.md)\)')
    for match in link_pattern.finditer(content):
        links.append({
            "description": match.group(1),
            "target": match.group(2)
        })

    return {
        "filename": target_file,
        "title": title,
        "ordering": note.ordering,
        "id": note.id,
        "content": content,
        "links": links
    }


@mcp.tool()
def search_zettel(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Full-text search in the Zettelkasten.

    Args:
        query: Search term (case-insensitive)
        limit: Maximum number of results (default: 10)
    """
    manager = get_zettelkasten_manager()
    files = manager.get_list_of_filenames()

    results = []
    query_lower = query.lower()

    for filename in files:
        if not manager.is_markdown_file(filename):
            continue

        try:
            content = manager.get_string_from_file_content(filename)
            content_lower = content.lower()

            if query_lower in content_lower:
                note = hf.create_Note(filename)

                # Extract title
                lines = content.split("\n")
                title = note.base_filename.replace("_", " ")
                if lines and lines[0].startswith("#"):
                    title = lines[0].lstrip("#").strip()

                # Find snippet around the match
                idx = content_lower.find(query_lower)
                start = max(0, idx - 50)
                end = min(len(content), idx + len(query) + 50)
                snippet = content[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."

                results.append({
                    "filename": filename,
                    "title": title,
                    "id": note.id,
                    "ordering": note.ordering,
                    "snippet": snippet.replace("\n", " ")
                })

                if len(results) >= limit:
                    break
        except Exception:
            continue

    return results


@mcp.tool()
def list_zettel(prefix: str = "", limit: int = 50) -> list[dict[str, Any]]:
    """List Zettel, optionally filtered by ordering prefix.

    Args:
        prefix: Filter by ordering prefix (e.g., "01" for topic 1)
        limit: Maximum number of results (default: 50)
    """
    manager = get_zettelkasten_manager()
    files = manager.get_list_of_filenames()

    results = []
    for filename in sorted(files):
        if not manager.is_markdown_file(filename):
            continue

        note = hf.create_Note(filename)

        # Filter by prefix if specified
        if prefix and not note.ordering.startswith(prefix):
            continue

        # Get title
        title = note.base_filename.replace("_", " ")
        try:
            content = manager.get_file_content(filename)
            if content and content[0].startswith("#"):
                title = content[0].lstrip("#").strip()
        except Exception:
            pass

        results.append({
            "filename": filename,
            "title": title,
            "ordering": note.ordering,
            "id": note.id
        })

        if len(results) >= limit:
            break

    return results


@mcp.tool()
def get_statistics() -> dict[str, Any]:
    """Get statistics about the Zettelkasten.

    Returns total count, topics breakdown, orphans, and other metrics.
    """
    manager = get_zettelkasten_manager()
    files = manager.get_list_of_filenames()

    total = 0
    topics: dict[str, int] = {}
    without_id = []
    without_ordering = []

    for filename in files:
        if not manager.is_markdown_file(filename):
            continue

        total += 1
        note = hf.create_Note(filename)

        # Track files without ID
        if not hf.is_valid_id(note.id):
            without_id.append(filename)

        # Track files without ordering
        if not note.ordering or not hf.is_valid_ordering(note.ordering):
            without_ordering.append(filename)
        elif note.ordering:
            # Count by top-level topic
            top_level = note.ordering.split("_")[0]
            topics[top_level] = topics.get(top_level, 0) + 1

    # Get link statistics
    try:
        all_links = ro.get_list_of_links(manager)
        invalid_links = ro.get_list_of_invalid_links(manager)
    except Exception:
        all_links = []
        invalid_links = []

    return {
        "total_zettel": total,
        "topics": topics,
        "without_id": without_id,
        "without_ordering": without_ordering,
        "total_links": len(all_links),
        "invalid_links": len(invalid_links)
    }


# =============================================================================
# Structure & Analysis Tools
# =============================================================================

@mcp.tool()
def get_links(identifier: str) -> dict[str, Any]:
    """Get all links for a Zettel (both outgoing and incoming).

    Args:
        identifier: Either the 9-character ID or the full filename
    """
    manager = get_zettelkasten_manager()
    files = manager.get_list_of_filenames()

    # Find the target file
    target_file = None
    if identifier.endswith(".md"):
        if manager.is_file_existing(identifier):
            target_file = identifier
    else:
        for filename in files:
            note = hf.create_Note(filename)
            if note.id == identifier:
                target_file = filename
                break

    if not target_file:
        return {"error": f"Zettel not found: {identifier}"}

    # Get all links
    all_links = ro.get_list_of_links(manager)

    outgoing = []
    incoming = []

    for link in all_links:
        if link.source == target_file:
            outgoing.append({
                "description": link.description,
                "target": link.target
            })
        elif link.target == target_file:
            incoming.append({
                "description": link.description,
                "source": link.source
            })

    return {
        "filename": target_file,
        "outgoing": outgoing,
        "incoming": incoming
    }


@mcp.tool()
def find_related(identifier: str, limit: int = 5) -> list[dict[str, Any]]:
    """Find Zettel related to the given one.

    Finds related notes through:
    - Direct links (outgoing and incoming)
    - Hierarchical relation (parent, children, siblings)

    Args:
        identifier: Either the 9-character ID or the full filename
        limit: Maximum number of results (default: 5)
    """
    manager = get_zettelkasten_manager()
    files = manager.get_list_of_filenames()

    # Find the target file
    target_file = None
    if identifier.endswith(".md"):
        if manager.is_file_existing(identifier):
            target_file = identifier
    else:
        for filename in files:
            note = hf.create_Note(filename)
            if note.id == identifier:
                target_file = filename
                break

    if not target_file:
        return [{"error": f"Zettel not found: {identifier}"}]

    target_note = hf.create_Note(target_file)
    related = []
    seen = set()

    # Get links
    all_links = ro.get_list_of_links(manager)

    for link in all_links:
        if link.source == target_file and link.target not in seen:
            seen.add(link.target)
            related.append({
                "filename": link.target,
                "relation_type": f"outgoing link: {link.description}"
            })
        elif link.target == target_file and link.source not in seen:
            seen.add(link.source)
            related.append({
                "filename": link.source,
                "relation_type": f"incoming link: {link.description}"
            })

    # Find hierarchical relations
    if target_note.ordering:
        ordering_parts = target_note.ordering.split("_")

        for filename in files:
            if filename in seen or filename == target_file:
                continue

            note = hf.create_Note(filename)
            if not note.ordering:
                continue

            other_parts = note.ordering.split("_")

            # Parent (one level up)
            if len(ordering_parts) > 1 and other_parts == ordering_parts[:-1]:
                seen.add(filename)
                related.append({
                    "filename": filename,
                    "relation_type": "parent"
                })

            # Child (one level down, starts with our ordering)
            elif (len(other_parts) == len(ordering_parts) + 1
                  and other_parts[:-1] == ordering_parts):
                seen.add(filename)
                related.append({
                    "filename": filename,
                    "relation_type": "child"
                })

            # Sibling (same parent)
            elif (len(other_parts) == len(ordering_parts)
                  and other_parts[:-1] == ordering_parts[:-1]
                  and other_parts != ordering_parts):
                seen.add(filename)
                related.append({
                    "filename": filename,
                    "relation_type": "sibling"
                })

    # Add titles to results
    for item in related[:limit]:
        if "error" not in item:
            try:
                content = manager.get_file_content(item["filename"])
                if content and content[0].startswith("#"):
                    item["title"] = content[0].lstrip("#").strip()
                else:
                    note = hf.create_Note(item["filename"])
                    item["title"] = note.base_filename.replace("_", " ")
            except Exception:
                note = hf.create_Note(item["filename"])
                item["title"] = note.base_filename.replace("_", " ")

    return related[:limit]


@mcp.tool()
def analyze_structure(topic: str = "") -> dict[str, Any]:
    """Analyze the structure of the Zettelkasten or a specific topic.

    Args:
        topic: Optional ordering prefix to filter (e.g., "01" for topic 1)
    """
    manager = get_zettelkasten_manager()

    try:
        analysis = analyse.create_graph_analysis(manager)

        # Filter by topic if specified
        if topic:
            filtered_files = [f for f in analysis.list_of_filenames
                            if hf.create_Note(f).ordering.startswith(topic)]
            filtered_links = [link for link in analysis.list_of_links
                            if hf.create_Note(link.source).ordering.startswith(topic)]
        else:
            filtered_files = analysis.list_of_filenames
            filtered_links = analysis.list_of_links

        # Build simplified tree representation
        tree_summary = []
        for filename in sorted(filtered_files)[:20]:  # Limit for readability
            note = hf.create_Note(filename)
            try:
                content = manager.get_file_content(filename)
                title = content[0].lstrip("#").strip() if content and content[0].startswith("#") else note.base_filename
            except Exception:
                title = note.base_filename.replace("_", " ")

            tree_summary.append({
                "ordering": note.ordering,
                "title": title,
                "id": note.id
            })

        # Link summary
        link_summary = []
        for link in filtered_links[:30]:  # Limit for readability
            link_summary.append({
                "source": link.source,
                "target": link.target,
                "type": link.description
            })

        return {
            "total_files": len(filtered_files),
            "total_links": len(filtered_links),
            "explicit_links": len([link for link in filtered_links
                                 if link.description not in ["train of thoughts", "detail / digression"]]),
            "structure_links": len([link for link in filtered_links
                                  if link.description in ["train of thoughts", "detail / digression"]]),
            "tree": tree_summary,
            "links": link_summary
        }
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# Reorganization Tools
# =============================================================================

@mcp.tool()
def preview_reorganize() -> dict[str, Any]:
    """Preview what reorganization would do.

    Shows planned renames to normalize the ordering scheme.
    Also shows files that need IDs added.
    """
    manager = get_zettelkasten_manager()
    files = manager.get_list_of_filenames()

    # Get files needing IDs
    id_commands = ro.attach_missing_ids(files)

    # Get files needing orderings
    ordering_commands = ro.attach_missing_orderings(files)

    # Get reorganization commands
    tokenized = ro.generate_tokenized_list(files)
    tree = ro.generate_tree(tokenized)
    potential_changes = ro.reorganize_filenames(tree)
    rename_commands = ro.create_rename_commands(potential_changes)

    # Get link corrections
    link_commands = ro.generate_list_of_link_correction_commands(manager)

    return {
        "add_ids": [{"old": cmd[1], "new": cmd[2]} for cmd in id_commands],
        "add_orderings": [{"old": cmd[1], "new": cmd[2]} for cmd in ordering_commands],
        "rename_for_ordering": [{"old": cmd[1], "new": cmd[2]} for cmd in rename_commands],
        "fix_links": [{
            "file": cmd.filename,
            "old_link": cmd.to_be_replaced,
            "new_link": cmd.replace_with
        } for cmd in link_commands],
        "summary": {
            "files_needing_ids": len(id_commands),
            "files_needing_orderings": len(ordering_commands),
            "files_to_rename": len(rename_commands),
            "links_to_fix": len(link_commands)
        }
    }


@mcp.tool()
def execute_reorganize(confirm: bool = False) -> dict[str, Any]:
    """Execute the reorganization of the Zettelkasten.

    This will:
    1. Add missing IDs to files
    2. Rename files to normalize the ordering scheme
    3. Fix broken links

    Args:
        confirm: Must be True to actually execute changes
    """
    if not confirm:
        return {
            "error": "Please set confirm=True to execute changes. "
                    "Use preview_reorganize first to see what will change."
        }

    manager = get_zettelkasten_manager()
    files = manager.get_list_of_filenames()

    results = {
        "ids_added": 0,
        "files_renamed": 0,
        "links_fixed": 0,
        "errors": []
    }

    try:
        # Step 1: Add missing IDs
        id_commands = ro.attach_missing_ids(files)
        for cmd in id_commands:
            try:
                manager.rename_file(cmd[1], cmd[2])
                results["ids_added"] += 1
            except Exception as e:
                results["errors"].append(f"Failed to add ID to {cmd[1]}: {e}")

        # Refresh file list after ID changes
        files = manager.get_list_of_filenames()

        # Step 2: Reorganize ordering
        tokenized = ro.generate_tokenized_list(files)
        tree = ro.generate_tree(tokenized)
        potential_changes = ro.reorganize_filenames(tree)
        rename_commands = ro.create_rename_commands(potential_changes)

        for cmd in rename_commands:
            try:
                manager.rename_file(cmd[1], cmd[2])
                results["files_renamed"] += 1
            except Exception as e:
                results["errors"].append(f"Failed to rename {cmd[1]}: {e}")

        # Refresh file list after renames
        files = manager.get_list_of_filenames()

        # Step 3: Fix links
        link_commands = ro.generate_list_of_link_correction_commands(manager)
        for cmd in link_commands:
            try:
                content = manager.get_string_from_file_content(cmd.filename)
                new_content = content.replace(cmd.to_be_replaced, cmd.replace_with)
                manager.overwrite_file_content(cmd.filename, new_content)
                results["links_fixed"] += 1
            except Exception as e:
                results["errors"].append(f"Failed to fix link in {cmd.filename}: {e}")

        results["success"] = True

    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Reorganization failed: {e}")

    return results


def run_server():
    """Initialize settings and run the MCP server."""
    st.check_directories(strict=False)
    mcp.run()


if __name__ == "__main__":
    run_server()
