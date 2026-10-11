import unittest

from receiverAddress import buildReceiverAddress


class BuildReceiverAddressTests(unittest.TestCase):
    def test_all_empty_falls_back_to_mbox(self):
        self.assertEqual(buildReceiverAddress(), r"\mbox{}")

    def test_all_none_falls_back_to_mbox(self):
        self.assertEqual(
            buildReceiverAddress(None, None, None, None, None, None), r"\mbox{}"
        )

    def test_whitespace_only_is_treated_as_empty(self):
        self.assertEqual(
            buildReceiverAddress(company="   ", prename=" ", surname="\t"),
            r"\mbox{}",
        )

    def test_full_address_uses_four_lines(self):
        result = buildReceiverAddress(
            company="Firma GmbH",
            prename="Max",
            surname="Mustermann",
            street="Musterstr. 1",
            plz="12345",
            place="Musterstadt",
        )
        self.assertEqual(
            result,
            r"Firma GmbH\\Max Mustermann\\Musterstr. 1\\12345 Musterstadt",
        )

    def test_single_company_line_has_no_trailing_separator(self):
        self.assertEqual(buildReceiverAddress(company="Firma"), r"Firma")

    def test_person_only(self):
        self.assertEqual(
            buildReceiverAddress(prename="Max", surname="Mustermann"),
            r"Max Mustermann",
        )

    def test_prename_only(self):
        self.assertEqual(buildReceiverAddress(prename="Max"), r"Max")

    def test_surname_only(self):
        self.assertEqual(buildReceiverAddress(surname="Mustermann"), r"Mustermann")

    def test_city_only_joins_plz_and_place(self):
        self.assertEqual(
            buildReceiverAddress(plz="12345", place="Musterstadt"), r"12345 Musterstadt"
        )

    def test_plz_only(self):
        self.assertEqual(buildReceiverAddress(plz="12345"), r"12345")

    def test_place_only(self):
        self.assertEqual(buildReceiverAddress(place="Musterstadt"), r"Musterstadt")

    def test_street_only(self):
        self.assertEqual(buildReceiverAddress(street="Musterstr. 1"), r"Musterstr. 1")

    def test_empty_lines_between_values_are_skipped(self):
        self.assertEqual(
            buildReceiverAddress(company="Firma", place="Stadt"), r"Firma\\Stadt"
        )

    def test_person_line_precedes_street_when_no_company(self):
        self.assertEqual(
            buildReceiverAddress(prename="Max", surname="M", street="Str 1"),
            r"Max M\\Str 1",
        )

    def test_values_are_stripped(self):
        self.assertEqual(
            buildReceiverAddress(company="  Firma  ", place=" Stadt "),
            r"Firma\\Stadt",
        )

    def test_latex_specials_are_escaped_per_line(self):
        self.assertEqual(
            buildReceiverAddress(company="A & B", prename="100%", surname="C#"),
            r"A \& B\\100\% C\#",
        )

    def test_line_separators_are_not_escaped(self):
        self.assertEqual(
            buildReceiverAddress(company="A&B", street="C%D"), r"A\&B\\C\%D"
        )

    def test_no_trailing_separator_after_last_line(self):
        result = buildReceiverAddress(
            company="Firma",
            prename="Max",
            surname="Mustermann",
            street="Str",
            plz="12345",
            place="Stadt",
        )
        self.assertFalse(result.endswith("\\\\"))
        self.assertEqual(result.count("\\\\"), 3)

    def test_output_is_single_line(self):
        result = buildReceiverAddress(
            company="Firma", prename="Max", surname="Mustermann", place="Stadt"
        )
        self.assertNotIn("\n", result)


if __name__ == "__main__":
    unittest.main()
