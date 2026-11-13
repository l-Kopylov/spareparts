import pytest
from apps.catalog import dicts


def test_choices_non_empty():
    for name in ("CONDITIONS", "VEHICLE_KINDS", "PRODUCT_FORMS",
                 "SEASONS", "RIM_TYPES"):
        choices = getattr(dicts, name)
        assert choices, f"{name} пуст"
        for val, label in choices:
            assert val, f"{name}: пустое value"
            assert label, f"{name}: пустая label"


def test_part_types_unique():
    assert len(set(dicts.PART_TYPES_AUTO)) == len(dicts.PART_TYPES_AUTO)
    assert len(set(dicts.PART_TYPES_MOTO)) == len(dicts.PART_TYPES_MOTO)


def test_wheel_form_fields_covers_all_product_forms():
    pf_values = {v for v, _ in dicts.PRODUCT_FORMS}
    assert set(dicts.WHEEL_FORM_FIELDS) == pf_values


def test_wheel_form_fields_required_subset_of_show():
    for pf, conf in dicts.WHEEL_FORM_FIELDS.items():
        assert set(conf["required"]).issubset(set(conf["show"])), \
            f"{pf}: required содержит поля вне show"


def test_seasons_has_four_values():
    assert len(dicts.SEASONS) == 4
    values = {v for v, _ in dicts.SEASONS}
    assert values == {"summer", "winter_stud", "winter_studless", "allseason"}