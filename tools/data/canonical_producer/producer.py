"""Build a deterministic CARDDATABASE + REGISTRY component candidate."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path
import shutil
from typing import Any, Mapping, Sequence

from .bridge import MODULE_NAMES, TOOL_ROOT, load_existing_modules


CARDDATABASE_PATH = "data/canonical/CARDDATABASE.xlsx"
REGISTRY_PATH = "data/canonical/REGISTRY.xlsx"
DEFAULT_OUTPUT_ROOT = "TEMP/data_build"

AUDITED_DATASETS = (
    CARDDATABASE_PATH,
    REGISTRY_PATH,
    "Aeterna dokumentációk/AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx",
    "Aeterna dokumentációk/LOOKUPS.xlsx",
    "Aeterna dokumentációk/cards.xlsx",
    "data/canonical/PRODUCT_CATALOG.xlsx",
    "data/workflows/DATA_REVIEW_LEDGER.xlsx",
    "design/naming/reviews/CARD_NAME_REVIEWS.xlsx",
)

PROFILE_ID = "canonical-component-candidate-v2"
PROFILE_SOURCE_ROLES = ("CARDDATABASE", "REGISTRY")
VALIDATION_POLICY_ID = "canonical-development-export-with-production-blockers-v1"
TOOL_CONTRACT_ID = "canonical-producer"
TOOL_CONTRACT_VERSION = "v1"
CANDIDATE_ID_DOMAIN = "aeterna-canonical-candidate-v1"
ZERO_HASH = "sha256:" + "0" * 64


class ProducerError(RuntimeError):
    """Stable producer failure with a machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class ProducerConfig:
    repository_root: Path
    carddatabase_path: str = CARDDATABASE_PATH
    registry_path: str = REGISTRY_PATH
    output_root: str = DEFAULT_OUTPUT_ROOT


@dataclass(frozen=True)
class BuildResult:
    candidate_root: Path
    candidate_id: str
    package_set_id: str
    component_count: int
    file_count: int
    source_hashes: Mapping[str, str]
    read_counts: Mapping[str, int]
    production_ready: bool
    publish_allowed: bool


def default_config(repository_root: Path | None = None) -> ProducerConfig:
    root = repository_root or Path(__file__).resolve().parents[3]
    return ProducerConfig(repository_root=root)


def _canonical_relative_path(value: str, package_set: Any) -> str:
    try:
        return package_set.canonical_relative_path(value)
    except package_set.PackageSetContractError as exc:
        raise ProducerError("SOURCE_PATH_INVALID", f"Invalid repository-relative path: {value!r}") from exc


def _resolve_under(root: Path, relative_path: str) -> Path:
    resolved = (root / Path(relative_path)).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ProducerError("SOURCE_PATH_INVALID", f"Path escapes repository: {relative_path}") from exc
    return resolved


def _validate_config(config: ProducerConfig, package_set: Any) -> tuple[Path, Path, Path]:
    root = config.repository_root.resolve()
    card_path = _canonical_relative_path(config.carddatabase_path, package_set)
    registry_path = _canonical_relative_path(config.registry_path, package_set)
    output_path = _canonical_relative_path(config.output_root, package_set)

    if card_path != CARDDATABASE_PATH:
        raise ProducerError(
            "CANONICAL_SOURCE_SUBSTITUTION_REJECTED",
            f"CARDDATABASE source must be {CARDDATABASE_PATH}.",
        )
    if registry_path != REGISTRY_PATH:
        raise ProducerError(
            "CANONICAL_SOURCE_SUBSTITUTION_REJECTED",
            f"REGISTRY source must be {REGISTRY_PATH}.",
        )
    if output_path != DEFAULT_OUTPUT_ROOT:
        raise ProducerError(
            "OUTPUT_ROOT_REJECTED",
            f"Candidate output must be {DEFAULT_OUTPUT_ROOT}.",
        )

    card = _resolve_under(root, card_path)
    registry = _resolve_under(root, registry_path)
    output = _resolve_under(root, output_path)
    for expected_name, path in (("CARDDATABASE", card), ("REGISTRY", registry)):
        if not path.is_file():
            raise ProducerError("CANONICAL_SOURCE_MISSING", f"{expected_name} source is missing.")
    return card, registry, output


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_write(path: Path, value: Any, package_set: Any) -> bytes:
    data = package_set.canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def _load_exported_tables(package_root: Path) -> dict[str, list[dict[str, Any]]]:
    tables: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(package_root.glob("*.json"), key=lambda item: item.name.encode("utf-8")):
        envelope = json.loads(path.read_text(encoding="utf-8"))
        table_id = envelope.get("table_id")
        records = envelope.get("records")
        if not isinstance(table_id, str) or not isinstance(records, list):
            raise ProducerError("CANONICAL_EXPORT_INVALID", f"Invalid export envelope: {path.name}")
        tables[table_id] = records
    return tables


