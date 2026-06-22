extends SceneTree


const LegalActionDebugPanelScript = preload("res://scripts/debug/legal_action_debug_panel.gd")
const CONTRACTS_PATH = "res://sample_contracts"


func _init() -> void:
	print("Running AETERNA legal action debug panel smoke test...")

	var panel = LegalActionDebugPanelScript.new()
	var result = panel.load_legal_action_view(CONTRACTS_PATH)
	var failed = false

	failed = _check_bool(result.get("ok", false), true, "legal_action_panel.ok") or failed
	failed = _check_value(result.get("schema_version", ""), "sample-legal-actions-v1", "schema_version") or failed
	failed = _check_value(result.get("match_id", ""), "sample-match-001", "match_id") or failed
	failed = _check_value(result.get("generated_for_snapshot_id", ""), "sample-snapshot-001", "generated_for_snapshot_id") or failed
	failed = _check_int(result.get("action_count", 0), 3, "actions") or failed
	failed = _check_int(result.get("enabled_count", 0), 2, "enabled") or failed
	failed = _check_int(result.get("disabled_count", 0), 1, "disabled") or failed
	failed = _check_int(result.get("resolved_cards", 0), 3, "resolved_cards") or failed
	failed = _check_int(result.get("missing_card_refs", 0), 0, "missing_card_refs") or failed
	failed = _check_int(result.get("blocking_errors", 0), 0, "blocking_errors") or failed

	print("actions: %d" % int(result.get("action_count", 0)))
	print("enabled: %d" % int(result.get("enabled_count", 0)))
	print("disabled: %d" % int(result.get("disabled_count", 0)))
	print("resolved_cards: %d" % int(result.get("resolved_cards", 0)))
	print("missing_card_refs: %d" % int(result.get("missing_card_refs", 0)))
	print("blocking_errors: %d" % int(result.get("blocking_errors", 0)))

	if failed:
		print("AETERNA legal action debug panel smoke test: FAILED")
		panel.free()
		quit(1)
		return

	print("AETERNA legal action debug panel smoke test: OK")
	panel.free()
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
