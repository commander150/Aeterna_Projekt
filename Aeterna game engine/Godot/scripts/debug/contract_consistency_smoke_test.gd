extends SceneTree


const JsonFileLoaderScript = preload("res://scripts/contract_loader/json_file_loader.gd")
const SampleContractsLoaderScript = preload("res://scripts/contract_loader/sample_contracts_loader.gd")
const CardReferenceResolverScript = preload("res://scripts/debug/card_reference_resolver.gd")

const CONTRACTS_PATH = "res://sample_contracts"
const RUNTIME_PACKAGE_PATH = "res://runtime_package"
const SNAPSHOT_SCHEMA = "sample-snapshot-v1"
const LEGAL_ACTIONS_SCHEMA = "sample-legal-actions-v1"
const EVENTS_SCHEMA = "sample-events-v1"


func _init() -> void:
	print("Running AETERNA contract consistency smoke test...")

	var result = _run_consistency_check(CONTRACTS_PATH, RUNTIME_PACKAGE_PATH)
	var failed = false

	failed = _check_bool(result.get("ok", false), true, "consistency.ok") or failed
	failed = _check_value(result.get("snapshot_schema", ""), SNAPSHOT_SCHEMA, "snapshot_schema") or failed
	failed = _check_value(result.get("legal_actions_schema", ""), LEGAL_ACTIONS_SCHEMA, "legal_actions_schema") or failed
	failed = _check_value(result.get("events_schema", ""), EVENTS_SCHEMA, "events_schema") or failed
	failed = _check_bool(result.get("match_id_consistent", false), true, "match_id_consistent") or failed
	failed = _check_bool(result.get("snapshot_ref_valid", false), true, "snapshot_ref_valid") or failed
	failed = _check_bool(result.get("diagnostics_valid", false), true, "diagnostics_valid") or failed
	failed = _check_int(result.get("missing_card_refs", 0), 0, "missing_card_refs") or failed
	failed = _check_int(result.get("blocking_errors", 0), 0, "blocking_errors") or failed

	print("snapshot_schema: %s" % str(result.get("snapshot_schema", "")))
	print("legal_actions_schema: %s" % str(result.get("legal_actions_schema", "")))
	print("events_schema: %s" % str(result.get("events_schema", "")))
	print("match_id: %s" % str(result.get("match_id", "")))
	print("snapshot_id: %s" % str(result.get("snapshot_id", "")))
	print("generated_for_snapshot_id: %s" % str(result.get("generated_for_snapshot_id", "")))
	print("match_id_consistent: %s" % str(result.get("match_id_consistent", false)))
	print("snapshot_ref_valid: %s" % str(result.get("snapshot_ref_valid", false)))
	print("diagnostics_valid: %s" % str(result.get("diagnostics_valid", false)))
	print("checked_card_refs: %d" % int(result.get("checked_card_refs", 0)))
	print("missing_card_refs: %d" % int(result.get("missing_card_refs", 0)))
	print("warnings: %d" % int(result.get("warnings", 0)))
	print("blocking_errors: %d" % int(result.get("blocking_errors", 0)))

	if failed:
		for error in result.get("errors", []):
			push_error(str(error))
		print("AETERNA contract consistency smoke test: FAILED")
		quit(1)
		return

	print("AETERNA contract consistency smoke test: OK")
	quit()


func _run_consistency_check(contracts_path, runtime_package_path):
	var result = _empty_result()

	var contracts_loader = SampleContractsLoaderScript.new()
	var contracts_result = contracts_loader.load_contracts(contracts_path)
	result["warnings"] = int(contracts_result.get("diagnostics_summary", {}).get("warnings", 0))
	result["blocking_errors"] = int(contracts_result.get("diagnostics_summary", {}).get("blocking_errors", 0))
	result["errors"].append_array(contracts_result.get("errors", []))

	var snapshot_read = JsonFileLoaderScript.read_json(_join_path(contracts_path, "sample_snapshot.json"))
	var legal_actions_read = JsonFileLoaderScript.read_json(_join_path(contracts_path, "sample_legal_actions.json"))
	var events_read = JsonFileLoaderScript.read_json(_join_path(contracts_path, "sample_events.json"))
	_collect_read_errors(result, snapshot_read)
	_collect_read_errors(result, legal_actions_read)
	_collect_read_errors(result, events_read)
	if not result["errors"].is_empty():
		return _finalize_result(result)

	var snapshot = snapshot_read.get("data", {})
	var legal_actions = legal_actions_read.get("data", {})
	var events = events_read.get("data", {})
	if typeof(snapshot) != TYPE_DICTIONARY or typeof(legal_actions) != TYPE_DICTIONARY or typeof(events) != TYPE_DICTIONARY:
		result["errors"].append("Sample contract roots must be objects.")
		return _finalize_result(result)

	result["snapshot_schema"] = str(snapshot.get("schema_version", ""))
	result["legal_actions_schema"] = str(legal_actions.get("schema_version", ""))
	result["events_schema"] = str(events.get("schema_version", ""))
	result["match_id"] = str(snapshot.get("match_id", ""))
	result["snapshot_id"] = str(snapshot.get("snapshot_id", ""))
	result["generated_for_snapshot_id"] = str(legal_actions.get("generated_for_snapshot_id", ""))

	_check_schema(result, result["snapshot_schema"], SNAPSHOT_SCHEMA, "snapshot_schema")
	_check_schema(result, result["legal_actions_schema"], LEGAL_ACTIONS_SCHEMA, "legal_actions_schema")
	_check_schema(result, result["events_schema"], EVENTS_SCHEMA, "events_schema")

	result["match_id_consistent"] = result["match_id"] == str(legal_actions.get("match_id", "")) and result["match_id"] == str(events.get("match_id", ""))
	if not bool(result["match_id_consistent"]):
		result["errors"].append("match_id values are not consistent.")

	result["snapshot_ref_valid"] = result["generated_for_snapshot_id"] == result["snapshot_id"]
	if not bool(result["snapshot_ref_valid"]):
		result["errors"].append("generated_for_snapshot_id does not match snapshot_id.")

	result["diagnostics_valid"] = _diagnostics_valid(snapshot) and _diagnostics_valid(legal_actions) and _diagnostics_valid(events)
	if not bool(result["diagnostics_valid"]):
		result["errors"].append("diagnostics blocks must contain warnings and blocking_errors arrays.")

	var resolver = CardReferenceResolverScript.new()
	var package_result = resolver.load_runtime_package(runtime_package_path)
	if not bool(package_result.get("ok", false)):
		result["errors"].append_array(package_result.get("errors", []))
		return _finalize_result(result)

	_check_snapshot_card_refs(snapshot, resolver, result)
	_check_legal_action_card_refs(legal_actions, resolver, result)
	_check_event_card_refs(events, resolver, result)

	return _finalize_result(result)


