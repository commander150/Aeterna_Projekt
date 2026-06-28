extends SceneTree


const JsonFileLoaderScript = preload("res://scripts/contract_loader/json_file_loader.gd")
const CardReferenceResolverScript = preload("res://scripts/debug/card_reference_resolver.gd")

const CONTRACTS_PATH = "res://debug_contracts"
const RUNTIME_PACKAGE_PATH = "res://runtime_package"
const ACTION_REQUEST_SCHEMA = "sample-action-request-v1"


func _init() -> void:
	print("Running AETERNA action request smoke test...")

	var result = _run_action_request_check(CONTRACTS_PATH, RUNTIME_PACKAGE_PATH)
	var failed = false

	failed = _check_bool(result.get("ok", false), true, "action_request.ok") or failed
	failed = _check_value(result.get("schema_version", ""), ACTION_REQUEST_SCHEMA, "schema_version") or failed
	failed = _check_value(result.get("match_id", ""), "sample-match-001", "match_id") or failed
	failed = _check_value(result.get("snapshot_id", ""), "sample-snapshot-001", "snapshot_id") or failed
	failed = _check_bool(result.get("match_id_consistent", false), true, "match_id_consistent") or failed
	failed = _check_bool(result.get("snapshot_id_valid", false), true, "snapshot_id_valid") or failed
	failed = _check_bool(result.get("based_on_action_valid", false), true, "based_on_action_valid") or failed
	failed = _check_bool(result.get("action_type_consistent", false), true, "action_type_consistent") or failed
	failed = _check_bool(result.get("diagnostics_valid", false), true, "diagnostics_valid") or failed
	failed = _check_int(result.get("missing_card_refs", 0), 0, "missing_card_refs") or failed
	failed = _check_int(result.get("blocking_errors", 0), 0, "blocking_errors") or failed

	print("schema_version: %s" % str(result.get("schema_version", "")))
	print("match_id: %s" % str(result.get("match_id", "")))
	print("snapshot_id: %s" % str(result.get("snapshot_id", "")))
	print("based_on_action_id: %s" % str(result.get("based_on_action_id", "")))
	print("based_on_action_valid: %s" % str(result.get("based_on_action_valid", false)))
	print("action_type_consistent: %s" % str(result.get("action_type_consistent", false)))
	print("checked_card_refs: %d" % int(result.get("checked_card_refs", 0)))
	print("missing_card_refs: %d" % int(result.get("missing_card_refs", 0)))
	print("warnings: %d" % int(result.get("warnings", 0)))
	print("blocking_errors: %d" % int(result.get("blocking_errors", 0)))

	if failed:
		for error in result.get("errors", []):
			push_error(str(error))
		print("AETERNA action request smoke test: FAILED")
		quit(1)
		return

	print("AETERNA action request smoke test: OK")
	quit()


func _run_action_request_check(contracts_path, runtime_package_path):
	var result = _empty_result()

	var snapshot_read = JsonFileLoaderScript.read_json(_join_path(contracts_path, "sample_snapshot.json"))
	var legal_actions_read = JsonFileLoaderScript.read_json(_join_path(contracts_path, "sample_legal_actions.json"))
	var events_read = JsonFileLoaderScript.read_json(_join_path(contracts_path, "sample_events.json"))
	var request_read = JsonFileLoaderScript.read_json(_join_path(contracts_path, "sample_action_request.json"))

	_collect_read_errors(result, snapshot_read)
	_collect_read_errors(result, legal_actions_read)
	_collect_read_errors(result, events_read)
	_collect_read_errors(result, request_read)
	if not result["errors"].is_empty():
		return _finalize_result(result)

	var snapshot = snapshot_read.get("data", {})
	var legal_actions = legal_actions_read.get("data", {})
	var events = events_read.get("data", {})
	var request = request_read.get("data", {})
	if typeof(snapshot) != TYPE_DICTIONARY or typeof(legal_actions) != TYPE_DICTIONARY or typeof(events) != TYPE_DICTIONARY or typeof(request) != TYPE_DICTIONARY:
		result["errors"].append("Sample contract roots must be objects.")
		return _finalize_result(result)

	result["schema_version"] = str(request.get("schema_version", ""))
	result["match_id"] = str(request.get("match_id", ""))
	result["snapshot_id"] = str(request.get("snapshot_id", ""))
	result["based_on_action_id"] = str(request.get("based_on_action_id", ""))

	if result["schema_version"] != ACTION_REQUEST_SCHEMA:
		result["errors"].append("schema_version expected %s, got %s" % [ACTION_REQUEST_SCHEMA, result["schema_version"]])

	result["match_id_consistent"] = result["match_id"] == str(snapshot.get("match_id", "")) and result["match_id"] == str(legal_actions.get("match_id", "")) and result["match_id"] == str(events.get("match_id", ""))
	if not bool(result["match_id_consistent"]):
		result["errors"].append("action request match_id does not match debug contracts.")

	result["snapshot_id_valid"] = result["snapshot_id"] == str(snapshot.get("snapshot_id", ""))
	if not bool(result["snapshot_id_valid"]):
		result["errors"].append("action request snapshot_id does not match sample snapshot.")

	var referenced_action = _find_action(legal_actions.get("actions", []), result["based_on_action_id"])
	result["based_on_action_valid"] = not referenced_action.is_empty()
	if not bool(result["based_on_action_valid"]):
		result["errors"].append("based_on_action_id does not reference a legal action.")

	result["action_type_consistent"] = bool(result["based_on_action_valid"]) and str(request.get("action_type", "")) == str(referenced_action.get("action_type", ""))
	if not bool(result["action_type_consistent"]):
		result["errors"].append("action request action_type does not match referenced action.")

	result["diagnostics_valid"] = _diagnostics_valid(request)
	if not bool(result["diagnostics_valid"]):
		result["errors"].append("action request diagnostics must contain warnings and blocking_errors arrays.")
	else:
		var diagnostics = request.get("diagnostics", {})
		result["warnings"] = diagnostics.get("warnings", []).size()
		result["blocking_errors"] = diagnostics.get("blocking_errors", []).size()

	var resolver = CardReferenceResolverScript.new()
	var package_result = resolver.load_runtime_package(runtime_package_path)
	if not bool(package_result.get("ok", false)):
		result["errors"].append_array(package_result.get("errors", []))
		return _finalize_result(result)

	if request.has("source_card_id"):
		_check_card_id(request.get("source_card_id", ""), resolver, result)
	_check_selected_targets(request.get("selected_targets", []), resolver, result)

	return _finalize_result(result)


func _find_action(actions, action_id):
	if typeof(actions) != TYPE_ARRAY:
		return {}
	for action in actions:
		if typeof(action) == TYPE_DICTIONARY and str(action.get("action_id", "")) == str(action_id):
			return action
	return {}


func _check_selected_targets(selected_targets, resolver, result) -> void:
	if typeof(selected_targets) != TYPE_ARRAY:
		result["errors"].append("selected_targets must be an array.")
		return
	for target in selected_targets:
		if typeof(target) != TYPE_DICTIONARY:
			continue
		var target_type = str(target.get("type", ""))
		if target_type == "card" or target_type == "card_id":
			_check_card_id(target.get("id", ""), resolver, result)


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
		"schema_version": "",
		"match_id": "",
		"snapshot_id": "",
		"based_on_action_id": "",
		"match_id_consistent": false,
		"snapshot_id_valid": false,
		"based_on_action_valid": false,
		"action_type_consistent": false,
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
