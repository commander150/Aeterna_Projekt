extends RefCounted
class_name SchemaChecker


const EXPECTED_SCHEMA_VERSION := "sample-runtime-package-v1"


static func check_manifest(manifest: Dictionary) -> Array:
	var errors: Array = []
	if str(manifest.get("schema_version", "")) != EXPECTED_SCHEMA_VERSION:
		errors.append(
			"Unsupported schema_version: %s, expected: %s"
			% [manifest.get("schema_version", ""), EXPECTED_SCHEMA_VERSION]
		)
	if not manifest.has("files") or typeof(manifest.get("files")) != TYPE_ARRAY:
		errors.append("Manifest files field must be an array.")
	if not manifest.has("validation_summary") or typeof(manifest.get("validation_summary")) != TYPE_DICTIONARY:
		errors.append("Manifest validation_summary field must be an object.")
	return errors


static func check_manifest_files(package_path: String, manifest: Dictionary) -> Array:
	var errors: Array = []
	for file_entry in manifest.get("files", []):
		if typeof(file_entry) != TYPE_DICTIONARY:
			errors.append("Manifest files contains a non-object entry.")
			continue
		var relative_path := str(file_entry.get("path", ""))
		if relative_path.is_empty():
			errors.append("Manifest files contains an empty path.")
			continue
		var full_path := join_path(package_path, relative_path)
		if not FileAccess.file_exists(full_path):
			errors.append("Manifest file entry does not exist: %s" % full_path)
	return errors


static func manifest_is_blocking(manifest: Dictionary) -> bool:
	var summary = manifest.get("validation_summary", {})
	if typeof(summary) != TYPE_DICTIONARY:
		return true
	return bool(summary.get("blocking", true))


static func check_cards(cards: Array, lookup_registry: LookupRegistry) -> Array:
	var errors: Array = []
	var seen_ids: Dictionary = {}

	for index in range(cards.size()):
		var card = cards[index]
		if typeof(card) != TYPE_DICTIONARY:
			errors.append("Card row %d is not an object." % index)
			continue

		var card_id := str(card.get("card_id", ""))
		if card_id.is_empty():
			errors.append("Card row %d has no card_id." % index)
		elif seen_ids.has(card_id):
			errors.append("Duplicate card_id: %s" % card_id)
		else:
			seen_ids[card_id] = true

		var card_type := str(card.get("card_type", ""))
		if not lookup_registry.has_value("card_type", card_type):
			errors.append("Card %s has unknown card_type: %s" % [card_id, card_type])

		var realm := str(card.get("realm", ""))
		if not lookup_registry.has_value("realm", realm):
			errors.append("Card %s has unknown realm: %s" % [card_id, realm])

	return errors


static func check_deck_refs(deck_registry: DeckRegistry, card_registry: CardRegistry) -> Array:
	return deck_registry.validate_deck_card_refs(card_registry)


static func join_path(base_path: String, relative_path: String) -> String:
	if base_path.ends_with("/"):
		return base_path + relative_path
	return base_path + "/" + relative_path