func _check_snapshot_card_refs(snapshot, resolver, result) -> void:
	var board = snapshot.get("board", {})
	if typeof(board) != TYPE_DICTIONARY:
		return
	var lanes = board.get("lanes", [])
	if typeof(lanes) == TYPE_ARRAY:
		for lane in lanes:
			if typeof(lane) == TYPE_DICTIONARY:
				_check_card_ref_array(lane.get("card_refs", []), resolver, result)
	_check_card_ref_array(board.get("currents", []), resolver, result)
	if snapshot.has("selected_card_id"):
		_check_card_id(snapshot.get("selected_card_id", ""), resolver, result)


func _check_legal_action_card_refs(legal_actions, resolver, result) -> void:
	var actions = legal_actions.get("actions", [])
	if typeof(actions) != TYPE_ARRAY:
		return
	for action in actions:
		if typeof(action) != TYPE_DICTIONARY:
			continue
		if action.has("source_card_id"):
			_check_card_id(action.get("source_card_id", ""), resolver, result)
		var target_refs = action.get("target_refs", [])
		if typeof(target_refs) == TYPE_ARRAY:
			for target_ref in target_refs:
				if typeof(target_ref) == TYPE_DICTIONARY:
					var target_type = str(target_ref.get("type", ""))
					if target_type == "card" or target_type == "card_id":
						_check_card_id(target_ref.get("id", ""), resolver, result)


func _check_event_card_refs(events, resolver, result) -> void:
	var event_rows = events.get("events", [])
	if typeof(event_rows) != TYPE_ARRAY:
		return
	for event_row in event_rows:
		if typeof(event_row) != TYPE_DICTIONARY:
			continue
		if event_row.has("card_id"):
			_check_card_id(event_row.get("card_id", ""), resolver, result)
		var refs = event_row.get("refs", {})
		if typeof(refs) == TYPE_DICTIONARY:
			for key in refs.keys():
				if _is_card_ref_key(str(key)):
					_check_card_id(refs.get(key), resolver, result)


func _check_card_ref_array(card_refs, resolver, result) -> void:
	if typeof(card_refs) != TYPE_ARRAY:
		return
	for card_ref in card_refs:
		if typeof(card_ref) == TYPE_DICTIONARY and card_ref.has("card_id"):
			_check_card_id(card_ref.get("card_id", ""), resolver, result)


func _check_card_id(card_id, resolver, result) -> void:
	result["checked_card_refs"] = int(result.get("checked_card_refs", 0)) + 1
	if not resolver.has_card(card_id):
		result["missing_card_refs"] = int(result.get("missing_card_refs", 0)) + 1
		result["errors"].append("Missing card ref: %s" % str(card_id))


func _diagnostics_valid(data) -> bool:
	if typeof(data) != TYPE_DICTIONARY:
		return false
	var diagnostics = data.get("diagnostics", null)
	if typeof(diagnostics) != TYPE_DICTIONARY:
		return false
	if typeof(diagnostics.get("warnings", null)) != TYPE_ARRAY:
		return false
	if typeof(diagnostics.get("blocking_errors", null)) != TYPE_ARRAY:
		return false
	return true


func _is_card_ref_key(key) -> bool:
	return key == "card_id" or key.ends_with("_card_id")


func _check_schema(result, actual, expected, label) -> void:
	if str(actual) != str(expected):
		result["errors"].append("%s expected %s, got %s" % [label, expected, actual])


func _collect_read_errors(result, read_result) -> void:
	if not bool(read_result.get("ok", false)):
		result["errors"].append_array(read_result.get("errors", []))


func _finalize_result(result):
	result["ok"] = result["errors"].is_empty() and int(result.get("missing_card_refs", 0)) == 0 and int(result.get("blocking_errors", 0)) == 0
	return result


func _empty_result():
	return {
		"ok": false,
		"errors": [],
		"snapshot_schema": "",
		"legal_actions_schema": "",
		"events_schema": "",
		"match_id": "",
		"snapshot_id": "",
		"generated_for_snapshot_id": "",
		"match_id_consistent": false,
		"snapshot_ref_valid": false,
		"diagnostics_valid": false,
		"checked_card_refs": 0,
		"missing_card_refs": 0,
		"warnings": 0,
		"blocking_errors": 0,
	}


func _join_path(base_path, relative_path):
	if str(base_path).ends_with("/"):
		return str(base_path) + str(relative_path)
	return str(base_path) + "/" + str(relative_path)


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
