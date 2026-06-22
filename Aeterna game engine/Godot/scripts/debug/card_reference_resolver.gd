extends RefCounted
class_name CardReferenceResolver


const RuntimePackageLoaderScript = preload("res://scripts/contract_loader/runtime_package_loader.gd")

var _card_registry
var _load_result = {}


func load_runtime_package(package_path):
	var loader = RuntimePackageLoaderScript.new()
	_load_result = loader.load_package(package_path)
	if bool(_load_result.get("ok", false)):
		_card_registry = loader.card_registry
	else:
		_card_registry = null
	return _load_result


func can_resolve() -> bool:
	return _card_registry != null


func has_card(card_id) -> bool:
	if _card_registry == null:
		return false
	return _card_registry.has_card(str(card_id))


func format_card(card_id) -> String:
	var card_id_text = str(card_id)
	if card_id_text.is_empty():
		return "UNKNOWN CARD: <empty>"
	if _card_registry == null or not _card_registry.has_card(card_id_text):
		return "UNKNOWN CARD: %s" % card_id_text

	var card = _card_registry.get_card(card_id_text)
	var name_hu = str(card.get("name_hu", ""))
	var card_type = str(card.get("card_type", ""))
	var realm = str(card.get("realm", ""))
	var clan = str(card.get("clan", ""))
	var realm_text = realm
	if not clan.is_empty():
		realm_text = "%s / %s" % [realm, clan]
	return "%s - %s [%s, %s]" % [card_id_text, name_hu, card_type, realm_text]
