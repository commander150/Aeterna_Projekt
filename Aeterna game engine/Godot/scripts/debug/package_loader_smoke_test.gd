extends SceneTree


const RuntimePackageLoaderScript = preload("res://scripts/contract_loader/runtime_package_loader.gd")
const PACKAGE_PATH = "res://runtime_package"


func _init() -> void:
	print("Running AETERNA package loader smoke test...")

	var loader = RuntimePackageLoaderScript.new()
	var result = loader.load_package(PACKAGE_PATH)
	var counts = result.get("loaded_counts", {})
	var ability_support_statuses = result.get("ability_support_statuses", {})
	var diagnostics = result.get("diagnostics_summary", {})
	var failed = false

	failed = _check_bool(result.get("ok", false), true, "loader_result.ok") or failed
	failed = _check_value(result.get("package_id", ""), "aeterna.sample_runtime_package", "package_id") or failed
	failed = _check_int(counts.get("cards", 0), 814, "cards") or failed
	failed = _check_int(counts.get("decks", 0), 28, "decks") or failed
	failed = _check_int(counts.get("lookup_groups", 0), 32, "lookup_groups") or failed
	failed = _check_int(counts.get("ability_modules", 0), 2, "ability_modules") or failed
	failed = _check_int(ability_support_statuses.get("declared_only", 0), 2, "ability_support_statuses.declared_only") or failed
	failed = _check_int(counts.get("normalization_aliases", 0), 1011, "normalization_aliases") or failed
	failed = _check_int(diagnostics.get("warnings", 0), 0, "warnings") or failed
	failed = _check_int(diagnostics.get("blocking_errors", 0), 0, "blocking_errors") or failed

	print("package_id: %s" % str(result.get("package_id", "")))
	print("package_version: %s" % str(result.get("package_version", "")))
	print("schema_version: %s" % str(result.get("schema_version", "")))
	print("cards: %d" % int(counts.get("cards", 0)))
	print("decks: %d" % int(counts.get("decks", 0)))
	print("lookup_groups: %d" % int(counts.get("lookup_groups", 0)))
	print("ability_modules: %d" % int(counts.get("ability_modules", 0)))
	print("ability_support_statuses: %s" % _format_counts(ability_support_statuses))
	print("normalization_aliases: %d" % int(counts.get("normalization_aliases", 0)))
	print("warnings: %d" % int(diagnostics.get("warnings", 0)))
	print("blocking_errors: %d" % int(diagnostics.get("blocking_errors", 0)))

	if failed:
		print("AETERNA package loader smoke test: FAILED")
		quit(1)
		return

	print("AETERNA package loader smoke test: OK")
	quit()


func _check_bool(actual, expected, label):
	if bool(actual) == bool(expected):
		return false
	push_error("%s expected %s, got %s" % [label, str(expected), str(actual)])
	return true


func _check_value(actual, expected, label):
	if str(actual) == str(expected):
		return false
	push_error("%s expected %s, got %s" % [label, str(expected), str(actual)])
	return true


func _check_int(actual, expected, label):
	if int(actual) == int(expected):
		return false
	push_error("%s expected %d, got %d" % [label, int(expected), int(actual)])
	return true


func _format_counts(counts) -> String:
	if typeof(counts) != TYPE_DICTIONARY:
		return ""
	var keys: Array = counts.keys()
	keys.sort()
	var parts: Array = []
	for key in keys:
		parts.append("%s=%d" % [str(key), int(counts.get(key, 0))])
	return ", ".join(parts)
