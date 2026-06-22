extends SceneTree


const EventLogDebugViewScript = preload("res://scripts/debug/event_log_debug_view.gd")
const CONTRACTS_PATH = "res://sample_contracts"


func _init() -> void:
	print("Running AETERNA event log debug view smoke test...")

	var view = EventLogDebugViewScript.new()
	var result = view.load_event_log_view(CONTRACTS_PATH)
	var failed = false

	failed = _check_bool(result.get("ok", false), true, "event_log_view.ok") or failed
	failed = _check_value(result.get("schema_version", ""), "sample-events-v1", "schema_version") or failed
	failed = _check_value(result.get("match_id", ""), "sample-match-001", "match_id") or failed
	failed = _check_int(result.get("event_count", 0), 4, "events") or failed
	failed = _check_int(result.get("first_sequence", 0), 1, "first_sequence") or failed
	failed = _check_int(result.get("last_sequence", 0), 4, "last_sequence") or failed
	failed = _check_int(result.get("resolved_cards", 0), 2, "resolved_cards") or failed
	failed = _check_int(result.get("missing_card_refs", 0), 0, "missing_card_refs") or failed
	failed = _check_int(result.get("blocking_errors", 0), 0, "blocking_errors") or failed

	print("events: %d" % int(result.get("event_count", 0)))
	print("first_sequence: %d" % int(result.get("first_sequence", 0)))
	print("last_sequence: %d" % int(result.get("last_sequence", 0)))
	print("resolved_cards: %d" % int(result.get("resolved_cards", 0)))
	print("missing_card_refs: %d" % int(result.get("missing_card_refs", 0)))
	print("blocking_errors: %d" % int(result.get("blocking_errors", 0)))

	if failed:
		print("AETERNA event log debug view smoke test: FAILED")
		view.free()
		quit(1)
		return

	print("AETERNA event log debug view smoke test: OK")
	view.free()
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