def _meta(tables: Mapping[str, Sequence[Mapping[str, Any]]]) -> dict[str, Any]:
    return {str(record["key"]): record.get("value") for record in tables["meta"]}


def _stage_record(result: Any) -> dict[str, Any]:
    rule_results = []
    for item in result.rule_results:
        execution = item.execution
        rule_results.append(
            {
                "blocking": item.rule.blocking,
                "diagnostics": [diagnostic.as_dict() for diagnostic in execution.diagnostics],
                "evaluated_record_count": execution.evaluated_record_count,
                "outcome": execution.outcome.value,
                "rule_id": execution.rule_id,
                "validation_kind_id": item.rule.validation_kind_id,
                "violation_count": execution.violation_count,
            }
        )
    return {
        "active_rule_count": result.active_rule_count,
        "blocking_fail_count": result.blocking_fail_count,
        "blocking_not_executed_count": result.blocking_not_executed_count,
        "blocking_unsupported_count": result.blocking_unsupported_count,
        "fail_count": result.fail_count,
        "not_applicable_count": result.not_applicable_count,
        "not_executed_count": result.not_executed_count,
        "pass_count": result.pass_count,
        "rule_results": rule_results,
        "stage_id": result.stage_id,
        "stage_verdict": result.stage_verdict.value,
        "unsupported_count": result.unsupported_count,
    }


def _validation_ledger(
    exported: Mapping[str, Mapping[str, Sequence[Mapping[str, Any]]]],
    modules: Mapping[str, Any],
) -> dict[str, Any]:
    rules = modules["canonical_validation_rules"]
    execution = modules["canonical_validation_execution"]
    stage = modules["canonical_validation_stage"]

    namespaced_tables: dict[str, Mapping[str, Sequence[Mapping[str, Any]]]] = {}
    component_namespaces: dict[str, str] = {}
    namespace_policies: dict[str, dict[str, str]] = {}
    rule_inputs = []
    for package_id in sorted(exported, key=lambda value: value.encode("utf-8")):
        tables = exported[package_id]
        meta = _meta(tables)
        namespace = str(meta["export_namespace"])
        namespaced_tables[namespace] = tables
        component_namespaces[package_id] = namespace
        namespace_policies[namespace] = {
            "external_reference_identifier_policy": str(meta["external_reference_identifier_policy"]),
            "table_identity_policy": str(meta["table_identity_policy"]),
        }
        rule_inputs.extend(
            rules.ValidationRuleInput(record, package_id)
            for record in tables["validation_rules"]
            if record.get("status") == "active"
        )

    catalog_result = rules.build_validation_rule_catalog(tuple(rule_inputs))
    if not catalog_result.is_valid:
        raise ProducerError(
            "CANONICAL_VALIDATION_CATALOG_INVALID",
            json.dumps([item.as_dict() for item in catalog_result.diagnostics], ensure_ascii=False),
        )
    context = execution.ValidationDataContext(
        namespaced_tables=namespaced_tables,
        component_namespaces=component_namespaces,
        namespace_policies=namespace_policies,
    )
    stages = [
        _stage_record(stage.run_validation_stage(catalog_result.catalog, stage_id, context))
        for stage_id in ("pre_export", "production_export")
    ]
    return {
        "candidate_export_mode": "development",
        "catalog_diagnostics": [],
        "production_export_permitted": False,
        "stages": stages,
        "validation_policy_id": VALIDATION_POLICY_ID,
    }


