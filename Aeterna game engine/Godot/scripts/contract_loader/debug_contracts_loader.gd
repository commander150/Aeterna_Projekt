extends RefCounted
class_name DebugContractsLoader


const JsonFileLoaderScript = preload("res://scripts/contract_loader/json_file_loader.gd")

const SNAPSHOT_SCHEMA = "sample-snapshot-v1"
const LEGAL_ACTIONS_SCHEMA = "sample-legal-actions-v1"
const EVENTS_SCHEMA = "sample-events-v1"


func load_contracts(base_path):
	var result = _empty_result()

	var snapshot_result = JsonFileLoaderScript.read_json(_join_path(base_path, "sample_snapshot.json"))
	var legal_actions_result = JsonFileLoaderScript.read_json(_join_path(base_path, "sample_legal_actions.json"))
	var events_result = JsonFileLoaderScript.read_json(_join_path(base_path, "sample_events.json"))

	_collect_read_errors(result, snapshot_result)
	_collect_read_errors(result, legal_actions_result)
	_collect_read_errors(result, events_result)
	if not result["errors"].is_empty():
		return _finalize(result)

	var snapshot = snapshot_result.get("data", {})
	var legal_actions = legal_actions_result.get("data", {})
	var events = events_result.get("data", {})

	result["snapshot_schema"] = str(snapshot.get("schema_version", ""))
	result["legal_actions_schema"] = str(legal_actions.get("schema_version", ""))
	result["events_schema"] = str(events.get("schema_version", ""))
	result["match_id"] = str(snapshot.get("match_id", ""))

	_check_schema(result, result["snapshot_schema"], SNAPSHOT_SCHEMA, "snapshot_schema")
	_check_schema(result, result["legal_actions_schema"], LEGAL_ACTIONS_SCHEMA, "legal_actions_schema")
	_check_schema(result, result["events_schema"], EVENTS_SCHEMA, "events_schema")

	var legal_match_id = str(legal_actions.get("match_id", ""))
	var events_match_id = str(events.get("match_id", ""))
	if result["match_id"] != legal_match_id:
		result["errors"].append("legal actions match_id does not match snapshot match_id")
	if result["match_id"] != events_match_id:
		result["errors"].append("events match_id does not match snapshot match_id")

	var players = snapshot.get("players", [])
	var actions = legal_actions.get("actions", [])
	var event_rows = events.get("events", [])

	if typeof(players) != TYPE_ARRAY:
		result["errors"].append("snapshot players must be an array")
		players = []
	if typeof(actions) != TYPE_ARRAY:
		result["errors"].append("legal actions must be an array")
		actions = []
	if typeof(event_rows) != TYPE_ARRAY:
		result["errors"].append("events must be an array")
		event_rows = []

	result["loaded_counts"] = {
		"players": players.size(),
		"actions": actions.size(),
		"events": event_rows.size(),
	}

	_collect_diagnostics(result, snapshot.get("diagnostics", {}))
	_collect_diagnostics(result, legal_actions.get("diagnostics", {}))
	_collect_diagnostics(result, events.get("diagnostics", {}))

	return _finalize(result)


func print_debug_summary(result):
	print("AETERNA debug contracts debug")
	print("snapshot_schema: %s" % str(result.get("snapshot_schema", "")))
	print("legal_actions_schema: %s" % str(result.get("legal_actions_schema", "")))
	print("events_schema: %s" % str(result.get("events_schema", "")))
	print("match_id: %s" % str(result.get("match_id", "")))
	var counts = result.get("loaded_counts", {})
	var diagnostics = result.get("diagnostics_summary", {})
	print("players: %d" % int(counts.get("players", 0)))
	print("actions: %d" % int(counts.get("actions", 0)))
	print("events: %d" % int(counts.get("events", 0)))
	print("warnings: %d" % int(diagnostics.get("warnings", 0)))
	print("blocking_errors: %d" % int(diagnostics.get("blocking_errors", 0)))
	print("ok: %s" % str(result.get("ok", false)))


func _empty_result():
	return {
		"ok": false,
		"errors": [],
		"warnings": [],
		"snapshot_schema": "",
		"legal_actions_schema": "",
		"events_schema": "",
		"match_id": "",
		"loaded_counts": {
			"players": 0,
			"actions": 0,
			"events": 0,
		},
		"diagnostics_summary": {
			"warnings": 0,
			"blocking_errors": 0,
		},
	}


func _collect_read_errors(result, read_result):
	if not bool(read_result.get("ok", false)):
		result["errors"].append_array(read_result.get("errors", []))


func _check_schema(result, actual, expected, label):
	if actual != expected:
		result["errors"].append("%s expected %s, got %s" % [label, expected, actual])


func _collect_diagnostics(result, diagnostics):
	if typeof(diagnostics) != TYPE_DICTIONARY:
		result["errors"].append("diagnostics must be an object")
		result["diagnostics_summary"]["blocking_errors"] = int(result["diagnostics_summary"]["blocking_errors"]) + 1
		return

	var warnings = diagnostics.get("warnings", [])
	var blocking_errors = diagnostics.get("blocking_errors", [])
	if typeof(warnings) != TYPE_ARRAY:
		result["errors"].append("diagnostics warnings must be an array")
		warnings = []
	if typeof(blocking_errors) != TYPE_ARRAY:
		result["errors"].append("diagnostics blocking_errors must be an array")
		blocking_errors = []

	result["warnings"].append_array(warnings)
	result["errors"].append_array(blocking_errors)
	result["diagnostics_summary"]["warnings"] = int(result["diagnostics_summary"]["warnings"]) + warnings.size()
	result["diagnostics_summary"]["blocking_errors"] = int(result["diagnostics_summary"]["blocking_errors"]) + blocking_errors.size()


func _finalize(result):
	result["ok"] = result["errors"].is_empty() and int(result["diagnostics_summary"].get("blocking_errors", 0)) == 0
	return result


func _join_path(base_path, relative_path):
	if str(base_path).ends_with("/"):
		return str(base_path) + str(relative_path)
	return str(base_path) + "/" + str(relative_path)
