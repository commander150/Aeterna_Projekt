extends RefCounted
class_name JsonFileLoader


static func read_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {
			"ok": false,
			"data": null,
			"errors": ["Missing JSON file: %s" % path],
		}

	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return {
			"ok": false,
			"data": null,
			"errors": ["Cannot open JSON file: %s" % path],
		}

	var text := file.get_as_text()
	var parser := JSON.new()
	var parse_error := parser.parse(text)
	if parse_error != OK:
		return {
			"ok": false,
			"data": null,
			"errors": [
				"Invalid JSON in %s at line %d: %s"
				% [path, parser.get_error_line(), parser.get_error_message()]
			],
		}

	return {
		"ok": true,
		"data": parser.data,
		"errors": [],
	}
