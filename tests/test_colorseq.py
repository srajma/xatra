from xatra.colorseq import Color, LinearColorSequence, RotatingColorSequence, atlas_color, rgb_to_oklch


def test_named_colors_use_hsl_ordering():
    assert Color.named("red").hex == "#ff0000"
    assert Color.named("blue").hex == "#0000ff"
    assert Color.named("white").hex == "#ffffff"


def test_hex_round_trip_is_exact():
    for value in ["#336699", "#ff0000", "#0e4ca1", "#fff"]:
        expected = value if len(value) == 7 else "#ffffff"
        assert Color.hex(value).hex == expected


def test_hsl_components_are_hue_saturation_lightness():
    h, s, l = Color.hex("#336699").hsl
    assert abs(h - 210 / 360) < 1e-6
    assert abs(s - 0.5) < 1e-6
    assert abs(l - 0.4) < 1e-6


def test_default_sequence_is_deterministic_and_distinct():
    a = LinearColorSequence()
    b = LinearColorSequence()
    first = [a[i].hex for i in range(12)]
    assert first == [b[i].hex for i in range(12)]
    assert len(set(first)) == 12


def test_default_palette_has_even_visual_weight():
    lightness = [rgb_to_oklch(*atlas_color(i).rgb)[0] for i in range(20)]
    assert min(lightness) > 0.65
    assert max(lightness) < 0.9


def test_seeded_sequence_steps_in_hsl():
    seq = LinearColorSequence(colors=[Color.hex("#ff0000")], step=Color.hsl(0.5, 0.0, 0.0))
    assert seq[1].hex == "#00ffff"
    assert seq[2].hex == "#ff0000"


def test_seeded_sequence_clamps_saturation_and_lightness():
    seq = LinearColorSequence(colors=[Color.hsl(0.0, 0.9, 0.9)], step=Color.hsl(0.0, 0.5, 0.5))
    h, s, l = seq[1].hsl
    assert s == 1.0 and l == 1.0


def test_rotating_sequence_from_matplotlib():
    seq = RotatingColorSequence().from_matplotlib_color_sequence("tab10")
    assert seq[0].hex == "#1f77b4"
    assert seq[10].hex == seq[0].hex
