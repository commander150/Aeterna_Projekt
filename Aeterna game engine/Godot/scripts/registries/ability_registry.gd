extends RefCounted
class_name AbilityRegistry


var _modules: Array = []
var _modules_by_id: Dictionary = {}


func load_ability_registry(data) -> Array:
	_modules = []
	_modules_by_id = {}
	var rows := _extract_rows(data)
	var errors: Array = []

	for index in range(rows.size()):
		var module = rows[index]
		if typeof(module) != TYPE_DICTIONARY:
			errors.append("Ability module row %d is not an object." % index)
			continue

		var module_id := str(module.get("module_id", ""))
		if module_id.is_empty():
			errors.append("Ability module row %d has no module_id." % index)
			continue
		if _modules_by_id.has(module_id):
			errors.append("Duplicate ability module_id: %s" % module_id)
			continue

		_modules.append(module)
		_modules_by_id[module_id] = module

	return errors


func has_module(module_id: String) -> bool:
	return _modules_by_id.has(module_id)


func get_module(module_id: String) -> Dictionary:
	return _modules_by_id.get(module_id, {})


func get_modules_by_support_status(status: String) -> Array:
	var result: Array = []
	for module in _modules:
		if str(module.get("support_status", "")) == status:
			result.append(module)
	return result


func get_all_modules() -> Array:
	return _modules.duplicate(true)


func count() -> int:
	return _modules.size()


func _extract_rows(data) -> Array:
	if typeof(data) == TYPE_ARRAY:
		return data
	if typeof(data) == TYPE_DICTIONARY:
		return data.get("ability_registry", [])
	return []
