extends RefCounted
class_name DeckRegistry


var _decks: Array = []
var _decks_by_id: Dictionary = {}


func load_decks(decks: Array) -> Array:
	_decks = []
	_decks_by_id = {}
	var errors: Array = []

	for index in range(decks.size()):
		var deck = decks[index]
		if typeof(deck) != TYPE_DICTIONARY:
			errors.append("Deck row %d is not an object." % index)
			continue

		var deck_id := str(deck.get("deck_id", ""))
		if deck_id.is_empty():
			errors.append("Deck row %d has no deck_id." % index)
			continue
		if _decks_by_id.has(deck_id):
			errors.append("Duplicate deck_id: %s" % deck_id)
			continue

		_decks.append(deck)
		_decks_by_id[deck_id] = deck

	return errors


func has_deck(deck_id: String) -> bool:
	return _decks_by_id.has(deck_id)


func get_deck(deck_id: String) -> Dictionary:
	return _decks_by_id.get(deck_id, {})


func validate_deck_card_refs(card_registry: CardRegistry) -> Array:
	var errors: Array = []
	for deck in _decks:
		var deck_id := str(deck.get("deck_id", ""))
		var entries = deck.get("card_entries", [])
		if typeof(entries) != TYPE_ARRAY:
			errors.append("Deck %s card_entries is not an array." % deck_id)
			continue

		for entry in entries:
			if typeof(entry) != TYPE_DICTIONARY:
				errors.append("Deck %s has a non-object card entry." % deck_id)
				continue
			var card_id := str(entry.get("card_id", ""))
			if not card_registry.has_card(card_id):
				errors.append("Deck %s references missing card_id: %s" % [deck_id, card_id])

	return errors


func get_all_decks() -> Array:
	return _decks.duplicate(true)


func count() -> int:
	return _decks.size()
