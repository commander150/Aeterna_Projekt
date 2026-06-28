extends Control
class_name SnapshotViewer


const JsonFileLoaderScript = preload("res://scripts/contract_loader/json_file_loader.gd")
const DebugContractsLoaderScript = preload("res://scripts/contract_loader/debug_contracts_loader.gd")
const CardReferenceResolverScript = preload("res://scripts/debug/card_reference_resolver.gd")

@export var contracts_path := "res://debug_contracts"
@export var runtime_package_path := "res://runtime_package"

var _label: Label
var _card_resolver


func _ready() -> void:
	_label = Label.new()
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(_label)

	var result = load_snapshot_view(contracts_path)
	print_debug_summary(result)
	_label.text = format_snapshot(result)


func load_snapshot_view(base_path):
	var result = _empty_result()
	_card_resolver = CardReferenceResolverScript.new()
	var package_result = _card_resolver.load_runtime_package(runtime_package_path)
	if not bool(package_result.get("ok", false)):
		result["errors"].append_array(package_result.get("errors", []))

	var contracts_loader = DebugContractsLoaderScript.new()
	var contracts_result = contracts_loader.load_contracts(base_path)
	result["ok"] = bool(contracts_result.get("ok", false))
	result["warnings"] = int(contracts_result.get("diagnostics_summary", {}).get("warnings", 0))
	result["blocking_errors"] = int(contracts_result.get("diagnostics_summary", {}).get("blocking_errors", 0))
	result["errors"].append_array(contracts_result.get("errors", []))

	var snapshot_result = JsonFileLoaderScript.read_json(_join_path(base_path, "sample_snapshot.json"))
	if not bool(snapshot_result.get("ok", false)):
		result["errors"].append_array(snapshot_result.get("errors", []))
		result["ok"] = false
		return result

	var snapshot = snapshot_result.get("data", {})
	if typeof(snapshot) != TYPE_DICTIONARY:
		result["errors"].append("sample_snapshot.json root must be an object")
		result["ok"] = false
		return result

	result["snapshot"] = snapshot
	result["match_id"] = str(snapshot.get("match_id", ""))
	result["snapshot_id"] = str(snapshot.get("snapshot_id", ""))
	result["active_player_id"] = str(snapshot.get("active_player_id", ""))
	result["turn_number"] = int(snapshot.get("turn_number", 0))
	result["phase"] = str(snapshot.get("phase", ""))
	result["players"] = snapshot.get("players", [])
	result["board"] = snapshot.get("board", {})
	result["board_entries"] = _count_board_entries(result["board"])
	var card_ref_counts = _count_resolved_board_cards(result["board"])
	result["resolved_cards"] = int(card_ref_counts.get("resolved_cards", 0))
	result["missing_card_refs"] = int(card_ref_counts.get("missing_card_refs", 0))
	return result


func print_debug_summary(result) -> void:
	print("AETERNA snapshot viewer debug")
	print("match_id: %s" % str(result.get("match_id", "")))
	print("snapshot_id: %s" % str(result.get("snapshot_id", "")))
	print("active_player_id: %s" % str(result.get("active_player_id", "")))
	print("turn_number: %d" % int(result.get("turn_number", 0)))
	print("phase: %s" % str(result.get("phase", "")))
	print("players: %d" % _count_players(result.get("players", [])))
	print("board_entries: %d" % int(result.get("board_entries", 0)))
	print("resolved_cards: %d" % int(result.get("resolved_cards", 0)))
	print("missing_card_refs: %d" % int(result.get("missing_card_refs", 0)))
	print("warnings: %d" % int(result.get("warnings", 0)))
	print("blocking_errors: %d" % int(result.get("blocking_errors", 0)))
	print("ok: %s" % str(result.get("ok", false)))


func format_snapshot(result):
	var lines = [
		"AETERNA snapshot viewer debug",
		"",
		"Match",
		"match_id: %s" % str(result.get("match_id", "")),
		"snapshot_id: %s" % str(result.get("snapshot_id", "")),
		"active_player_id: %s" % str(result.get("active_player_id", "")),
		"turn_number: %d" % int(result.get("turn_number", 0)),
		"phase: %s" % str(result.get("phase", "")),
		"",
		"Players",
	]

	var players = result.get("players", [])
	if typeof(players) == TYPE_ARRAY:
		for player in players:
			lines.append(_format_player(player))

	lines.append("")
	lines.append("Board")
	lines.append_array(_format_board(result.get("board", {})))
	lines.append("")
	lines.append("Diagnostics")
	lines.append("warnings: %d" % int(result.get("warnings", 0)))
	lines.append("blocking_errors: %d" % int(result.get("blocking_errors", 0)))
	lines.append("resolved_cards: %d" % int(result.get("resolved_cards", 0)))
	lines.append("missing_card_refs: %d" % int(result.get("missing_card_refs", 0)))
	lines.append("ok: %s" % str(result.get("ok", false)))

	var errors = result.get("errors", [])
	if not errors.is_empty():
		lines.append("")
		lines.append("Errors")
		for error in errors:
			lines.append("- %s" % str(error))

	return "\n".join(lines)


