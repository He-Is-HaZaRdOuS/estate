from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import UserError
from odoo.tests import tagged

@tagged('post_install', '-at_install')
class EstatePropertyTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(EstatePropertyTestCase, cls).setUpClass()

        # Creating a test partner
        cls.partner_a = cls.env['res.partner'].create({
            'name': 'Test Partner A',
            'email': 'partner_a@example.com',
            'phone': '+123456789',
            'company_id': 1,
        })

        # Creating a test property
        cls.property = cls.env['estate.property'].create({
            'name': 'Test Property',
            'expected_price': 100000,
            'state': 'new',
            'garden': True,
            'garden_area': 100,
            'garden_orientation': 'north',
            'buyer': cls.partner_a.id,
        })

        # Creating an offer for the property
        cls.offer = cls.env['estate.property.offer'].create({
            'price': 50000,
            'property_id': cls.property.id,
            'partner_id': cls.partner_a.id,
            'state': 'accepted',
        })

    def test_create_offer_on_sold_property(self):
        """Test that creating an offer on a sold property raises a UserError."""
        self.property.state = 'sold'
        with self.assertRaises(UserError):
            self.env['estate.property.offer'].create({
                'price': 60000,
                'property_id': self.property.id,
                'partner_id': self.partner_a.id,
            })

    def test_sell_property_without_accepted_offer(self):
        """Test that trying to sell a property without an accepted offer raises a UserError."""
        self.property.offer_ids.unlink()  # Remove all offers
        with self.assertRaises(UserError):
            self.property.action_sell()

    def test_successful_property_sale(self):
        """Test that a property with an accepted offer can be successfully sold."""
        self.property.offer_ids = [(0, 0, {'price': 70000, 'state': 'accepted', 'partner_id': self.partner_a.id})]
        self.property.action_sell()
        self.assertEqual(self.property.state, 'sold', "The property state should be 'sold'.")

    def test_garden_reset_on_uncheck(self):
        """Test that Garden Area and Orientation are reset when the Garden checkbox is unchecked."""
        # Simulate opening the form view of the property
        with Form(self.property) as property_form:
            # Initially, garden is checked, so garden_area and garden_orientation should have values
            self.assertEqual(property_form.garden, True)
            self.assertEqual(property_form.garden_area, 100)
            self.assertEqual(property_form.garden_orientation, 'north')

            # Uncheck the garden checkbox
            property_form.garden = False

            # Save the form
            property_form.save()

        # After unchecking the garden checkbox, garden_area and garden_orientation should be reset
        self.assertEqual(self.property.garden_area, 0, "The garden area should be reset to 0.")
        self.assertFalse(self.property.garden_orientation, "The garden orientation should be reset.")
