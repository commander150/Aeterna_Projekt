extends RefCounted
class_name RuntimePackageLoader


const JsonFileLoaderScript = preload("res://scripts/contract_loader/json_file_loader.gd")
const JsonlFileLoaderScript = preload("res://scripts/contract_loader/jsonl_file_loader.gd")
const SchemaCheckerScript = preload("res://scripts/contract_loader/schema_checker.gd")
const DiagnosticsReaderScript = preload("res://scripts/contract_loader/diagnostics_reader.gd")
const CardRegistryScript = preload("res://scripts/registries/card_registry.gd")
const DeckRegistryScript = preload("res://scripts/registries/deck_registry.gd")
const LookupRegistryScript = preload("res://scripts/registries/lookup_registry.gd")
const AbilityRegistryScript = preload("res://scripts/registries/ability_registry.gd")

const SUPPORT_STATUS_ATTENTION := [
	"unsupported",
	"partial",
	"fallback_required",
	"not_checked",
	"manual_review_required",
]


var card_registry: CardRegistry
var deck_registry: DeckRegistry
var lookup_registry: LookupRegistry
var ability_registry: AbilityRegistry


func load_package(package_path: String) -> Dictionary:
	card_registry = CardRegistryScript.new()
	deck_registry = DeckRegistryScript.new()
	lookup_registry = LookupRegistryScript.new()
	ability_registry = AbilityRegistryScript.new()

	var result := _empty_result()
	var manifest_result := JsonFileLoaderScript.read_json(_join_path(package_path, "manifest.json"))
	if not bool(manifest_result.get("ok", false)):
		result["errors"].append_array(manifest_result.get("errors", []))
		return _finalize_result(result)

	var manifest = manifest_result.get("data")
	if typeof(manifest) != TYPE_DICTIONARY:
		result["errors"].append("manifest.json root must be an object.")
		return _finalize_result(result)

	result["package_id"] = str(manifest.get("package_id", ""))
	result["package_version"] = str(manifest.get("package_version", ""))
	result["schema_version"] = str(manifest.get("schema_version", ""))

	result["errors"].append_array(SchemaCheckerScript.check_manifest(manifest))
	result["errors"].append_array(SchemaCheckerScript.check_manifest_files(package_path, manifest))
	result["blocking"] = SchemaCheckerScript.manifest_is_blocking(manifest)
	if result["blocking"]:
		result["errors"].append("Manifest validation_summary.blocking is true.")
	if not result["errors"].is_empty():
		return _finalize_result(result)

	var cards_result := JsonlFileLoaderScript.read_jsonl(_join_path(package_path, "cards.jsonl"))
	var decks_result := JsonlFileLoaderScript.read_jsonl(_join_path(package_path, "decks.jsonl"))
	var lookups_result := JsonFileLoaderScript.read_json(_join_path(package_path, "lookups.json"))
	var aliases_result := JsonFileLoaderScript.read_json(_join_path(package_path, "aliases.json"))
	var normalization_aliases_result := _read_optional_json(package_path, "normalization_aliases.json")
	var ability_result := JsonFileLoaderScript.read_json(_join_path(package_path, "ability_registry.json"))
	var engine_support_result := JsonFileLoaderScript.read_json(_join_path(package_path, "engine_support.json"))
	var diagnostics_result := JsonFileLoaderScript.read_json(_join_path(package_path, "diagnostics.json"))

	_collect_read_errors(result, cards_result)
	_collect_read_errors(result, decks_result)
	_collect_read_errors(result, lookups_result)
	_collect_read_errors(result, aliases_result)
	_collect_read_errors(result, normalization_aliases_result)
	_collect_read_errors(result, ability_result)
	_collect_read_errors(result, engine_support_result)
	_collect_read_errors(result, diagnostics_result)
	if not result["errors"].is_empty():
		return _finalize_result(result)

	var cards: Array = cards_result.get("rows", [])
	var decks: Array = decks_result.get("rows", [])
	var lookups = lookups_result.get("data")
	var ability_data = ability_result.get("data")
	var diagnostics_data = diagnostics_result.get("data")

	result["errors"].append_array(lookup_registry.load_lookups(lookups))
	result["errors"].append_array(card_registry.load_cards(cards))
	result["errors"].append_array(deck_registry.load_decks(decks))
	result["errors"].append_array(ability_registry.load_ability_registry(ability_data))
	result["errors"].append_array(SchemaCheckerScript.check_cards(cards, lookup_registry))
	result["errors"].append_array(SchemaCheckerScript.check_deck_refs(deck_registry, card_registry))

	result["warnings"].append_array(DiagnosticsReaderScript.get_warning_messages(diagnostics_data))
	result["errors"].append_array(DiagnosticsReaderScript.get_blocking_messages(diagnostics_data))
	var diagnostics_summary: Dictionary = DiagnosticsReaderScript.summarize(diagnostics_data)
	result["diagnostics_summary"] = diagnostics_summary
	result["blocking"] = int(diagnostics_summary.get("blocking_errors", 0)) > 0

	var engine_support_files := 0
	if typeof(engine_support_result.get("data")) == TYPE_DICTIONARY:
		engine_support_files = 1
	var ability_support_statuses := ability_registry.get_support_status_counts()

	result["loaded_counts"] = {
		"cards": card_registry.count(),
		"decks": deck_registry.count(),
		"lookup_groups": lookup_registry.get_group_count(),
		"ability_modules": ability_registry.count(),
		"aliases": _count_wrapped_array(aliases_result.get("data"), "aliases"),
		"normalization_aliases": _count_wrapped_array(normalization_aliases_result.get("data"), "normalization_aliases"),
		"engine_support_files": engine_support_files,
	}
	result["ability_support_statuses"] = ability_support_statuses
	_collect_ability_support_notes(result, ability_support_statuses)
	result["audit_notes"].append("Abilities are registered only; no card ability execution is performed.")
	result["package_loaded"] = result["errors"].is_empty() and not result["blocking"]

	return _finalize_result(result)