def _file_descriptors(package_root: Path, candidate_relative_root: str, manifest_name: str, package_set: Any) -> tuple[Any, ...]:
    descriptors = []
    for path in sorted(package_root.glob("*.json"), key=lambda item: item.name.encode("utf-8")):
        data = path.read_bytes()
        descriptors.append(
            package_set.FileDescriptor(
                relative_path=f"{candidate_relative_root}/{path.name}",
                size_bytes=len(data),
                file_hash=package_set.sha256_bytes(data),
                role="manifest" if path.name == manifest_name else "canonical_table",
            )
        )
    return tuple(descriptors)


def _component(
    package_root: Path,
    component_kind: str,
    tables: Mapping[str, Sequence[Mapping[str, Any]]],
    dependencies: tuple[Any, ...],
    package_set: Any,
) -> Any:
    meta = _meta(tables)
    manifest_name = str(meta["export_manifest_file"])
    relative_root = f"components/{component_kind}"
    descriptors = _file_descriptors(package_root, relative_root, manifest_name, package_set)
    manifest_bytes = (package_root / manifest_name).read_bytes()
    value = package_set.ComponentDescriptor(
        component_format_version=package_set.COMPONENT_FORMAT_VERSION,
        component_identity=ZERO_HASH,
        component_id=component_kind.casefold(),
        component_kind=component_kind,
        package_id=str(meta["workbook_id"]),
        schema_version=str(meta["schema_version"]),
        data_version=str(meta["data_version"]),
        content_hash=package_set.compute_component_content_hash(descriptors),
        manifest_file=f"{relative_root}/{manifest_name}",
        manifest_hash=package_set.sha256_bytes(manifest_bytes),
        dependencies=dependencies,
        consumer_requirement=package_set.CONSUMER_REQUIRED,
    )
    return replace(value, component_identity=package_set.compute_component_identity(value))


def _readiness() -> dict[str, Any]:
    blockers = [
        {
            "id": "HD-01",
            "impact": "BLOCKING_FOR_PRODUCTION_PARITY",
            "status": "OPEN",
            "summary": "Four runtime/master cells require a truth decision.",
        },
        {
            "id": "P01",
            "impact": "BLOCKING_FOR_PRODUCTION_PARITY",
            "status": "OPEN / REQUIRES_TECHNICAL_SEMANTIC_REVIEW",
            "summary": "Canonical structured coverage does not prove full legacy semantic parity.",
        },
        {
            "id": "P04 / HD-07",
            "impact": "BLOCKING_FOR_PRODUCTION_PARITY",
            "status": "OPEN",
            "summary": "REGISTRY export does not prove LOOKUPS retirement readiness.",
        },
        {
            "id": "P08",
            "impact": "NON_RUNTIME_BLOCKER",
            "status": "SCHEMA_GAP",
            "summary": "No dependency from the canonical component candidate contract was found.",
        },
        {
            "id": "P09",
            "impact": "NON_RUNTIME_BLOCKER",
            "status": "OPEN",
            "summary": "No dependency from the canonical component candidate contract was found.",
        },
    ]
    return {
        "blockers": blockers,
        "candidate_build_allowed": True,
        "consumer_cutover": "NOT_STARTED",
        "legacy_fallback_count": 0,
        "legacy_fallback_removal": "NOT_COMPLETE",
        "production_ready": False,
        "publish_allowed": False,
        "verdict": "PRODUCTION_RUNTIME_PARITY_BLOCKED",
    }


def _blocker_markdown(readiness: Mapping[str, Any]) -> str:
    lines = [
        "# W3B.4A Runtime Readiness",
        "",
        "- Candidate build: `PASS`",
        "- Production ready: `false`",
        "- Publish allowed: `false`",
        "- Verdict: `PRODUCTION_RUNTIME_PARITY_BLOCKED`",
        "",
        "| Blocker | Status | Runtime impact |",
        "|---|---|---|",
    ]
    for blocker in readiness["blockers"]:
        lines.append(f"| {blocker['id']} | {blocker['status']} | {blocker['impact']} |")
    lines.extend(
        [
            "",
            "The canonical candidate preserves current CARDDATABASE and REGISTRY data exactly.",
            "It does not infer legacy ability, lookup, alias, or HD-01 truth values.",
            "",
        ]
    )
    return "\n".join(lines)


def _tool_identities(root: Path, package_set: Any) -> list[dict[str, str]]:
    paths = [
        TOOL_ROOT / "canonical_export" / (module.rsplit(".", 1)[-1] + ".py")
        for module in MODULE_NAMES
    ]
    return [
        {
            "path": path.as_posix(),
            "sha256": package_set.sha256_bytes((root / path).read_bytes()),
        }
        for path in paths
    ]


