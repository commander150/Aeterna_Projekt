extends Control
class_name UnifiedDebugDashboard


const SnapshotViewerScript = preload("res://scripts/debug/snapshot_viewer.gd")
const LegalActionDebugPanelScript = preload("res://scripts/debug/legal_action_debug_panel.gd")
const EventLogDebugViewScript = preload("res://scripts/debug/event_log_debug_view.gd")

@export var contracts_path := "res://debug_contracts"

var _label: Label
var _snapshot_viewer
var _legal_action_panel
var _event_log_view


func _ready() -> void:
	_label = Label.new()
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(_label)

	var result = load_dashboard(contracts_path)
	print_debug_summary(result)
	_label.text = format_dashboard(result)


func _notification(what) -> void:
	if what == NOTIFICATION_PREDELETE:
		free_loaded_views()


func load_dashboard(base_path):
	free_loaded_views()
	_snapshot_viewer = SnapshotViewerScript.new()
	_legal_action_panel = LegalActionDebugPanelScript.new()
	_event_log_view = EventLogDebugViewScript.new()

	var snapshot = _snapshot_viewer.load_snapshot_view(base_path)
	var legal_actions = _legal_action_panel.load_legal_action_view(base_path)
	var event_log = _event_log_view.load_event_log_view(base_path)

	var result = {
		"snapshot": snapshot,
		"legal_actions": legal_actions,
		"event_log": event_log,
		"resolved_cards": _sum_ints([
			snapshot.get("resolved_cards", 0),
			legal_actions.get("resolved_cards", 0),
			event_log.get("resolved_cards", 0),
		]),
		"missing_card_refs": _sum_ints([
			snapshot.get("missing_card_refs", 0),
			legal_actions.get("missing_card_refs", 0),
			event_log.get("missing_card_refs", 0),
		]),
		"warnings": _max_ints([
			snapshot.get("warnings", 0),
			legal_actions.get("warnings", 0),
			event_log.get("warnings", 0),
		]),
		"blocking_errors": _max_ints([
			snapshot.get("blocking_errors", 0),
			legal_actions.get("blocking_errors", 0),
			event_log.get("blocking_errors", 0),
		]),
		"ok": false,
	}
	result["ok"] = bool(snapshot.get("ok", false)) and bool(legal_actions.get("ok", false)) and bool(event_log.get("ok", false))
	return result


func free_loaded_views() -> void:
	if _snapshot_viewer != null and is_instance_valid(_snapshot_viewer):
		_snapshot_viewer.free()
	if _legal_action_panel != null and is_instance_valid(_legal_action_panel):
		_legal_action_panel.free()
	if _event_log_view != null and is_instance_valid(_event_log_view):
		_event_log_view.free()
	_snapshot_viewer = null
	_legal_action_panel = null
	_event_log_view = null


func print_debug_summary(result) -> void:
	var snapshot = result.get("snapshot", {})
	var legal_actions = result.get("legal_actions", {})
	var event_log = result.get("event_log", {})

	print("AETERNA unified debug dashboard")
	print("match_id: %s" % str(snapshot.get("match_id", "")))
	print("snapshot_id: %s" % str(snapshot.get("snapshot_id", "")))
	print("players: %d" % _count_players(snapshot.get("players", [])))
	print("board_entries: %d" % int(snapshot.get("board_entries", 0)))
	print("actions: %d" % int(legal_actions.get("action_count", 0)))
	print("enabled: %d" % int(legal_actions.get("enabled_count", 0)))
	print("disabled: %d" % int(legal_actions.get("disabled_count", 0)))
	print("events: %d" % int(event_log.get("event_count", 0)))
	print("first_sequence: %d" % int(event_log.get("first_sequence", 0)))
	print("last_sequence: %d" % int(event_log.get("last_sequence", 0)))
	print("resolved_cards: %d" % int(result.get("resolved_cards", 0)))
	print("missing_card_refs: %d" % int(result.get("missing_card_refs", 0)))
	print("warnings: %d" % int(result.get("warnings", 0)))
	print("blocking_errors: %d" % int(result.get("blocking_errors", 0)))
	print("ok: %s" % str(result.get("ok", false)))


