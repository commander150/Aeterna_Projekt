import hashlib
import unittest

import test_canonical_validation_execution as base


execution = base.execution
rules = base.rules

POLICIES = {
    "table_identity_policy": "export_namespace_colon_table_id",
    "external_reference_identifier_policy": "namespace_colon_identifier",
}


def field_schema(
    table_id,
    field_name,
    *,
    field_id=None,
    data_type="string",
    nullable=False,
    reference_table_id=None,
    reference_field_id=None,
):
    return {
        "field_id": field_id or f"fld_{table_id}_{field_name}",
        "table_id": table_id,
        "field_name": field_name,
        "data_type": data_type,
        "required_mode": "conditional" if nullable else "always",
        "nullable": nullable,
        "null_handling": "explicit_null" if nullable else "forbidden",
        "reference_table_id": reference_table_id,
        "reference_field_id": reference_field_id,
        "status": "active",
    }


def make_rule(expression, *, target_field="reference_id", rule_id="qualified_test"):
    record = {field: "#NULL" for field in rules.RULE_RECORD_FIELDS}
    record.update(
        {
            "validation_rule_id": rule_id,
            "rule_scope_id": "cross_table",
            "target_table_id": "items",
            "target_field_id": f"fld_items_{target_field}",
            "validation_kind_id": "qualified_reference_match",
            "condition_expression": expression,
            "severity_id": "critical",
            "blocking": True,
            "error_code": "TEST_QUALIFIED_REFERENCE_INVALID",
            "message": "The qualified reference must match.",
            "validation_stage_id": "pre_export",
            "status": "active",
            "source_id": "src_test",
            "source_ref": f"ITEMS.{target_field}",
        }
    )
    result = rules.build_validation_rule_catalog(
        (rules.ValidationRuleInput(record, "registry-component"),)
    )
    if not result.is_valid:
        raise AssertionError(result.diagnostics)
    return result.catalog.rules[0]


def namespace_tables(
    *,
    items=(),
    references=({"reference_id": "known"},),
    value_registry=None,
    event_types=({"event_type_id": "evt", "event_kind_id": "resolve"},),
    schema_table_overrides=(),
    extra_tables=None,
):
    value_registry = value_registry if value_registry is not None else (
        {
            "registry_value_id": "event_kind_resolve",
            "group_id": "event_kind",
            "value_id": "resolve",
        },
        {
            "registry_value_id": "modifier_kind_add",
            "group_id": "modifier_kind",
            "value_id": "add",
        },
    )
    schema_tables = [
        {"table_id": "items", "primary_key": "item_id", "status": "active"},
        {
            "table_id": "references",
            "primary_key": "reference_id",
            "status": "active",
        },
        {
            "table_id": "value_registry",
            "primary_key": "registry_value_id",
            "status": "active",
        },
        {
            "table_id": "event_types",
            "primary_key": "event_type_id",
            "status": "active",
        },
        {
            "table_id": "schema_tables",
            "primary_key": "table_id",
            "status": "active",
        },
        {
            "table_id": "schema_fields",
            "primary_key": "field_id",
            "status": "active",
        },
    ]
    schema_tables.extend(schema_table_overrides)
    schema_fields = [
        field_schema("items", "item_id"),
        field_schema("items", "reference_id", nullable=True),
        field_schema("items", "registry_value_id", nullable=True),
        field_schema("items", "expected_value", nullable=True),
        field_schema("items", "expected_key"),
        field_schema("items", "target_registry_value_id", nullable=True),
        field_schema("items", "qualifier", nullable=True),
        field_schema("items", "target_table_id", nullable=True),
        field_schema("items", "target_record_id", nullable=True),
        field_schema("references", "reference_id"),
        field_schema("value_registry", "registry_value_id"),
        field_schema("value_registry", "group_id"),
        field_schema("value_registry", "value_id"),
        field_schema("event_types", "event_type_id"),
        field_schema("event_types", "event_kind_id"),
        field_schema("schema_tables", "table_id"),
        field_schema("schema_fields", "field_id"),
        field_schema(
            "schema_fields",
            "table_id",
            reference_table_id="schema_tables",
            reference_field_id="fld_schema_tables_table_id",
        ),
    ]
    tables = {
        "schema_tables": tuple(schema_tables),
        "schema_fields": tuple(schema_fields),
        "items": tuple(items),
        "references": tuple(references),
        "value_registry": tuple(value_registry),
        "event_types": tuple(event_types),
    }
    tables.update(extra_tables or {})
    return tables