def _candidate_identity_preimage(
    *,
    package_set_id: str,
    source_hashes: Mapping[str, str],
    tool_identities: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    return {
        "domain": CANDIDATE_ID_DOMAIN,
        "low_level_tools": [dict(item) for item in tool_identities],
        "package_set_id": package_set_id,
        "sources": [
            {"path": path, "sha256": source_hashes[path]}
            for path in (CARDDATABASE_PATH, REGISTRY_PATH)
        ],
        "tool_contract_id": TOOL_CONTRACT_ID,
        "tool_contract_version": TOOL_CONTRACT_VERSION,
        "validation_policy_id": VALIDATION_POLICY_ID,
    }


def _profile_contract() -> dict[str, Any]:
    """Return the path-independent semantic package-set profile contract."""

    return {
        "component_kinds": list(PROFILE_SOURCE_ROLES),
        "legacy_fallback_allowed": False,
        "producer_source_roles": list(PROFILE_SOURCE_ROLES),
        "tool_contract_id": TOOL_CONTRACT_ID,
        "tool_contract_version": TOOL_CONTRACT_VERSION,
    }


def _compute_candidate_id(
    *,
    package_set_id: str,
    source_hashes: Mapping[str, str],
    tool_identities: Sequence[Mapping[str, str]],
    package_set: Any,
) -> str:
    preimage = _candidate_identity_preimage(
        package_set_id=package_set_id,
        source_hashes=source_hashes,
        tool_identities=tool_identities,
    )
    return package_set.sha256_bytes(package_set.canonical_json_bytes(preimage))


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256_file(path)
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix())
        if path.is_file()
    }


def _publish_immutable_candidate(staging: Path, candidate_root: Path) -> None:
    if candidate_root.exists():
        if _tree_hashes(staging) != _tree_hashes(candidate_root):
            raise ProducerError(
                "CANDIDATE_ID_COLLISION",
                "Existing candidate bytes do not match the deterministic build.",
            )
        shutil.rmtree(staging)
        return
    staging.replace(candidate_root)