func format_dashboard(result):
	var snapshot = result.get("snapshot", {})
	var legal_actions = result.get("legal_actions", {})
	var event_log = result.get("event_log", {})

	var lines = [
		"AETERNA unified debug dashboard",
		"",
		"Snapshot summary",
		"match_id: %s" % str(snapshot.get("match_id", "")),
		"snapshot_id: %s" % str(snapshot.get("snapshot_id", "")),
		"active_player_id: %s" % str(snapshot.get("active_player_id", "")),
		"turn_number: %d" % int(snapshot.get("turn_number", 0)),
		"phase: %s" % str(snapshot.get("phase", "")),
		"players: %d" % _count_players(snapshot.get("players", [])),
		"board_entries: %d" % int(snapshot.get("board_entries", 0)),
		"resolved_cards: %d" % int(snapshot.get("resolved_cards", 0)),
		"missing_card_refs: %d" % int(snapshot.get("missing_card_refs", 0)),
		"",
		"Legal actions",
		"actions: %d" % int(legal_actions.get("action_count", 0)),
		"enabled: %d" % int(legal_actions.get("enabled_count", 0)),
		"disabled: %d" % int(legal_actions.get("disabled_count", 0)),
		"resolved_cards: %d" % int(legal_actions.get("resolved_cards", 0)),
		"missing_card_refs: %d" % int(legal_actions.get("missing_card_refs", 0)),
	]

	var actions = legal_actions.get("actions", [])
	if typeof(actions) == TYPE_ARRAY:
		for action in actions:
			lines.append(_format_action_row(action))

	lines.append("")
	lines.append("Event log")
	lines.append("events: %d" % int(event_log.get("event_count", 0)))
	lines.append("first_sequence: %d" % int(event_log.get("first_sequence", 0)))
	lines.append("last_sequence: %d" % int(event_log.get("last_sequence", 0)))
	lines.append("resolved_cards: %d" % int(event_log.get("resolved_cards", 0)))
	lines.append("missing_card_refs: %d" % int(event_log.get("missing_card_refs", 0)))

	var events = event_log.get("events", [])
	if typeof(events) == TYPE_ARRAY:
		for event_row in events:
			lines.append(_format_event_row(event_row))

	lines.append("")
	lines.append("Diagnostics")
	lines.append("warnings: %d" % int(result.get("warnings", 0)))
	lines.append("blocking_errors: %d" % int(result.get("blocking_errors", 0)))
	lines.append("ok: %s" % str(result.get("ok", false)))

	return "\n".join(lines)


func _format_action_row(action):
	if typeof(action) != TYPE_DICTIONARY:
		return "- invalid action row"
	var status = "disabled"
	if bool(action.get("enabled", false)):
		status = "enabled"
	var parts = [
		"- %s | %s | %s | %s" % [
			str(action.get("action_id", "")),
			str(action.get("action_type", "")),
			status,
			str(action.get("label_hu", "")),
		]
	]
	if action.has("source_card_id"):
		parts.append("source=%s" % _legal_action_panel._format_card_id(action.get("source_card_id", "")))
	if action.has("disabled_reason"):
		parts.append("disabled_reason=%s" % str(action.get("disabled_reason", "")))
	return " | ".join(parts)


func _format_event_row(event_row):
	if typeof(event_row) != TYPE_DICTIONARY:
		return "- invalid event row"
	var parts = [
		"- #%d | %s | %s" % [
			int(event_row.get("sequence", 0)),
			str(event_row.get("event_type", "")),
			str(event_row.get("message_hu", "")),
		]
	]
	if event_row.has("card_id"):
		parts.append("card=%s" % _event_log_view._format_card_id(event_row.get("card_id", "")))
	return " | ".join(parts)


func _count_players(players):
	if typeof(players) == TYPE_ARRAY:
		return players.size()
	return 0


func _sum_ints(values):
	var total = 0
	for value in values:
		total += int(value)
	return total


func _max_ints(values):
	var highest = 0
	for value in values:
		if int(value) > highest:
			highest = int(value)
	return highest