func _format_player(player):
	if typeof(player) != TYPE_DICTIONARY:
		return "- invalid player row"
	return "- %s | %s | realm=%s | seals=%d | deck=%d | hand=%d | wellspring=%d | void=%d" % [
		str(player.get("player_id", "")),
		str(player.get("display_name", "")),
		str(player.get("realm", "")),
		int(player.get("seals_remaining", 0)),
		int(player.get("deck_count", 0)),
		int(player.get("hand_count", 0)),
		int(player.get("wellspring_count", 0)),
		int(player.get("void_count", 0)),
	]


func _format_board(board):
	var lines = []
	if typeof(board) != TYPE_DICTIONARY:
		return ["- invalid board object"]

	var lanes = board.get("lanes", [])
	lines.append("lanes:")
	if typeof(lanes) == TYPE_ARRAY:
		for lane in lanes:
			lines.append(_format_lane(lane))
	else:
		lines.append("- invalid lanes value")

	var currents = board.get("currents", [])
	lines.append("currents:")
	if typeof(currents) == TYPE_ARRAY:
		for current in currents:
			lines.append("  - %s" % _format_card_ref(current))
	else:
		lines.append("- invalid currents value")
	return lines


func _format_lane(lane):
	if typeof(lane) != TYPE_DICTIONARY:
		return "- invalid lane row"
	var parts = [
		"- lane_id=%s" % str(lane.get("lane_id", "")),
		"controller=%s" % str(lane.get("controller_player_id", "")),
	]
	var card_refs = lane.get("card_refs", [])
	var refs = []
	if typeof(card_refs) == TYPE_ARRAY:
		for card_ref in card_refs:
			refs.append(_format_card_ref(card_ref))
	parts.append("cards=[%s]" % ", ".join(refs))
	return " | ".join(parts)


func _format_card_ref(card_ref):
	if typeof(card_ref) != TYPE_DICTIONARY:
		return "invalid_card_ref"
	var parts = [
		"card=%s" % _format_card_id(card_ref.get("card_id", "")),
		"instance_id=%s" % str(card_ref.get("instance_id", "")),
		"zone=%s" % str(card_ref.get("zone", "")),
	]
	if card_ref.has("owner_player_id"):
		parts.append("owner=%s" % str(card_ref.get("owner_player_id", "")))
	if card_ref.has("position"):
		parts.append("position=%s" % str(card_ref.get("position", "")))
	return " ".join(parts)


func _format_card_id(card_id):
	if _card_resolver == null:
		return "UNKNOWN CARD: %s" % str(card_id)
	return _card_resolver.format_card(card_id)


func _count_players(players):
	if typeof(players) == TYPE_ARRAY:
		return players.size()
	return 0


func _count_board_entries(board):
	if typeof(board) != TYPE_DICTIONARY:
		return 0
	var count = 0
	var lanes = board.get("lanes", [])
	if typeof(lanes) == TYPE_ARRAY:
		for lane in lanes:
			if typeof(lane) == TYPE_DICTIONARY:
				var card_refs = lane.get("card_refs", [])
				if typeof(card_refs) == TYPE_ARRAY:
					count += card_refs.size()
	var currents = board.get("currents", [])
	if typeof(currents) == TYPE_ARRAY:
		count += currents.size()
	return count


func _count_resolved_board_cards(board):
	var result = {
		"resolved_cards": 0,
		"missing_card_refs": 0,
	}
	if typeof(board) != TYPE_DICTIONARY:
		return result

	var lanes = board.get("lanes", [])
	if typeof(lanes) == TYPE_ARRAY:
		for lane in lanes:
			if typeof(lane) == TYPE_DICTIONARY:
				var card_refs = lane.get("card_refs", [])
				_count_card_ref_array(card_refs, result)

	var currents = board.get("currents", [])
	_count_card_ref_array(currents, result)
	return result


func _count_card_ref_array(card_refs, result):
	if typeof(card_refs) != TYPE_ARRAY:
		return
	for card_ref in card_refs:
		if typeof(card_ref) == TYPE_DICTIONARY and card_ref.has("card_id"):
			_count_card_id(card_ref.get("card_id", ""), result)


func _count_card_id(card_id, result):
	if _card_resolver != null and _card_resolver.has_card(card_id):
		result["resolved_cards"] = int(result.get("resolved_cards", 0)) + 1
	else:
		result["missing_card_refs"] = int(result.get("missing_card_refs", 0)) + 1


func _empty_result():
	return {
		"ok": false,
		"errors": [],
		"warnings": 0,
		"blocking_errors": 0,
		"match_id": "",
		"snapshot_id": "",
		"active_player_id": "",
		"turn_number": 0,
		"phase": "",
		"players": [],
		"board": {},
		"board_entries": 0,
		"resolved_cards": 0,
		"missing_card_refs": 0,
		"snapshot": {},
	}


func _join_path(base_path, relative_path):
	if str(base_path).ends_with("/"):
		return str(base_path) + str(relative_path)
	return str(base_path) + "/" + str(relative_path)