def build_candidate(config: ProducerConfig | None = None) -> BuildResult:
    """Build and verify one immutable canonical component candidate."""

    config = config or default_config()
    root = config.repository_root.resolve()
    modules = load_existing_modules(root)
    package_set = modules["canonical_package_set"]
    card_path, registry_path, output_root = _validate_config(config, package_set)

    read_counts = {path: 0 for path in AUDITED_DATASETS}
    source_hashes: dict[str, str] = {}
    for relative_path, source_path in ((CARDDATABASE_PATH, card_path), (REGISTRY_PATH, registry_path)):
        source_hashes[relative_path] = package_set.sha256_bytes(source_path.read_bytes())
        read_counts[relative_path] += 1

    output_root.mkdir(parents=True, exist_ok=True)
    staging = output_root / ".canonical-candidate-staging"
    if staging.exists():
        shutil.rmtree(staging)
    components_root = staging / "components"
    components_root.mkdir(parents=True)

    exporter = modules["canonical_workbook_exporter"]
    try:
        read_counts[CARDDATABASE_PATH] += 1
        read_counts[REGISTRY_PATH] += 1
        exporter.export_canonical_workbooks(
            (card_path, registry_path),
            components_root,
            production=False,
        )
    except exporter.CanonicalExportError as exc:
        shutil.rmtree(staging, ignore_errors=True)
        details = json.dumps([item.as_dict() for item in exc.diagnostics], ensure_ascii=False)
        raise ProducerError("CANONICAL_EXPORT_BLOCKED", details) from exc

    exported = {
        "aeterna_carddatabase": _load_exported_tables(components_root / "CARDDATABASE"),
        "aeterna_registry": _load_exported_tables(components_root / "REGISTRY"),
    }
    ledger = _validation_ledger(exported, modules)
    ledger_bytes = _canonical_write(staging / "validation" / "ledger.json", ledger, package_set)

    registry = _component(
        components_root / "REGISTRY",
        "REGISTRY",
        exported["aeterna_registry"],
        (),
        package_set,
    )
    card_meta = _meta(exported["aeterna_carddatabase"])
    dependency = package_set.DependencyDescriptor(
        target_component_id=registry.component_id,
        target_component_kind=registry.component_kind,
        target_package_id=registry.package_id,
        minimum_schema_version=registry.schema_version,
        minimum_data_version=registry.data_version,
        bound_component_identity=registry.component_identity,
        bound_content_hash=registry.content_hash,
    )
    carddatabase = _component(
        components_root / "CARDDATABASE",
        "CARDDATABASE",
        exported["aeterna_carddatabase"],
        (dependency,),
        package_set,
    )

    profile_contract = _profile_contract()
    value = package_set.PackageSet(
        package_set_format_version=package_set.PACKAGE_SET_FORMAT_VERSION,
        package_set_id=ZERO_HASH,
        package_set_profile_id=PROFILE_ID,
        profile_contract_hash=package_set.sha256_bytes(package_set.canonical_json_bytes(profile_contract)),
        validation_policy_id=VALIDATION_POLICY_ID,
        components=(carddatabase, registry),
        validation_ledger_file="validation/ledger.json",
        validation_ledger_hash=package_set.sha256_bytes(ledger_bytes),
    )
    value = replace(value, package_set_id=package_set.compute_package_set_identity(value))
    verification = package_set.verify_package_set(value)
    if not verification.is_valid:
        shutil.rmtree(staging, ignore_errors=True)
        raise ProducerError(
            "PACKAGE_SET_INVALID",
            json.dumps([item.as_dict() for item in verification.diagnostics], ensure_ascii=False),
        )

    tool_identities = _tool_identities(root, package_set)
    candidate_id = _compute_candidate_id(
        package_set_id=value.package_set_id,
        source_hashes=source_hashes,
        tool_identities=tool_identities,
        package_set=package_set,
    )
    _canonical_write(staging / "package_set.json", value.as_dict(), package_set)
    readiness = _readiness()
    _canonical_write(staging / "readiness.json", readiness, package_set)
    (staging / "blocker_report.md").write_text(
        _blocker_markdown(readiness), encoding="utf-8", newline="\n"
    )
    _canonical_write(
        staging / "producer_diagnostics.json",
        {
            "candidate_build": "PASS",
            "diagnostics": [],
            "production_validation": "BLOCKED",
            "production_validation_reason": "Open canonical diagnostics and semantic parity blockers.",
        },
        package_set,
    )
    _canonical_write(
        staging / "producer_read_audit.json",
        {
            "counts": read_counts,
            "scope": "producer execution only; documentation, tests, and review hashing excluded",
        },
        package_set,
    )
    _canonical_write(
        staging / "provenance.json",
        {
            "canonical_export_mode": "development_candidate",
            "candidate_id": candidate_id,
            "candidate_identity_domain": CANDIDATE_ID_DOMAIN,
            "package_set_id": value.package_set_id,
            "profile_contract": profile_contract,
            "sources": [
                {
                    "data_version": str(card_meta["data_version"]),
                    "dataset_identity": "aeterna_carddatabase",
                    "path": CARDDATABASE_PATH,
                    "schema_version": str(card_meta["schema_version"]),
                    "sha256": source_hashes[CARDDATABASE_PATH],
                },
                {
                    "data_version": str(_meta(exported["aeterna_registry"])["data_version"]),
                    "dataset_identity": "aeterna_registry",
                    "path": REGISTRY_PATH,
                    "schema_version": str(_meta(exported["aeterna_registry"])["schema_version"]),
                    "sha256": source_hashes[REGISTRY_PATH],
                },
            ],
            "tool_contract_id": TOOL_CONTRACT_ID,
            "tool_contract_version": TOOL_CONTRACT_VERSION,
            "tool_identities": tool_identities,
            "validation_policy_id": VALIDATION_POLICY_ID,
        },
        package_set,
    )

    candidate_root = output_root / candidate_id.removeprefix("sha256:")
    _publish_immutable_candidate(staging, candidate_root)
    errors = verify_candidate(candidate_root, root)
    if errors:
        raise ProducerError("CANDIDATE_VERIFICATION_FAILED", "; ".join(errors))
    return BuildResult(
        candidate_root=candidate_root,
        candidate_id=candidate_id,
        package_set_id=value.package_set_id,
        component_count=2,
        file_count=sum(path.is_file() for path in candidate_root.rglob("*")),
        source_hashes=source_hashes,
        read_counts=read_counts,
        production_ready=False,
        publish_allowed=False,
    )


