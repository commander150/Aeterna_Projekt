extends Control
class_name EventLogDebugView


const JsonFileLoaderScript = preload("res://scripts/contract_loader/json_file_loader.gd")
const SampleContractsLoaderScript = preload("res://scripts/contract_loader/sample_contracts_loader.gd")
const CardReferenceResolverScript = preload("res://scripts/debug/card_reference_resolver.gd")

@export var contracts_path := "res://sample_contracts"
@export var runtime_package_path := "res://sample_runtime_package"

var _label: Label
var _card_resolver


func _ready() -> void:
	_label = Label.new()
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(_label)

	var result = load_event_log_view(contracts_path)
	print_debug_summary(result)
	_label.text = format_panel(result)


func load_event_log_view(base_path):
	var result = _empty_result()
	_card_resolver = CardReferenceResolverScript.new()
	var package_result = _card_resolver.load_runtime_package(runtime_package_path)
	if not bool(package_result.get("ok", false)):
		result["errors"].append_array(package_result.get("errors", []))

	var contracts_loader = SampleContractsLoaderScript.new()
	var contracts_result = contracts_loader.load_contracts(base_path)
	result["ok"] = bool(contracts_result.get("ok", false))
	result["warnings"] = int(contracts_result.get("diagnostics_summary", {}).get("warnings", 0))
	result["blocking_errors"] = int(contracts_result.get("diagnostics_summary", {}).get("blocking_errors", 0))
	result["errors"].append_array(contracts_result.get("errors", []))

	var events_result = JsonFileLoaderScript.read_json(_join_path(base_path, "sample_events.json"))
	if not bool(events_result.get("ok", false)):
		result["errors"].append_array(events_result.get("errors", []))
		result["ok"] = false
		return result

	var data = events_result.get("data", {})
	if typeof(data) != TYPE_DICTIONARY:
		result["errors"].append("sample_events.json root must be an object")
		result["ok"] = false
		return result

	var events = data.get("events", [])
	if typeof(events) != TYPE_ARRAY:
		result["errors"].append("sample_events.json events must be an array")
		result["ok"] = false
		events = []

	var sorted_events = _sorted_events_by_sequence(events)
	result["event_log"] = data
	result["schema_version"] = str(data.get("schema_version", ""))
	result["match_id"] = str(data.get("match_id", ""))
	result["events"] = sorted_events
	result["event_count"] = sorted_events.size()
	result["first_sequence"] = _get_sequence_at(sorted_events, 0)
	result["last_sequence"] = _get_sequence_at(sorted_events, sorted_events.size() - 1)
	var card_ref_counts = _count_resolved_event_cards(sorted_events)
	result["resolved_cards"] = int(card_ref_counts.get("resolved_cards", 0))
	result["missing_card_refs"] = int(card_ref_counts.get("missing_card_refs", 0))
	result["ok"] = result["ok"] and result["errors"].is_empty()
	return result


func print_debug_summary(result) -> void:
	print("AETERNA event log debug view")
	print("schema_version: %s" % str(result.get("schema_version", "")))
	print("match_id: %s" % str(result.get("match_id", "")))
	print("events: %d" % int(result.get("event_count", 0)))
	print("first_sequence: %d" % int(result.get("first_sequence", 0)))
	print("last_sequence: %d" % int(result.get("last_sequence", 0)))
	print("resolved_cards: %d" % int(result.get("resolved_cards", 0)))
	print("missing_card_refs: %d" % int(result.get("missing_card_refs", 0)))
	print("warnings: %d" % int(result.get("warnings", 0)))
	print("blocking_errors: %d" % int(result.get("blocking_errors", 0)))
	print("ok: %s" % str(result.get("ok", false)))