def make_context(*, registry=None, carddatabase=None, reverse=False, policies=None):
    registry = registry or namespace_tables()
    namespaced = [("registry", registry)]
    if carddatabase is not None:
        namespaced.append(("carddatabase", carddatabase))
    if reverse:
        namespaced = [
            (
                namespace,
                {
                    table_id: tuple(reversed(records))
                    for table_id, records in reversed(tuple(tables.items()))
                },
            )
            for namespace, tables in reversed(namespaced)
        ]
    namespace_policies = {
        namespace: dict(POLICIES)
        for namespace, _ in namespaced
    }
    namespace_policies.update(policies or {})
    return execution.ValidationDataContext(
        namespaced_tables=dict(namespaced),
        component_namespaces={"registry-component": "registry"},
        namespace_policies=namespace_policies,
    )


def run(expression, items, *, target_field="reference_id", **context_options):
    context_options.setdefault("registry", namespace_tables(items=items))
    return execution.execute_qualified_reference_match_rule(
        make_rule(expression, target_field=target_field),
        make_context(**context_options),
    )


class TestQualifiedReferenceExecutor(unittest.TestCase):
    def test_false_guard_passes_without_evaluating_body(self):
        result = run(
            'when(reference_id == null,exists("missing","id",reference_id))',
            ({"item_id": "one", "reference_id": "known"},),
        )
        self.assertEqual(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(result.diagnostics, ())

    def test_simple_exists_pass_and_failure_are_distinct(self):
        expression = 'exists("references","reference_id",reference_id)'
        passed = run(
            expression,
            ({"item_id": "one", "reference_id": "known"},),
        )
        failed = run(
            expression,
            ({"item_id": "one", "reference_id": "missing"},),
        )
        self.assertEqual(passed.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(failed.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(failed.violation_count, 1)
        self.assertEqual(
            failed.diagnostics[0].code,
            execution.VALIDATION_QUALIFIED_REFERENCE_INVARIANT_FAILED,
        )

    def test_lookup_consistency_pass_and_failure(self):
        expression = (
            'lookup("references","reference_id",reference_id,'
            '"reference_id") == expected_value'
        )
        passed = run(
            expression,
            ({
                "item_id": "one",
                "reference_id": "known",
                "expected_value": "known",
            },),
        )
        failed = run(
            expression,
            ({
                "item_id": "one",
                "reference_id": "known",
                "expected_value": "other",
            },),
        )
        self.assertEqual(passed.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(failed.outcome, execution.ValidationOutcome.FAIL)

    def test_group_value_and_domain_lookup_pass_and_failure(self):
        expression = (
            'group_of(target_registry_value_id) == "event_kind" and '
            'value_of(target_registry_value_id) == '
            'lookup("event_types","event_type_id",qualifier,"event_kind_id")'
        )
        passed = run(
            expression,
            ({
                "item_id": "one",
                "target_registry_value_id": "event_kind_resolve",
                "qualifier": "evt",
            },),
            target_field="qualifier",
        )
        failed = run(
            expression,
            ({
                "item_id": "one",
                "target_registry_value_id": "modifier_kind_add",
                "qualifier": "evt",
            },),
            target_field="qualifier",
        )
        self.assertEqual(passed.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(failed.outcome, execution.ValidationOutcome.FAIL)

    def test_dynamic_primary_key_and_exists_pass(self):
        expression = (
            "exists(target_table_id,primary_key_of(target_table_id),"
            "target_record_id)"
        )
        result = run(
            expression,
            ({
                "item_id": "one",
                "target_table_id": "references",
                "target_record_id": "known",
            },),
            target_field="target_record_id",
        )
        self.assertEqual(result.outcome, execution.ValidationOutcome.PASS)

    def test_unknown_dynamic_table_and_malformed_runtime_value_fail_closed(self):
        expression = (
            "exists(target_table_id,primary_key_of(target_table_id),"
            "target_record_id)"
        )
        unknown = run(
            expression,
            ({
                "item_id": "one",
                "target_table_id": "unknown",
                "target_record_id": "known",
            },),
            target_field="target_record_id",
        )
        malformed = run(
            expression,
            ({
                "item_id": "one",
                "target_table_id": "references",
                "target_record_id": None,
            },),
            target_field="target_record_id",
        )
        self.assertEqual(unknown.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            unknown.diagnostics[0].code,
            execution.VALIDATION_QUALIFIED_REFERENCE_RESOLUTION_INVALID,
        )
        self.assertEqual(malformed.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            malformed.diagnostics[0].code,
            execution.VALIDATION_QUALIFIED_REFERENCE_TARGET_RECORD_INVALID,
        )
        self.assertTrue(
            malformed.diagnostics[0].reason.startswith(
                "expression_evaluation_error:"
            )
        )

    def test_reversed_rows_produce_identical_diagnostics(self):
        expression = 'exists("references","reference_id",reference_id)'
        items = (
            {"item_id": "two", "reference_id": "missing-b"},
            {"item_id": "one", "reference_id": "missing-a"},
        )
        registry = namespace_tables(
            items=items,
            references=(
                {"reference_id": "other-b"},
                {"reference_id": "other-a"},
            ),
        )
        rule = make_rule(expression)
        forward = execution.execute_qualified_reference_match_rule(
            rule, make_context(registry=registry)
        )
        reverse = execution.execute_qualified_reference_match_rule(
            rule, make_context(registry=registry, reverse=True)
        )
        self.assertEqual(forward, reverse)


class TestValueOfContract(unittest.TestCase):
    EXPRESSION = "value_of(registry_value_id) == expected_value"

    def execute(self, registry_value_id, expected_value, *, value_registry=None):
        registry = namespace_tables(
            items=({
                "item_id": "one",
                "registry_value_id": registry_value_id,
                "expected_value": expected_value,
            },),
            value_registry=value_registry,
        )
        return execution.execute_qualified_reference_match_rule(
            make_rule(self.EXPRESSION, target_field="registry_value_id"),
            make_context(registry=registry),
        )

    def test_full_ids_from_different_groups_resolve_exact_value(self):
        for registry_id, expected in (
            ("event_kind_resolve", "resolve"),
            ("modifier_kind_add", "add"),
        ):
            with self.subTest(registry_id=registry_id):
                result = self.execute(registry_id, expected)
                self.assertEqual(result.outcome, execution.ValidationOutcome.PASS)

    def test_unknown_short_and_alias_ids_do_not_resolve(self):
        for registry_id in ("unknown_full_id", "resolve", "feloldas"):
            with self.subTest(registry_id=registry_id):
                result = self.execute(registry_id, None)
                self.assertEqual(result.outcome, execution.ValidationOutcome.PASS)

    def test_duplicate_and_malformed_authority_fail_deterministically(self):
        duplicate = (
            {
                "registry_value_id": "event_kind_resolve",
                "group_id": "event_kind",
                "value_id": "resolve",
            },
            {
                "registry_value_id": "event_kind_resolve",
                "group_id": "other",
                "value_id": "resolve",
            },
        )
        forward = self.execute(
            "event_kind_resolve", "resolve", value_registry=duplicate
        )
        reverse = self.execute(
            "event_kind_resolve",
            "resolve",
            value_registry=tuple(reversed(duplicate)),
        )
        self.assertEqual(forward, reverse)
        self.assertEqual(
            forward.diagnostics[0].reason, "lookup_ambiguous"
        )

        for malformed in (
            ({"group_id": "event_kind", "value_id": "resolve"},),
            ({
                "registry_value_id": "event_kind_resolve",
                "group_id": "event_kind",
            },),
        ):
            with self.subTest(malformed=malformed):
                result = self.execute(
                    "event_kind_resolve", "resolve", value_registry=malformed
                )
                self.assertEqual(result.outcome, execution.ValidationOutcome.FAIL)
                self.assertEqual(
                    result.diagnostics[0].code,
                    execution.VALIDATION_QUALIFIED_REFERENCE_RESOLUTION_INVALID,
                )


class TestPrimaryKeyOfContract(unittest.TestCase):
    EXPRESSION = "primary_key_of(target_table_id) == expected_key"

    def execute(self, table_source, expected_key, *, registry=None, carddatabase=None):
        registry = registry or namespace_tables(
            items=({
                "item_id": "one",
                "target_table_id": table_source,
                "expected_key": expected_key,
            },)
        )
        return execution.execute_qualified_reference_match_rule(
            make_rule(self.EXPRESSION, target_field="target_table_id"),
            make_context(registry=registry, carddatabase=carddatabase),
        )

    def test_local_and_qualified_tables_return_field_names(self):
        local = self.execute("references", "reference_id")
        carddatabase = namespace_tables(
            extra_tables={"cards": ({"card_id": "IGN-HAM-044"},)},
            schema_table_overrides=(
                {"table_id": "cards", "primary_key": "card_id", "status": "active"},
            ),
        )
        carddatabase["schema_fields"] += (field_schema("cards", "card_id"),)
        qualified = self.execute(
            "carddatabase:cards", "card_id", carddatabase=carddatabase
        )
        self.assertEqual(local.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(qualified.outcome, execution.ValidationOutcome.PASS)
        self.assertNotEqual("card_id", "fld_cards_card_id")

    def test_schema_tables_is_the_primary_key_authority(self):
        registry = namespace_tables(
            items=({
                "item_id": "one",
                "target_table_id": "references",
                "expected_key": "reference_id",
            },)
        )
        registry.pop("references")
        result = self.execute(
            "references", "reference_id", registry=registry
        )
        self.assertEqual(result.outcome, execution.ValidationOutcome.PASS)

    def test_unknown_table_and_namespace_fail_closed(self):
        unknown_table = namespace_tables(
            items=({
                "item_id": "one",
                "target_table_id": "orphan",
                "expected_key": "orphan_id",
            },),
            extra_tables={"orphan": ()},
        )
        for table_source, registry in (
            ("orphan", unknown_table),
            ("unknown:cards", None),
        ):
            with self.subTest(table_source=table_source):
                result = self.execute(
                    table_source, "orphan_id", registry=registry
                )
                self.assertEqual(result.outcome, execution.ValidationOutcome.FAIL)
                self.assertEqual(
                    result.diagnostics[0].code,
                    execution.VALIDATION_QUALIFIED_REFERENCE_RESOLUTION_INVALID,
                )

    def test_duplicate_missing_blank_and_malformed_primary_keys_fail(self):
        cases = (
            (
                {"table_id": "references", "primary_key": "reference_id", "status": "active"},
                "primary_key_table_ambiguous",
            ),
            (
                {"table_id": "broken", "status": "active"},
                "primary_key_value_invalid",
            ),
            (
                {"table_id": "broken", "primary_key": "", "status": "active"},
                "primary_key_value_invalid",
            ),
            (
                {"table_id": "broken", "primary_key": 7, "status": "active"},
                "primary_key_value_invalid",
            ),
        )
        for override, reason in cases:
            table_source = override["table_id"]
            extra = {} if table_source == "references" else {table_source: ()}
            registry = namespace_tables(
                items=({
                    "item_id": "one",
                    "target_table_id": table_source,
                    "expected_key": "reference_id",
                },),
                schema_table_overrides=(override,),
                extra_tables=extra,
            )
            with self.subTest(reason=reason):
                result = self.execute(
                    table_source, "reference_id", registry=registry
                )
                self.assertEqual(result.outcome, execution.ValidationOutcome.FAIL)
                self.assertEqual(result.diagnostics[0].reason, reason)

    def test_reversed_duplicate_authority_is_deterministic(self):
        override = {
            "table_id": "references",
            "primary_key": "reference_id",
            "status": "active",
        }
        registry = namespace_tables(
            items=({
                "item_id": "one",
                "target_table_id": "references",
                "expected_key": "reference_id",
            },),
            schema_table_overrides=(override,),
        )
        rule = make_rule(self.EXPRESSION, target_field="target_table_id")
        forward = execution.execute_qualified_reference_match_rule(
            rule, make_context(registry=registry)
        )
        reverse = execution.execute_qualified_reference_match_rule(
            rule, make_context(registry=registry, reverse=True)
        )
        self.assertEqual(forward, reverse)


class TestQualifiedCrossNamespaceProjection(unittest.TestCase):
    def test_explicit_qualified_field_identity_routes_without_fallback(self):
        registry = namespace_tables(
            items=({
                "item_id": "one",
                "reference_id": "carddatabase:fld_cards_card_id",
                "expected_value": "carddatabase:cards",
            },)
        )
        carddatabase = namespace_tables()
        carddatabase["schema_fields"] += (
            field_schema("cards", "card_id", field_id="fld_cards_card_id"),
        )
        expression = (
            'exists("schema_fields","field_id",reference_id) and '
            'lookup("schema_fields","field_id",reference_id,"table_id") '
            "== expected_value"
        )
        result = execution.execute_qualified_reference_match_rule(
            make_rule(expression),
            make_context(registry=registry, carddatabase=carddatabase),
        )
        self.assertEqual(result.outcome, execution.ValidationOutcome.PASS)

    def test_missing_policy_or_unknown_qualified_namespace_fails_closed(self):
        for reference_id, policies, reason in (
            (
                "carddatabase:fld_cards_card_id",
                {"registry": {}},
                "qualified_key_policy_missing",
            ),
            ("unknown:fld_cards_card_id", None, "qualified_key_namespace_unknown"),
        ):
            registry = namespace_tables(
                items=({"item_id": "one", "reference_id": reference_id},)
            )
            result = execution.execute_qualified_reference_match_rule(
                make_rule('exists("schema_fields","field_id",reference_id)'),
                make_context(
                    registry=registry,
                    carddatabase=namespace_tables(),
                    policies=policies,
                ),
            )
            with self.subTest(reason=reason):
                self.assertEqual(result.outcome, execution.ValidationOutcome.FAIL)
                self.assertEqual(result.diagnostics[0].reason, reason)


class TestCurrentQualifiedReferenceCorpus(unittest.TestCase):
    EXPECTED_IDS = {
        "val_localization_registry_value_entity_exists",
        "val_migration_map_target_field_matches_table",
        "val_migration_map_target_record_exists",
        "val_value_relations_duration_qualifier_match",
        "val_value_relations_event_qualifier_match",
        "val_value_relations_modifier_qualifier_match",
        "val_value_relations_restriction_qualifier_match",
    }

    def test_all_seven_current_rules_pass_and_workbooks_remain_unchanged(self):
        before = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in base.WORKBOOKS
        }
        catalog, context = base.current_corpus_catalog_and_context()
        selected = catalog.by_kind("qualified_reference_match")
        results = tuple(
            execution.execute_qualified_reference_match_rule(rule, context)
            for rule in selected
        )
        self.assertEqual(len(selected), 7)
        self.assertEqual({rule.rule_id for rule in selected}, self.EXPECTED_IDS)
        self.assertTrue(all(rule.blocking for rule in selected))
        self.assertEqual(
            {result.rule_id: result.evaluated_record_count for result in results},
            {
                "val_localization_registry_value_entity_exists": 167,
                "val_migration_map_target_field_matches_table": 85,
                "val_migration_map_target_record_exists": 85,
                "val_value_relations_duration_qualifier_match": 59,
                "val_value_relations_event_qualifier_match": 59,
                "val_value_relations_modifier_qualifier_match": 59,
                "val_value_relations_restriction_qualifier_match": 59,
            },
        )
        self.assertTrue(
            all(result.outcome is execution.ValidationOutcome.PASS for result in results)
        )
        self.assertTrue(all(result.violation_count == 0 for result in results))
        self.assertTrue(all(result.diagnostics == () for result in results))
        after = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in base.WORKBOOKS
        }
        self.assertEqual(before, after)

    def test_current_results_are_independent_of_source_order(self):
        forward_catalog, forward_context = base.current_corpus_catalog_and_context()
        reverse_catalog, reverse_context = base.current_corpus_catalog_and_context(
            reverse=True
        )
        forward = tuple(
            execution.execute_qualified_reference_match_rule(rule, forward_context)
            for rule in forward_catalog.by_kind("qualified_reference_match")
        )
        reverse = tuple(
            execution.execute_qualified_reference_match_rule(rule, reverse_context)
            for rule in reverse_catalog.by_kind("qualified_reference_match")
        )
        self.assertEqual(forward, reverse)


if __name__ == "__main__":
    unittest.main()
