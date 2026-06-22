extends SceneTree


const UnifiedDebugDashboardScript = preload("res://scripts/debug/unified_debug_dashboard.gd")
const CONTRACTS_PATH = "res://sample_contracts"


func _init() -> void:
	print("Running AETERNA unified debug dashboard smoke test...")

	var dashboard = UnifiedDebugDashboardScript.new()
	var result = dashboard.load_dashboard(CONTRACTS_PATH)
	var snapshot = result.get("snapshot", {})
	var legal_actions = result.get("legal_actions", {})
	var event_log = result.get("event_log", {})
	var failed = false

	failed = _check_bool(snapshot.get("ok", false), true, "snapshot.ok") or failed
	failed = _check_bool(legal_actions.get("ok", false), true, "legal_actions.ok") or failed
	failed = _check_bool(event_log.get("ok", false), true, "event_log.ok") or failed
	failed = _check_value(snapshot.get("match_id", ""), "sample-match-001", "match_id") or failed
	failed = _check_value(snapshot.get("snapshot_id", ""), "sample-snapshot-001", "snapshot_id") or failed
	failed = _check_int(dashboard._count_players(snapshot.get("players", [])), 2, "players") or failed
	failed = _check_int(snapshot.get("board_entries", 0), 2, "board_entries") or failed
	failed = _check_int(legal_actions.get("action_count", 0), 3, "actions") or failed
	failed = _check_int(legal_actions.get("enabled_count", 0), 2, "enabled") or failed
	failed = _check_int(legal_actions.get("disabled_count", 0), 1, "disabled") or failed
	failed = _check_int(event_log.get("event_count", 0), 4, "events") or failed
	failed = _check_int(event_log.get("first_sequence", 0), 1, "first_sequence") or failed
	failed = _check_int(event_log.get("last_sequence", 0), 4, "last_sequence") or failed
	failed = _check_int(result.get("resolved_cards", 0), 7, "resolved_cards") or failed
	failed = _check_int(result.get("missing_card_refs", 0), 0, "missing_card_refs") or failed
	failed = _check_int(result.get("blocking_errors", 0), 0, "blocking_errors") or failed
	failed = _check_bool(result.get("ok", false), true, "dashboard.ok") or failed

	print("snapshot: OK")
	print("legal_actions: OK")
	print("event_log: OK")
	print("resolved_cards: %d" % int(result.get("resolved_cards", 0)))
	print("missing_card_refs: %d" % int(result.get("missing_card_refs", 0)))
	print("blocking_errors: %d" % int(result.get("blocking_errors", 0)))

	if failed:
		print("AETERNA unified debug dashboard smoke test: FAILED")
		dashboard.free_loaded_views()
		dashboard.free()
		quit(1)
		return

	print("AETERNA unified debug dashboard smoke test: OK")
	dashboard.free_loaded_views()
	dashboard.free()
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
