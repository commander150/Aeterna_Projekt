extends RefCounted
class_name JsonlFileLoader


static func read_jsonl(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {
			"ok": false,
			"rows": [],
			"errors": ["Missing JSONL file: %s" % path],
		}

	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return {
			"ok": false,
			"rows": [],
			"errors": ["Cannot open JSONL file: %s" % path],
		}

	var rows: Array = []
	var errors: Array = []
	var line_number := 0
	while not file.eof_reached():
		var line := file.get_line()
		line_number += 1
		if line.strip_edges().is_empty():
			continue

		var parser := JSON.new()
		var parse_error := parser.parse(line)
		if parse_error != OK:
			errors.append(
				"Invalid JSONL in %s at line %d: %s"
				% [path, line_number, parser.get_error_message()]
			)
			continue
		if typeof(parser.data) != TYPE_DICTIONARY:
			errors.append("JSONL row is not an object in %s at line %d" % [path, line_number])
			continue
		rows.append(parser.data)

	return {
		"ok": errors.is_empty(),
		"rows": rows,
		"errors": errors,
	}
