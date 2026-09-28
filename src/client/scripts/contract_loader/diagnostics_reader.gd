extends RefCounted
class_name DiagnosticsReader


static func extract_diagnostics(data) -> Array:
	if typeof(data) == TYPE_ARRAY:
		return data
	if typeof(data) == TYPE_DICTIONARY:
		return data.get("diagnostics", [])
	return []


static func summarize(data) -> Dictionary:
	var diagnostics := extract_diagnostics(data)
	var warnings := 0
	var errors := 0
	var blocking_errors := 0

	for item in diagnostics:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		if str(item.get("severity", "")) == "warning":
			warnings += 1
		if str(item.get("severity", "")) == "error":
			errors += 1
		if bool(item.get("blocking", false)):
			blocking_errors += 1

	return {
		"total": diagnostics.size(),
		"warnings": warnings,
		"errors": errors,
		"blocking_errors": blocking_errors,
	}


static func get_warning_messages(data) -> Array:
	var warnings: Array = []
	for item in extract_diagnostics(data):
		if typeof(item) == TYPE_DICTIONARY and str(item.get("severity", "")) == "warning":
			warnings.append(str(item.get("message_hu", item.get("code", "diagnostic_warning"))))
	return warnings


static func get_blocking_messages(data) -> Array:
	var errors: Array = []
	for item in extract_diagnostics(data):
		if typeof(item) == TYPE_DICTIONARY and bool(item.get("blocking", false)):
			errors.append(str(item.get("message_hu", item.get("code", "blocking_diagnostic"))))
	return errors
