import git
from .models import DiffAnalysis, FileDiff


def get_repo(path: str = ".") -> git.Repo:
    return git.Repo(path, search_parent_directories=True)


def get_staged_diff(path: str = ".") -> str:
    repo = get_repo(path)
    return repo.git.diff("--cached", universal_newlines=True, encoding="utf-8")


def get_unstaged_diff(path: str = ".") -> str:
    repo = get_repo(path)
    return repo.git.diff(encoding="utf-8")


def has_staged_changes(path: str = ".") -> bool:
    return bool(get_staged_diff(path))


def parse_diff(diff: str, path: str = ".") -> DiffAnalysis:
    if not diff:
        return DiffAnalysis(
            files_changed=[],
            total_additions=0,
            total_deletions=0,
            change_summary="No changes were detected."
        )

    files = []
    total_add = 0
    total_delete = 0

    # Parsing diff stats
    try:
        repo = get_repo(path)
        stats = repo.git.diff("--cached", "--stat", encoding="utf-8")
        for line in stats.split('\n')[:-1]:
            if '|' in line:
                parts = line.split('|')
                path = parts[0].strip()
                changes = parts[1].strip().split()

                add = changes[0].count('+') if changes else 0
                delete = changes[0].count('-') if changes else 0

                total_add += add
                total_delete += delete

                files.append(FileDiff(
                    path=path,
                    additions=add,
                    deletions=delete,
                    changes_summary=f"{add} additions, {delete} deletions"
                ))
    except (git.exc.GitCommandError, IndexError, AttributeError) as e:
        pass

    return DiffAnalysis(
        files_changed=files,
        total_additions=total_add,
        total_deletions=total_delete,
        change_summary=f"{len(files)} files changed."
    )