func print_debug_summary(result: Dictionary) -> void:
	print("AETERNA package loader debug")
	print("package_id: %s" % result.get("package_id", ""))
	print("package_version: %s" % result.get("package_version", ""))
	print("schema_version: %s" % result.get("schema_version", ""))
	var counts = result.get("loaded_counts", {})
	print("cards: %d" % int(counts.get("cards", 0)))
	print("decks: %d" % int(counts.get("decks", 0)))
	print("lookup_groups: %d" % int(counts.get("lookup_groups", 0)))
	print("ability_modules: %d" % int(counts.get("ability_modules", 0)))
	print("ability_support_statuses: %s" % _format_counts(result.get("ability_support_statuses", {})))
	print("normalization_aliases: %d" % int(counts.get("normalization_aliases", 0)))
	var summary = result.get("diagnostics_summary", {})
	print("warnings: %d" % int(summary.get("warnings", 0)))
	print("blocking_errors: %d" % int(summary.get("blocking_errors", 0)))
	print("ok: %s" % str(result.get("ok", false)))


func _empty_result() -> Dictionary:
	return {
		"ok": false,
		"package_loaded": false,
		"package_id": "",
		"package_version": "",
		"schema_version": "",
		"blocking": false,
		"errors": [],
		"warnings": [],
		"audit_notes": [],
		"loaded_counts": {
			"cards": 0,
			"decks": 0,
			"lookup_groups": 0,
			"ability_modules": 0,
			"aliases": 0,
			"normalization_aliases": 0,
			"engine_support_files": 0,
		},
		"ability_support_statuses": {},
		"diagnostics_summary": {
			"total": 0,
			"warnings": 0,
			"errors": 0,
			"blocking_errors": 0,
		},
	}


func _collect_ability_support_notes(result: Dictionary, status_counts: Dictionary) -> void:
	for status in SUPPORT_STATUS_ATTENTION:
		var count := int(status_counts.get(status, 0))
		if count > 0:
			result["warnings"].append("Ability support status requires attention: %s=%d" % [status, count])
	if int(status_counts.get("declared_only", 0)) > 0:
		result["audit_notes"].append(
			"Ability support status declared_only=%d: modules are registered but not executable." % int(status_counts.get("declared_only", 0))
		)


func _format_counts(counts) -> String:
	if typeof(counts) != TYPE_DICTIONARY:
		return ""
	var keys := counts.keys()
	keys.sort()
	var parts: Array = []
	for key in keys:
		parts.append("%s=%d" % [str(key), int(counts.get(key, 0))])
	return ", ".join(parts)


func _finalize_result(result: Dictionary) -> Dictionary:
	result["ok"] = result["errors"].is_empty() and not result["blocking"] and result["package_loaded"]
	return result


func _collect_read_errors(result: Dictionary, read_result: Dictionary) -> void:
	if not bool(read_result.get("ok", false)):
		result["errors"].append_array(read_result.get("errors", []))


func _read_optional_json(package_path: String, relative_path: String) -> Dictionary:
	var full_path := _join_path(package_path, relative_path)
	if not FileAccess.file_exists(full_path):
		return {
			"ok": true,
			"data": {},
			"errors": [],
		}
	return JsonFileLoaderScript.read_json(full_path)


func _count_wrapped_array(data, key: String) -> int:
	if typeof(data) == TYPE_ARRAY:
		return data.size()
	if typeof(data) == TYPE_DICTIONARY:
		var rows = data.get(key, [])
		if typeof(rows) == TYPE_ARRAY:
			return rows.size()
	return 0


func _join_path(base_path: String, relative_path: String) -> String:
	if base_path.ends_with("/"):
		return base_path + relative_path
	return base_path + "/" + relative_path