def verify_candidate(candidate_root: Path, repository_root: Path | None = None) -> tuple[str, ...]:
    """Verify file hashes, references, paths, bindings, and readiness flags."""

    root = (repository_root or Path(__file__).resolve().parents[3]).resolve()
    modules = load_existing_modules(root)
    package_set = modules["canonical_package_set"]
    errors: list[str] = []
    manifest_path = candidate_root / "package_set.json"
    if not manifest_path.is_file():
        return ("package_set.json is missing",)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    components = payload.get("components", [])
    if {item.get("component_kind") for item in components} != {"CARDDATABASE", "REGISTRY"}:
        errors.append("canonical component set is incomplete")
    by_kind = {item["component_kind"]: item for item in components}

    try:
        typed_components = tuple(
            package_set.ComponentDescriptor(
                component_format_version=item["component_format_version"],
                component_identity=item["component_identity"],
                component_id=item["component_id"],
                component_kind=item["component_kind"],
                package_id=item["package_id"],
                schema_version=item["schema_version"],
                data_version=item["data_version"],
                content_hash=item["content_hash"],
                manifest_file=item["manifest_file"],
                manifest_hash=item["manifest_hash"],
                dependencies=tuple(
                    package_set.DependencyDescriptor(**dependency)
                    for dependency in item["dependencies"]
                ),
                consumer_requirement=item["consumer_requirement"],
            )
            for item in components
        )
        typed_set = package_set.PackageSet(
            package_set_format_version=payload["package_set_format_version"],
            package_set_id=payload["package_set_id"],
            package_set_profile_id=payload["package_set_profile_id"],
            profile_contract_hash=payload["profile_contract_hash"],
            validation_policy_id=payload["validation_policy_id"],
            components=typed_components,
            validation_ledger_file=payload["validation_ledger_file"],
            validation_ledger_hash=payload["validation_ledger_hash"],
        )
    except (KeyError, TypeError, package_set.PackageSetContractError):
        errors.append("package-set manifest shape is invalid")
    else:
        contract_verification = package_set.verify_package_set(typed_set)
        errors.extend(
            f"package-set contract: {item.code}"
            for item in contract_verification.diagnostics
        )
    for component in components:
        try:
            manifest_file = package_set.canonical_relative_path(component["manifest_file"])
        except package_set.PackageSetContractError:
            errors.append(f"unsafe manifest path for {component.get('component_kind')}")
            continue
        manifest = candidate_root / manifest_file
        if not manifest.is_file():
            errors.append(f"missing manifest: {manifest_file}")
        elif package_set.sha256_bytes(manifest.read_bytes()) != component["manifest_hash"]:
            errors.append(f"manifest hash mismatch: {manifest_file}")
        component_root = manifest.parent
        descriptors = _file_descriptors(component_root, str(Path(manifest_file).parent).replace("\\", "/"), manifest.name, package_set)
        if package_set.compute_component_content_hash(descriptors) != component["content_hash"]:
            errors.append(f"content hash mismatch: {component.get('component_kind')}")

    ledger_file = payload.get("validation_ledger_file")
    try:
        ledger_relative = package_set.canonical_relative_path(ledger_file)
    except package_set.PackageSetContractError:
        errors.append("unsafe validation ledger path")
    else:
        ledger = candidate_root / ledger_relative
        if not ledger.is_file() or package_set.sha256_bytes(ledger.read_bytes()) != payload.get("validation_ledger_hash"):
            errors.append("validation ledger hash mismatch")

    if "CARDDATABASE" in by_kind and "REGISTRY" in by_kind:
        dependencies = by_kind["CARDDATABASE"].get("dependencies", [])
        if len(dependencies) != 1:
            errors.append("CARDDATABASE dependency binding is missing")
        else:
            dependency = dependencies[0]
            registry = by_kind["REGISTRY"]
            if dependency.get("bound_component_identity") != registry.get("component_identity"):
                errors.append("REGISTRY component identity binding mismatch")
            if dependency.get("bound_content_hash") != registry.get("content_hash"):
                errors.append("REGISTRY content hash binding mismatch")

    readiness_path = candidate_root / "readiness.json"
    if not readiness_path.is_file():
        errors.append("readiness.json is missing")
    else:
        readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
        if readiness.get("production_ready") is not False or readiness.get("publish_allowed") is not False:
            errors.append("readiness flags permit production or publish")
        blocker_ids = {item.get("id") for item in readiness.get("blockers", [])}
        if not {"P01", "P04 / HD-07", "HD-01"}.issubset(blocker_ids):
            errors.append("required production blockers are missing")

    provenance_path = candidate_root / "provenance.json"
    if not provenance_path.is_file():
        errors.append("provenance.json is missing")
    else:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        source_items = provenance.get("sources", [])
        sources = {
            item.get("path"): item.get("sha256")
            for item in source_items
            if isinstance(item, dict)
        }
        if (
            not isinstance(source_items, list)
            or len(source_items) != 2
            or set(sources) != {CARDDATABASE_PATH, REGISTRY_PATH}
        ):
            errors.append("provenance source set is not the canonical pair")
        for source_path in (CARDDATABASE_PATH, REGISTRY_PATH):
            if not package_set.is_sha256(sources.get(source_path)):
                errors.append(f"provenance source hash is invalid: {source_path}")
            else:
                try:
                    package_set.canonical_relative_path(source_path)
                except package_set.PackageSetContractError:
                    errors.append(f"unsafe provenance source path: {source_path}")

        tool_identities = provenance.get("tool_identities", [])
        if not isinstance(tool_identities, list) or not tool_identities:
            errors.append("low-level tool identities are missing")
        else:
            for item in tool_identities:
                if not isinstance(item, dict) or not package_set.is_sha256(item.get("sha256")):
                    errors.append("low-level tool identity hash is invalid")
                    continue
                try:
                    package_set.canonical_relative_path(item.get("path"))
                except package_set.PackageSetContractError:
                    errors.append("low-level tool identity path is unsafe")

        if provenance.get("package_set_id") != payload.get("package_set_id"):
            errors.append("provenance package_set_id mismatch")
        if provenance.get("candidate_identity_domain") != CANDIDATE_ID_DOMAIN:
            errors.append("candidate identity domain mismatch")
        if provenance.get("tool_contract_id") != TOOL_CONTRACT_ID:
            errors.append("producer tool contract ID mismatch")
        if provenance.get("tool_contract_version") != TOOL_CONTRACT_VERSION:
            errors.append("producer tool contract version mismatch")
        if provenance.get("validation_policy_id") != VALIDATION_POLICY_ID:
            errors.append("candidate validation policy mismatch")

        if all(
            package_set.is_sha256(sources.get(path))
            for path in (CARDDATABASE_PATH, REGISTRY_PATH)
        ) and isinstance(tool_identities, list) and tool_identities:
            try:
                expected_candidate_id = _compute_candidate_id(
                    package_set_id=payload.get("package_set_id"),
                    source_hashes=sources,
                    tool_identities=tool_identities,
                    package_set=package_set,
                )
            except (KeyError, TypeError, package_set.PackageSetContractError):
                errors.append("candidate identity preimage is invalid")
            else:
                if provenance.get("candidate_id") != expected_candidate_id:
                    errors.append("candidate_id mismatch")
                if candidate_root.name != expected_candidate_id.removeprefix("sha256:"):
                    errors.append("candidate directory identity mismatch")

    read_audit_path = candidate_root / "producer_read_audit.json"
    if not read_audit_path.is_file():
        errors.append("producer_read_audit.json is missing")
    else:
        read_audit = json.loads(read_audit_path.read_text(encoding="utf-8"))
        counts = read_audit.get("counts", {})
        if any(counts.get(path) != 0 for path in AUDITED_DATASETS[2:]):
            errors.append("legacy or non-runtime producer read detected")
        if any(
            not isinstance(counts.get(path), int) or counts.get(path) < 1
            for path in (CARDDATABASE_PATH, REGISTRY_PATH)
        ):
            errors.append("canonical producer source read is missing")

    forbidden_fragments = (str(root), "E:\\", "C:\\")
    for path in candidate_root.rglob("*"):
        if path.is_file() and path.suffix in {".json", ".md"}:
            text = path.read_text(encoding="utf-8")
            if any(fragment in text for fragment in forbidden_fragments):
                errors.append(f"absolute or legacy source path leaked into {path.name}")
    return tuple(sorted(set(errors)))
