extends Control
class_name PackageDebugView


const RuntimePackageLoaderScript = preload("res://scripts/contract_loader/runtime_package_loader.gd")

@export var package_path := "res://runtime_package"

var _label: Label


func _ready() -> void:
	_label = Label.new()
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(_label)

	var loader = RuntimePackageLoaderScript.new()
	var result := loader.load_package(package_path)
	loader.print_debug_summary(result)
	_label.text = _format_result(result)


func _format_result(result: Dictionary) -> String:
	var counts = result.get("loaded_counts", {})
	var ability_support_statuses = result.get("ability_support_statuses", {})
	var summary = result.get("diagnostics_summary", {})
	var lines := [
		"AETERNA sample runtime package loader",
		"",
		"ok: %s" % str(result.get("ok", false)),
		"package_id: %s" % result.get("package_id", ""),
		"package_version: %s" % result.get("package_version", ""),
		"schema_version: %s" % result.get("schema_version", ""),
		"",
		"cards: %d" % int(counts.get("cards", 0)),
		"decks: %d" % int(counts.get("decks", 0)),
		"lookup_groups: %d" % int(counts.get("lookup_groups", 0)),
		"ability_modules: %d" % int(counts.get("ability_modules", 0)),
		"ability_support_statuses: %s" % _format_counts(ability_support_statuses),
		"normalization_aliases: %d" % int(counts.get("normalization_aliases", 0)),
		"warnings: %d" % int(summary.get("warnings", 0)),
		"blocking_errors: %d" % int(summary.get("blocking_errors", 0)),
	]

	var errors: Array = result.get("errors", [])
	if not errors.is_empty():
		lines.append("")
		lines.append("Errors:")
		for error in errors:
			lines.append("- %s" % str(error))

	var warnings: Array = result.get("warnings", [])
	if not warnings.is_empty():
		lines.append("")
		lines.append("Warnings:")
		for warning in warnings:
			lines.append("- %s" % str(warning))

	return "\n".join(lines)


func _format_counts(counts) -> String:
	if typeof(counts) != TYPE_DICTIONARY:
		return ""
	var keys: Array = counts.keys()
	keys.sort()
	var parts: Array = []
	for key in keys:
		parts.append("%s=%d" % [str(key), int(counts.get(key, 0))])
	return ", ".join(parts)
