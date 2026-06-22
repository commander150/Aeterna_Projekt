extends Control
class_name LegalActionDebugPanel


const JsonFileLoaderScript = preload("res://scripts/contract_loader/json_file_loader.gd")
const SampleContractsLoaderScript = preload("res://scripts/contract_loader/sample_contracts_loader.gd")

@export var contracts_path := "res://sample_contracts"

var _label: Label


func _ready() -> void:
	_label = Label.new()
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(_label)

	var result = load_legal_action_view(contracts_path)
	print_debug_summary(result)
	_label.text = format_panel(result)


func load_legal_action_view(base_path):
	var result = _empty_result()

	var contracts_loader = SampleContractsLoaderScript.new()
	var contracts_result = contracts_loader.load_contracts(base_path)
	result["ok"] = bool(contracts_result.get("ok", false))
	result["warnings"] = int(contracts_result.get("diagnostics_summary", {}).get("warnings", 0))
	result["blocking_errors"] = int(contracts_result.get("diagnostics_summary", {}).get("blocking_errors", 0))
	result["errors"].append_array(contracts_result.get("errors", []))

	var actions_result = JsonFileLoaderScript.read_json(_join_path(base_path, "sample_legal_actions.json"))
	if not bool(actions_result.get("ok", false)):
		result["errors"].append_array(actions_result.get("errors", []))
		result["ok"] = false
		return result

	var data = actions_result.get("data", {})
	if typeof(data) != TYPE_DICTIONARY:
		result["errors"].append("sample_legal_actions.json root must be an object")
		result["ok"] = false
		return result

	var actions = data.get("actions", [])
	if typeof(actions) != TYPE_ARRAY:
		result["errors"].append("sample_legal_actions.json actions must be an array")
		result["ok"] = false
		actions = []

	result["legal_actions"] = data
	result["schema_version"] = str(data.get("schema_version", ""))
	result["match_id"] = str(data.get("match_id", ""))
	result["active_player_id"] = str(data.get("active_player_id", ""))
	result["generated_for_snapshot_id"] = str(data.get("generated_for_snapshot_id", ""))
	result["actions"] = actions
	result["action_count"] = actions.size()
	result["enabled_count"] = _count_actions_by_enabled(actions, true)
	result["disabled_count"] = _count_actions_by_enabled(actions, false)
	result["ok"] = result["ok"] and result["errors"].is_empty()
	return result


func print_debug_summary(result) -> void:
	print("AETERNA legal action debug panel")
	print("schema_version: %s" % str(result.get("schema_version", "")))
	print("match_id: %s" % str(result.get("match_id", "")))
	print("generated_for_snapshot_id: %s" % str(result.get("generated_for_snapshot_id", "")))
	print("actions: %d" % int(result.get("action_count", 0)))
	print("enabled: %d" % int(result.get("enabled_count", 0)))
	print("disabled: %d" % int(result.get("disabled_count", 0)))
	print("warnings: %d" % int(result.get("warnings", 0)))
	print("blocking_errors: %d" % int(result.get("blocking_errors", 0)))
	print("ok: %s" % str(result.get("ok", false)))


func format_panel(result):
	var lines = [
		"AETERNA legal action debug panel",
		"",
		"Basics",
		"schema_version: %s" % str(result.get("schema_version", "")),
		"match_id: %s" % str(result.get("match_id", "")),
		"active_player_id: %s" % str(result.get("active_player_id", "")),
		"generated_for_snapshot_id: %s" % str(result.get("generated_for_snapshot_id", "")),
		"",
		"Enabled actions",
	]

	var actions = result.get("actions", [])
	if typeof(actions) == TYPE_ARRAY:
		for action in actions:
			if _is_action_enabled(action):
				lines.append(_format_action(action))

	lines.append("")
	lines.append("Disabled actions")
	if typeof(actions) == TYPE_ARRAY:
		for action in actions:
			if not _is_action_enabled(action):
				lines.append(_format_action(action))

	lines.append("")
	lines.append("Summary")
	lines.append("actions: %d" % int(result.get("action_count", 0)))
	lines.append("enabled: %d" % int(result.get("enabled_count", 0)))
	lines.append("disabled: %d" % int(result.get("disabled_count", 0)))
	lines.append("warnings: %d" % int(result.get("warnings", 0)))
	lines.append("blocking_errors: %d" % int(result.get("blocking_errors", 0)))
	lines.append("ok: %s" % str(result.get("ok", false)))

	var errors = result.get("errors", [])
	if not errors.is_empty():
		lines.append("")
		lines.append("Errors")
		for error in errors:
			lines.append("- %s" % str(error))

	return "\n".join(lines)


func _format_action(action):
	if typeof(action) != TYPE_DICTIONARY:
		return "- invalid action row"

	var lines = [
		"- %s | type=%s | enabled=%s | %s" % [
			str(action.get("action_id", "")),
			str(action.get("action_type", "")),
			str(action.get("enabled", false)),
			str(action.get("label_hu", "")),
		]
	]
	if action.has("source_card_id"):
		lines.append("  source_card_id: %s" % str(action.get("source_card_id", "")))
	if action.has("target_refs"):
		lines.append("  target_refs: %s" % _format_target_refs(action.get("target_refs", [])))
	if action.has("cost_summary"):
		lines.append("  cost_summary: %s" % _format_cost_summary(action.get("cost_summary", {})))
	if action.has("disabled_reason"):
		lines.append("  disabled_reason: %s" % str(action.get("disabled_reason", "")))
	return "\n".join(lines)


func _format_target_refs(target_refs):
	if typeof(target_refs) != TYPE_ARRAY:
		return "invalid_target_refs"
	var parts = []
	for target_ref in target_refs:
		if typeof(target_ref) == TYPE_DICTIONARY:
			parts.append("%s:%s" % [str(target_ref.get("type", "")), str(target_ref.get("id", ""))])
		else:
			parts.append("invalid_target_ref")
	return ", ".join(parts)


func _format_cost_summary(cost_summary):
	if typeof(cost_summary) != TYPE_DICTIONARY:
		return "invalid_cost_summary"
	var parts = []
	for key in cost_summary.keys():
		parts.append("%s=%s" % [str(key), str(cost_summary.get(key))])
	return ", ".join(parts)


func _count_actions_by_enabled(actions, enabled):
	if typeof(actions) != TYPE_ARRAY:
		return 0
	var count = 0
	for action in actions:
		if _is_action_enabled(action) == bool(enabled):
			count += 1
	return count


func _is_action_enabled(action):
	if typeof(action) != TYPE_DICTIONARY:
		return false
	return bool(action.get("enabled", false))


func _empty_result():
	return {
		"ok": false,
		"errors": [],
		"warnings": 0,
		"blocking_errors": 0,
		"schema_version": "",
		"match_id": "",
		"active_player_id": "",
		"generated_for_snapshot_id": "",
		"actions": [],
		"action_count": 0,
		"enabled_count": 0,
		"disabled_count": 0,
		"legal_actions": {},
	}


func _join_path(base_path, relative_path):
	if str(base_path).ends_with("/"):
		return str(base_path) + str(relative_path)
	return str(base_path) + "/" + str(relative_path)