func format_panel(result):
	var lines = [
		"AETERNA event log debug view",
		"",
		"Basics",
		"schema_version: %s" % str(result.get("schema_version", "")),
		"match_id: %s" % str(result.get("match_id", "")),
		"",
		"Events",
	]

	var events = result.get("events", [])
	if typeof(events) == TYPE_ARRAY:
		for event_row in events:
			lines.append(_format_event(event_row))

	lines.append("")
	lines.append("Summary")
	lines.append("events: %d" % int(result.get("event_count", 0)))
	lines.append("first_sequence: %d" % int(result.get("first_sequence", 0)))
	lines.append("last_sequence: %d" % int(result.get("last_sequence", 0)))
	lines.append("resolved_cards: %d" % int(result.get("resolved_cards", 0)))
	lines.append("missing_card_refs: %d" % int(result.get("missing_card_refs", 0)))
	lines.append("warnings: %d" % int(result.get("warnings", 0)))
	lines.append("blocking_errors: %d" % int(result.get("blocking_errors", 0)))
	lines.append("ok: %s" % str(result.get("ok", false)))

	var errors = result.get("errors", [])
	if not errors.is_empty():
		lines.append("")
		lines.append("Errors")
		for error in errors:
			lines.append("- %s" % str(error))

	return "\n".join(lines)


func _format_event(event_row):
	if typeof(event_row) != TYPE_DICTIONARY:
		return "- invalid event row"

	var lines = [
		"- #%d | %s | type=%s | %s" % [
			int(event_row.get("sequence", 0)),
			str(event_row.get("event_id", "")),
			str(event_row.get("event_type", "")),
			str(event_row.get("message_hu", "")),
		]
	]
	if event_row.has("actor_player_id"):
		lines.append("  actor_player_id: %s" % str(event_row.get("actor_player_id", "")))
	if event_row.has("card_id"):
		lines.append("  card_id: %s" % _format_card_id(event_row.get("card_id", "")))
	if event_row.has("refs"):
		lines.append("  refs: %s" % _format_refs(event_row.get("refs", {})))
	return "\n".join(lines)


func _format_refs(refs):
	if typeof(refs) != TYPE_DICTIONARY:
		return "invalid_refs"
	var parts = []
	for key in refs.keys():
		if _is_card_ref_key(str(key)):
			parts.append("%s=%s" % [str(key), _format_card_id(refs.get(key))])
		else:
			parts.append("%s=%s" % [str(key), str(refs.get(key))])
	return ", ".join(parts)


func _format_card_id(card_id):
	if _card_resolver == null:
		return "UNKNOWN CARD: %s" % str(card_id)
	return _card_resolver.format_card(card_id)


func _sorted_events_by_sequence(events):
	var sorted_events = []
	if typeof(events) != TYPE_ARRAY:
		return sorted_events
	for event_row in events:
		sorted_events.append(event_row)

	var index = 1
	while index < sorted_events.size():
		var current = sorted_events[index]
		var previous_index = index - 1
		while previous_index >= 0 and _event_sequence(sorted_events[previous_index]) > _event_sequence(current):
			sorted_events[previous_index + 1] = sorted_events[previous_index]
			previous_index -= 1
		sorted_events[previous_index + 1] = current
		index += 1
	return sorted_events


func _event_sequence(event_row):
	if typeof(event_row) != TYPE_DICTIONARY:
		return 0
	return int(event_row.get("sequence", 0))


func _get_sequence_at(events, index):
	if typeof(events) != TYPE_ARRAY:
		return 0
	if index < 0 or index >= events.size():
		return 0
	return _event_sequence(events[index])


func _count_resolved_event_cards(events):
	var result = {
		"resolved_cards": 0,
		"missing_card_refs": 0,
	}
	if typeof(events) != TYPE_ARRAY:
		return result
	for event_row in events:
		if typeof(event_row) != TYPE_DICTIONARY:
			continue
		if event_row.has("card_id"):
			_count_card_id(event_row.get("card_id", ""), result)
		var refs = event_row.get("refs", {})
		if typeof(refs) == TYPE_DICTIONARY:
			for key in refs.keys():
				if _is_card_ref_key(str(key)):
					_count_card_id(refs.get(key), result)
	return result


func _is_card_ref_key(key):
	return key == "card_id" or key.ends_with("_card_id")


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
		"schema_version": "",
		"match_id": "",
		"events": [],
		"event_count": 0,
		"first_sequence": 0,
		"last_sequence": 0,
		"resolved_cards": 0,
		"missing_card_refs": 0,
		"event_log": {},
	}


func _join_path(base_path, relative_path):
	if str(base_path).ends_with("/"):
		return str(base_path) + str(relative_path)
	return str(base_path) + "/" + str(relative_path)
