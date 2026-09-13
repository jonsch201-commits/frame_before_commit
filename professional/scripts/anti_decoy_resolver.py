"""
scripts/anti_decoy_resolver.py — Anti-Decoy Peer Trunk & Exchange Resolver

Prevents creating or reading shallow decoy exchange directories (e.g., G:/.../Claude Foundational Layer/exchange
instead of G:/.../Claude Foundational Layer/claude-foundational-layer/exchange).

Enforces:
1. Repository marker validation: A trunk root is only valid if it contains repository markers
   (CLAUDE.md, .git, wiki/index.md, THE-BOOK.md, etc.). Never trusts bare exchange/inbound existence!
2. Repo-named directory preference: Prefers known nested directories like claude-foundational-layer,
   claude-professional, claude-ssp.
3. Ambiguity resolution: If both shallow and nested exchange exist, flags AMBIGUOUS-ROOT and selects
   the marked repository.
4. Write protection: Forbids write operations that create exchange/inbound if the target has no valid
   repository marker.
"""

import os
import sys
import logging
import warnings
from pathlib import Path
from typing import Optional, Union, Tuple, List

logger = logging.getLogger("anti_decoy_resolver")

# Canonical markers that distinguish real repositories from decoys
DEFAULT_REPO_MARKERS = (
    "CLAUDE.md",
    ".git",
    "wiki/index.md",
    "THE-BOOK.md",
    "CLAUDE-STANDARDS.md",
)

# Known repository directory names preferred when resolving nested layouts
PREFERRED_REPO_NAMES = (
    "claude-foundational-layer",
    "claude-professional",
    "claude-ssp",
    "claude-personal",
    "claude-secretary",
    "antigravity-hub",
)

class DecoyRootError(ValueError):
    """Raised when a directory is rejected as an invalid decoy root lacking repository markers."""
    pass

class AmbiguousRootWarning(UserWarning):
    """Warning flagged when both shallow and nested exchange paths exist."""
    pass

_LAST_STATUS: str = "OK"

def get_last_status() -> str:
    """Returns the status from the most recent resolve_exchange_dir call."""
    return _LAST_STATUS

def has_repo_marker(path: Path, markers: Tuple[str, ...] = DEFAULT_REPO_MARKERS) -> bool:
    """
    Checks whether a directory contains any canonical repository marker:
    CLAUDE.md, .git, wiki/index.md, THE-BOOK.md, etc.
    """
    if not path.is_dir():
        return False
    for marker in markers:
        cand = path / marker
        if cand.exists():
            return True
    return False

def find_nested_marked_repo(
    base_dir: Path,
    markers: Tuple[str, ...] = DEFAULT_REPO_MARKERS,
    scan_general: bool = True
) -> Optional[Path]:
    """
    Finds a valid nested repository under base_dir.
    Checks preferred names first (fast O(1) lookups), then general subdirectories if scan_general=True.
    """
    if not base_dir.is_dir():
        return None

    # 1. Preferred names first (fast targeted lookups)
    candidates: List[str] = list(PREFERRED_REPO_NAMES)
    derived = base_dir.name.lower().replace(" ", "-")
    if derived not in candidates:
        candidates.append(derived)

    for name in candidates:
        sub = base_dir / name
        if sub.is_dir() and has_repo_marker(sub, markers):
            return sub

    if not scan_general:
        return None

    # 2. General subdirectories fallback (excluding standard auxiliary dirs)
    aux_dirs = {"exchange", ".git", ".claude", "wiki", "raw", "scripts", "outbox", "inbound", "reports", "scratch"}
    try:
        for sub in base_dir.iterdir():
            if sub.is_dir() and sub.name.lower() not in aux_dirs:
                if has_repo_marker(sub, markers):
                    return sub
    except Exception:
        pass

    return None

