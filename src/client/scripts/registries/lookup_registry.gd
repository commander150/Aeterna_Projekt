extends RefCounted
class_name LookupRegistry


var _groups: Dictionary = {}


func load_lookups(lookups) -> Array:
	_groups = {}
	var rows := _extract_rows(lookups)
	var errors: Array = []

	for index in range(rows.size()):
		var row = rows[index]
		if typeof(row) != TYPE_DICTIONARY:
			errors.append("Lookup row %d is not an object." % index)
			continue

		var group := str(row.get("lookup_group", ""))
		var value := str(row.get("value", ""))
		if group.is_empty() or value.is_empty():
			errors.append("Lookup row %d has no lookup_group or value." % index)
			continue

		if not _groups.has(group):
			_groups[group] = {}
		_groups[group][value] = row

	return errors


func has_value(lookup_group: String, value: String) -> bool:
	return _groups.has(lookup_group) and _groups[lookup_group].has(value)


func get_label_hu(lookup_group: String, value: String) -> String:
	if not has_value(lookup_group, value):
		return ""
	return str(_groups[lookup_group][value].get("label_hu", value))


func get_values_for_group(lookup_group: String) -> Array:
	if not _groups.has(lookup_group):
		return []
	return _groups[lookup_group].keys()


func get_group_count() -> int:
	return _groups.size()


func _extract_rows(lookups) -> Array:
	if typeof(lookups) == TYPE_ARRAY:
		return lookups
	if typeof(lookups) == TYPE_DICTIONARY:
		return lookups.get("lookups", [])
	return []
