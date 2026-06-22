extends RefCounted
class_name CardRegistry


var _cards: Array = []
var _cards_by_id: Dictionary = {}


func load_cards(cards: Array) -> Array:
	_cards = []
	_cards_by_id = {}
	var errors: Array = []

	for index in range(cards.size()):
		var card = cards[index]
		if typeof(card) != TYPE_DICTIONARY:
			errors.append("Card row %d is not an object." % index)
			continue

		var card_id := str(card.get("card_id", ""))
		if card_id.is_empty():
			errors.append("Card row %d has no card_id." % index)
			continue
		if _cards_by_id.has(card_id):
			errors.append("Duplicate card_id: %s" % card_id)
			continue

		_cards.append(card)
		_cards_by_id[card_id] = card

	return errors


func has_card(card_id: String) -> bool:
	return _cards_by_id.has(card_id)


func get_card(card_id: String) -> Dictionary:
	return _cards_by_id.get(card_id, {})


func get_all_cards() -> Array:
	return _cards.duplicate(true)


func get_cards_by_type(card_type: String) -> Array:
	var result: Array = []
	for card in _cards:
		if str(card.get("card_type", "")) == card_type:
			result.append(card)
	return result


func get_cards_by_realm(realm: String) -> Array:
	var result: Array = []
	for card in _cards:
		if str(card.get("realm", "")) == realm:
			result.append(card)
	return result


func count() -> int:
	return _cards.size()
