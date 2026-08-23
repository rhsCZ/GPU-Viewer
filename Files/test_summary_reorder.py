import SummaryViewer


def test_move_card_in_registry():
    registry = [
        ("system", object()),
        ("vulkan", object()),
        ("opengl", object()),
    ]

    result = SummaryViewer._move_card_in_registry(registry, "opengl", "system")

    assert [card_id for card_id, _ in result] == ["opengl", "system", "vulkan"]