def resolve_exchange_dir(
    path: Union[Path, str],
    strict: bool = True,
    return_status: bool = False,
    markers: Tuple[str, ...] = DEFAULT_REPO_MARKERS
) -> Union[Path, Tuple[Path, str]]:
    """
    Resolves the canonical exchange directory for a given trunk root, exchange dir, or inbound dir.

    Rules:
    1. Prefer repo-named directories first (e.g. claude-foundational-layer, claude-professional).
    2. Validate repository markers (CLAUDE.md, .git, wiki/index.md). Never trust bare exchange/inbound!
    3. If both shallow and nested exchange exist, flag AMBIGUOUS-ROOT and pick the marked repo.
    4. If no marker exists in the path or any nested directory, reject as DECOY_ROOT.

    Parameters:
        path: Trunk root, exchange dir, or inbound dir.
        strict: If True, raises DecoyRootError when directory lacks markers.
        return_status: If True, returns (resolved_path, status_str).
                       If False, returns resolved_path.
        markers: Tuple of repository marker relative paths.

    Returns:
        Path to canonical exchange dir, or (Path, status_str) if return_status=True.
    """
    global _LAST_STATUS
    p = Path(path)

    # Determine base directory
    if p.name == "inbound" and p.parent.name == "exchange":
        base_dir = p.parent.parent
    elif p.name == "exchange":
        base_dir = p.parent
    else:
        base_dir = p

    if not base_dir.exists():
        if strict:
            _LAST_STATUS = "DECOY_ROOT"
            raise DecoyRootError(f"DECOY_ROOT: Directory does not exist: '{base_dir}'")
        _LAST_STATUS = "DECOY_ROOT"
        if return_status:
            return (base_dir / "exchange", "DECOY_ROOT")
        return base_dir / "exchange"

    base_has_marker = has_repo_marker(base_dir, markers)
    # Check preferred nested names first (fast)
    nested_repo = find_nested_marked_repo(base_dir, markers, scan_general=False)
    if nested_repo is None and not base_has_marker:
        # Fallback to general subdirectory search only when base itself lacks markers
        nested_repo = find_nested_marked_repo(base_dir, markers, scan_general=True)

    shallow_exchange = base_dir / "exchange"
    shallow_has_exchange = shallow_exchange.is_dir()

    # Ambiguity evaluation: both shallow and nested exist
    if nested_repo is not None:
        nested_exchange = nested_repo / "exchange"
        if shallow_has_exchange:
            # Both shallow exchange and nested marked repo exist!
            status = "AMBIGUOUS-ROOT"
            _LAST_STATUS = status
            msg = (
                f"[AMBIGUOUS-ROOT] Both shallow ({shallow_exchange}) and nested ({nested_exchange}) "
                f"exist under '{base_dir}'. Selecting marked repository: '{nested_repo}'."
            )
            logger.warning(msg)
            warnings.warn(msg, AmbiguousRootWarning, stacklevel=2)
            print(msg)
            if return_status:
                return (nested_exchange, status)
            return nested_exchange
        else:
            # Only nested marked repo exists
            status = "OK"
            _LAST_STATUS = status
            if return_status:
                return (nested_exchange, status)
            return nested_exchange

    # No nested marked repo found; check base_dir itself
    if base_has_marker:
        status = "OK"
        _LAST_STATUS = status
        target_exchange = base_dir / "exchange"
        if return_status:
            return (target_exchange, status)
        return target_exchange

    # Neither base_dir nor any nested dir has repository markers!
    # A bare exchange/inbound folder without markers is rejected as DECOY_ROOT
    status = "DECOY_ROOT"
    _LAST_STATUS = status
    err_msg = (
        f"DECOY_ROOT: Directory '{base_dir}' lacks repository markers "
        f"({', '.join(markers)}). Never trust bare exchange/inbound existence!"
    )
    if strict:
        raise DecoyRootError(err_msg)

    if return_status:
        return (shallow_exchange, status)
    return shallow_exchange

def safe_prepare_inbox(
    target: Union[Path, str],
    strict: bool = True,
    markers: Tuple[str, ...] = DEFAULT_REPO_MARKERS
) -> Path:
    """
    Safely resolves and prepares target inbox directory for writing:
    1. Resolves exchange directory using resolve_exchange_dir().
    2. Validates that the repository root of the resolved exchange directory contains markers.
    3. Forbids creating exchange/inbound if repository marker is missing.
    4. Creates inbound dir only if marker is validated.

    Returns Path to inbound directory.
    Raises DecoyRootError if target lacks repository markers.
    """
    ex_dir = resolve_exchange_dir(target, strict=strict, markers=markers)
    repo_root = ex_dir.parent

    if not has_repo_marker(repo_root, markers):
        raise DecoyRootError(
            f"DECOY_ROOT: Forbidding write! Repository marker missing in '{repo_root}'. "
            "Cannot create exchange/inbound without repository markers."
        )

    inbox = ex_dir / "inbound"
    inbox.mkdir(parents=True, exist_ok=True)
    return inbox
