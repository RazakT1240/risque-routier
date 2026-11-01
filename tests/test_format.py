"""Formatage français unique (CLAUDE.md §9)."""

from app.components.format import (
    INSECABLE,
    MILLIERS,
    MOINS,
    NA,
    delta,
    fmt_number,
    fmt_pct,
    fmt_ratio,
)


def test_fmt_number():
    assert fmt_number(12345) == f"12{MILLIERS}345"
    assert fmt_number(1234.56, 1) == f"1{MILLIERS}234,6"
    assert fmt_number(-3.2, 1) == f"{MOINS}3,2"
    assert fmt_number(-0.01, 1) == "0,0"
    assert fmt_number(None) == NA
    assert fmt_number(float("nan")) == NA
    assert fmt_number(2.5, 1, signe=True) == "+2,5"


def test_fmt_pct_et_ratio():
    assert fmt_pct(12.44) == f"12,4{INSECABLE}%"
    assert fmt_ratio(1.316) == f"×{INSECABLE}1,32"
    assert fmt_pct(None) == NA


def test_delta_suit_le_sens_pour_l_assureur():
    hausse = delta(110, 100, "2024")
    assert hausse["sens"] == "defavorable" and hausse["texte"].startswith("▲")
    baisse = delta(90, 100, "2024")
    assert baisse["sens"] == "favorable" and baisse["texte"].startswith("▼")
    # Indicateur où « plus » est bon : la hausse devient favorable
    assert delta(110, 100, "2024", plus_est_mauvais=False)["sens"] == "favorable"
    assert delta(100, 100, "2024")["sens"] == "neutre"
    assert delta(100, None, "2019")["texte"].startswith(NA)


def test_valeurs_inattendues():
    import pandas as pd
    assert fmt_number(pd.NA) == NA
    assert fmt_number("abc") == NA
    assert fmt_ratio(-0.5) == f"×{INSECABLE}{MOINS}0,50"
    assert delta(100.04, 100, "2024")["sens"] == "neutre"
