import importlib.util
import sys
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "canonical_export"
    / "canonical_package_set.py"
)


def load_package_set_module():
    spec = importlib.util.spec_from_file_location("canonical_package_set", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


package_set = load_package_set_module()

HASH_0 = "sha256:" + "0" * 64
HASH_1 = "sha256:" + "1" * 64
HASH_2 = "sha256:" + "2" * 64
HASH_3 = "sha256:" + "3" * 64
HASH_4 = "sha256:" + "4" * 64
HASH_5 = "sha256:" + "5" * 64


def dependency(
    target_component_id="registry",
    target_component_kind="REGISTRY",
    target_package_id="aeterna_registry",
    minimum_schema_version="0.5.1",
    minimum_data_version="0.16.7",
    bound_component_identity=HASH_1,
    bound_content_hash=HASH_2,
):
    return package_set.DependencyDescriptor(
        target_component_id=target_component_id,
        target_component_kind=target_component_kind,
        target_package_id=target_package_id,
        minimum_schema_version=minimum_schema_version,
        minimum_data_version=minimum_data_version,
        bound_component_identity=bound_component_identity,
        bound_content_hash=bound_content_hash,
    )


def component(
    component_id="registry",
    component_kind="REGISTRY",
    package_id="aeterna_registry",
    schema_version="0.5.1",
    data_version="0.16.7",
    content_hash=HASH_2,
    manifest_file="manifest.json",
    manifest_hash=HASH_3,
    dependencies=(),
    consumer_requirement="required",
):
    descriptor = package_set.ComponentDescriptor(
        component_format_version=package_set.COMPONENT_FORMAT_VERSION,
        component_identity=HASH_0,
        component_id=component_id,
        component_kind=component_kind,
        package_id=package_id,
        schema_version=schema_version,
        data_version=data_version,
        content_hash=content_hash,
        manifest_file=manifest_file,
        manifest_hash=manifest_hash,
        dependencies=tuple(dependencies),
        consumer_requirement=consumer_requirement,
    )
    return replace(
        descriptor,
        component_identity=package_set.compute_component_identity(descriptor),
    )


def manifest(components, profile_id="production-v1", policy_id="strict-v1", ledger_hash=HASH_5):
    value = package_set.PackageSet(
        package_set_format_version=package_set.PACKAGE_SET_FORMAT_VERSION,
        package_set_id=HASH_0,
        package_set_profile_id=profile_id,
        profile_contract_hash=HASH_4,
        validation_policy_id=policy_id,
        components=tuple(components),
        validation_ledger_file="validation/ledger.json",
        validation_ledger_hash=ledger_hash,
    )
    return replace(value, package_set_id=package_set.compute_package_set_identity(value))


def diagnostic_codes(result):
    return {item.code for item in result.diagnostics}


class TestCanonicalSerialization(unittest.TestCase):
    def test_dict_insertion_order_does_not_change_bytes(self):
        first = {"z": 2, "a": 1}
        second = {"a": 1, "z": 2}

        self.assertEqual(
            package_set.canonical_json_bytes(first),
            package_set.canonical_json_bytes(second),
        )
        self.assertEqual(package_set.canonical_json_bytes(first), b'{"a":1,"z":2}')

    def test_unicode_is_stable_utf8_without_bom_or_ascii_escaping(self):
        actual = package_set.canonical_json_bytes({"name": "Őrző / Æterna"})

        self.assertEqual(actual, '{"name":"Őrző / Æterna"}'.encode("utf-8"))
        self.assertFalse(actual.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\\u", actual)

    def test_supported_scalars_are_deterministic(self):
        value = {"none": None, "false": False, "integer": -12, "text": "x", "true": True}

        self.assertEqual(
            package_set.canonical_json_bytes(value),
            b'{"false":false,"integer":-12,"none":null,"text":"x","true":true}',
        )

    def test_list_is_accepted_and_bool_is_not_serialized_as_integer(self):
        self.assertEqual(
            package_set.canonical_json_bytes([True, False, 1, 0]),
            b"[true,false,1,0]",
        )

    def test_signed_int64_boundaries_have_literal_portable_encoding(self):
        self.assertEqual(
            package_set.canonical_json_bytes(
                [package_set.INT64_MIN, package_set.INT64_MAX]
            ),
            b"[-9223372036854775808,9223372036854775807]",
        )

    def test_integers_outside_signed_int64_are_rejected(self):
        for value in (package_set.INT64_MIN - 1, package_set.INT64_MAX + 1):
            with self.subTest(value=value):
                with self.assertRaises(package_set.PackageSetContractError) as raised:
                    package_set.canonical_json_bytes(value)
                self.assertEqual(
                    raised.exception.diagnostics[0].code,
                    "PACKAGE_CANONICAL_VALUE_UNSUPPORTED",
                )

    def test_repeated_serialization_is_byte_identical(self):
        value = {"items": [3, 2, 1], "nested": {"b": "B", "a": "A"}}

        outputs = [package_set.canonical_json_bytes(value) for _ in range(10)]

        self.assertEqual(len(set(outputs)), 1)

    def test_unsupported_values_are_rejected_with_structured_diagnostic(self):
        cyclic = []
        cyclic.append(cyclic)
        cases = [
            (1, 2),
            {"set"},
            frozenset({"frozen"}),
            b"bytes",
            bytearray(b"bytes"),
            Decimal("1"),
            1.0,
            object(),
            {1: "non-string key"},
            cyclic,
        ]
        for value in cases:
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaises(package_set.PackageSetContractError) as raised:
                    package_set.canonical_json_bytes(value)
                self.assertEqual(
                    raised.exception.diagnostics[0].code,
                    "PACKAGE_CANONICAL_VALUE_UNSUPPORTED",
                )

    def test_composed_and_decomposed_unicode_are_not_normalized(self):
        composed = package_set.canonical_json_bytes("\u00e9")
        decomposed = package_set.canonical_json_bytes("e\u0301")

        self.assertEqual(composed, b'"\xc3\xa9"')
        self.assertEqual(decomposed, b'"e\xcc\x81"')
        self.assertNotEqual(composed, decomposed)
        self.assertNotEqual(
            package_set.sha256_bytes(composed),
            package_set.sha256_bytes(decomposed),
        )

    def test_lone_surrogates_are_rejected_with_structured_diagnostic(self):
        for value in ("\ud800", "\udfff"):
            with self.subTest(code_point=f"U+{ord(value):04X}"):
                with self.assertRaises(package_set.PackageSetContractError) as raised:
                    package_set.canonical_json_bytes(value)
                self.assertEqual(
                    raised.exception.diagnostics[0].code,
                    "PACKAGE_CANONICAL_VALUE_UNSUPPORTED",
                )

    def test_non_bmp_scalar_has_literal_utf8_encoding(self):
        self.assertEqual(
            package_set.canonical_json_bytes("\U00010000"),
            b'"\xf0\x90\x80\x80"',
        )

    def test_identity_sorting_uses_explicit_utf8_bytes(self):
        bmp = "\ue000"
        non_bmp = "\U00010000"

        self.assertEqual(
            sorted((non_bmp, bmp), key=package_set.utf8_sort_key),
            [bmp, non_bmp],
        )
        self.assertEqual(package_set.utf8_sort_key(bmp).hex(), "ee8080")
        self.assertEqual(package_set.utf8_sort_key(non_bmp).hex(), "f0908080")
        self.assertEqual(
            sorted((non_bmp, bmp), key=lambda value: value.encode("utf-16-be")),
            [non_bmp, bmp],
        )

    def test_object_keys_use_utf8_byte_order(self):
        self.assertEqual(
            package_set.canonical_json_bytes({"\U00010000": 2, "\ue000": 1}),
            b'{"\xee\x80\x80":1,"\xf0\x90\x80\x80":2}',
        )

    def test_json_control_character_representation_is_literal(self):
        value = '"\\\b\f\n\r\t\x00\x1f'

        actual = package_set.canonical_json_bytes(value)

        self.assertEqual(actual, b'"\\"\\\\\\b\\f\\n\\r\\t\\u0000\\u001f"')
        self.assertFalse(actual.startswith(b"\xef\xbb\xbf"))
        self.assertFalse(actual.endswith(b"\n"))


class TestHashAndPathContract(unittest.TestCase):
    def test_sha256_has_prefixed_lowercase_known_value(self):
        self.assertEqual(
            package_set.sha256_bytes(b"abc"),
            "sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )

    def test_one_byte_change_changes_hash(self):
        self.assertNotEqual(package_set.sha256_bytes(b"a"), package_set.sha256_bytes(b"b"))

    def test_safe_posix_path_is_accepted(self):
        self.assertEqual(package_set.canonical_relative_path("cards/data.json"), "cards/data.json")

    def test_windows_separators_are_canonicalized(self):
        self.assertEqual(package_set.canonical_relative_path(r"cards\data.json"), "cards/data.json")

        first = package_set.FileDescriptor("cards/data.json", 2, HASH_1, "table")
        second = package_set.FileDescriptor(r"cards\data.json", 2, HASH_1, "table")
        self.assertEqual(
            package_set.compute_component_content_hash([first]),
            package_set.compute_component_content_hash([second]),
        )

    def test_absolute_paths_are_rejected(self):
        for path in ("/root/data.json", r"C:\root\data.json", r"\\server\data.json"):
            with self.subTest(path=path):
                with self.assertRaises(package_set.PackageSetContractError):
                    package_set.canonical_relative_path(path)

    def test_parent_traversal_is_rejected(self):
        for path in ("../x", "cards/../x", r"cards\..\x"):
            with self.subTest(path=path):
                with self.assertRaises(package_set.PackageSetContractError):
                    package_set.canonical_relative_path(path)

    def test_empty_path_is_rejected(self):
        for path in ("", "   "):
            with self.subTest(path=path):
                with self.assertRaises(package_set.PackageSetContractError):
                    package_set.canonical_relative_path(path)

    def test_content_hash_sorts_paths_and_includes_role(self):
        first = package_set.FileDescriptor("z.json", 2, HASH_1, "table")
        second = package_set.FileDescriptor("a.json", 3, HASH_2, "manifest")

        self.assertEqual(
            package_set.compute_component_content_hash([first, second]),
            package_set.compute_component_content_hash([second, first]),
        )
        changed_role = replace(first, role="manifest")
        self.assertNotEqual(
            package_set.compute_component_content_hash([first, second]),
            package_set.compute_component_content_hash([changed_role, second]),
        )

    def test_invalid_file_shape_and_duplicate_canonical_path_are_rejected(self):
        cases = (
            package_set.FileDescriptor("data.json", -1, HASH_1, "table"),
            package_set.FileDescriptor("data.json", 1, "bad-hash", "table"),
            package_set.FileDescriptor("data.json", 1, HASH_1, ""),
        )
        for descriptor in cases:
            with self.subTest(descriptor=descriptor):
                with self.assertRaises(package_set.PackageSetContractError):
                    package_set.compute_component_content_hash((descriptor,))

        duplicate_a = package_set.FileDescriptor("cards/data.json", 1, HASH_1, "table")
        duplicate_b = package_set.FileDescriptor(r"cards\data.json", 1, HASH_1, "table")
        with self.assertRaises(package_set.PackageSetContractError):
            package_set.compute_component_content_hash((duplicate_a, duplicate_b))


class TestComponentIdentity(unittest.TestCase):
    def test_same_input_has_same_identity(self):
        value = component()
        self.assertEqual(
            package_set.compute_component_identity(value),
            package_set.compute_component_identity(value),
        )

    def test_content_hash_changes_identity(self):
        first = component(content_hash=HASH_1)
        second = component(content_hash=HASH_2)
        self.assertNotEqual(first.component_identity, second.component_identity)

    def test_dependency_binding_changes_identity(self):
        first = component(component_id="cards", dependencies=(dependency(bound_content_hash=HASH_1),))
        second = component(component_id="cards", dependencies=(dependency(bound_content_hash=HASH_2),))
        self.assertNotEqual(first.component_identity, second.component_identity)

    def test_dependency_input_order_does_not_change_identity(self):
        registry = dependency()
        localization = dependency(
            target_component_id="localization",
            target_component_kind="LOCALIZATION",
            target_package_id="aeterna_localization",
            bound_component_identity=HASH_3,
            bound_content_hash=HASH_4,
        )
        first = component(component_id="cards", dependencies=(registry, localization))
        second = component(component_id="cards", dependencies=(localization, registry))
        self.assertEqual(first.component_identity, second.component_identity)

    def test_stored_component_identity_is_not_its_own_preimage(self):
        value = component()
        tampered_stored_value = replace(value, component_identity=HASH_5)

        self.assertEqual(
            package_set.compute_component_identity(value),
            package_set.compute_component_identity(tampered_stored_value),
        )
        self.assertNotIn(b'"component_identity"', package_set.component_identity_preimage(value))

    def test_tampered_stored_component_identity_fails_verification(self):
        value = component()
        valid_set = manifest((value,))
        tampered = replace(
            valid_set,
            components=(replace(value, component_identity=HASH_5),),
        )

        result = package_set.verify_package_set(tampered)

        self.assertFalse(result.is_valid)
        self.assertIn("PACKAGE_HASH_COMPONENT_MISMATCH", diagnostic_codes(result))

    def test_tampered_content_or_dependency_binding_fails_verification(self):
        cards = component(component_id="cards", dependencies=(dependency(),))
        valid_set = manifest((cards,))

        tampered_content = replace(cards, content_hash=HASH_4)
        tampered_dependency = replace(
            cards,
            dependencies=(replace(cards.dependencies[0], bound_content_hash=HASH_5),),
        )
        for tampered_component in (tampered_content, tampered_dependency):
            with self.subTest(tampered_component=tampered_component):
                value = replace(valid_set, components=(tampered_component,))
                self.assertIn(
                    "PACKAGE_HASH_COMPONENT_MISMATCH",
                    diagnostic_codes(package_set.verify_package_set(value)),
                )


class TestPackageSetIdentity(unittest.TestCase):
    def test_component_input_order_does_not_change_set_id(self):
        registry = component()
        cards = component(
            component_id="cards",
            component_kind="CARDDATABASE",
            package_id="aeterna_carddatabase",
            dependencies=(dependency(bound_component_identity=registry.component_identity),),
        )

        self.assertEqual(
            manifest((registry, cards)).package_set_id,
            manifest((cards, registry)).package_set_id,
        )

    def test_component_content_or_identity_change_changes_set_id(self):
        first = component(content_hash=HASH_1)
        second = component(content_hash=HASH_2)

        self.assertNotEqual(manifest((first,)).package_set_id, manifest((second,)).package_set_id)

        tampered_identity = replace(first, component_identity=HASH_5)
        self.assertNotEqual(
            manifest((first,)).package_set_id,
            manifest((tampered_identity,)).package_set_id,
        )

    def test_profile_change_changes_set_id(self):
        value = component()
        self.assertNotEqual(
            manifest((value,), profile_id="profile-a").package_set_id,
            manifest((value,), profile_id="profile-b").package_set_id,
        )

    def test_validation_policy_change_changes_set_id(self):
        value = component()
        self.assertNotEqual(
            manifest((value,), policy_id="policy-a").package_set_id,
            manifest((value,), policy_id="policy-b").package_set_id,
        )

    def test_ledger_hash_change_changes_set_id(self):
        value = component()
        self.assertNotEqual(
            manifest((value,), ledger_hash=HASH_1).package_set_id,
            manifest((value,), ledger_hash=HASH_2).package_set_id,
        )

    def test_provenance_metadata_is_absent_from_identity_contract(self):
        value = manifest((component(),))
        preimage = package_set.package_set_identity_preimage(value)

        for forbidden in (b"timestamp", b"compiler", b"git_commit", b"absolute_source_path", b"build_note"):
            self.assertNotIn(forbidden, preimage)

    def test_stored_set_id_is_not_preimage_and_tamper_fails_verification(self):
        value = manifest((component(),))
        tampered = replace(value, package_set_id=HASH_0)

        self.assertEqual(
            package_set.compute_package_set_identity(value),
            package_set.compute_package_set_identity(tampered),
        )
        self.assertNotIn(b'"package_set_id"', package_set.package_set_identity_preimage(value))
        self.assertIn("PACKAGE_SET_ID_MISMATCH", diagnostic_codes(package_set.verify_package_set(tampered)))


class TestPackageSetVerifier(unittest.TestCase):
    def test_empty_component_set_is_rejected(self):
        value = package_set.PackageSet(
            package_set_format_version=package_set.PACKAGE_SET_FORMAT_VERSION,
            package_set_id=HASH_0,
            package_set_profile_id="production-v1",
            profile_contract_hash=HASH_1,
            validation_policy_id="strict-v1",
            components=(),
            validation_ledger_file="ledger.json",
            validation_ledger_hash=HASH_2,
        )
        self.assertIn("PACKAGE_SET_MANIFEST_INCOMPLETE", diagnostic_codes(package_set.verify_package_set(value)))

    def test_duplicate_component_id_is_rejected(self):
        first = component(component_kind="REGISTRY")
        second = component(component_kind="CARDDATABASE", package_id="other")
        value = manifest((first, second))
        self.assertIn("PACKAGE_COMPONENT_DUPLICATE_ID", diagnostic_codes(package_set.verify_package_set(value)))

    def test_invalid_consumer_requirement_is_rejected(self):
        valid = component()
        invalid = replace(valid, consumer_requirement="yes")
        value = replace(manifest((valid,)), components=(invalid,))
        self.assertIn("PACKAGE_COMPONENT_MANIFEST_INVALID", diagnostic_codes(package_set.verify_package_set(value)))

    def test_malformed_hash_is_rejected(self):
        invalid = replace(component(), content_hash="ABC")
        value = replace(manifest((component(),)), components=(invalid,))
        self.assertIn("PACKAGE_HASH_COMPONENT_MISMATCH", diagnostic_codes(package_set.verify_package_set(value)))

    def test_unsafe_manifest_path_is_rejected(self):
        invalid = replace(component(), manifest_file="../manifest.json")
        value = replace(manifest((component(),)), components=(invalid,))
        self.assertIn("PACKAGE_COMPONENT_MANIFEST_INVALID", diagnostic_codes(package_set.verify_package_set(value)))

    def test_full_source_tuple_dependency_is_rejected_as_self(self):
        valid = component()
        invalid = replace(valid, dependencies=(dependency(target_component_id="registry"),))
        value = replace(manifest((valid,)), components=(invalid,))
        result = package_set.verify_package_set(value)
        self.assertTrue(any(item.context.get("reason") == "self_dependency" for item in result.diagnostics))

    def test_full_target_tuple_duplicate_dependency_is_rejected(self):
        target = dependency()
        valid = component(component_id="cards", component_kind="CARDDATABASE")
        invalid = replace(valid, dependencies=(target, target))
        value = replace(manifest((valid,)), components=(invalid,))
        result = package_set.verify_package_set(value)
        self.assertTrue(any(item.context.get("reason") == "duplicate_dependency_target" for item in result.diagnostics))

    def test_same_dependency_kind_and_id_in_different_packages_is_not_duplicate(self):
        first = dependency(target_package_id="package-a")
        second = dependency(target_package_id="package-b")
        cards = component(
            component_id="cards",
            component_kind="CARDDATABASE",
            package_id="cards-package",
            dependencies=(first, second),
        )

        result = package_set.verify_package_set(manifest((cards,)))

        self.assertTrue(result.is_valid)
        self.assertFalse(
            any(
                item.context.get("reason") == "duplicate_dependency_target"
                for item in result.diagnostics
            )
        )

    def test_same_component_id_with_other_package_and_kind_is_not_self(self):
        other = dependency(
            target_component_id="registry",
            target_component_kind="CARDDATABASE",
            target_package_id="other-package",
        )
        registry = component(dependencies=(other,))

        result = package_set.verify_package_set(manifest((registry,)))

        self.assertTrue(result.is_valid)
        self.assertFalse(
            any(
                item.context.get("reason") == "self_dependency"
                for item in result.diagnostics
            )
        )

    def test_unsupported_schema_is_rejected(self):
        value = replace(manifest((component(),)), package_set_format_version="2")
        self.assertIn("PACKAGE_SET_SCHEMA_UNSUPPORTED", diagnostic_codes(package_set.verify_package_set(value)))

    def test_empty_component_fields_and_dependency_target_are_rejected(self):
        valid = component(component_id="cards", component_kind="CARDDATABASE")
        empty_id = replace(valid, component_id="")
        empty_target = replace(
            valid,
            dependencies=(dependency(target_component_id=""),),
        )
        empty_id_result = package_set.verify_package_set(
            replace(manifest((valid,)), components=(empty_id,))
        )
        empty_target_result = package_set.verify_package_set(
            replace(manifest((valid,)), components=(empty_target,))
        )

        self.assertIn("PACKAGE_COMPONENT_MANIFEST_INVALID", diagnostic_codes(empty_id_result))
        self.assertIn("PACKAGE_DEPENDENCY_TARGET_MISSING", diagnostic_codes(empty_target_result))

    def test_malformed_dependency_binding_is_rejected(self):
        valid = component(component_id="cards", component_kind="CARDDATABASE")
        invalid = replace(
            valid,
            dependencies=(dependency(bound_component_identity="bad-hash"),),
        )
        value = replace(manifest((valid,)), components=(invalid,))
        self.assertIn(
            "PACKAGE_DEPENDENCY_IDENTITY_MISMATCH",
            diagnostic_codes(package_set.verify_package_set(value)),
        )

    def test_diagnostics_are_identical_for_reversed_invalid_components(self):
        valid_a = component(
            component_id="a",
            component_kind="CARDDATABASE",
            package_id="package-a",
        )
        valid_b = component(
            component_id="b",
            component_kind="REGISTRY",
            package_id="package-b",
        )
        invalid_a = replace(valid_a, content_hash="bad-hash")
        invalid_b = replace(valid_b, manifest_file="../manifest.json")
        base = manifest((valid_a, valid_b))

        first = package_set.verify_package_set(
            replace(base, components=(invalid_a, invalid_b))
        )
        second = package_set.verify_package_set(
            replace(base, components=(invalid_b, invalid_a))
        )

        self.assertFalse(first.is_valid)
        self.assertEqual(first.diagnostics, second.diagnostics)

    def test_duplicate_component_diagnostics_do_not_depend_on_tied_sort_order(self):
        first_component = component(
            component_id="duplicate",
            component_kind="REGISTRY",
            package_id="package-a",
            content_hash=HASH_1,
        )
        second_component = component(
            component_id="duplicate",
            component_kind="REGISTRY",
            package_id="package-b",
            content_hash=HASH_2,
        )
        base = manifest((first_component, second_component))

        first = package_set.verify_package_set(
            replace(base, components=(first_component, second_component))
        )
        second = package_set.verify_package_set(
            replace(base, components=(second_component, first_component))
        )

        self.assertEqual(first.diagnostics, second.diagnostics)
        self.assertEqual(
            diagnostic_codes(first),
            {"PACKAGE_COMPONENT_DUPLICATE_ID"},
        )

    def test_malformed_runtime_field_types_return_only_structured_diagnostics(self):
        valid = component(
            component_id="cards",
            component_kind="CARDDATABASE",
            package_id="cards-package",
        )
        malformed_dependency = replace(
            dependency(),
            target_component_id=object(),
            target_component_kind=[],
        )
        malformed_component = replace(
            valid,
            component_id="\ud800",
            component_kind=[],
            consumer_requirement=object(),
            dependencies=(malformed_dependency, object()),
        )
        value = replace(
            manifest((valid,)),
            components=(malformed_component, object()),
        )

        result = package_set.verify_package_set(value)

        self.assertFalse(result.is_valid)
        self.assertTrue(result.diagnostics)
        canonical_scalar_types = (type(None), bool, int, str)
        for diagnostic in result.diagnostics:
            self.assertIn(type(diagnostic.code), canonical_scalar_types)
            self.assertIn(type(diagnostic.message), canonical_scalar_types)
            for context_value in diagnostic.context.values():
                self.assertIn(type(context_value), canonical_scalar_types)
                if type(context_value) is str:
                    self.assertFalse(
                        any(
                            0xD800 <= ord(character) <= 0xDFFF
                            for character in context_value
                        )
                    )

    def test_arbitrary_stored_identity_types_do_not_escape_verifier(self):
        valid_component = component()
        valid_set = manifest((valid_component,))
        cases = (
            replace(
                valid_set,
                components=(replace(valid_component, component_identity=object()),),
            ),
            replace(valid_set, package_set_id=object()),
        )

        for value in cases:
            with self.subTest(value=value):
                result = package_set.verify_package_set(value)
                self.assertFalse(result.is_valid)
                self.assertTrue(result.diagnostics)


class TestExtensibilityAndPolicy(unittest.TestCase):
    def test_three_component_set_is_deterministic_and_not_two_kind_hardcoded(self):
        registry = component()
        cards = component(component_id="cards", component_kind="CARDDATABASE", package_id="cards")
        presentation = component(
            component_id="presentation",
            component_kind="PRESENTATION",
            package_id="presentation",
            consumer_requirement="optional",
        )

        first = manifest((registry, cards, presentation))
        second = manifest((presentation, registry, cards))

        self.assertEqual(first.package_set_id, second.package_set_id)
        self.assertTrue(package_set.verify_package_set(first).is_valid)

    def test_all_known_unknown_requirement_states_are_explicit(self):
        cases = {
            ("REGISTRY", "required"): "known_required",
            ("REGISTRY", "optional"): "known_optional",
            ("FUTURE", "required"): "unknown_required",
            ("FUTURE", "optional"): "unknown_optional",
        }
        for (kind, requirement), expected in cases.items():
            with self.subTest(kind=kind, requirement=requirement):
                value = component(
                    component_id=f"{kind}-{requirement}",
                    component_kind=kind,
                    consumer_requirement=requirement,
                )
                self.assertEqual(package_set.classify_component_support(value), expected)

    def test_unknown_optional_kind_is_accepted(self):
        value = component(component_kind="PRESENTATION", consumer_requirement="optional")
        self.assertTrue(package_set.verify_package_set(manifest((value,))).is_valid)

    def test_unknown_required_kind_is_blocked_by_consumer_policy(self):
        value = component(component_kind="FUTURE", consumer_requirement="required")
        result = package_set.verify_package_set(manifest((value,)))
        self.assertIn("PACKAGE_COMPONENT_REQUIRED_KIND_UNSUPPORTED", diagnostic_codes(result))


class TestGoldenConformanceVectors(unittest.TestCase):
    REGISTRY_IDENTITY = "sha256:6c9a1ae90644c70feff2d442fc41a6a385ea22a4ce92fadefded91ea05d0545b"
    CARDS_IDENTITY = "sha256:b63c2258aa8b5771bb40cf5340ec6887bd380fe069ad28b388997719cdcf554a"
    PRESENTATION_IDENTITY = "sha256:1f0d788af9889d57cb0c6b66b6b26f268c6ea14c8c03e1a7b7549a968964c945"
    VECTOR_A_SET_ID = "sha256:7f773fc01f00f5a5d46ff51acdec52e4bb0eb47e23ae9e3705da7380c57d198e"
    VECTOR_B_SET_ID = "sha256:ebd1dc36dfe377b91b99feb7ac196b6e74af31094f8a8ae83b05bc92e3ceceaa"

    def _vectors(self):
        registry = component(content_hash=HASH_1, manifest_hash=HASH_2)
        cards = component(
            component_id="cards",
            component_kind="CARDDATABASE",
            package_id="aeterna_carddatabase",
            schema_version="0.7.0",
            data_version="0.19.2",
            content_hash=HASH_3,
            manifest_file="carddatabase/manifest.json",
            manifest_hash=HASH_4,
            dependencies=(
                dependency(
                    bound_component_identity=registry.component_identity,
                    bound_content_hash=registry.content_hash,
                ),
            ),
        )
        presentation = component(
            component_id="presentation",
            component_kind="PRESENTATION",
            package_id="aeterna_presentation",
            schema_version="1.0.0",
            data_version="1.0.0",
            content_hash=HASH_4,
            manifest_file="presentation/manifest.json",
            manifest_hash=HASH_5,
            dependencies=(
                dependency(
                    target_component_id="cards",
                    target_component_kind="CARDDATABASE",
                    target_package_id="aeterna_carddatabase",
                    minimum_schema_version="0.7.0",
                    minimum_data_version="0.19.2",
                    bound_component_identity=cards.component_identity,
                    bound_content_hash=cards.content_hash,
                ),
            ),
            consumer_requirement="optional",
        )
        return registry, cards, presentation

    def test_vector_a_registry_and_carddatabase(self):
        registry, cards, _ = self._vectors()
        value = manifest((registry, cards))

        self.assertEqual(registry.component_identity, self.REGISTRY_IDENTITY)
        self.assertEqual(cards.component_identity, self.CARDS_IDENTITY)
        self.assertEqual(value.package_set_id, self.VECTOR_A_SET_ID)
        self.assertTrue(package_set.verify_package_set(value).is_valid)

    def test_vector_b_adds_fictional_optional_presentation_component(self):
        registry, cards, presentation = self._vectors()
        value = manifest((presentation, cards, registry))

        self.assertEqual(presentation.component_identity, self.PRESENTATION_IDENTITY)
        self.assertEqual(value.package_set_id, self.VECTOR_B_SET_ID)
        self.assertTrue(package_set.verify_package_set(value).is_valid)

    def test_vector_registry_component_preimage_is_literal_and_portable(self):
        registry, _, _ = self._vectors()
        expected = (
            b'{"component_format_version":"1","component_id":"registry",'
            b'"component_kind":"REGISTRY","content_hash":"sha256:' + b"1" * 64
            + b'","data_version":"0.16.7","dependencies":[],"domain":'
            b'"aeterna-component-v1","package_id":"aeterna_registry",'
            b'"schema_version":"0.5.1"}'
        )

        self.assertEqual(package_set.component_identity_preimage(registry), expected)


if __name__ == "__main__":
    unittest.main()
