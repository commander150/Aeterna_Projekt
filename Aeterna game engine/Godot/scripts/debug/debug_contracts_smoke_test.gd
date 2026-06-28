extends SceneTree


const DebugContractsLoaderScript = preload("res://scripts/contract_loader/debug_contracts_loader.gd")
const CONTRACTS_PATH = "res://debug_contracts"


func _init() -> void:
	print("Running AETERNA debug contracts smoke test...")

	var loader = DebugContractsLoaderScript.new()
	var result = loader.load_contracts(CONTRACTS_PATH)
	var counts = result.get("loaded_counts", {})
	var diagnostics = result.get("diagnostics_summary", {})
	var failed = false

	failed = _check_bool(result.get("ok", false), true, "contracts_result.ok") or failed
	failed = _check_value(result.get("snapshot_schema", ""), "sample-snapshot-v1", "snapshot_schema") or failed
	failed = _check_value(result.get("legal_actions_schema", ""), "sample-legal-actions-v1", "legal_actions_schema") or failed
	failed = _check_value(result.get("events_schema", ""), "sample-events-v1", "events_schema") or failed
	failed = _check_int(counts.get("actions", 0), 3, "actions") or failed
	failed = _check_int(counts.get("events", 0), 4, "events") or failed
	failed = _check_int(diagnostics.get("blocking_errors", 0), 0, "blocking_errors") or failed

	print("snapshot_schema: %s" % str(result.get("snapshot_schema", "")))
	print("legal_actions_schema: %s" % str(result.get("legal_actions_schema", "")))
	print("events_schema: %s" % str(result.get("events_schema", "")))
	print("actions: %d" % int(counts.get("actions", 0)))
	print("events: %d" % int(counts.get("events", 0)))
	print("blocking_errors: %d" % int(diagnostics.get("blocking_errors", 0)))

	if failed:
		print("AETERNA debug contracts smoke test: FAILED")
		quit(1)
		return

	print("AETERNA debug contracts smoke test: OK")
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
