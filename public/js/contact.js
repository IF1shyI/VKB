  // Client-side JavaScript för att hantera form submission
  document.getElementById('contactFormElement').addEventListener('submit', async function (e) {
    e.preventDefault();  // Förhindrar att sidan laddas om

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const subject = document.getElementById('subject').value;
    const message = document.getElementById('message').value;

    try {
      const response = await fetch('/api/submit-form', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name,
          email: email,
          subject: subject,
          message: message,
        }),
      });

      if (response.ok) {
        document.getElementById('contactForm').style.display = 'none';
        const thankYouMessage = document.getElementById('thankYouMessage');
        thankYouMessage.style.display = 'block';
        setTimeout(() => {
          thankYouMessage.classList.add('show');
        }, 100);
      } else {
        alert('Något gick fel. Försök igen senare.');
      }
    } catch (error) {
      console.error('Fel vid skickandet av formuläret:', error);
      alert('Ett tekniskt fel inträffade. Försök igen senare.');
    }
  });