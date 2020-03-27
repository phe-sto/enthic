# -*- coding: utf-8 -*-
"""
==================================
Test the flask server and it's API
==================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from json import loads, dumps
from random import randint, choice
from string import ascii_letters, digits

import pytest
from enthic.utils.error_json_response import ErrorJSONResponse
from enthic.utils.json_response import JSONResponse
from enthic.utils.ok_json_response import OKJSONResponse
from requests import get, post, delete, put

EXISTING_SIREN_EXISTING_YEAR = ((5420120, 2016), (5450119, 2015),
                                (5520176, 2016), (5520242, 2016),
                                (5541552, 2017), (5720644, 2016),
                                (5580113, 2016), (5580501, 2016),
                                (5580683, 2016), (5620034, 2016),
                                (5420120, 2017), (5620190, 2016),
                                (5650031, 2016), (5650148, 2016),
                                (5650189, 2016), (5680541, 2016),
                                (5720164, 2016), (5720552, 2018),
                                (5720602, 2016), (5720610, 2016),
                                (5720602, 2016), (5720610, 2016),
                                (5580113, 2016))

EXISTING_SIREN = tuple(siren[0] for siren in EXISTING_SIREN_EXISTING_YEAR)

NOT_EXISTING_SIREN = (999999999, 999999998, 999999998, 999999997,
                      999999996, 999999995, 999999994, 999999993,
                      999999992, 999999991)

EXISTING_SIREN_NOT_EXISTING_YEAR = tuple((siren, 1254) for siren in EXISTING_SIREN)

EXISTING_DENOMINATION_EXISTING_YEAR = (
    ("AESTERA ALLIANCE EVOLUTION SYNERGIE TECHNIQUE RESTAURATION A", 2013),
    ("AESTERA GESTION", 2013),
    ("AESTETYPE", 2018),
    ("AESTHESIS", 2016),
    ("AESTHETIC", 2017),
    ("L'ABRI FAMILIAL", 2016),
    ("AESTHETIC ROMY D", 2015),
    ("AESTHETIC SOLUTIONS TECHNOLOGIES", 2016),
    ("AESUS", 2016),
    ("AET", 2017),
    ("AET CONSULTING", 2017),
    ("AET DEVELOPPEMENT", 2016),
    ("AET TECHNOLOGIES", 2016),
    ("AETA AUDIO SYSTEMS", 2016),
    ("AETA CONSEIL", 2016),
    ("AETAD", 2016),
    ("AETAS DEVELOPPEMENT", 2015),
    ("AETB", 2016),
    ("AETERNAM FILMS", 2016),
    ("AETERNIA", 2016),
    ("AETH", 2016),
    ("AETHER", 2017),
    ("AETHER FINANCIAL SERVICES", 2016),
    ("AETHER STUDIO", 2016),
    ("AETHICA", 2016))

EXISTING_DENOMINATION_NO_BUNDLE = ("ETABLISSEMENTS GAETAN COPPIER ET FILS",
                                   "SOCIETE RIQUIER ET CIE",
                                   "EMILE BARNEAUD ET FILS",
                                   "SARL BAS ALPINE D AUTOCARS",
                                   "2GS SECURITE",
                                   "2GS SERVICES",
                                   "2GSI",
                                   "2GSL CONSEILS",
                                   "2GT",)

EXISTING_SIREN_NO_BUNDLE = (5450093,
                            5550108,
                            5620174,
                            5620364,
                            638201871,
                            500206172,
                            353135718,
                            350655205,
                            423419704,
                            509430609,
                            329490510,
                            352688758,
                            487800070,
                            338688591,
                            451644868,
                            339933715,
                            391969623,
                            327743977,
                            328612247,
                            509412177)
EXISTING_DENOMINATION = tuple(
    denomination[0] for denomination in EXISTING_DENOMINATION_EXISTING_YEAR)

NOT_EXISTING_DENOMINATION = tuple(
    denomination + "ZzzzzzZ99996666" for denomination in EXISTING_DENOMINATION)


def test_ok_json_response():
    """
    Test OKJSONResponse with wrong object.
    """
    with pytest.raises(TypeError):
        OKJSONResponse({2})


def test_error_json_response():
    """
    Test ErrorJSONResponse with wrong object.
    """
    with pytest.raises(TypeError):
        ErrorJSONResponse({2})


def test_json_response():
    """
    Test JSONResponse with wrong object.
    """
    with pytest.raises(TypeError):
        JSONResponse({2})


@pytest.fixture()
def host():
    """
    Fixture of the API host.
       :return: String representing the host address.
    """
    return "127.0.0.1:5000"


@pytest.mark.parametrize("siren", EXISTING_SIREN + EXISTING_SIREN_NO_BUNDLE)
def test_existing_siren(host, siren):
    """
    Test the /company/siren endpoint with existing SIREN. Should return a JSON
    and RC 200.

       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
    """
    response = get("http://" + host + "/company/siren/" + str(siren))
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("siren", NOT_EXISTING_SIREN)
def test_not_existing_siren(host, siren):
    """
    Test the /company/siren endpoint with none existing SIREN. Should return a
    JSON and RC 404.

       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
    """
    response = get("http://" + host + "/company/siren/" + str(siren))
    assert response.status_code == 404, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("siren", (-22,  # NEGATIVE
                                   9999999999)  # SUPERIOR TO 9
                         )
def test_wrong_siren(host, siren):
    """
    Test the /company/siren endpoint with wrong SIREN. Should return a JSON.

       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
    """
    response = get("http://" + host + "/company/siren/" + str(siren))
    assert response.status_code in (400, 404)


@pytest.mark.parametrize("method", (put,
                                    delete,
                                    post))
def test_siren_wrong_method(host, method):
    """
    Test the /company/siren endpoint with the wrong method. Should return a JSON
    and a 404 status.

       :param host: Fixture of the API host.the wrong method to test.
    """
    response = method("http://" + host + "/company/siren/" + "410660492")
    assert response.status_code == 405, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("siren", EXISTING_SIREN)
def test_existing_siren_average(host, siren):
    """
    Test the /company/siren/average endpoint. Should return a JSON and RC 200.

       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
    """
    response = get("http://" + host + "/company/siren/" + str(siren) + "/average")
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("siren", NOT_EXISTING_SIREN)
def test_not_existing_siren_average(host, siren):
    """
    Test the /company/siren/average endpoint. Should return a JSON and RC 404.

       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
    """
    response = get("http://" + host + "/company/siren/" + str(siren) + "/average")
    assert response.status_code == 404, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("method", (put,
                                    delete,
                                    post))
def test_siren_wrong_method_average(host, method):
    """
    Test the /company/siren/average endpoint with the wrong method. Should
    return a JSON and a 404 status.

       :param host: Fixture of the API host.the wrong method to test.
    """
    response = method("http://" + host + "/company/siren/" + "410660492" + "/average")
    assert response.status_code == 405, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("siren,year", EXISTING_SIREN_NOT_EXISTING_YEAR)
def test_existing_siren_not_existing_year(host, siren, year):
    """
    Test the /company/siren/year endpoint. Should return a JSON  and RC 404.

       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
       :param year: Parametrise fixture of the year to return.
    """
    response = get("http://" + host + "/company/siren/" + str(siren) + "/" + str(year))
    assert response.status_code == 404, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("siren,year", EXISTING_SIREN_EXISTING_YEAR)
def test_existing_siren_existing_year(host, siren, year):
    """
    Test the /company/siren/year endpoint. Should return a JSON  and RC 20.

       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
       :param year: Parametrise fixture of the year to return.
    """
    response = get("http://" + host + "/company/siren/" + str(siren) + "/" + str(year))
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("method", (put,
                                    delete,
                                    post))
def test_siren_year_wrong_method(host, method):
    """
    Test the /company/siren/year endpoint with the wrong method. Should return a
    JSON and a 404 status.

       :param host: Fixture of the API host.the wrong method to test.
    """
    response = method("http://" + host + "/company/siren/" + "410660492/2016")
    assert response.status_code == 405, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("siren,year", ((-22, 20192),  # NEGATIVE
                                        (9999999999, "2019f"))  # SUPERIOR TO 9
                         )
def test_siren_wrong_year(host, siren, year):
    """
    Test the /company/siren/year endpoint. Should return a JSON with
    information a wrong year.

       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
    """
    response = get("http://" + host + "/company/siren/" + str(siren) + "/" + str(year))
    assert response.status_code in (400, 404), "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("siren", (-22,  # NEGATIVE
                                   9999999999))  # SUPERIOR TO 9
def test_wrong_siren_average(host, siren):
    """
    Test the /company/siren/average endpoint with wrong SIREN. Should return a JSON.

       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
    """
    response = get("http://" + host + "/company/siren/" + str(siren) + "/average")
    assert response.status_code in (400, 404)


@pytest.mark.parametrize("denomination", EXISTING_DENOMINATION + EXISTING_DENOMINATION_NO_BUNDLE)
def test_existing_denomination(host, denomination):
    """
    Test the /company/denomination endpoint with existing denomination. Should
    return a JSON and RC 200.

       :param host: Fixture of the API host.
       :param denomination: Parametrise fixture of a company official name.
    """
    response = get("http://" + host + "/company/denomination/" + denomination)
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("denomination", NOT_EXISTING_DENOMINATION)
def test_not_existing_denomination(host, denomination):
    """
    Test the /company/denomination endpoint with fake denomination. Should
    return a JSON and RC404.

       :param host: Fixture of the API host.
       :param denomination: Parametrise fixture of a company official name.
    """
    response = get("http://" + host + "/company/denomination/" + denomination)
    assert response.status_code == 404, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("method", (put,
                                    delete,
                                    post))
def test_denomination_wrong_method(host, method):
    """
    Test the /company/denomination endpoint with the wrong method. Should return a
    JSON and a 404 status.

       :param host: Fixture of the API host.the wrong method to test.
    """
    response = method("http://" + host + "/company/denomination/" + "410660492/")
    assert response.status_code == 405, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("denomination", EXISTING_DENOMINATION)
def test_denomination_average(host, denomination):
    """
    Test the /company/denomination/average endpoint. Should return a JSON.

       :param host: Fixture of the API host.
       :param denomination: Parametrise fixture of a company official name.
    """
    response = get("http://" + host + "/company/denomination/" + denomination + "/average")
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("method", (put,
                                    delete,
                                    post))
def test_denomination_wrong_method_average(host, method):
    """
    Test the /company/denomination/average endpoint with the wrong method.
    Should return a JSON and a 404 status.

       :param host: Fixture of the API host.the wrong method to test.
    """
    response = method("http://" + host + "/company/denomination/" + "410660492/average")
    assert response.status_code == 405, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("denomination,year", EXISTING_DENOMINATION_EXISTING_YEAR)
def test_denomination_year(host, denomination, year):
    """
    Test the /company/denomination/year endpoint. Should return a JSON and RC 200.

       :param host: Fixture of the API host.
       :param denomination: Parametrise fixture of a company official name.
       :param year: Parametrise fixture of the year to return.
    """
    response = get("http://" + host + "/company/denomination/" + denomination + "/" + str(year))
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("method", (put,
                                    delete,
                                    post))
def test_denomination_year_wrong_method(host, method):
    """
    Test the /company/denomination/year endpoint with the wrong method. Should return a
    JSON and a 404 status.

       :param host: Fixture of the API host.the wrong method to test.
    """
    response = method("http://" + host + "/company/denomination/" + "410660492/2016")
    assert response.status_code == 405, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("denomination,year", (("RCV PEINTURE", 209),
                                               ("RESEAUX ELECTRIQUE & INFORMATIQUE", '201s9'),
                                               ("TOTO SASU", 20189)))  # DOES NOT EXIST
def test_denomination_wrong_year(host, denomination, year):
    """
    Test the /company/denomination/year endpoint. Should return a JSON. Tested
    with a wrong year.

       :param host: Fixture of the API host.
       :param denomination: Parametrise fixture of a company official name.
       :param year: Parametrise fixture of the year to return.
    """
    response = get("http://" + host + "/company/denomination/" + denomination + "/" + str(year))
    assert response.status_code == 400, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


def test_ontology(host):
    """
    Test the GET of the ontology on the URL /company/ontology.

       :param host: Fixture of the API host.
    """
    response = get("http://" + host + "/company/ontology")
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("method", (put,
                                    delete,
                                    post))
def test_ontology_wrong_method(host, method):
    """
    Test the ontology on the URL /company/ontology endpoint with the wrong
    method. Should return a JSON and a 405 status.

       :param host: Fixture of the API host.the wrong method to test.
    """
    response = method("http://" + host + "/company/ontology")
    assert response.status_code == 405, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("probe,limit", [(probe, randint(0, 20)) for probe in
                                         EXISTING_DENOMINATION + EXISTING_SIREN +
                                         NOT_EXISTING_SIREN + NOT_EXISTING_DENOMINATION])
def test_search(host, probe, limit):
    """
    Test the /company/search endpoint with existing or not probes. Should return
    a JSON and RC 200.

       :param host: Fixture of the API host.
       :param probe: Parametrize fixture of the string to search.
       :param limit: Parametrize fixture of limit of result to return.
    """
    response = post("http://" + host + "/company/search/", dumps({"probe": probe, "limit": limit}))
    assert loads(response.text) is not None, "NOT RETURNING A JSON, INSTEAD: %s" % response.text
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("probe,limit", [(choice(digits), randint(0, 1000)) for _ in range(0, 100)])
def test_search_random_letter(host, probe, limit):
    """
    Test the /company/search endpoint with a random letter. Should return a JSON.

       :param probe: Parametrize fixture of the string to search.
       :param limit: Parametrize fixture of limit of result to return.
       :param host: Fixture of the API host.
    """
    letter = choice(ascii_letters)
    response = post("http://" + host + "/company/search/", dumps({"probe": probe,
                                                                  "limit": limit}))
    assert response.status_code == 200, "WRONG HTTP RETURN CODE WITH PUN {}".format(letter)
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("probe,limit", [(choice(digits), randint(0, 1000)) for _ in range(0, 100)])
def test_search_random_digit(host, probe, limit):
    """
    Test the /company/search endpoint with a random letter. Should return a JSON.

       :param probe: Parametrize fixture of the string to search.
       :param limit: Parametrize fixture of limit of result to return.
       :param host: Fixture of the API host.
    """
    digit = choice(digits)
    response = post("http://" + host + "/company/search/", dumps({"probe": probe,
                                                                  "limit": limit}))
    assert response.status_code == 200, "WRONG HTTP RETURN CODE WITH PUN {}".format(digit)
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("body", ((1),
                                  ("toto"),
                                  (True),
                                  )
                         )
def test_search_wrong_type(host, body):
    """
    Test the /company/search endpoint with wrong type requets body. Should
    return a JSON and status 400.

       :param host: Fixture of the API host.
       :param body: Parametrize fixture of the request body.
    """
    response = post("http://" + host + "/company/search/", dumps(body))
    assert response.status_code == 400, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("probe,per_page", [(probe, randint(0, 40)) for probe in
                                            EXISTING_DENOMINATION + EXISTING_SIREN +
                                            NOT_EXISTING_SIREN + NOT_EXISTING_DENOMINATION])
def test_search_page(host, probe, per_page):
    """
    Test the /company/search/page endpoint with existing or not probes. Should return
    a JSON and RC 200.

       :param host: Fixture of the API host.
       :param probe: Parametrize fixture of the string to search.
       :param per_page: Parametrize fixture of the number of results by page.
    """
    response = get(
        "http://" + host + "/company/search/page?probe=%s&per_page=%s" % (probe, per_page))
    assert loads(response.text) is not None, "NOT RETURNING A JSON, INSTEAD: %s" % response.text
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("probe", EXISTING_DENOMINATION + EXISTING_SIREN)
def test_search_page_random_page(host, probe):
    """
    Test the /company/search/page endpoint with existing on a random page.
    Should return a JSON and RC 200.

       :param host: Fixture of the API host.
       :param probe: Parametrize fixture of the string to search.
    """
    response = get(
        "http://" + host + "/company/search/page?probe=%s&page=1&per_page=1" % probe)
    assert loads(response.text) is not None, "NOT RETURNING A JSON, INSTEAD: %s" % response.text
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("probe,limit", (("toto", "pouet"),
                                         (2, "toto"),
                                         ("toto", 10000000000),
                                         )
                         )
def test_wrong_value_search(host, probe, limit):
    """
    Test the /company/search endpoint posting a wrong JSON values. Should return
    a JSON.

       :param host: Fixture of the API host.
       :param probe: Parametrize fixture of the string to search.
       :param limit: Parametrize fixture of limit of result to return.
    """
    response = post("http://" + host + "/company/search/", dumps({"probe": probe, "limit": limit}))
    assert response.status_code == 400
    assert loads(response.text)["@type"] == "Error", "NOT A JSON-LD ERROR"


def test_wrong_key_search(host):
    """
    Test the /company/search endpoint posting a wrong JSON keys. Should return a
    JSON.

       :param host: Fixture of the API host.
       :param probe: Parametrize fixture of the string to search.
       :param limit: Parametrize fixture of limit of result to return.
    """
    response = post("http://" + host + "/company/search/", dumps({"toto": "pouet", "limit": 2}))
    assert response.status_code == 400
    assert loads(response.text)["@type"] == "Error", "NOT A JSON-LD ERROR"


@pytest.mark.parametrize("page", ("/404.html",
                                  "/index.html",
                                  "/documentation/index.html",
                                  "/500.html",))
def test_html_pages(host, page):
    """
    Test static html page, such as swagger description page 500 and 404.

       :param host: Fixture of the API host.
       :param page: Parametrise fixture of a page to get.
    """
    response = get("http://" + host + page)
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("page", ("/4040.html",
                                  "/indexx.html",
                                  "/5005.html",))
def test_404(host, page):
    """
    Test unknown URL.

       :param host: Fixture of the API host.
       :param page: Parametrise fixture of a page to get.
    """
    response = get("http://" + host + page)
    assert response.status_code == 404, "WRONG HTTP RETURN CODE"


def test_swagger_json(host):
    """
    Test static swagger.json.

       :param host: Fixture of the API host.
    """
    response = get("http://" + host + "/swagger.json")
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text)["swagger"] == "2.0", \
        "NOT A SWAGGER 2.0 JSON DESCRIPTION"
