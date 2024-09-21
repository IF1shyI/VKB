import fs from 'fs';
import path from 'path';

export async function post({ request }) {
    const data = await request.json();
    const { name, email, subject, message } = data;

    const markdownContent = `
# Kontaktförfrågan

**Namn**: ${name}  
**Email**: ${email}  
**Ämne**: ${subject}  

**Meddelande**:  
${message}

---

Datum: ${new Date().toLocaleString()}
`;

    const fileName = `contact_${Date.now()}.md`;
    const filePath = path.join(process.cwd(), 'feedback', fileName);

    return new Promise((resolve, reject) => {
        fs.writeFile(filePath, markdownContent, (err) => {
            if (err) {
                console.error('Fel vid skapandet av Markdown-filen:', err);
                return reject(new Response('Serverfel. Kunde inte spara meddelandet.', { status: 500 }));
            }
            console.log('Markdown-fil skapad:', filePath);
            resolve(new Response('Formulärdata mottaget och sparad.', { status: 200 }));
        });
    });
}
