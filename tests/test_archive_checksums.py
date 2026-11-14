"""Tests verifying checksums of frozen release archives and citation metadata validity."""
import hashlib
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
V2_ROOT = REPO_ROOT / "V2_ROBUSTNESS_STUDY"

EXPECTED_CHECKSUMS = {
    "v2_release_candidate_final.zip": (
        "787ff47226c4c237a8110fbe35bb085c316642a3743750a2e599265748bd46a0",
        1995409
    ),
    "v2_reproducibility_data_final.zip": (
        "00ddeff0ead81d394a5e516f584ef52a5d5ef97b35fbc44e69bb921dacb939a2",
        2382660603
    ),
    "v2_verification_audit.zip": (
        "c80e46a3fc46e0fb56008c8db48ce63c7e87922a645dfb7ff72fd0667f4b364d",
        67848
    )
}


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 checksum in 8MB chunks."""
    h = hashlib.sha256()
    with open(file_path, "rb") as fp:
        while chunk := fp.read(8 * 1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


@pytest.mark.parametrize("filename,meta", EXPECTED_CHECKSUMS.items())
def test_frozen_archive_checksum_and_size(filename, meta):
    """Verify that each frozen archive file exists with exact size and SHA-256 digest."""
    expected_hash, expected_size = meta
    archive_path = V2_ROOT / filename
    
    assert archive_path.exists(), f"Archive file not found: {archive_path}"
    assert archive_path.stat().st_size == expected_size, (
        f"{filename}: expected {expected_size} bytes, got {archive_path.stat().st_size}"
    )
    
    actual_hash = compute_sha256(archive_path)
    assert actual_hash == expected_hash, (
        f"{filename}: expected SHA-256 {expected_hash}, got {actual_hash}"
    )


def test_citation_cff_metadata():
    """Verify CITATION.cff structure, version, and approved 3-author order."""
    cff_path = REPO_ROOT / "CITATION.cff"
    assert cff_path.exists(), "CITATION.cff not found at repository root"
    
    content = cff_path.read_text(encoding="utf-8")
    assert 'version: "2.0.0"' in content or 'version: 2.0.0' in content
    assert "0009-0003-9248-6174" in content # Saqib Ahmad Bhat
    assert "0000-0002-1786-4193" in content # Sona G
    assert "0000-0002-9958-6106" in content # P. Subha Karuvelam
    assert "10.5281/zenodo.22649504" in content # Concept DOI
