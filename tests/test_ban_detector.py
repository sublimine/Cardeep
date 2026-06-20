"""Semantic block detection: 200-interstitials, 403-challenge vs 403-ban, 404."""
from pipeline.engine import ban_detector
from pipeline.engine.ban_detector import Verdict


def test_clean_200_is_ok():
    assert ban_detector.classify(200, "<html><body>" + "x" * 40000 + "</body></html>") == Verdict.OK


def test_cloudflare_just_a_moment_200_is_challenge():
    body = "<html><head><title>Just a moment...</title></head>" \
           "<body>Checking your browser. Ray ID: abc cf-chl-</body></html>"
    assert ban_detector.classify(200, body) == Verdict.CHALLENGE


def test_cf_mitigated_header_is_challenge_regardless_of_code():
    assert ban_detector.classify(200, "x" * 50000, {"cf-mitigated": "challenge"}) == Verdict.CHALLENGE


def test_datadome_interstitial_is_challenge():
    body = "<html>blocked by datadome geo.captcha-delivery.com</html>"
    assert ban_detector.classify(403, body) == Verdict.CHALLENGE


def test_akamai_reference_403_is_challenge():
    body = "Access Denied. Reference #18.abc _abck akamai sensor"
    # contains both ban marker (access denied) AND challenge markers -> challenge
    assert ban_detector.classify(403, body) == Verdict.CHALLENGE


def test_hard_ban_403_is_banned():
    body = "Access Denied: you have been blocked. " + "y" * 3000
    assert ban_detector.classify(403, body) == Verdict.BANNED


def test_404_is_not_found():
    assert ban_detector.classify(404, "nope") == Verdict.NOT_FOUND
    assert ban_detector.classify(410, "gone") == Verdict.NOT_FOUND


def test_empty_403_is_challenge_not_ban():
    # An empty/short 403 (no body) is more likely a silent challenge than a ban.
    assert ban_detector.classify(403, "") == Verdict.CHALLENGE


def test_is_blocked_helper():
    assert ban_detector.is_blocked(403, "datadome") is True
    assert ban_detector.is_blocked(200, "x" * 40000) is False
