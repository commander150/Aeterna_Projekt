extends Control
class_name SampleContractsDebugView


const SampleContractsLoaderScript = preload("res://scripts/contract_loader/sample_contracts_loader.gd")

@export var contracts_path := "res://sample_contracts"

var _label: Label


func _ready() -> void:
	_label = Label.new()
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(_label)

	var loader = SampleContractsLoaderScript.new()
	var result = loader.load_contracts(contracts_path)
	loader.print_debug_summary(result)
	_label.text = _format_result(result)


func _format_result(result):
	var counts = result.get("loaded_counts", {})
	var diagnostics = result.get("diagnostics_summary", {})
	var lines = [
		"AETERNA sample contracts debug",
		"",
		"ok: %s" % str(result.get("ok", false)),
		"snapshot_schema: %s" % str(result.get("snapshot_schema", "")),
		"legal_actions_schema: %s" % str(result.get("legal_actions_schema", "")),
		"events_schema: %s" % str(result.get("events_schema", "")),
		"match_id: %s" % str(result.get("match_id", "")),
		"",
		"players: %d" % int(counts.get("players", 0)),
		"actions: %d" % int(counts.get("actions", 0)),
		"events: %d" % int(counts.get("events", 0)),
		"warnings: %d" % int(diagnostics.get("warnings", 0)),
		"blocking_errors: %d" % int(diagnostics.get("blocking_errors", 0)),
	]

	var errors = result.get("errors", [])
	if not errors.is_empty():
		lines.append("")
		lines.append("Errors:")
		for error in errors:
			lines.append("- %s" % str(error))

	return "\n".join(lines)
