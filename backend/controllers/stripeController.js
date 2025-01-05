require('dotenv').config();
const stripe = require('stripe')(process.env.STRIPE_KEY);

// Hantera Stripe-betalning
exports.createPaymentIntent = async (req, res) => {
  const { tierPrice, customerName, customerEmail } = req.body;

  if (!tierPrice || !customerName || !customerEmail) {
    return res.status(400).json({ message: 'Missing required fields' });
  }

  try {
    const customer = await stripe.customers.create({
      name: customerName,
      email: customerEmail,
    });

    const paymentIntent = await stripe.paymentIntents.create({
      amount: tierPrice * 100, // Belopp i öre
      currency: 'sek',
      customer: customer.id,
    });

    res.status(200).json({
      client_secret: paymentIntent.client_secret,
      customer_id: customer.id,
    });
  } catch (err) {
    res.status(500).json({ message: 'Error creating payment intent', error: err.message });
  }
};
