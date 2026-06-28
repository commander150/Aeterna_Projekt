extends SceneTree


const SnapshotViewerScript = preload("res://scripts/debug/snapshot_viewer.gd")
const CONTRACTS_PATH = "res://debug_contracts"


func _init() -> void:
	print("Running AETERNA snapshot viewer smoke test...")

	var viewer = SnapshotViewerScript.new()
	var result = viewer.load_snapshot_view(CONTRACTS_PATH)
	var failed = false

	failed = _check_bool(result.get("ok", false), true, "snapshot_viewer.ok") or failed
	failed = _check_value(result.get("match_id", ""), "sample-match-001", "match_id") or failed
	failed = _check_value(result.get("snapshot_id", ""), "sample-snapshot-001", "snapshot_id") or failed
	failed = _check_int(viewer._count_players(result.get("players", [])), 2, "players") or failed
	failed = _check_int(result.get("resolved_cards", 0), 2, "resolved_cards") or failed
	failed = _check_int(result.get("missing_card_refs", 0), 0, "missing_card_refs") or failed
	failed = _check_int(result.get("blocking_errors", 0), 0, "blocking_errors") or failed

	print("match_id: %s" % str(result.get("match_id", "")))
	print("snapshot_id: %s" % str(result.get("snapshot_id", "")))
	print("players: %d" % viewer._count_players(result.get("players", [])))
	print("resolved_cards: %d" % int(result.get("resolved_cards", 0)))
	print("missing_card_refs: %d" % int(result.get("missing_card_refs", 0)))
	print("blocking_errors: %d" % int(result.get("blocking_errors", 0)))

	if failed:
		print("AETERNA snapshot viewer smoke test: FAILED")
		viewer.free()
		quit(1)
		return

	print("AETERNA snapshot viewer smoke test: OK")
	viewer.free()
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
